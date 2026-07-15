"""PlaywrightBrowserController -- the policy-gated browser-automation impl (15 US P2).

The concrete implementation behind the frozen ``BrowserController`` Protocol in
``cexai.tools._shared.types``. ``execute`` runs a ``BrowserAction`` against an
injected browser backend and returns the typed 3-plane ``BrowserActionResult``
(Visual ``visual_ref`` / Structured ``structured`` / Action ``action_taken``,
FR-014). The write-gate and audit COMPOSE with the v0.3 ``cexai.governance``
subsystems -- this lane REFERENCES that vocabulary, it does not duplicate it:

  * gating (FR-003/004): a ``write``-class action on a write-capable domain is
    enqueued through the governance ``ApprovalGate`` and the caller receives the
    tools-local ``ApprovalPendingError`` (the still-PENDING, not-yet-terminal
    leaf). After a human verdict, re-invoking ``execute`` resolves the request via
    the same gate: ``approved`` -> the action runs; ``denied`` / ``timeout`` ->
    the governance terminal verdicts ``ApprovalDeniedError`` / ``ApprovalTimeoutError``.
    A read action (or any action with no gate wired / not on a write-capable
    domain) runs ungated.
  * audit (SC-001): every action emits an ``AuditRecord`` through the governance
    ``audit`` exporter, carrying the ``session_id`` -- a multi-step workflow shares
    one ``session_id`` across its records.

Offline-first (Article XIV): the browser backend is INJECTED so the suite drives a
fake. The default backend is an offline-safe headless echo (no live browser, no
network) -- production injects a real Playwright-backed backend through the
vertical-08 MCP gateway. ``playwright`` is therefore NOT a package dependency and
is never imported at module load; it rides behind the ``BrowserBackend`` seam.

Bare construction (``PlaywrightBrowserController()``) does no IO and is a valid
structural ``BrowserController`` -- mirroring the ``FileApprovalGate`` precedent.

absorbs: 15_auto-browser
"""

from __future__ import annotations

import warnings
from collections.abc import Iterable, Mapping
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Protocol, runtime_checkable
from urllib.parse import urlsplit

from cexai.governance._shared.errors import ApprovalDeniedError, ApprovalTimeoutError
from cexai.governance._shared.types import ApprovalGate
from cexai.governance.audit import AuditRecord, audit_path, export_audit
from cexai.tools._shared.errors import ApprovalPendingError
from cexai.tools._shared.types import BrowserAction, BrowserActionResult, BrowserSession

__all__ = [
    "BrowserBackend",
    "WritePolicy",
    "HostWritePolicy",
    "UnconfiguredWritePolicyWarning",
    "PlaywrightBrowserController",
]

_WRITE = "write"
_ANONYMOUS_SESSION = "anonymous"


def _now_iso() -> str:
    """Current UTC instant (tz-aware) as ISO-8601 -- the audit-record timestamp."""
    return datetime.now(timezone.utc).isoformat()


@runtime_checkable
class BrowserBackend(Protocol):
    """The browser-execution seam. ``run`` performs ``action`` against an open
    browser and returns the 3-plane ``BrowserActionResult`` (FR-014). Injected so
    tests run offline with a fake; production wires a Playwright-backed backend
    through the MCP gateway. The controller adds policy-gating + audit AROUND this
    seam -- the backend itself is gate-agnostic."""

    def run(self, action: BrowserAction) -> BrowserActionResult:
        """Execute ``action`` and return its typed 3-plane result."""
        ...


@runtime_checkable
class WritePolicy(Protocol):
    """The domain write-capability classifier (FR-003). ``is_write_capable``
    returns ``True`` for a target whose host is write-capable (POST / form-submit /
    payment / account-change require approval there) and ``False`` for a read-only
    host. Combined with ``BrowserAction.action_class == 'write'`` this decides
    whether the approval gate trips (FR-004)."""

    def is_write_capable(self, target: str) -> bool:
        """Return whether ``target``'s host is a write-capable (approval-gated) domain."""
        ...


class UnconfiguredWritePolicyWarning(RuntimeWarning):
    """Raised (as a ``warnings.warn``, not an exception) when a ``HostWritePolicy``
    is constructed with an EMPTY allowlist and ``strict=False`` (the default). That
    combination classifies NOTHING as write-capable, so every write action runs
    UNGATED -- a default-ALLOW security posture (R-221). The warning makes a prod
    misconfiguration VISIBLE instead of silent; pass ``strict=True`` to fail closed
    instead, or configure ``write_capable_hosts`` to opt out of this warning."""


class HostWritePolicy:
    """A host-allowlist write policy (FR-003 / US P2 acceptance #1). A target is
    write-capable when its host is in the configured set (exact match or a
    subdomain of a listed host). The default empty allowlist classifies NOTHING as
    write-capable -- so with no policy configured, writes are ungated (the v1
    policy.yaml opt-in surface; a malformed real policy.yaml is the impl wave's
    fail-closed ``PolicyConfigError``, out of this offline lane's scope).

    That empty-allowlist default is a default-ALLOW security posture, so it must
    announce itself (R-221): constructing with no hosts and ``strict=False`` (the
    default -- kept for backward compatibility with the offline/v1 flow) emits
    ``UnconfiguredWritePolicyWarning``. Passing ``strict=True`` opts into
    fail-closed behaviour instead -- with an empty allowlist, EVERY target is then
    classified write-capable (so every write is gated) rather than none. A
    non-empty ``write_capable_hosts`` allowlist is unaffected by ``strict`` either
    way -- explicit configuration is never overridden."""

    def __init__(
        self, write_capable_hosts: Iterable[str] = (), *, strict: bool = False
    ) -> None:
        self._hosts = frozenset(host.lower() for host in write_capable_hosts)
        self._strict = strict
        if not self._hosts and not self._strict:
            warnings.warn(
                "HostWritePolicy() constructed with an empty allowlist and "
                "strict=False -- is_write_capable() will classify NOTHING as "
                "write-capable, so every write action runs UNGATED (default-ALLOW). "
                "Configure write_capable_hosts, or pass strict=True to fail closed.",
                UnconfiguredWritePolicyWarning,
                stacklevel=2,
            )

    def is_write_capable(self, target: str) -> bool:
        host = (urlsplit(target).hostname or "").lower()
        if not host:
            return False
        if host in self._hosts:
            return True
        if any(host.endswith("." + listed) for listed in self._hosts):
            return True
        # Unconfigured + strict: fail closed -- treat every resolvable host as
        # write-capable rather than assuming it is read-only (R-221).
        return not self._hosts and self._strict


class _HeadlessEchoBackend:
    """The offline-safe default backend (no live browser, no network). Returns a
    deterministic 3-plane result describing the requested action so bare
    construction + ``execute`` works offline (Article XIV). This is NOT a
    fail-open gate -- gating is decided independently by the policy + approval gate
    BEFORE the backend is ever reached; this default only stands in for a real
    Playwright backend until one is injected by the MCP gateway."""

    def run(self, action: BrowserAction) -> BrowserActionResult:
        return BrowserActionResult(
            action_id=action.action_id,
            action_taken=f"{action.action_type} -> {action.target}",
            visual_ref=None,
            structured={},
        )


class PlaywrightBrowserController:
    """Policy-gated browser controller (the frozen ``BrowserController`` seam).

    Construct bare for the offline defaults (echo backend, no gate, empty policy,
    anonymous session, in-memory-only audit), or inject:

      * ``backend``  -- a ``BrowserBackend`` (fake in tests / Playwright in prod).
      * ``gate``     -- a governance ``ApprovalGate`` (e.g. ``FileApprovalGate``);
                        ``None`` disables gating (every action runs ungated).
      * ``policy``   -- a ``WritePolicy`` classifying write-capable domains.
      * ``session``  -- the ``BrowserSession`` whose ``session_id`` threads every
                        audit record (SC-001).
      * ``audit_root`` + ``mission_id`` -- when set, the audit trail is exported via
                        the governance ``export_audit`` to ``audit_path(mission_id)``.
      * ``requester`` -- the principal recorded as the approval requester / audit
                        actor (defaults to the session id).
      * ``approval_timeout_seconds`` -- informational, carried on a raised
                        ``ApprovalTimeoutError`` (the gate owns the real deadline).

    Gating is active only when a gate is wired AND the action is ``write``-class AND
    the policy classifies the target host write-capable -- so a read action, or any
    action with no gate, runs ungated and returns its result directly.
    """

    def __init__(
        self,
        *,
        backend: BrowserBackend | None = None,
        gate: ApprovalGate | None = None,
        policy: WritePolicy | None = None,
        session: BrowserSession | None = None,
        audit_root: Path | str | None = None,
        mission_id: str | None = None,
        requester: str | None = None,
        approval_timeout_seconds: float = 0.0,
    ) -> None:
        self._backend: BrowserBackend = backend if backend is not None else _HeadlessEchoBackend()
        self._gate = gate
        self._policy: WritePolicy = policy if policy is not None else HostWritePolicy()
        self._session = session
        self._session_id = session.session_id if session is not None else _ANONYMOUS_SESSION
        self._audit_root = Path(audit_root) if audit_root is not None else None
        self._mission_id = mission_id if mission_id is not None else self._session_id
        self._requester = requester if requester is not None else self._session_id
        self._approval_timeout_seconds = float(approval_timeout_seconds)
        # action_id -> request_id of an enqueued, not-yet-resolved write action.
        self._pending: dict[str, str] = {}
        self._audit_records: list[AuditRecord] = []

    @property
    def audit_records(self) -> tuple[AuditRecord, ...]:
        """The ordered audit trail emitted so far (one record per audited event)."""
        return tuple(self._audit_records)

    # -- BrowserController protocol ---------------------------------------------- #
    def execute(self, action: BrowserAction) -> BrowserActionResult:
        """Execute ``action`` and return its typed 3-plane ``BrowserActionResult``.
        A gated write raises ``ApprovalPendingError`` until approved (then runs on
        re-invocation); a denied / timed-out request raises the governance terminal
        verdict. Every executed action emits an audit record carrying the session_id."""
        if self._is_gated(action):
            self._gate_write(action)  # raises pending / denied / timeout, else returns to proceed
        result = self._backend.run(action)
        self._emit_audit(action, outcome="executed")
        return result

    # -- internals --------------------------------------------------------------- #
    def _is_gated(self, action: BrowserAction) -> bool:
        """A write-class action on a write-capable domain, with a gate wired (FR-003/004)."""
        return (
            self._gate is not None
            and action.action_class == _WRITE
            and self._policy.is_write_capable(action.target)
        )

    def _gate_write(self, action: BrowserAction) -> None:
        """Enqueue (first call -> raise ``ApprovalPendingError``) or resolve (later
        call) the write action through the governance ``ApprovalGate``. Returns
        normally only when the request resolved ``approved`` (the caller proceeds);
        otherwise raises the pending / denied / timeout outcome."""
        operation = f"{action.action_type} {action.target}"
        request_id = self._pending.get(action.action_id)
        if request_id is None:
            request = self._gate.request(operation, self._requester)
            self._pending[action.action_id] = request.request_id
            self._emit_audit(action, outcome="approval_pending", request_id=request.request_id)
            raise ApprovalPendingError(request.request_id, operation)

        status = self._gate.await_decision(request_id)
        if status == "approved":
            del self._pending[action.action_id]
            self._emit_audit(action, outcome="approved", request_id=request_id)
            return
        del self._pending[action.action_id]
        if status == "denied":
            self._emit_audit(action, outcome="denied", request_id=request_id)
            raise ApprovalDeniedError(request_id)
        self._emit_audit(action, outcome="timeout", request_id=request_id)
        raise ApprovalTimeoutError(request_id, self._approval_timeout_seconds)

    def _emit_audit(
        self, action: BrowserAction, *, outcome: str, request_id: str | None = None
    ) -> None:
        """Emit one ``AuditRecord`` for ``action`` (SC-001 / FR-006). The session_id
        rides in ``detail`` so a multi-step workflow's records share it; when an
        audit sink is configured the record is also exported through the governance
        ``export_audit`` (reuse -- this lane registers no audit vocabulary)."""
        detail: dict[str, Any] = {
            "session_id": self._session_id,
            "action_id": action.action_id,
            "action_class": action.action_class,
            "target": action.target,
        }
        if request_id is not None:
            detail["request_id"] = request_id
        record = AuditRecord(
            timestamp=_now_iso(),
            actor=self._requester,
            operation=action.action_type,
            outcome=outcome,
            mission_id=self._mission_id,
            detail=detail,
        )
        self._audit_records.append(record)
        if self._audit_root is not None:
            export_audit([record], audit_path(self._mission_id, root_dir=self._audit_root))
