# -*- coding: utf-8 -*-
"""cex_rbac_audit.py -- the append-only RBAC violation audit sink (the thin wrapper).

cex_rbac.py wired the pure decision (authorize) + the halting gate (enforce); by design
authorize() does NO I/O so it stays trivially testable and safe to call anywhere. This
module adds the audit tier the policy mandates (p09_rbac_tenant_isolation "Audit Trail"):
a tenant-rooted, append-only violation log, emitted by a thin wrapper around enforce --
exactly the "natural home" the RBAC learning record ([[p10_lr_rbac_principal_session]]
item #2) names. The pure decision stays pure; logging lives here.

  - log_rbac_violation()  -- append ONE JSONL record to the tenant-rooted sink.
  - classify_severity()   -- map a denial to CRITICAL | HIGH | MEDIUM per the policy table.
  - enforce_audited()      -- authorize; on DENY log the violation then HALT (SystemExit),
                             mirroring cex_rbac.enforce; on ALLOW return the principal.

Sink path (policy): .cex/tenants/<tid>/runtime/signals/rbac_violation.log -- resolved via
the ONE canonical resolver (cex_tenant_paths.resolve_tenant_path, surface='runtime'). With
CEX_TENANT_ID UNSET the sink is the legacy global .cex/runtime/signals/rbac_violation.log,
byte-path-identical to pre-tenant behavior. Tenant-rooted + append-only per the policy.

Severity table (p09_rbac_tenant_isolation):
  Cross-tenant access attempt   -> CRITICAL
  Secret access by member/viewer -> HIGH
  Self-score attempt            -> HIGH
  (any other matrix denial)     -> MEDIUM

BEHAVIOR-PRESERVING INVARIANT (the IRON RULE, inherited from cex_rbac): with NO principal
bound, enforce_audited() is a no-op that ALLOWS (returns None) and writes NOTHING -- the
legacy single-tenant path is byte-identical to today. The sink is only ever touched when a
bound principal is actually DENIED.

FAIL-OPEN on the LOG, FAIL-CLOSED on the DECISION: a denial ALWAYS halts (enforce posture);
if the audit write itself fails (disk full, race), we never convert that into a security
bypass and never crash the halting path -- the SystemExit still fires. Audit loss is logged
to stderr, never swallowed silently and never allowed to mask the deny.

Layering (acyclic): cex_rbac_audit -> cex_rbac -> cex_tenant_paths -> cex_bootstrap.
ASCII-only per .claude/rules/ascii-code-rule.md.
"""
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent
if str(_ROOT / "_tools") not in sys.path:
    sys.path.insert(0, str(_ROOT / "_tools"))

# Reuse the canonical decision + tenant guard -- never reinvented.
from cex_rbac import authorize  # noqa: E402

LOG_NAME = "rbac_violation.log"

# Severity constants (the policy table values).
CRITICAL = "CRITICAL"
HIGH = "HIGH"
MEDIUM = "MEDIUM"

# Resource-name tokens that indicate the SECRETS surface (for the member/viewer rule).
_SECRET_TOKENS = ("secret", "secrets", ".env", "oauth", "credential", "api_key", "apikey")
# Action/resource tokens that indicate a self-score attempt (quality is peer-assigned).
_SELF_SCORE_TOKENS = ("self_score", "selfscore", "quality", "score")


def _now_iso():
    """UTC ISO-8601 timestamp (ASCII). Audit records are time-ordered + append-only."""
    return datetime.now(timezone.utc).isoformat()


def _resolve_log_path(tenant_id=None):
    """Tenant-rooted sink path via the ONE canonical resolver (surface=runtime/signals).
    Degrade-never: if cex_tenant_paths is not importable in this context, fall back to the
    legacy global join -- single-tenant safe, byte-path-identical to pre-tenant."""
    try:
        from cex_tenant_paths import resolve_tenant_path
        return resolve_tenant_path("signals", LOG_NAME, surface="runtime",
                                   tenant_id=tenant_id, create=True)
    except Exception:
        sink = _ROOT / ".cex" / "runtime" / "signals"
        sink.mkdir(parents=True, exist_ok=True)
        return sink / LOG_NAME


def _resource_name(resource):
    """Display name of a resource: a bare string is itself; a Resource exposes .name."""
    if resource is None:
        return None
    if isinstance(resource, str):
        return resource
    return getattr(resource, "name", str(resource))


def _resource_tenant(resource):
    """Tenant carried by a resource (None for a bare string / tenant-less resource)."""
    if resource is None or isinstance(resource, str):
        return None
    return getattr(resource, "tenant_id", None)


def _has_token(text, tokens):
    """True if any token appears (case-insensitive) in text. None-safe."""
    if not text:
        return False
    low = str(text).lower()
    return any(tok in low for tok in tokens)


def classify_severity(principal, action, resource=None):
    """Map a DENIED (principal, action, resource) to a policy severity.

    Order matters -- the most severe matching rule wins:
      1. Cross-tenant access attempt   -> CRITICAL (resource carries a tenant != principal's).
      2. Secret access by member/viewer -> HIGH    (secrets surface + a low-privilege role).
      3. Self-score attempt            -> HIGH     (quality/score action -- peer-assigned only).
      4. otherwise                     -> MEDIUM   (an ordinary role-matrix denial).
    A None principal cannot generate a violation (default-allow), so this assumes bound."""
    role = (getattr(principal, "role", "") or "").strip().lower()
    p_tid = getattr(principal, "tenant_id", None)
    r_tid = _resource_tenant(resource)
    r_name = _resource_name(resource)

    # 1. Cross-tenant: the resource is tenant-scoped and does NOT match the principal's tenant.
    if r_tid is not None and p_tid is not None and str(r_tid) != str(p_tid):
        return CRITICAL
    # 2. Secret access by a low-privilege role.
    if role in ("member", "viewer") and _has_token(r_name, _SECRET_TOKENS):
        return HIGH
    # 3. Self-score attempt.
    if _has_token(action, _SELF_SCORE_TOKENS) or _has_token(r_name, _SELF_SCORE_TOKENS):
        return HIGH
    return MEDIUM


def log_rbac_violation(principal, action, resource=None, severity=None, reason=None,
                       tenant_id=None):
    """Append ONE JSONL record to the tenant-rooted, append-only violation sink.

    The record is self-describing (ts, severity, principal, role, type, bound tenant, action,
    resource name + tenant, reason). severity defaults to classify_severity(). tenant_id
    overrides the sink's tenant root (defaults to the active CEX_TENANT_ID).

    FAIL-OPEN: never raises. An audit write failure is reported to stderr and the path is
    returned as None -- audit loss must never become a crash or (worse) a silent security
    bypass. Returns the sink Path on success, None on a write failure."""
    if severity is None:
        severity = classify_severity(principal, action, resource)
    record = {
        "ts": _now_iso(),
        "event": "rbac_violation",
        "severity": severity,
        "principal_id": getattr(principal, "principal_id", None),
        "role": getattr(principal, "role", None),
        "principal_type": getattr(principal, "principal_type", None),
        "bound_tenant": getattr(principal, "tenant_id", None),
        "action": str(action),
        "resource": _resource_name(resource),
        "resource_tenant": _resource_tenant(resource),
        "reason": reason,
        "pid": os.getpid(),
    }
    try:
        path = _resolve_log_path(tenant_id=tenant_id)
        # Append-only: open in 'a' mode, one compact JSON object per line.
        with open(path, "a", encoding="utf-8") as fh:
            fh.write(json.dumps(record, ensure_ascii=True, sort_keys=True) + "\n")
        return path
    except Exception as exc:  # fail-open: audit loss must not mask the deny or crash
        sys.stderr.write("[rbac-audit] WARN: could not write violation log: %s\n" % exc)
        return None


def _deny_reason(principal, action, resource=None):
    """Human-readable reason a denial fired, for the audit record. Re-derives the cause from
    the same inputs authorize() used (cross-tenant vs role-matrix vs unknown role)."""
    role = (getattr(principal, "role", "") or "").strip().lower()
    p_tid = getattr(principal, "tenant_id", None)
    r_tid = _resource_tenant(resource)
    if r_tid is not None and p_tid is not None and str(r_tid) != str(p_tid):
        return ("cross-tenant access: principal bound to %r may not touch %r"
                % (p_tid, r_tid))
    from cex_rbac import ROLES
    if role not in ROLES:
        return "unknown role %r grants nothing (deny-by-default)" % role
    return "role %r is not granted action %r (deny-by-default role matrix)" % (role, action)


def enforce_audited(principal, action, resource=None):
    """The audited halting gate -- the thin wrapper around enforce the policy calls for.

    Identical control flow to cex_rbac.enforce (fail-closed: SystemExit on deny), with ONE
    addition: a denied bound principal writes a violation record to the append-only sink
    BEFORE the halt. On allow, returns the principal. With NO principal bound, allows and
    returns None and writes NOTHING -- the behavior-preserving invariant, unchanged.

    The deny ALWAYS halts even if the audit write fails (log_rbac_violation is fail-open):
    audit is a side effect of the gate, never a precondition for it."""
    if principal is None:
        return None  # no principal bound -> legacy default-allow (UNCHANGED, no audit)
    if authorize(principal, action, resource):
        return principal
    reason = _deny_reason(principal, action, resource)
    severity = classify_severity(principal, action, resource)
    log_rbac_violation(principal, action, resource, severity=severity, reason=reason)
    who = getattr(principal, "principal_id", "?")
    role = getattr(principal, "role", "?")
    raise SystemExit(
        "ERROR: RBAC DENIED -- principal %r (role=%r) may not %s %r "
        "(deny-by-default role matrix, fail-closed; logged %s)"
        % (who, role, action, _resource_name(resource), severity))


__all__ = [
    "CRITICAL", "HIGH", "MEDIUM", "LOG_NAME",
    "classify_severity", "log_rbac_violation", "enforce_audited",
]
