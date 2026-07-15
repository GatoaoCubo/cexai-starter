"""Tenant-scoped Supabase data adapter -- the framework-side data-plane guard
(mission MULTITENANT_DATA_PLANE, task T1; spec_multitenant_data_plane_v1 A.1-A.5).

This is the data lane's sibling of ``governance.rbac.inference_gate`` (C2). The
inference gate stops the framework DISPATCHING a cross-tenant inference; this
adapter stops the framework ISSUING a cross-tenant DB call -- the SAME fail-closed
string-equality invariant, enforced on a third surface (file -> inference -> data).

THE BOUNDARY RULE (ADR D6 / spec A.1 -- non-negotiable):
    The adapter takes ``tenant_id`` as an EXPLICIT parameter and MUST NOT import
    repo-root ``_tools``. ``cexai`` is extraction-bound (cexai/pyproject.toml:
    "designed for eventual extraction ... does NOT discover this tree"). Importing
    ``_tools.cex_tenant_paths`` would (a) fail outright from the package context
    (``ModuleNotFoundError: cex_tenant_paths``, already verified by
    ``inference_gate.py``) and (b) drag monorepo filesystem state
    (``ROOT`` / ``TENANTS_DIR`` / ``.cex/tenants/``) into the package. So the
    adapter MIRRORS the cross-tenant equality invariant the same way
    ``inference_gate.py`` does -- it does NOT import it (see
    ``_deny_cross_tenant_equality`` below). ``_tools`` resolves ``CEX_TENANT_ID``
    at the edge and PASSES ``tenant_id`` IN (spec A.4); the package never reads the
    environment and is a pure function of its arguments.

WHY MIRROR, NOT IMPORT (spec A.3, identical seam to C2):
    ``inference_gate.py`` already documents and resolves this exact tension. The
    mirror keeps ONE behavioural contract across three enforcement points: file
    (``deny_cross_tenant``), inference (``authorize_inference``), and data
    (``SupabaseDataAdapter``). If a future refactor moves ``deny_cross_tenant``
    into ``cexai``, all three swap to the single primitive -- the
    ``_deny_cross_tenant_equality`` helper isolates the mirrored logic so the swap
    is a one-function change (same TODO as ``inference_gate.py``).

POOLED-CONNECTION HAZARD (spec A.5 -- load-bearing):
    ``set_config(..., is_local := true)`` is MANDATORY. Supabase pooled connections
    (PgBouncer / Supavisor transaction mode) are reused across requests. A
    ``set_config`` with ``is_local := false`` would leak tenant A's claim to the
    next borrower of the connection -> a silent cross-tenant read. The adapter
    ALWAYS binds with ``is_local=True`` (transaction-scoped) and the caller binds
    INSIDE the same transaction as the query.

HONEST CAVEAT (framework vs DB): the cross-tenant mirror here is DEFENCE-IN-DEPTH.
    The DB-side guard is the RESTRICTIVE RLS policy (spec B.2); this framework-side
    check refuses an obviously-crossing call BEFORE it hits the DB. RLS remains the
    authoritative boundary; a missing/misapplied policy is not covered by this
    module (that is the drift-check's job, spec C.2).

ASCII-only per .claude/rules/ascii-code-rule.md. Import-light (Article VIII): no
concrete DB driver is imported at module load -- the ``DbSession`` Protocol is the
injected seam (a real impl wraps psycopg/asyncpg from a Supabase pooler; offline
tests pass a fake).

absorbs: convergence/multitenant-data-plane (T1 -- SupabaseDataAdapter)
"""

from __future__ import annotations

import json
import logging
from collections.abc import Callable, Mapping, Sequence
from typing import Any, Protocol, runtime_checkable

from cexai.governance.data.errors import TenantDataDenied

__all__ = [
    "DbSession",
    "SupabaseDataAdapter",
]

# Dedicated audit logger (security observability -- mission MULTITENANT_DATA_PLANE
# adversarial-review MEDIUM: cross-tenant denials were invisible). Same stdlib
# idiom every cexai module uses (``logging.getLogger("cexai.<module>")`` -- e.g.
# cexai.memory.vector). Self-contained in stdlib so the extraction boundary holds
# (cexai MUST NOT import repo-root tools). A WARNING-level structured event is
# emitted on EVERY deny so a probing pattern (repeated cross-tenant attempts)
# leaves a trace an alert can fire on. Handler config is the host app's job; this
# module only emits.
_AUDIT = logging.getLogger("cexai.governance.audit")

# The audit event name carried on every cross-tenant-denial record (a stable
# token an alert rule / log query keys on, never a parsed message).
_AUDIT_EVENT_CROSS_TENANT_DENIED = "cross_tenant_denied"


def _audit_cross_tenant_denied(
    *, bound: str | None, target: str | None, operation: str, reason: str
) -> None:
    """Emit ONE structured WARNING audit event for a cross-tenant denial.

    REDACTION CONTRACT (founder-mandated -- secrets-redacted): the event logs ONLY
    non-secret identifiers -- the bound tenant id, the target tenant id, the
    operation tag, and the reason token. It NEVER logs SQL text, query params, row
    / payload data, or any credential. Tenant ids are non-secret routing
    identifiers (the same values the deny message already carries), so logging them
    is safe; everything sensitive is deliberately absent from the call site.

    DEGRADE-NEVER (founder-mandated -- observability must never break the security
    path): the entire emit is wrapped so that ANY logging failure (a broken
    handler, a serialization error, a monkeypatched logger that raises) is
    swallowed here and the caller still raises ``TenantDataDenied``. A blanket
    ``except Exception`` is correct: this is a best-effort side-channel, not the
    security control -- the deny is.

    The fields ride on the LogRecord via ``extra=`` (so a structured handler /
    ``caplog`` can read ``record.event`` / ``record.bound_tenant`` / ... ) AND are
    interpolated into the human message from the SAME non-secret values."""
    try:
        _AUDIT.warning(
            "cross_tenant_denied op=%s reason=%s bound=%r target=%r",
            operation,
            reason,
            bound,
            target,
            extra={
                "event": _AUDIT_EVENT_CROSS_TENANT_DENIED,
                "bound_tenant": bound,
                "target_tenant": target,
                "operation": operation,
                "reason": reason,
            },
        )
    except Exception:  # noqa: BLE001 -- degrade-never: logging must never break deny
        # Best-effort observability. Swallow EVERYTHING so the security deny the
        # caller is about to raise is neither suppressed nor altered. Do not even
        # re-log here (a second emit could hit the same broken handler).
        pass

# The FIXED PG session-claim key the adapter writes (spec A.2 / B.2). Both planes
# -- Supabase Auth (end-users) and the agent set_config path -- resolve the tenant
# out of this same claim, so ONE RLS expression serves both.
_DEFAULT_CLAIM_KEY = "request.jwt.claims"

# The VERIFIED-claims field carrying the bound tenant. Mirrors
# ``authorize_inference``'s ``verified_claims["tenant"]`` -- the value the C1
# verifier already validated, never a caller-asserted one.
_TENANT_CLAIM_FIELD = "tenant"

# The column name the RLS policy reads out of the claim JSON (spec B.2:
# ``request.jwt.claims ... ->> 'tenant_id'``).
_CLAIM_TENANT_ID_FIELD = "tenant_id"


@runtime_checkable
class DbSession(Protocol):
    """The minimal pooled-connection seam the adapter drives (spec A.2).

    An injected, test-fakeable Protocol (mirrors ``jwt_guard``'s injected
    ``verifier``): a real impl wraps a psycopg/asyncpg connection borrowed from a
    Supabase pooler; offline tests pass a fake. The adapter NEVER imports a
    concrete driver at module load (Article VIII -- import-light)."""

    def execute(self, sql: str, params: Sequence[Any] | None = ...) -> Any:
        """Execute ``sql`` with optional positional ``params`` and return the
        driver-native result (cursor / rows). The adapter does not interpret the
        result -- it is the seam to the live connection."""
        ...

    def set_config(self, key: str, value: str, is_local: bool) -> None:
        """Set a PG run-time setting (``SELECT set_config(key, value,
        is_local)``). ``is_local=True`` scopes it to the current transaction so a
        pooled connection cannot leak it to the next borrower (spec A.5)."""
        ...


def _deny_cross_tenant_equality(target: str, bound: str, op: str = "data") -> str:
    """The mirrored cross-tenant equality invariant (spec A.3 -- NOT imported).

    Deliberately identical in semantics to ``_tools.cex_tenant_paths.
    deny_cross_tenant``'s core check and to ``inference_gate.
    _deny_cross_tenant_equality``: fail-closed STRING EQUALITY -- a principal bound
    to ``bound`` may touch ``target`` ONLY when ``target == bound``. Returns the
    validated ``target`` on allow; raises ``TenantDataDenied('cross_tenant', ...)``
    on mismatch. Isolated as its own function so that if ``deny_cross_tenant`` ever
    becomes cleanly importable from this package, the swap is a one-line change
    here and nowhere else.

    NOTE on the comparison: like ``deny_cross_tenant`` this is exact string
    equality with no normalization. The bound tenant is the one a C1 verifier
    already validated as part of an authentic signed token (trusted input); the
    integrity guarantee is the signature, so this module does not re-sanitize."""
    if target != bound:
        raise TenantDataDenied("cross_tenant", bound=bound, target=target, op=op)
    return target


def _coerce_tenant(value: Any) -> str:
    """Project a raw tenant value to a stripped string. ``None`` -> empty string;
    everything else is ``str()``-d then stripped. Empty result means 'no usable
    tenant', which every caller treats as a fail-closed deny."""
    if value is None:
        return ""
    return str(value).strip()


class SupabaseDataAdapter:
    """Tenant-scoped data adapter (ADR D6 / spec A.2).

    Constructed with a ``DbSession`` factory and the FIXED claim key
    ``request.jwt.claims``. Every method takes ``tenant_id`` EXPLICITLY; none reads
    ``CEX_TENANT_ID`` (that resolution is the ``_tools`` edge's job -- spec A.4), so
    the adapter stays a pure function of its arguments and the extraction boundary
    holds.

    The ``session_factory`` is held for callers that want the adapter to mint a
    fresh ``DbSession`` (a real impl borrows a pooled connection); the per-call
    methods take a ``session`` explicitly so the claim-bind and the query share ONE
    transaction (spec A.5)."""

    def __init__(
        self,
        session_factory: Callable[[], DbSession],
        *,
        claim_key: str = _DEFAULT_CLAIM_KEY,
    ) -> None:
        self._session_factory = session_factory
        self._claim_key = claim_key

    # -- the agent / framework plane (spec A.4 second plane) ----------------- #
    def bind_session_tenant(
        self, session: DbSession, verified_claims: Mapping[str, Any]
    ) -> str:
        """Set the PG session claim from a C1-VERIFIED principal so RLS applies on
        a pooled connection (spec A.2 / A.4).

        Reads ``verified_claims['tenant']`` -- the VERIFIED claim, never a
        caller-asserted value (same rule as ``authorize_inference``). Emits, via
        ``session.set_config``, the equivalent of::

            SELECT set_config('request.jwt.claims',
                              json_build_object('tenant_id', <tenant>)::text, true)

        with ``is_local=True`` so the claim is scoped to the current transaction
        and never leaks to the next borrower of a pooled connection (spec A.5).

        Returns the bound ``tenant_id``. Fail-closed:
          * ``TenantDataDenied('missing_tenant')`` if the verified claims carry no
            usable ``tenant`` (deny-by-default: the data path has no global
            single-tenant mode, the stricter posture from ``authorize_inference``).
          * ``TenantDataDenied('claim_bind_failed')`` if ``set_config`` itself
            raises -- the claim is not set, so RLS cannot be relied on; refuse
            rather than run the connection unscoped (the deny chains the original
            error as its cause)."""
        bound = _coerce_tenant(verified_claims.get(_TENANT_CLAIM_FIELD))
        if not bound:
            # A bind with no usable verified tenant is a denied bind -- audit it so
            # a probing pattern at the bind tier leaves a trace too (operation=bind).
            # claim_bind_failed (set_config raised) is an infra error, NOT an
            # access denial, so it is deliberately NOT audited here.
            _audit_cross_tenant_denied(
                bound=None, target=None, operation="bind", reason="missing_tenant"
            )
            raise TenantDataDenied("missing_tenant")

        # json.dumps gives the deterministic, injection-safe claim JSON the RLS
        # policy reads (``... ->> 'tenant_id'``). Equivalent to PG
        # json_build_object('tenant_id', <tenant>)::text but built on the framework
        # side so the value is a bound argument, never string-concatenated SQL.
        claim_value = json.dumps({_CLAIM_TENANT_ID_FIELD: bound})
        try:
            session.set_config(self._claim_key, claim_value, is_local=True)
        except TenantDataDenied:
            raise
        except Exception as exc:  # set_config failed -> claim not set -> refuse
            raise TenantDataDenied("claim_bind_failed", bound=bound) from exc
        # Record the bind we just issued on THIS session object so the
        # framework-side mirror (query/write -> _bound_tenant) has a source of
        # truth WITHOUT re-reading PG state. Written only after set_config
        # succeeded, inside the caller's transaction; the adapter keeps no global
        # state of its own (it mutates only the session handed in).
        try:
            session._cexai_bound_tenant = bound  # type: ignore[attr-defined]
        except (AttributeError, TypeError):
            # A session that forbids attribute set (e.g. __slots__ without the
            # field) cannot carry the marker -> the mirror would fail-closed on the
            # next call, so surface the bind as failed now rather than later.
            raise TenantDataDenied("claim_bind_failed", bound=bound)
        return bound

    # -- reads + writes (framework-side mirror is defence-in-depth) ---------- #
    def query(
        self,
        session: DbSession,
        tenant_id: str,
        sql: str,
        params: Sequence[Any] | None = None,
    ) -> Any:
        """Run a read under ``tenant_id`` (spec A.2).

        PRECONDITION: the session claim is already bound for this transaction
        (``bind_session_tenant``). The adapter additionally MIRRORS the cross-tenant
        equality check (``_deny_cross_tenant_equality``) of the bound claim vs
        ``tenant_id`` as defence-in-depth -- RLS (spec B.2) is the DB-side guard,
        this is the framework-side guard. A mismatch raises
        ``TenantDataDenied('cross_tenant')`` BEFORE the DB is touched. A missing /
        empty ``tenant_id`` raises ``TenantDataDenied('missing_tenant')``. Any deny
        emits ONE audit event first (security observability)."""
        self._guard_call(session, tenant_id, op="data", audit_op="query")
        return session.execute(sql, params)

    def write(
        self,
        session: DbSession,
        tenant_id: str,
        sql: str,
        params: Sequence[Any] | None = None,
    ) -> Any:
        """As ``query`` but for INSERT/UPDATE/DELETE (spec A.2). The ``WITH CHECK``
        clause of the RLS policy (spec B.2) is the DB-side write guard; this method
        applies the SAME framework-side cross-tenant mirror as ``query``, raising
        ``TenantDataDenied('cross_tenant')`` on a bound-vs-target mismatch before
        the DB is touched and ``TenantDataDenied('missing_tenant')`` on an empty
        ``tenant_id``. Any deny emits ONE audit event first (security
        observability)."""
        self._guard_call(session, tenant_id, op="data_write", audit_op="write")
        return session.execute(sql, params)

    # -- internal ------------------------------------------------------------ #
    def _guard_call(
        self, session: DbSession, tenant_id: str, *, op: str, audit_op: str
    ) -> str:
        """Shared precondition for ``query`` / ``write``: resolve the bound claim
        off the session and enforce the cross-tenant mirror against ``tenant_id``.

        ``audit_op`` is the normalized operation tag (``query`` / ``write``) carried
        on the audit event; ``op`` is the deny-message tag on ``TenantDataDenied``.

        Every deny path emits EXACTLY ONE structured audit event (WARNING) BEFORE
        the raise (security observability): a missing/empty target, an unbound
        session, and a bound-vs-target mismatch each log once. The emit is
        degrade-never (a logging failure never suppresses the raise -- see
        ``_audit_cross_tenant_denied``).

        Fail-closed:
          * empty ``tenant_id`` -> ``TenantDataDenied('missing_tenant')`` (no target
            to authorize).
          * no bound claim on the session -> ``TenantDataDenied('missing_tenant')``
            (deny-by-default: refuse to run a call whose tenant scope is unknown,
            the same stricter posture as ``authorize_inference``'s
            ``missing_bound_tenant``).
          * bound != target -> ``TenantDataDenied('cross_tenant')`` via
            ``_deny_cross_tenant_equality``."""
        target = _coerce_tenant(tenant_id)
        if not target:
            _audit_cross_tenant_denied(
                bound=None, target=None, operation=audit_op, reason="missing_tenant"
            )
            raise TenantDataDenied("missing_tenant", op=op)
        bound = self._bound_tenant(session)
        if not bound:
            _audit_cross_tenant_denied(
                bound=None, target=target, operation=audit_op, reason="missing_tenant"
            )
            raise TenantDataDenied("missing_tenant", target=target, op=op)
        if target != bound:
            # Emit BEFORE delegating to the mirror so the audit fires exactly once
            # on the mismatch (the mirror then raises). Reason "mismatch" matches the
            # adversarial-review vocabulary; the deny leaf still carries its own
            # "cross_tenant" token unchanged (zero-regression on the raised type).
            _audit_cross_tenant_denied(
                bound=bound, target=target, operation=audit_op, reason="mismatch"
            )
        return _deny_cross_tenant_equality(target, bound, op=op)

    def _bound_tenant(self, session: DbSession) -> str:
        """Read back the tenant bound on ``session`` (set by
        ``bind_session_tenant``). The adapter tracks the bind it issued via a
        per-session marker so the framework-side mirror works against any
        ``DbSession`` (including a fake) WITHOUT a DB round-trip. Absent marker ->
        empty string (treated as unbound -> fail-closed deny upstream)."""
        marker = getattr(session, "_cexai_bound_tenant", None)
        return _coerce_tenant(marker)
