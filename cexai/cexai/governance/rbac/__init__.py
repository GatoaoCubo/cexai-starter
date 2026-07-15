"""RBAC subsystem -- opt-in JWT authorization (impl: v0.3-W3b).

Designed-in role-based access control with JWT-verified ``viewer`` / ``dev`` roles
(05_agno US P3 / FR-007): a ``viewer`` dispatch attempt is rejected 403, ``dev``
proceeds, and dev mode with no token is allowed at zero overhead (FR-008); an
expired token yields 401 + ``WWW-Authenticate`` (FR-011). Roles reuse the existing
``rbac_policy`` + ``role_assignment`` kinds. The freeze keeps RBAC dormant -- the
module is import-light and never loaded on the no-auth dev path (SC-005). The
frozen ``Role`` / ``AuthToken`` / ``AuthGuard`` contracts live in
``cexai.governance._shared.types``; W3b ships the concrete ``JwtAuthGuard`` behind
that seam here. The expiry 401 (FR-011) is the LOCAL ``AuthTokenExpiredError`` leaf
(``rbac.errors``); the 403 ``RbacForbiddenError`` stays in the frozen ``_shared``
tree and is re-exported here for caller ergonomics. ``enforce`` / ``is_dev_mode``
are the dispatch-path checkpoint (dev mode = no token = zero overhead, FR-008).

absorbs: 05_agno/rbac
"""

from cexai.governance._shared.errors import RbacForbiddenError
from cexai.governance.rbac.errors import AuthTokenExpiredError
from cexai.governance.rbac.jwt_guard import JwtAuthGuard, enforce, is_dev_mode

__all__ = [
    "JwtAuthGuard",
    "enforce",
    "is_dev_mode",
    "AuthTokenExpiredError",
    "RbacForbiddenError",
]
