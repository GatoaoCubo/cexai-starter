# -*- coding: utf-8 -*-
"""cex_rbac.py -- the principal/session/role-matrix model (RBAC enforcement tier).

A2.x (cex_tenant_paths.py) wired the cross-tenant DENY invariant in code
(deny_cross_tenant: a principal bound to tenant A may never touch tenant B). The
A3 eval honestly marked the full RBAC matrix PARTIAL: there was no principal/session
model and no role matrix (owner/admin/member/viewer x create/alter/approve/publish).
This module closes that gap WITHOUT reinventing the tenant guard:

  - Principal           -- an authenticated identity (user|agent|session) bound to
                           {tenant_id, principal_id, role}.
  - active_principal()  -- the session model: read CEX_PRINCIPAL / CEX_ROLE (mirroring
                           the established CEX_TENANT_ID contract). Unset -> None.
  - authorize()         -- deny-by-default role-matrix predicate (returns bool).
  - enforce()           -- the halting form (raises SystemExit on deny), matching the
                           fail-closed posture of deny_cross_tenant.
  - Resource            -- a tenant-scoped resource handle for the cross-tenant check.

BEHAVIOR-PRESERVING INVARIANT (the IRON RULE): when NO principal is bound (single-
tenant / legacy path, CEX_PRINCIPAL unset), authorize() returns True -- enforcement is
byte-identically UNCHANGED from today (default-allow). The role matrix engages ONLY
when a principal/session is active. Honest partial beats fake green.

Layering (acyclic): cex_rbac -> cex_tenant_paths -> cex_bootstrap. The cross-tenant
deny + tenant resolver + id guard are IMPORTED from cex_tenant_paths, never reinvented.

Policy source: N03_engineering/P09_config/p09_rbac_tenant_isolation.md (roles enum +
deny-by-default model). Role binding: p02_ra_tenant_admin. Permission layers
(create/alter/approve/publish): CLAUDE.md. ASCII-only per .claude/rules/ascii-code-rule.md.
"""
import os
import sys
from dataclasses import dataclass
from typing import Optional

# Reuse the canonical tenant guard + cross-tenant deny from A2.x -- one source of truth.
from cex_tenant_paths import deny_cross_tenant, active_tenant_id
from cex_bootstrap import _safe_tenant_id

# --------------------------------------------------------------------------- #
# Vocabulary (the policy enum + the CLAUDE.md permission layers)              #
# --------------------------------------------------------------------------- #
# Roles: exactly the p09_rbac_tenant_isolation enum (owner/admin/member/viewer).
ROLES = ("owner", "admin", "member", "viewer")

# Actions: the CLAUDE.md artifact-lifecycle permission layers (create/alter/approve/
# publish) + read + delete. This is the LIFECYCLE matrix; the policy's resource-tier
# matrix (read/write/delete/admin/dispatch x brand_config/runtime/...) is the sibling
# surface enforced by the path resolver + deny_cross_tenant.
ACTIONS = ("read", "create", "alter", "approve", "publish", "delete")

# Deny-by-default role x action matrix. A role grants ONLY the actions in its set;
# anything absent (or an unknown role/action) is denied. Escalating privilege:
#   viewer  -> read only (strictly read-only, policy deny_viewer_mutate).
#   member  -> read + produce (create/alter), but NO governance/destructive action.
#   admin   -> member + governance (approve/publish), but NOT delete (owner-only).
#   owner   -> full control incl. delete (policy: owner alone holds 'd'+'a').
# This is consistent with p09_rbac_tenant_isolation (owner strictly > admin > member >
# viewer) and satisfies the lifecycle permission layers.
_MATRIX = {
    "owner":  frozenset({"read", "create", "alter", "approve", "publish", "delete"}),
    "admin":  frozenset({"read", "create", "alter", "approve", "publish"}),
    "member": frozenset({"read", "create", "alter"}),
    "viewer": frozenset({"read"}),
}


# --------------------------------------------------------------------------- #
# Principal + Resource models                                                 #
# --------------------------------------------------------------------------- #
@dataclass(frozen=True)
class Principal:
    """An authenticated identity bound to {tenant_id, principal_id, role}.

    principal_id   -- the identity (a user/agent/session id).
    role           -- one of ROLES; an unknown role grants nothing (deny-by-default).
    tenant_id      -- the bound tenant (None == single-tenant/global; no cross-tenant
                      boundary to cross, consistent with deny_cross_tenant bound=None).
    principal_type -- the identity kind: user | agent | session (informational)."""
    principal_id: str
    role: str
    tenant_id: Optional[str] = None
    principal_type: str = "user"


@dataclass(frozen=True)
class Resource:
    """A resource an action targets. name is the resource class or artifact path/kind;
    tenant_id (when set) drives the cross-tenant check in authorize(). A bare string or
    None resource carries no tenant -> only the role matrix applies."""
    name: str
    tenant_id: Optional[str] = None


# --------------------------------------------------------------------------- #
# Session model (env contract, mirrors CEX_TENANT_ID)                         #
# --------------------------------------------------------------------------- #
def active_principal():
    """The bound principal from the session env contract. Returns None when CEX_PRINCIPAL
    is unset -> NO principal -> legacy default-allow (the behavior-preserving invariant).

    Contract (mirrors CEX_TENANT_ID):
      CEX_PRINCIPAL      -- the principal id (required to bind; unset -> None).
      CEX_ROLE           -- the role (lower-cased; an invalid role still binds but the
                            matrix denies every action -> fail-closed).
      CEX_TENANT_ID      -- the bound tenant (reused via active_tenant_id()).
      CEX_PRINCIPAL_TYPE -- user|agent|session (optional, default 'user')."""
    pid = (os.environ.get("CEX_PRINCIPAL") or "").strip()
    if not pid:
        return None
    role = (os.environ.get("CEX_ROLE") or "").strip().lower()
    ptype = (os.environ.get("CEX_PRINCIPAL_TYPE") or "user").strip().lower() or "user"
    return Principal(principal_id=pid, role=role,
                     tenant_id=active_tenant_id(), principal_type=ptype)


def bind_principal(principal_id, role, tenant_id=None, principal_type="user"):
    """Construct a Principal explicitly (the non-env path -- for callers that resolve an
    identity themselves). tenant_id is sanitized fail-closed when provided. role is
    normalized to lower-case; an unknown role grants nothing (deny-by-default)."""
    tid = _safe_tenant_id(tenant_id) if tenant_id else None
    return Principal(principal_id=str(principal_id),
                     role=(role or "").strip().lower(),
                     tenant_id=tid,
                     principal_type=(principal_type or "user").strip().lower() or "user")


# --------------------------------------------------------------------------- #
# Authorization (deny-by-default role matrix + cross-tenant deny reuse)        #
# --------------------------------------------------------------------------- #
def _resource_tenant(resource):
    """Extract a tenant_id from a resource, or None. A bare string / None carries no
    tenant (role matrix only); a Resource (or any object with .tenant_id) carries one."""
    if resource is None or isinstance(resource, str):
        return None
    return getattr(resource, "tenant_id", None)


def _log_deny(principal, action, resource):
    """Wire a DENY verdict to the violation sink (cex_rbac_audit.log_rbac_violation).

    Single-layer logging: authorize() is the FIRST layer to see a deny, so it logs;
    enforce() delegates through authorize() and must NOT log again. When the call
    chain runs through cex_rbac_audit (its enforce_audited wrapper), THAT layer
    writes its own richer record (reason + severity) -- we defer to it so the sink
    still receives exactly ONE line per denial, never two.

    FAIL-OPEN: any exception in logging is swallowed -- a logging failure never
    changes the verdict and never raises out of the decision path."""
    try:
        # Defer to the audit wrapper when it is in the call chain (it logs itself).
        frame = sys._getframe(1)
        while frame is not None:
            mod = frame.f_globals.get("__name__", "")
            if mod.rpartition(".")[2] == "cex_rbac_audit":
                return
            frame = frame.f_back
        # Lazy import: cex_rbac_audit imports cex_rbac at module top -- importing it
        # at OUR module top would be a cycle. log_rbac_violation is itself fail-open.
        from cex_rbac_audit import log_rbac_violation
        log_rbac_violation(principal, action, resource)
    except Exception:
        pass  # FAIL-OPEN: logging failure must never alter or mask the verdict


def authorize(principal, action, resource=None):
    """Deny-by-default role-matrix predicate. Returns True on allow, False on deny.
    Every DENY is reported to the append-only violation sink via _log_deny (best-
    effort, fail-open -- the verdict itself is never affected by logging).

    THE BEHAVIOR-PRESERVING INVARIANT: principal is None -> True (legacy default-allow,
    byte-identical to today). Enforcement engages ONLY when a principal is bound.

    When a principal IS bound, BOTH gates must pass:
      1. Cross-tenant: if the resource carries a tenant_id, delegate to deny_cross_tenant
         (the A2.x invariant -- reused, never reinvented). A cross-tenant target (or a
         malformed one) -> deny. A principal with tenant_id=None is single-tenant: no
         boundary to cross (deny_cross_tenant bound=None allows).
      2. Role matrix: the action must be granted to the principal's role. An unknown role
         or unknown action -> deny (fail-closed -- nothing is granted implicitly)."""
    if principal is None:
        return True  # no principal bound -> legacy default-allow (UNCHANGED)

    # Gate 1: cross-tenant deny (reuse A2.x; fail-closed on a malformed target).
    rtid = _resource_tenant(resource)
    if rtid is not None:
        try:
            deny_cross_tenant(rtid, bound_tenant_id=principal.tenant_id, op=str(action))
        except SystemExit:
            _log_deny(principal, action, resource)
            return False

    # Gate 2: deny-by-default role matrix (normalize role -> fail-closed on unknown).
    allowed = _MATRIX.get(str(principal.role).strip().lower())
    if not allowed:
        _log_deny(principal, action, resource)
        return False
    if action in allowed:
        return True
    _log_deny(principal, action, resource)
    return False


def enforce(principal, action, resource=None):
    """The halting form of authorize() -- the fail-closed gate (matches deny_cross_tenant).
    Returns the principal on allow; raises SystemExit on deny. Use this where a denial
    must HALT the operation (a governance gate); use authorize() for a boolean predicate.

    No-principal -> allow (returns None), preserving legacy default-allow behavior."""
    # Single-layer deny logging: authorize() (the layer that sees the deny first)
    # already wrote the violation record -- enforce() must NOT log a second line.
    if not authorize(principal, action, resource):
        who = getattr(principal, "principal_id", "?")
        role = getattr(principal, "role", "?")
        raise SystemExit(
            "ERROR: RBAC DENIED -- principal %r (role=%r) may not %s %r "
            "(deny-by-default role matrix, fail-closed)"
            % (who, role, action, getattr(resource, "name", resource)))
    return principal


__all__ = [
    "ROLES", "ACTIONS",
    "Principal", "Resource",
    "active_principal", "bind_principal",
    "authorize", "enforce",
]
