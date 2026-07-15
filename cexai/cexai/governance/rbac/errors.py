"""RBAC-local exception leaf -- the JWT-expiry 401 (CEXAI v0.3-W3b).

``AuthTokenExpiredError`` is a LOCAL leaf of the governance error tree: it lives
HERE in the rbac lane, NOT in the frozen ``cexai.governance._shared.errors``. Per
N07's locked W3b decision the v0.3-W3 ``_shared`` error names are frozen, and the
FR-011 401 case is owned by this lane -- so the leaf is defined where it is raised
and re-exported from ``cexai.governance.rbac``. It still subclasses the frozen
``GovernanceError`` (imported from ``_shared``), so a single ``except CexaiError``
-- or ``except GovernanceError`` -- still catches it, exactly like the frozen
``RbacForbiddenError`` [403] sibling.

Spec provenance (cexai-specs/05_agno/spec.md):
  * FR-011 / US P3 edge case "JWT expired" -- on an expired token the system
    returns 401 with header ``WWW-Authenticate: Bearer realm="cexai",
    error="invalid_token"`` so the client refreshes / re-auths.

absorbs: 05_agno/rbac
"""

from __future__ import annotations

from cexai.governance._shared.errors import GovernanceError

__all__ = ["AuthTokenExpiredError"]

# The FR-011 challenge value (the right-hand side of the WWW-Authenticate header).
# Fixed for v1: realm "cexai", RFC 6750 invalid_token error code. A transport
# layer emits it verbatim as ``WWW-Authenticate: <this>`` alongside the 401.
_WWW_AUTHENTICATE_CHALLENGE = 'Bearer realm="cexai", error="invalid_token"'


class AuthTokenExpiredError(GovernanceError):
    """A presented JWT had passed its expiry (05 US P3 edge case / FR-011). Maps
    to HTTP 401 (NOT the 403 of ``RbacForbiddenError`` -- the role MIGHT be
    allowed; the credential is simply stale). ``http_status`` carries the 401 and
    ``www_authenticate`` carries the Bearer challenge string transports send as
    the ``WWW-Authenticate`` header so the client refreshes. ``subject`` is the
    principal from the expired token and ``expires_at`` is its ISO-8601 deadline,
    both surfaced for the audit-log entry."""

    http_status: int = 401
    www_authenticate: str = _WWW_AUTHENTICATE_CHALLENGE

    def __init__(self, subject: str, expires_at: str) -> None:
        self.subject = subject
        self.expires_at = expires_at
        super().__init__(
            f"token for subject {subject!r} expired at {expires_at} [401]"
        )
