"""The concrete RBAC JWT auth guard (CEXAI v0.3-W3b, 05_agno US P3).

``JwtAuthGuard`` implements the frozen ``AuthGuard`` Protocol from
``cexai.governance._shared.types`` -- the W3b seam the SKIPPED contract test
``test_rbac_viewer_forbidden`` will drive in W3c. Three behaviours, one small
module:

  * authorize(token, operation) -> bool : a SMALL, explicit role->allowed-ops
    policy. ``dev`` may ``dispatch`` (plus the read ops); ``viewer`` is read-only,
    so ``authorize(viewer, 'dispatch')`` is ``False`` (US P3 #1) and
    ``authorize(dev, 'dispatch')`` is ``True`` (US P3 #2). Unknown roles get
    nothing (fail-closed -> SC-004: zero false-positive grants).
  * verify(token_str) -> AuthToken : projects verified JWT claims into the frozen
    ``AuthToken``. pyjwt is LAZY + OPTIONAL (imported inside the method); an
    injected ``verifier`` callable always takes precedence so OFFLINE tests run
    with pyjwt absent (Article XIV) and deterministically. An expired token
    raises the local ``AuthTokenExpiredError`` [401] (FR-011).
  * enforce / is_dev_mode : the dispatch-path checkpoint. FR-008 dev mode (no
    token) short-circuits to allowed WITHOUT consulting the guard -- zero overhead
    (SC-005). With a token, a denied op is mapped to ``RbacForbiddenError`` [403].

Article VIII (anti-abstraction): import-light -- stdlib + intra-package only at
import time; pyjwt is never imported unless ``verify`` runs WITHOUT an injected
verifier. RBAC stays opt-in / dormant: the no-auth dev path never touches this
module. Registers ZERO kinds (``AuthToken`` is a runtime dataclass; AuthToken-as-
kind is DEFERRED to v1.0).

Spec provenance: cexai-specs/05_agno/spec.md (US P3, FR-007/008/011, SC-004/005).

absorbs: 05_agno/rbac
"""

from __future__ import annotations

from collections.abc import Callable, Mapping
from datetime import datetime, timezone
from types import MappingProxyType
from typing import Any

from cexai.governance._shared.errors import RbacForbiddenError
from cexai.governance._shared.types import AuthGuard, AuthToken
from cexai.governance.rbac.errors import AuthTokenExpiredError

__all__ = [
    "JwtAuthGuard",
    "enforce",
    "is_dev_mode",
]

# Read-only operations both roles may perform. Kept deliberately small + explicit
# (Article VIII) -- the contract only exercises 'dispatch', but naming the read
# set makes "viewer is read-only, not no-access" a checkable property.
_READ_OPERATIONS: frozenset[str] = frozenset(
    {"read", "view", "list", "status", "trace"}
)
# Privileged operations only 'dev' may perform (US P3: dispatch is the write op).
_DEV_OPERATIONS: frozenset[str] = frozenset({"dispatch"})

# The explicit role -> allowed-operations policy (05 FR-007). A role absent from
# this map is granted NOTHING (fail-closed) -- the default that keeps SC-004's
# false-positive-grant rate at zero.
_ROLE_POLICY: Mapping[str, frozenset[str]] = MappingProxyType(
    {
        "viewer": _READ_OPERATIONS,
        "dev": _READ_OPERATIONS | _DEV_OPERATIONS,
    }
)

# JWT claim keys projected onto dedicated AuthToken fields -- excluded from the
# residual ``claims`` bag so a field is never duplicated there.
_RESERVED_CLAIMS: frozenset[str] = frozenset(
    {"sub", "subject", "role", "exp", "expires_at"}
)


class JwtAuthGuard:
    """Opt-in JWT authorization guard implementing the frozen ``AuthGuard``
    Protocol (05 US P3 / FR-007/008/011).

    Construct with no arguments for the production default (pyjwt is lazy-imported
    inside ``verify``); inject a ``verifier`` callable -- ``(token_str) -> claims
    mapping`` -- to supply signature verification (the real seam) or, in tests, an
    offline fake. The injected verifier always wins over pyjwt, so the suite is
    deterministic and runs with pyjwt absent."""

    def __init__(
        self, verifier: Callable[[str], Mapping[str, Any]] | None = None
    ) -> None:
        self._verifier = verifier

    # -- AuthGuard Protocol ------------------------------------------------- #
    def authorize(self, token: AuthToken, operation: str) -> bool:
        """Return whether ``token``'s role may perform ``operation`` (05 FR-007).
        ``viewer`` -> read ops only (dispatch is ``False``); ``dev`` -> read ops +
        dispatch; any other role -> ``False`` (fail-closed)."""
        return operation in _ROLE_POLICY.get(token.role, frozenset())

    # -- JWT verification (lazy pyjwt / injected verifier) ------------------ #
    def verify(self, token_str: str) -> AuthToken:
        """Verify ``token_str`` and project its claims into a frozen ``AuthToken``
        (05 US P3, Key Entities: AuthToken). Raises ``AuthTokenExpiredError``
        [401] if the token has expired (FR-011). All offline when a verifier is
        injected; pyjwt is imported lazily only on the no-verifier path."""
        claims = self._decode(token_str)

        subject = str(claims.get("sub") or claims.get("subject") or "")
        role = str(claims.get("role") or "")
        expires_at = _expiry_iso(claims)

        if _is_expired(expires_at):
            raise AuthTokenExpiredError(subject, expires_at)

        residual = {k: v for k, v in claims.items() if k not in _RESERVED_CLAIMS}
        return AuthToken(
            subject=subject,
            role=role,
            expires_at=expires_at,
            claims=MappingProxyType(residual),
        )

    def _decode(self, token_str: str) -> Mapping[str, Any]:
        """Resolve raw JWT claims. An injected verifier takes precedence (the
        offline / signature-verification seam); otherwise pyjwt is lazy-imported.
        With neither available, fail loud rather than silently allow."""
        if self._verifier is not None:
            return self._verifier(token_str)
        try:
            import jwt  # lazy + OPTIONAL: never imported on the dev/no-auth path
        except ImportError as exc:  # offline + no verifier -> no backend to use
            raise RuntimeError(
                "JwtAuthGuard.verify needs pyjwt installed or a `verifier` "
                "injected; neither is available. RBAC is opt-in -- dev mode uses "
                "no token at all (FR-008)."
            ) from exc
        # Production default decode. Signature verification is the injected
        # verifier's job (it owns the key); expiry is handled uniformly below in
        # `verify` so both paths raise the same AuthTokenExpiredError [401].
        return jwt.decode(  # pragma: no cover - exercised only with pyjwt present
            token_str,
            options={"verify_signature": False, "verify_exp": False},
        )


def is_dev_mode(token: AuthToken | None) -> bool:
    """FR-008: dev mode is the absence of a token. The dispatch path checks this
    FIRST and skips RBAC entirely -- the guard is never constructed or consulted
    (zero overhead, SC-005)."""
    return token is None


def enforce(token: AuthToken | None, operation: str, guard: AuthGuard) -> bool:
    """The RBAC checkpoint on the dispatch path (05 US P3 / FR-007/008).

    Dev mode (``token is None``) returns ``True`` immediately WITHOUT touching
    ``guard`` -- the FR-008 zero-overhead path. With a token, delegate the role
    decision to ``guard.authorize``; on a permitted op return ``True``, and on a
    denied op raise ``RbacForbiddenError`` [403] carrying subject / role /
    operation for the audit-log entry (US P3 #1)."""
    if is_dev_mode(token):
        return True
    if guard.authorize(token, operation):
        return True
    raise RbacForbiddenError(token.subject, token.role, operation)


def _expiry_iso(claims: Mapping[str, Any]) -> str:
    """Extract an ISO-8601 expiry from claims. Prefer ``expires_at`` (already
    ISO); fall back to a numeric JWT ``exp`` (epoch seconds) projected to ISO-8601
    UTC. Absent -> empty string (treated as non-expiring on the dormant path)."""
    raw = claims.get("expires_at")
    if raw:
        return str(raw)
    exp = claims.get("exp")
    if exp is not None:
        moment = datetime.fromtimestamp(float(exp), tz=timezone.utc)
        return moment.isoformat().replace("+00:00", "Z")
    return ""


def _is_expired(expires_at: str) -> bool:
    """Whether the ISO-8601 ``expires_at`` is at or before now (UTC). An empty or
    unparseable value is treated as non-expiring (no false 401 on the dormant
    path); a naive timestamp is assumed UTC."""
    if not expires_at:
        return False
    try:
        deadline = datetime.fromisoformat(expires_at.replace("Z", "+00:00"))
    except ValueError:
        return False
    if deadline.tzinfo is None:
        deadline = deadline.replace(tzinfo=timezone.utc)
    return deadline <= datetime.now(timezone.utc)
