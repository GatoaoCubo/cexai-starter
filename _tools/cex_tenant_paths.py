# -*- coding: utf-8 -*-
"""cex_tenant_paths.py -- the ONE canonical tenant-path resolver (HYBRID isolation).

A2 (cex_bootstrap.py, 62da7c839) wired the BRAND tier of multi-tenant isolation: a
per-tenant brand_config under .cex/tenants/<tid>/ plus a fail-closed id guard
(_safe_tenant_id). A3 (0af6e77a1) HONESTLY documented the enforcement-tier gaps. This
module CLOSES them with a single source of truth instead of editing ~50 scattered tools:

  - resolve_tenant_path()  -- repo-wide path guard (closes the resolution-guard gap;
                              p08_adr warns this guard "becomes load-bearing").
  - tenant_brand_dir()     -- brand surface    (.cex/tenants/<tid>/brand).
  - tenant_runtime_dir()   -- runtime surface  (.cex/tenants/<tid>/runtime).
  - tenant_secrets_dir()   -- secrets surface  (.cex/tenants/<tid>/secrets).
  - tenant_memory_dir()    -- memory surface   (.cex/tenants/<tid>/memory).
  - load_tenant_secrets()  -- per-tenant .env loader (closes the secret-isolation gap).
  - global_env_keys()      -- keys in the global .env (must hold NO tenant key).
  - memory_namespace()/assert_memory_key() -- the p10 memory namespace guard.
  - deny_cross_tenant()    -- the RBAC cross-tenant deny invariant, enforced in code.

Contract (established by A2): the active tenant is CEX_TENANT_ID. When UNSET, every
resolver returns the LEGACY GLOBAL path -- the single-tenant default stays byte-identical
to pre-A2 behavior (no .cex/tenants/ indirection, nothing created). The tenant id is
sanitized fail-closed by _safe_tenant_id, REUSED from cex_bootstrap -- one guard, never
reinvented.

Design:    N03_engineering/P08_architecture/p08_adr_multitenant_hybrid.md
Contracts: p10_marc_tenant_isolation (memory), p09_oauth_tenant (secrets),
           p09_rbac_tenant_isolation (deny_cross_tenant).
ASCII-only per .claude/rules/ascii-code-rule.md.
"""
import os
from pathlib import Path

# Reuse the canonical, fail-closed id guard + roots from A2 -- never reinvent them.
# (cex_bootstrap does NOT import this module at load time, so this stays acyclic.)
from cex_bootstrap import _safe_tenant_id, ROOT, TENANTS_DIR

# Legacy global surfaces: the single-tenant default resolves to these (pre-A2 paths).
# 'secrets' maps to the repo root because the legacy global .env lives there; callers
# read it via load_tenant_secrets(), they do not enumerate the dir.
_GLOBAL = {
    "brand": ROOT / ".cex" / "brand",
    "runtime": ROOT / ".cex" / "runtime",
    "secrets": ROOT,
    "memory": ROOT / ".cex" / "memory",
    # 'ft' = the fine-tune corpus + adapter root. It lives OUTSIDE .cex/ (the
    # legacy _data/ft), so single-tenant mode stays byte-identical to today's
    # corpus path; tenant mode resolves to .cex/tenants/<tid>/ft, bringing the
    # FT surface under the fail-closed guard. This is the convergence prereq:
    # it closes the train-time FT cross-tenant leak (T5) and gives compute
    # routing a residency anchor for FT artifacts (T4). See
    # N07_admin/P08_architecture/handoff_convergence_investigation_verified.md.
    "ft": ROOT / "_data" / "ft",
    # 'overlay' = the per-tenant BEHAVIOR overlay root (CONVERGENCE T1 -- the
    # overlay tier of p08_adr_convergence_overlay_tier.md). It holds a tenant's
    # named extension-point overlays (kinds overlay first: kinds_overlay.yaml;
    # routing/builders/rules to follow). It maps to a legacy global path that is
    # INERT in single-tenant mode -- nothing lives there and nothing reads it
    # unless CEX_TENANT_ID is set -- so the single-tenant default stays
    # byte-identical to today; tenant mode resolves to .cex/tenants/<tid>/overlay,
    # bringing the overlay surface under the same fail-closed guard as the other
    # surfaces. Additive, mirrors how 'ft' was added: a NEW surface, no existing
    # surface is touched. NOTE this is NOT one of the four tenant-MUTABLE write
    # surfaces (runtime/brand/memory/secrets) the call-site ratchet measures, so
    # adding it does not perturb cex_tenant_callsite_audit's baseline.
    "overlay": ROOT / ".cex" / "overlays",
}
_SURFACES = tuple(_GLOBAL.keys())

# The global .env -- per the isolation invariant it MUST hold no tenant-scoped key.
GLOBAL_ENV = ROOT / ".env"


# --------------------------------------------------------------------------- #
# Tenant resolution                                                           #
# --------------------------------------------------------------------------- #
def active_tenant_id():
    """The bound tenant from CEX_TENANT_ID (fail-closed via _safe_tenant_id). Returns
    None when unset -> single-tenant global mode (legacy paths, nothing isolated)."""
    raw = os.environ.get("CEX_TENANT_ID")
    if not raw:
        return None
    return _safe_tenant_id(raw)


def _norm(p):
    """Fully-resolved absolute path (collapses '..' + symlinks) without requiring the
    path to exist. realpath is the cross-platform primitive the containment check needs."""
    return Path(os.path.realpath(str(p)))


def _surface_root(surface, tenant_id=None):
    """Root dir for a surface. Tenant-scoped when a tenant is active, else legacy global.
    Unknown surface -> hard fail (fail-closed; a typo must never silently widen scope)."""
    if surface not in _GLOBAL:
        raise SystemExit("ERROR: unknown tenant surface %r (allowed: %s)"
                         % (surface, ", ".join(_SURFACES)))
    tid = tenant_id if tenant_id is not None else active_tenant_id()
    if tid is None:
        return _GLOBAL[surface]
    return TENANTS_DIR / _safe_tenant_id(tid) / surface


def tenant_brand_dir(tenant_id=None):
    """Brand surface root: .cex/tenants/<tid>/brand (tenant) | .cex/brand (global)."""
    return _surface_root("brand", tenant_id)


def tenant_runtime_dir(tenant_id=None):
    """Runtime surface root: .cex/tenants/<tid>/runtime (tenant) | .cex/runtime (global)."""
    return _surface_root("runtime", tenant_id)


def tenant_secrets_dir(tenant_id=None):
    """Secrets surface root: .cex/tenants/<tid>/secrets (tenant) | repo root (global,
    where the legacy .env lives). Read via load_tenant_secrets(), never enumerated."""
    return _surface_root("secrets", tenant_id)


def tenant_memory_dir(tenant_id=None):
    """Memory surface root: .cex/tenants/<tid>/memory (tenant) | .cex/memory (global).
    The per-tenant semantic store root (p10_marc_tenant_isolation)."""
    return _surface_root("memory", tenant_id)


# --------------------------------------------------------------------------- #
# Resolution guard (closes mechanism 2: guard ALL path builders, not just id) #
# --------------------------------------------------------------------------- #
def resolve_tenant_path(*parts, **kwargs):
    """THE repo-wide resolution guard -- the keystone the ADR calls load-bearing.

    Build a path under the active tenant's <surface> root from *parts, then assert the
    fully-resolved real path stays INSIDE that root. Any escape ('..', an absolute
    injection, a symlink pointing out) raises SystemExit -- fail-closed, the same posture
    as _safe_tenant_id. This is the single seam every tool should call instead of joining
    tenant paths by hand; it makes the id-level guard repo-wide.

    Keyword args:
      surface    -- one of brand|runtime|secrets|memory|ft|overlay (default 'runtime').
      tenant_id  -- override the active tenant (defaults to CEX_TENANT_ID).
      create     -- when True, mkdir -p the parent dir of the resolved path.

    Single-tenant default (CEX_TENANT_ID unset) resolves under the legacy global surface,
    so an unset environment behaves byte-identically to pre-A2."""
    surface = kwargs.pop("surface", "runtime")
    tenant_id = kwargs.pop("tenant_id", None)
    create = kwargs.pop("create", False)
    if kwargs:
        raise SystemExit("ERROR: resolve_tenant_path got unexpected kwargs: %s"
                         % ", ".join(sorted(kwargs)))

    root = _surface_root(surface, tenant_id)
    candidate = root.joinpath(*[str(p) for p in parts])
    root_r = _norm(root)
    cand_r = _norm(candidate)
    if cand_r != root_r and root_r not in cand_r.parents:
        raise SystemExit(
            "ERROR: tenant path escape blocked -- %r resolves outside surface root %r "
            "(fail-closed)" % (str(candidate), str(root)))
    if create:
        cand_r.parent.mkdir(parents=True, exist_ok=True)
    return cand_r


# --------------------------------------------------------------------------- #
# Secret isolation (closes mechanism 4: per-tenant secret loader)             #
# --------------------------------------------------------------------------- #
def _parse_env(path):
    """Minimal .env parser: KEY=VALUE per line; skip blanks + '#' comments + malformed
    lines. Strips surrounding quotes. Degrade-never: a missing file yields an empty dict."""
    out = {}
    p = Path(path)
    if not p.exists():
        return out
    for line in p.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, val = line.partition("=")
        key = key.strip()
        if key.lower().startswith("export "):
            key = key[len("export "):].strip()
        val = val.strip().strip('"').strip("'")
        if key:
            out[key] = val
    return out


def load_tenant_secrets(tenant_id=None, apply=False):
    """Per-tenant secret loader (closes the secret gap; p09_oauth_tenant).

    Read .cex/tenants/<tid>/secrets/.env (via the guarded resolver) into a dict. In
    single-tenant mode (no CEX_TENANT_ID) this reads the legacy global root .env. The
    global .env MUST hold no tenant-scoped key -- per-tenant credentials live ONLY under
    the tenant root, so tenant A's keys can never reach tenant B. When apply=True, inject
    into os.environ but only for keys NOT already set (never clobber a live value).

    Degrade-never: a tenant with no .env yet yields an empty dict, not an error."""
    env_path = resolve_tenant_path(".env", surface="secrets", tenant_id=tenant_id)
    secrets = _parse_env(env_path)
    if apply:
        for k, v in secrets.items():
            os.environ.setdefault(k, v)
    return secrets


def global_env_keys():
    """Keys present in the GLOBAL .env. Per the isolation invariant this set MUST contain
    no tenant-scoped credential -- tenant keys live only under .cex/tenants/<tid>/secrets/."""
    return set(_parse_env(GLOBAL_ENV).keys())


# --------------------------------------------------------------------------- #
# Memory namespace guard (closes the memory surface; p10_marc_tenant_isolation)#
# --------------------------------------------------------------------------- #
def memory_namespace(tenant_id=None):
    """The memory key namespace prefix for the active tenant: '<tid>/' (p10_marc). Empty
    string in single-tenant global mode (no prefix == legacy behavior, unchanged)."""
    tid = tenant_id if tenant_id is not None else active_tenant_id()
    return "" if tid is None else _safe_tenant_id(tid) + "/"


def assert_memory_key(key, tenant_id=None):
    """Namespace guard for a memory key (p10_marc read/write pipeline). A key must be
    prefixed by the bound namespace '<tid>/'. A foreign- or un-prefixed key in tenant mode
    is a cross-namespace recall -> HALT (fail-closed). Returns the key on allow. In global
    mode (no namespace) every key is allowed -- there is no other tenant to bleed into."""
    ns = memory_namespace(tenant_id)
    if ns and not str(key).startswith(ns):
        raise SystemExit(
            "ERROR: memory key %r escapes tenant namespace %r -- cross-namespace recall "
            "denied (p10_marc, fail-closed)" % (str(key), ns))
    return key


# --------------------------------------------------------------------------- #
# RBAC cross-tenant deny (mechanism 3 -- the single load-bearing deny rule)    #
# --------------------------------------------------------------------------- #
def deny_cross_tenant(target_tenant_id, bound_tenant_id=None, op="access"):
    """RBAC deny-by-default isolation gate (p09_rbac_tenant_isolation: deny_cross_tenant).

    THE isolation invariant in code: a principal bound to tenant A may NEVER touch tenant
    B. Compare the requested target against the bound tenant (CEX_TENANT_ID by default) and
    HALT (SystemExit) on mismatch -- fail-closed. Returns the validated target id on allow.

    HONEST SCOPE: this enforces the cross-tenant boundary, which is the most important of
    the RBAC deny rules. The full role matrix (owner/admin/member/viewer x resource) is NOT
    wired -- there is no principal/session/role model yet. That is a documented follow-up,
    not a fabricated pass."""
    bound = bound_tenant_id if bound_tenant_id is not None else active_tenant_id()
    target = _safe_tenant_id(target_tenant_id)
    if bound is None:
        # Single-tenant global: there is no other tenant to cross into.
        return target
    bound = _safe_tenant_id(bound)
    if target != bound:
        raise SystemExit(
            "ERROR: cross-tenant %s DENIED -- principal bound to %r may not touch %r "
            "(deny_cross_tenant, fail-closed)" % (op, bound, target))
    return target


__all__ = [
    "active_tenant_id",
    "tenant_brand_dir", "tenant_runtime_dir", "tenant_secrets_dir", "tenant_memory_dir",
    "resolve_tenant_path",
    "load_tenant_secrets", "global_env_keys", "GLOBAL_ENV",
    "memory_namespace", "assert_memory_key",
    "deny_cross_tenant",
]
