"""FileApprovalGate -- the v1 file-based HITL approval gate (05_agno US P2 / FR-005/006/010).

The concrete implementation behind the frozen ``ApprovalGate`` Protocol in
``cexai.governance._shared.types``. A HITL-tagged operation calls ``request`` to
emit a ``pending`` ``ApprovalRequest`` and pause; a human (or, in tests, the
``approver`` helper) records a verdict in the request's watch file; the caller
``await_decision``s until the request reaches a terminal state.

Transport (FR-006, v1 = file-only; email / Slack / webhook are v1.5): one JSON
watch file per request at ``{approvals_dir}/{request_id}.json``. ``request`` writes
it with status ``pending`` and an empty ``verdicts`` list; an approver appends
``{"approver", "verdict"}`` entries (see ``approver.record_verdict``); the gate
polls, resolves, and stamps the terminal status back into the same file so the
file is the complete pending -> terminal record (the audit lane reads it).

Resolution (FR-010, M-of-N): the optional ``ApprovalPolicy`` sets M
(``approvers_required``) of N (``approvers_total``); the default is 1-of-1. A
single ``deny`` is a VETO -- it aborts to ``denied`` regardless of approvals (US P2
acceptance #3). Otherwise the request is ``approved`` once M DISTINCT approvers have
recorded ``approve`` (the same approver twice counts once). A malformed policy
(``required < 1`` or ``required > total``) is rejected at construction
(Gating-Wrath: never silently mis-gate).

Approver identity (R-202, roster/allowlist): the watch-file ``approver`` string is a
bare, unauthenticated claim by default -- v1 has no cryptographic binding to it unless
a verifier is configured (see CRYPTO-BINDING below). The minimal, honest floor this
module DOES enforce even without one: an optional ``approvers_roster`` (constructor
kwarg, propagated into the watch file's persisted ``policy`` and read back by
``resolve_verdicts``) -- when configured, an ``approve`` from an approver string NOT
on the roster is ignored; it NEVER counts toward M, so an unknown approver alone can
never manufacture an ``approved`` result. ``approvers_roster=None`` (the default)
preserves the pre-R-202 behavior verbatim for every existing caller that does not
configure one. The ``deny`` veto path is intentionally untouched by the roster (still
any recorded deny, from any approver string, aborts to ``denied`` -- unchanged).

CRYPTO-BINDING (R-202 follow-up, opt-in): the roster restricts WHICH names count but
a plaintext name is still forgeable by anyone who can write the watch file. An
optional ``verifier`` (constructor kwarg -- the callable returned by
``cexai.governance.rbac.principal_signing.make_principal_verifier``) closes that hole
for approvals: when a verifier is configured, an ``approve`` entry MUST carry a
``token`` (a JWS minted by the approver via ``mint_principal_token``) to count toward
M; ``resolve_verdicts`` calls ``verifier(token)`` and, on success, tallies the
VERIFIED principal (the token's ``sub`` claim) rather than the bare ``approver``
string -- so a forged/tampered/expired/wrong-key token, or a bare approve with no
token at all, never counts. Composes with the roster: when both are configured, the
verified ``sub`` must ALSO be a roster member. The verifier is instance state (a
callable + JWKS + in-memory replay store cannot round-trip through JSON the way the
roster does), so -- unlike the roster -- it is NOT persisted into the watch file; a
gate resolving a request must be constructed with the SAME verifier the request was
opened under. ``verifier=None`` (the default) is untouched: resolution falls back to
the existing roster/bare-string behavior byte-for-byte, so no existing caller changes
behavior by not passing one. The ``deny`` veto remains intentionally unauthenticated
here too, matching the roster's existing precedent -- unchanged.

CRYPTO-BINDING FIX2 (poll-safe replay): ``await_decision`` polls the SAME watch file
repeatedly until it resolves, so a naive ``self._verifier`` hookup would re-present an
already-verified token to the verifier's one-time ``jti`` replay check on every poll
and lose that approver's credit after the first poll -- turning a valid M-of-N>=2
approval into a guaranteed timeout. ``_resolve`` therefore never passes
``self._verifier`` directly to ``resolve_verdicts``; it wraps it via
``_wrapped_verifier`` in a per-watch-file (per ``path``) cache of already-accepted
tokens, so a still-pending request's already-verified entries keep counting across
polls while a token replayed against a DIFFERENT request still hits the real
verifier and its replay defense unchanged. See ``_wrapped_verifier`` for the full
rationale.

Two return seams, by design:
  * ``await_decision(request_id) -> str`` is the frozen Protocol method: it RETURNS
    the terminal ``ApprovalStatus`` value (``approved`` | ``denied`` | ``timeout``).
    This is what the W3c contract sig drives.
  * ``await_or_raise(request_id) -> None`` is the caller-side convenience: it maps a
    non-approval terminal to the spec-named abort -- ``denied`` ->
    ``ApprovalDeniedError(request_id)`` (mission marks ``denied_by_human``),
    ``timeout`` -> ``ApprovalTimeoutError(request_id, waited_seconds)`` (mission marks
    ``approval_timeout``) -- and returns on ``approved`` so the gated action proceeds.

Offline + instant (Article XIV): ``timeout_seconds`` (production default 24h, US P2
#4), ``poll_interval_seconds``, and ``approvals_dir`` are all constructor-injectable,
so tests run against a ``tmp_path`` with millisecond deadlines and never wait a real
24h or block on a live human. A transient unreadable/partial watch file during a
poll is treated as still-``pending`` (fail-closed: corruption never auto-approves).

This REUSES the existing ``hitl_config`` kind (policy / tagging is config) and
registers NO new kind: it only PRODUCES ``ApprovalRequest`` instances at runtime.

absorbs: 05_agno/hitl
"""

from __future__ import annotations

import json
import time
import uuid
from collections.abc import Callable, Iterable, Mapping
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

from cexai.governance._shared.errors import ApprovalDeniedError, ApprovalTimeoutError
from cexai.governance._shared.types import ApprovalPolicy, ApprovalRequest

__all__ = [
    "FileApprovalGate",
    "resolve_verdicts",
    "APPROVE",
    "DENY",
    "VALID_VERDICTS",
    "PENDING",
    "APPROVED",
    "DENIED",
    "TIMEOUT",
]

# Production default deadline: 24h -- one business-day decision cycle (05 US P2 #4).
# Tests inject milliseconds via the constructor; this constant is never their value.
_DEFAULT_TIMEOUT_SECONDS: float = 24 * 60 * 60
# How often the gate re-reads the watch file while pending. 1s is fine for the v1
# file transport; tests inject a sub-millisecond interval. v1.5 push transports
# (email / Slack / webhook) replace polling entirely (FR-006).
_DEFAULT_POLL_INTERVAL_SECONDS: float = 1.0
# v1 transport root -- one watch file per request lives here. Created lazily on the
# first ``request`` so bare construction does no IO (the isinstance smoke check).
_DEFAULT_APPROVALS_DIR: Path = Path(".cexai") / "approvals"

# Verdict tokens an approver records, and the pending + terminal statuses. PUBLIC so
# offline callers that never spin up a live gate -- notably the constitution enforcer's
# Commandment VIII (gate_irreversible) -- speak the SAME approval vocabulary and reuse
# the SAME M-of-N resolution (resolve_verdicts) instead of re-deriving "approved".
APPROVE = "approve"
DENY = "deny"
VALID_VERDICTS = (APPROVE, DENY)

PENDING = "pending"
APPROVED = "approved"
DENIED = "denied"
TIMEOUT = "timeout"

# Back-compat private aliases (the existing instance methods reference these names).
_APPROVE = APPROVE
_DENY = DENY
_VALID_VERDICTS = VALID_VERDICTS
_PENDING = PENDING
_APPROVED = APPROVED
_DENIED = DENIED
_TIMEOUT = TIMEOUT


def resolve_verdicts(
    verdicts: Any,
    approvers_required: int = 1,
    roster: frozenset[str] | None = None,
    verifier: Callable[[str], Mapping[str, Any]] | None = None,
) -> str:
    """Pure M-of-N resolution over recorded verdict entries -- no IO, no clock.

    The single home of the approve/deny tally rule (FR-010), extracted so any caller
    can resolve a recorded verdict list identically to the live gate: a single ``deny``
    is a VETO (-> ``DENIED``) regardless of approvals; otherwise ``APPROVED`` once
    ``approvers_required`` DISTINCT approvers recorded ``approve`` (the same approver
    twice counts once); otherwise ``PENDING``. Each entry is a mapping with
    ``approver`` / ``verdict`` keys; a non-mapping entry is ignored (fail-closed --
    malformed input never manufactures an approval). ``FileApprovalGate._resolve``
    delegates here, and the offline constitution enforcer (Commandment VIII) reuses it
    to decide whether an ``irreversible`` action carries recorded human approval.

    ``roster`` (R-202, approver allowlist): when provided, only ``approve`` entries
    whose (bare-string or, if ``verifier`` is set, cryptographically VERIFIED)
    approver identity is a member of ``roster`` are counted toward
    ``approvers_required`` -- an approve outside the roster is silently excluded
    (never raises; matches the existing fail-closed style of this function).
    ``roster=None`` (the default) skips the filter entirely, so every existing caller
    that does not pass a roster resolves exactly as before this fix. The ``deny``
    veto is NOT filtered by ``roster`` -- any recorded deny still aborts to
    ``DENIED`` regardless of who recorded it, unchanged from pre-R-202 behavior.

    ``verifier`` (R-202 crypto-binding, optional): the callable returned by
    ``principal_signing.make_principal_verifier`` -- ``verify(token_str) ->
    claims dict``, raising on ANY failure. When provided, a bare ``approver`` string
    is NO LONGER trusted for tallying: each ``approve`` entry must carry a ``token``
    (a non-empty string) that ``verifier(token)`` accepts; the DISTINCT identity
    tallied is the verified claims' ``sub`` (the signed principal), not the
    unauthenticated ``approver`` field. An entry with a missing/blank/non-string
    ``token``, or a token the verifier rejects for ANY reason (forged signature,
    tampered claims, expired, replayed, wrong key, wrong alg, ...), is excluded --
    it NEVER counts toward M and never raises out of this function (fail-closed,
    same style as the roster filter and the JSON-corruption path below). Composes
    with ``roster``: when both are set, the verified ``sub`` must ALSO be a roster
    member to count. ``verifier=None`` (the default) is a complete no-op -- tallying
    reverts to the bare ``approver`` string exactly as before this parameter existed,
    so no existing caller (including every call site that predates R-202) changes
    behavior by not passing one. The ``deny`` veto remains unauthenticated even when
    a verifier is configured, matching the roster's existing precedent."""
    entries = verdicts if isinstance(verdicts, (list, tuple)) else ()
    if any(isinstance(e, Mapping) and e.get("verdict") == DENY for e in entries):
        return DENIED
    if verifier is not None:
        # Crypto-binding path: a bare `approver` string is never trusted here. Only
        # a token that verifies successfully contributes an identity, and that
        # identity is the token's OWN verified `sub` -- never the unauthenticated
        # `approver` field alongside it.
        approved: set[Any] = set()
        for e in entries:
            if not (isinstance(e, Mapping) and e.get("verdict") == APPROVE):
                continue
            token = e.get("token")
            if not isinstance(token, str) or not token:
                continue  # missing/blank/non-string token never counts
            try:
                claims = verifier(token)
            except Exception:
                # ANY verification failure (forged sig, tampered payload, expired,
                # replayed jti, wrong/unknown kid, wrong alg, ...) is a non-count,
                # never a raise out of a pure resolver (fail-closed).
                continue
            sub = claims.get("sub") if isinstance(claims, Mapping) else None
            if sub:
                approved.add(sub)
    else:
        approved = {
            e.get("approver")
            for e in entries
            if isinstance(e, Mapping) and e.get("verdict") == APPROVE
        }
    if roster is not None:
        # Unknown approvers never count toward M (R-202 invariant): filter to the
        # configured roster before tallying distinct approvals.
        approved &= roster
    if len(approved) >= approvers_required:
        return APPROVED
    return PENDING


def _now() -> datetime:
    """Current UTC instant (tz-aware) -- the basis for the expiry deadline."""
    return datetime.now(timezone.utc)


class FileApprovalGate:
    """A file-based ``ApprovalGate``: emits a pending request, awaits a recorded
    verdict, resolves to a terminal approve / deny / timeout status.

    Construct bare (``FileApprovalGate()``) for the production 24h, 1s-poll,
    ``.cexai/approvals`` defaults, or inject ``approvals_dir`` / ``timeout_seconds``
    / ``poll_interval_seconds`` / ``policy`` for offline tests and M-of-N gating.
    Bare construction performs no IO; the approvals directory is created on the
    first ``request``.

    ``approvers_roster`` (R-202, optional, keyword-only): the set of approver ids
    authorized to cast an ``approve`` vote toward the M-of-N threshold. When set, it
    is stamped into every request's watch file (so ``_resolve`` reads the SAME roster
    back, even across process restarts) and an ``approve`` from an approver outside
    it never counts toward M (see ``resolve_verdicts``). Left ``None`` (the default),
    the gate trusts any approver string verbatim -- identical to pre-R-202 behavior,
    so no existing caller changes behavior by not passing this.

    ``verifier`` (R-202 crypto-binding, optional, keyword-only): the callable
    returned by ``cexai.governance.rbac.principal_signing.make_principal_verifier``
    (``verify(token_str) -> claims dict``, raises on any failure). When set, an
    ``approve`` entry must carry a token that verifies successfully to count toward
    M -- the tallied identity is the token's verified ``sub``, not the bare
    ``approver`` string (see ``resolve_verdicts``). Composes with
    ``approvers_roster`` (the verified ``sub`` must also be on the roster, if one is
    set). Unlike the roster, the verifier is NOT persisted into the watch file (a
    callable + its JWKS + in-memory replay store cannot round-trip through JSON) --
    a gate that resolves a request must be constructed with the SAME verifier the
    request was opened under. Left ``None`` (the default), resolution is byte-for-byte
    the pre-existing roster/bare-string behavior; no existing caller changes behavior
    by not passing this.
    """

    def __init__(
        self,
        *,
        approvals_dir: Path | str | None = None,
        timeout_seconds: float = _DEFAULT_TIMEOUT_SECONDS,
        poll_interval_seconds: float = _DEFAULT_POLL_INTERVAL_SECONDS,
        policy: ApprovalPolicy | None = None,
        approvers_roster: Iterable[str] | None = None,
        verifier: Callable[[str], Mapping[str, Any]] | None = None,
    ) -> None:
        self._approvals_dir = (
            Path(approvals_dir) if approvals_dir is not None else _DEFAULT_APPROVALS_DIR
        )
        self._timeout_seconds = float(timeout_seconds)
        self._poll_interval_seconds = float(poll_interval_seconds)
        self._policy = policy if policy is not None else ApprovalPolicy(1, 1)
        # R-202: None means "no roster configured" -- unchanged pre-fix behavior.
        # A configured roster is frozen (defensive copy of whatever iterable was
        # passed) so a caller mutating their source list afterward cannot drift it.
        self._approvers_roster: frozenset[str] | None = (
            frozenset(approvers_roster) if approvers_roster is not None else None
        )
        # R-202 crypto-binding: None means "no verifier configured" -- resolution
        # falls back to the roster/bare-string path, unchanged. A configured
        # verifier is kept as instance state only (never written to the watch
        # file -- see the class docstring).
        self._verifier: Callable[[str], Mapping[str, Any]] | None = verifier
        # R-202-FIX2: per-request cache of tokens THIS instance has already seen the
        # verifier accept, keyed by watch-file path. See ``_wrapped_verifier`` for the
        # full rationale -- this exists to stop ``await_decision``'s poll loop from
        # re-presenting an already-verified token to a one-time-replay-checked
        # verifier and losing credit for it (found by adversarial review of the
        # original crypto-binding fix). Empty until a verifier is configured and a
        # token succeeds; unused entirely on the no-verifier path.
        self._verified_claims_cache: dict[Path, dict[str, Mapping[str, Any]]] = {}
        # Gating-Wrath: a malformed M-of-N policy is rejected here, never at the gate
        # (a request that can never resolve approved is a silent deadlock otherwise).
        required = self._policy.approvers_required
        total = self._policy.approvers_total
        if not 1 <= required <= total:
            raise ValueError(
                "invalid M-of-N approval policy: require 1 <= approvers_required "
                f"<= approvers_total, got required={required} total={total}"
            )

    # -- ApprovalGate protocol --------------------------------------------------- #
    def request(self, operation: str, requester: str) -> ApprovalRequest:
        """Emit a ``pending`` ``ApprovalRequest`` for a HITL-tagged ``operation`` and
        write its verdict-watch file (05 US P2 acceptance #1 / FR-005/006). The
        deadline is stamped now + ``timeout_seconds``; the caller then
        ``await_decision``s on the returned ``request_id``."""
        request_id = "appr-" + uuid.uuid4().hex[:12]
        expires_at = (_now() + timedelta(seconds=self._timeout_seconds)).isoformat()
        request = ApprovalRequest(
            request_id=request_id,
            operation=operation,
            requester=requester,
            expires_at=expires_at,
            status=_PENDING,
        )
        self._write_watch_file(request)
        return request

    def await_decision(self, request_id: str) -> str:
        """Block until the request reaches a terminal state, then return its
        ``ApprovalStatus`` value (``approved`` | ``denied`` | ``timeout``). Polls the
        watch file every ``poll_interval_seconds``; resolves immediately if a verdict
        is already recorded; returns ``timeout`` once the stamped deadline passes with
        no decision. The terminal status is persisted back into the watch file."""
        path = self._path(request_id)
        deadline = self._deadline(path)
        while True:
            status = self._resolve(path)
            if status != _PENDING:
                self._persist_status(path, status)
                return status
            now = _now()
            if now >= deadline:
                self._persist_status(path, _TIMEOUT)
                return _TIMEOUT
            remaining = (deadline - now).total_seconds()
            # Clamp the final sleep to the deadline so a coarse poll interval never
            # overshoots a short (test-injected) timeout.
            time.sleep(min(self._poll_interval_seconds, remaining))

    # -- caller-side convenience (the spec error seam) --------------------------- #
    def await_or_raise(self, request_id: str) -> None:
        """Await a verdict and map a non-approval terminal to its spec abort: ``denied``
        -> ``ApprovalDeniedError(request_id)``, ``timeout`` ->
        ``ApprovalTimeoutError(request_id, waited_seconds)``. Returns ``None`` on
        ``approved`` so the caller proceeds with the gated action."""
        status = self.await_decision(request_id)
        if status == _DENIED:
            raise ApprovalDeniedError(request_id)
        if status == _TIMEOUT:
            raise ApprovalTimeoutError(request_id, self._timeout_seconds)

    # -- internals --------------------------------------------------------------- #
    def _path(self, request_id: str) -> Path:
        """The watch-file path for ``request_id`` under the approvals directory."""
        return self._approvals_dir / f"{request_id}.json"

    def _write_watch_file(self, request: ApprovalRequest) -> None:
        """Create the approvals dir (lazily) and write the initial pending record --
        the file the approver records verdicts in and the gate polls."""
        self._approvals_dir.mkdir(parents=True, exist_ok=True)
        policy: dict[str, Any] = {
            "approvers_required": self._policy.approvers_required,
            "approvers_total": self._policy.approvers_total,
            # R-202: stamp the configured roster (sorted list for stable JSON;
            # None when no roster was configured) so _resolve reads back the
            # SAME roster this request was opened under, even in a fresh process.
            "approvers_roster": (
                sorted(self._approvers_roster)
                if self._approvers_roster is not None
                else None
            ),
        }
        if self._verifier is not None:
            # R-202 crypto-binding: informational only (the verifier callable itself
            # cannot be persisted -- see class docstring). Only stamped when a
            # verifier IS configured, so the no-verifier watch-file schema stays
            # byte-for-byte identical to the pre-crypto-binding format.
            policy["requires_signed_approval"] = True
        record = {
            "request_id": request.request_id,
            "operation": request.operation,
            "requester": request.requester,
            "expires_at": request.expires_at,
            "status": request.status,
            "policy": policy,
            "verdicts": [],
        }
        self._path(request.request_id).write_text(
            json.dumps(record, indent=2) + "\n", encoding="utf-8"
        )

    def _deadline(self, path: Path) -> datetime:
        """Parse the stamped ISO-8601 ``expires_at`` into the tz-aware deadline. A
        missing file here means ``await_decision`` was called for an unknown request
        -- a programming error that should surface loudly, so it is not caught."""
        return datetime.fromisoformat(self._read(path)["expires_at"])

    def _resolve(self, path: Path) -> str:
        """Apply the M-of-N policy to the recorded verdicts via the shared
        ``resolve_verdicts`` rule. A transient unreadable/partial file is treated as
        ``pending`` (fail-closed: corruption never auto-approves -- it waits, then
        times out)."""
        try:
            data = self._read(path)
            verdicts = data.get("verdicts", [])
            policy = data.get("policy", {})
        except (json.JSONDecodeError, OSError):
            return _PENDING
        required = policy.get("approvers_required", 1)
        # R-202: read the roster back from the watch file itself (not from
        # self._approvers_roster) so resolution is correct even if _resolve runs in
        # a different process/instance than the one that wrote the request -- the
        # file is the single source of truth for the policy a request was opened
        # under. A missing/non-list entry means "no roster was configured".
        roster_entry = policy.get("approvers_roster")
        roster = frozenset(roster_entry) if isinstance(roster_entry, list) else None
        # R-202 crypto-binding: the verifier is THIS instance's own state (never
        # persisted -- see class docstring), so it comes from self, not the file.
        # R-202-FIX2: never hand the raw ``self._verifier`` to ``resolve_verdicts``
        # here -- wrap it in the per-request cache first (see ``_wrapped_verifier``),
        # so ``await_decision``'s repeated polling of this SAME watch file does not
        # re-present an already-accepted token to a one-time-replay-checked verifier.
        verifier = self._wrapped_verifier(path) if self._verifier is not None else None
        return resolve_verdicts(verdicts, required, roster, verifier)

    def _wrapped_verifier(self, path: Path) -> Callable[[str], Mapping[str, Any]]:
        """Wrap ``self._verifier`` with a per-request (per watch-file ``path``)
        verified-claims cache so ``resolve_verdicts`` -- called fresh on EVERY poll
        of ``await_decision`` -- does not re-present an already-successfully-verified
        token to the underlying ``make_principal_verifier`` callable a second time.

        WHY THIS EXISTS (R-202-FIX2, caught by adversarial review of the original
        crypto-binding fix): ``make_principal_verifier`` enforces a one-time ``jti``
        replay defense -- a SECOND call with the same token raises
        ``PrincipalTokenError('replay')`` (by design, to stop a captured token being
        reused). ``await_decision`` polls ``_resolve`` in a loop until the watch file
        reaches a terminal state; every poll re-reads the SAME recorded verdict
        entries from disk and re-resolves them from scratch via ``resolve_verdicts``,
        which -- without this cache -- would call ``self._verifier(token)`` again on
        every single poll. For an M-of-N >= 2 policy where approvals arrive on
        different polls (the entire reason polling exists), a token that verified
        successfully on poll N would then be rejected as a replay on poll N+1 for
        the exact same still-pending entry, permanently losing that approver's
        credit and turning a fully valid, distinct-principal approval into a
        guaranteed timeout. This wrapper caches a SUCCESSFUL verification of an
        ALREADY-RECORDED entry -- it does not skip verification: a token is only
        ever cached after ``self._verifier(token)`` itself accepted it.

        SCOPED PER WATCH-FILE PATH (not global, not shared across requests): a token
        that verified for request A must NOT be treated as pre-verified for a
        DIFFERENT request B -- that would defeat the underlying jti replay defense,
        which exists precisely to stop a captured, previously-valid token from being
        reused across DIFFERENT approval contexts. Caching by ``path`` means: the
        identical entry, re-read from the identical watch file across repeated
        polls of the SAME request, keeps counting; the SAME token string presented
        against ANY OTHER request still goes to the real ``self._verifier`` and
        still hits its jti replay rejection exactly as before this fix.

        FAIL-CLOSED, unchanged: a token that FAILS verification is never cached --
        the underlying exception propagates to ``resolve_verdicts``'s own
        ``except Exception: continue``, so a forged/tampered/expired token keeps
        failing on every single poll, forever, exactly as before this wrapper was
        added. Only genuine successes are cached, never failures."""
        verifier = self._verifier
        assert verifier is not None  # only called from _resolve when one is set
        cache = self._verified_claims_cache.setdefault(path, {})

        def _cached_verify(token: str) -> Mapping[str, Any]:
            cached = cache.get(token)
            if cached is not None:
                return cached
            claims = verifier(token)  # raises on failure -- never cached, never swallowed
            cache[token] = claims
            return claims

        return _cached_verify

    def _persist_status(self, path: Path, status: str) -> None:
        """Stamp the terminal ``status`` back into the watch file (pending -> terminal),
        so the file is the complete lifecycle record for the audit lane."""
        data = self._read(path)
        data["status"] = status
        path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")

    @staticmethod
    def _read(path: Path) -> dict[str, Any]:
        """Read and parse the watch file (the single source of truth for a request)."""
        return json.loads(path.read_text(encoding="utf-8"))
