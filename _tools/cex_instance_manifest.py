# -*- coding: utf-8 -*-
"""cex_instance_manifest.py -- the T6 INSTANCE MANIFEST (CONVERGENCE C10).

ONE CEX instance = THREE independently-versioned axes bound by ONE manifest + ONE
lock, so onboarding a company is "bootstrap a tenant + bind a manifest", NEVER a fork.

Design (the source of truth this implements):
    N03_engineering/P06_schema/p06_is_instance_manifest.md

The three axes (each owned by an independent party on an independent release cadence):
  1. framework      -- cex-lab (this repo)     -- semver of the framework, we own + bump.
  2. tenant_overlay -- the company (tenant #1)  -- overlay package semver, they own + bump.
  3. fabric_endpoint-- vendor_fabric (EXTERNAL)     -- referenced by CONTRACT version only.

ADDITIVE / ZERO-REGRESSION CONTRACT (the safety invariant):
  - This is a NEW sibling module. cex_bootstrap imports it lazily (function body, never
    at load time) so the bootstrap import graph stays acyclic + load-time-unchanged.
  - The manifest + lock are NEW state written ALONGSIDE .bootstrapped, NEVER replacing it
    (the design's "lock supersedes .bootstrapped" is the long-term plan; this implementation
    leaves .bootstrapped / is_bootstrapped / --check byte-identically intact).
  - Single-tenant mode (no CEX_TENANT_ID) and the existing --tenant brand flow are unchanged
    when no manifest axes are supplied. The manifest is OPTIONAL, additive state.
  - Paths go through cex_tenant_paths.resolve_tenant_path (fail-closed, the repo-wide guard).
    We never hand-join tenant paths.

Reproducibility: the lock pins each axis's resolved version + a content hash (Part B.1), so a
party bumping a version cannot silently break the instance -- drift is DETECTED, surfaced, and
gated (fail-closed on an incompatible framework/contract version), never absorbed (Part B.2).

ASCII-only per .claude/rules/ascii-code-rule.md. stdlib only (hashlib/json + yaml-if-present).
"""
import hashlib
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "_tools"))

# yaml is a hard dependency of the repo tooling. Do NOT auto-fetch it at import time
# (audit R11): an unpinned ``pip install`` inside a governance-path tool is a supply-
# chain hazard (network fetch + arbitrary code on install, no integrity pin). Fail
# with a clear, actionable message instead and let the operator install it.
try:
    import yaml
except ImportError as exc:  # pragma: no cover - pyyaml ships with the repo tooling
    raise ImportError(
        "cex_instance_manifest requires PyYAML, which is not installed. "
        "Install it explicitly: 'pip install pyyaml' (or 'python -m pip install "
        "pyyaml'). It is NOT auto-fetched (no unpinned network install in a "
        "governance-path tool)."
    ) from exc

# The repo-wide, fail-closed path guard (the ONE seam; never hand-join tenant paths).
from cex_tenant_paths import resolve_tenant_path

# This module's own schema + bootstrap-producer version (recorded in the lock).
SCHEMA_VERSION = "1.0.0"        # matches p06_is_instance_manifest.md version
BOOTSTRAP_VERSION = "1.0.0"     # cex_bootstrap producer that emits this lock shape

# Deterministic framework-version source (axis 1). archetypes/VERSION.yaml::cex_version is
# the committed, repo-owned version manifest (bumped by _tools/bump_version.py). We read a
# FILE, never call git at import (git describe is non-deterministic across clones/shallows and
# would couple load-time to a subprocess). Fallback constant keeps a checkout with no VERSION
# file deterministic rather than crashing.
VERSION_YAML = ROOT / "archetypes" / "VERSION.yaml"
_FRAMEWORK_VERSION_FALLBACK = "0.0.0"

# What the framework build EXPOSES to the overlay + fabric axes. These are framework-owned
# constants (axis 1 publishes them); the compat matrix (B.3) checks the other axes against them.
FRAMEWORK_OVERLAY_CONTRACT_VERSION = "1.0.0"
FRAMEWORK_SUPPORTED_FABRIC_CONTRACTS = (">=1.0.0 <2.0.0",)
DEFAULT_FROZEN_SURFACES = ("8f_pipeline",)

# Residency ranking for the overlay_x_fabric predicate (B.3). lan_only(0) < region(1) < any(2):
# a LOWER rank is STRICTER. The governing intent (B.3 comment + GDP residency_overrides_cost):
# "an overlay demanding lan_only MUST NOT be bound to an 'any' fabric" -- i.e. the bound fabric
# must be AT LEAST AS STRICT as the overlay demands. Predicate (evaluate_compat):
#   fabric_rank <= overlay_demand_rank   (fabric stricter-or-equal satisfies the demand).
# (The doc's literal formula reads 'demand_rank <= fabric_rank'; that contradicts its own
# worked example, so we implement the example's intent -- the stricter sovereignty guarantee.)
_RESIDENCY_RANK = {"lan_only": 0, "region": 1, "any": 2}

MANIFEST_NAME = "instance.yaml"
LOCK_NAME = "instance.lock"


# --------------------------------------------------------------------------- #
# Deterministic version sourcing (axis 1)                                     #
# --------------------------------------------------------------------------- #
def framework_version() -> str:
    """The cex-lab framework version, read deterministically from archetypes/VERSION.yaml
    (key: cex_version). FILE-based, never `git describe` -- reproducible across clones and
    never couples import to a subprocess. Degrade-never: a missing/malformed file yields the
    fallback constant rather than crashing the bind."""
    try:
        if VERSION_YAML.exists():
            data = yaml.safe_load(VERSION_YAML.read_text(encoding="utf-8")) or {}
            v = data.get("cex_version")
            if v:
                return str(v).strip()
    except Exception:
        pass
    return _FRAMEWORK_VERSION_FALLBACK


# --------------------------------------------------------------------------- #
# Content hashing (Part B.1 -- what makes drift DETECTABLE)                    #
# --------------------------------------------------------------------------- #
def _hash_obj(obj) -> str:
    """sha256 of a canonical JSON encoding of a dict/list (sorted keys, ASCII). Stable across
    runs + platforms, so a re-hash on the next boot compares meaningfully against the lock."""
    blob = json.dumps(obj, sort_keys=True, ensure_ascii=True, separators=(",", ":"))
    return "sha256:" + hashlib.sha256(blob.encode("ascii")).hexdigest()


def _normalize_axes(framework_axis: dict, tenant_overlay_axis: dict,
                    fabric_axis: dict) -> dict:
    """The canonical (hashable) projection of the three axes -- the subset whose change
    constitutes drift. Stored verbatim so verify can re-derive + compare it later."""
    return {
        "framework": {
            "version": framework_axis.get("version"),
            "source": framework_axis.get("source"),
            "ref": framework_axis.get("ref"),
            "overlay_contract_version": framework_axis.get("overlay_contract_version"),
            "frozen_surfaces": list(framework_axis.get("frozen_surfaces", [])),
        },
        "tenant_overlay": {
            "tenant_id": tenant_overlay_axis.get("tenant_id"),
            "version": tenant_overlay_axis.get("version"),
            "requires_overlay_contract": tenant_overlay_axis.get("requires_overlay_contract"),
            "overlays": tenant_overlay_axis.get("overlays", {}),
            "residency_demand": tenant_overlay_axis.get("residency_demand", "any"),
        },
        "fabric_endpoint": {
            "enabled": bool(fabric_axis.get("enabled", False)),
            "contract_version": fabric_axis.get("contract_version"),
            "base_url": fabric_axis.get("base_url"),
            "residency": fabric_axis.get("residency"),
            "posture": fabric_axis.get("posture"),
        },
    }


# --------------------------------------------------------------------------- #
# Minimal semver range satisfaction (Part B.3 -- the cross-axis compat matrix) #
# --------------------------------------------------------------------------- #
def _parse_semver(v: str):
    """(major, minor, patch) ints from a 'X.Y.Z' string (pre-release/build stripped). Missing
    components default to 0. ValueError on a non-numeric core -> caller treats as unsatisfiable."""
    core = str(v).strip().lstrip("vV").split("+", 1)[0].split("-", 1)[0]
    parts = (core.split(".") + ["0", "0", "0"])[:3]
    return tuple(int(p) for p in parts)


def version_satisfies(version: str, spec: str) -> bool:
    """True if `version` satisfies `spec`. Supports a space-separated conjunction of
    comparators (>=, >, <=, <, =/==) and a bare exact version. Deliberately small (no pip
    dependency): the design only needs ranges like '>=2.0.0 <3.0.0' and exact pins. A spec we
    cannot parse returns False (fail-closed -- an unparseable constraint never silently passes)."""
    if version is None or spec is None:
        return False
    spec = str(spec).strip()
    if not spec:
        return True
    try:
        ver = _parse_semver(version)
    except (ValueError, AttributeError):
        return False
    ops = [(">=", lambda a, b: a >= b), ("<=", lambda a, b: a <= b),
           ("==", lambda a, b: a == b), (">", lambda a, b: a > b),
           ("<", lambda a, b: a < b), ("=", lambda a, b: a == b)]
    for token in spec.split():
        matched = None
        for sym, fn in ops:
            if token.startswith(sym):
                matched = (sym, fn)
                break
        try:
            if matched is None:                      # bare version == exact pin
                if ver != _parse_semver(token):
                    return False
            else:
                sym, fn = matched
                bound = _parse_semver(token[len(sym):])
                if not fn(ver, bound):
                    return False
        except (ValueError, AttributeError):
            return False                             # unparseable comparand -> fail-closed
    return True


def _spec_satisfies_any(version: str, specs) -> bool:
    """True if `version` satisfies AT LEAST ONE spec in the list (used for the framework's
    published supported_fabric_contracts range list)."""
    return any(version_satisfies(version, s) for s in specs)


def evaluate_compat(axes: dict) -> dict:
    """Evaluate the three cross-axis predicates (B.3). Returns the compat_resolved block:
    each predicate -> 'ok' | 'fail', plus an overall 'status' (valid | incompatible) and a
    human-readable 'reasons' list naming the exact failing pair + unsatisfied range.

      framework_x_overlay : framework.overlay_contract_version IN overlay.requires_overlay_contract
      framework_x_fabric  : fabric.contract_version IN framework.supported_fabric_contracts
      overlay_x_fabric    : residency_rank(overlay demand) <= residency_rank(fabric.residency)

    fabric predicates are vacuously 'ok' when the fabric axis is disabled (local-only routing)."""
    fw = axes["framework"]
    ov = axes["tenant_overlay"]
    fab = axes["fabric_endpoint"]
    reasons = []

    fw_x_ov = version_satisfies(fw.get("overlay_contract_version"),
                                ov.get("requires_overlay_contract"))
    if not fw_x_ov:
        reasons.append(
            "framework_x_overlay: framework overlay_contract_version %r NOT in overlay "
            "requires_overlay_contract %r" % (fw.get("overlay_contract_version"),
                                              ov.get("requires_overlay_contract")))

    if fab.get("enabled"):
        fw_x_fab = _spec_satisfies_any(fab.get("contract_version"),
                                       FRAMEWORK_SUPPORTED_FABRIC_CONTRACTS)
        if not fw_x_fab:
            reasons.append(
                "framework_x_fabric: fabric contract_version %r NOT in framework "
                "supported_fabric_contracts %r" % (fab.get("contract_version"),
                                                   list(FRAMEWORK_SUPPORTED_FABRIC_CONTRACTS)))
        demand = ov.get("residency_demand") or "any"
        fab_res = fab.get("residency") or "lan_only"
        # fabric must be AT LEAST AS STRICT as the overlay demands: fabric_rank <= demand_rank.
        ov_x_fab = _RESIDENCY_RANK.get(fab_res, 0) <= _RESIDENCY_RANK.get(demand, 2)
        if not ov_x_fab:
            reasons.append(
                "overlay_x_fabric: fabric residency %r is looser than overlay demand %r "
                "(residency overrides cost)" % (fab_res, demand))
    else:
        fw_x_fab = True
        ov_x_fab = True

    ok = fw_x_ov and fw_x_fab and ov_x_fab
    return {
        "framework_x_overlay": "ok" if fw_x_ov else "fail",
        "framework_x_fabric": "ok" if fw_x_fab else "fail",
        "overlay_x_fabric": "ok" if ov_x_fab else "fail",
        "status": "valid" if ok else "incompatible",
        "reasons": reasons,
    }


# --------------------------------------------------------------------------- #
# Axis builders (apply defaults from Part A; normalize caller input)          #
# --------------------------------------------------------------------------- #
def _build_framework_axis(framework_version_in=None) -> dict:
    """Axis 1 (cex-lab). Defaults framework.version to the deterministic repo source."""
    fw = dict(framework_version_in or {}) if isinstance(framework_version_in, dict) else {}
    version = (framework_version_in if isinstance(framework_version_in, str)
               else fw.get("version")) or framework_version()
    return {
        "version": version,
        "source": fw.get("source", "git"),
        "ref": fw.get("ref", "v" + version),
        "frozen_surfaces": list(fw.get("frozen_surfaces", DEFAULT_FROZEN_SURFACES)),
        "overlay_contract_version": fw.get("overlay_contract_version",
                                           FRAMEWORK_OVERLAY_CONTRACT_VERSION),
    }


def _build_overlay_axis(tenant_id: str, tenant_overlay_ref=None) -> dict:
    """Axis 2 (the company). `tenant_overlay_ref` may be a version string OR a dict of overlay
    fields. brand_config defaults to the tenant's brand_config path (folds in today's brand axis).
    Validation: any key in `overlays` naming a framework frozen surface is REJECTED (8F is the
    moat -- enforced at bind, not just documented)."""
    ov = dict(tenant_overlay_ref) if isinstance(tenant_overlay_ref, dict) else {}
    version = (tenant_overlay_ref if isinstance(tenant_overlay_ref, str)
               else ov.get("version")) or "0.1.0"
    brand_cfg = ov.get("brand_config") or (
        ".cex/tenants/%s/brand/brand_config.yaml" % tenant_id)
    overlays = dict(ov.get("overlays", {}))
    frozen = set(DEFAULT_FROZEN_SURFACES)
    bad = [k for k in overlays if k in frozen]
    if bad:
        raise ValueError(
            "overlay targets a frozen surface: %s (frozen_surfaces=%s; 8F is frozen)"
            % (", ".join(sorted(bad)), sorted(frozen)))
    return {
        "tenant_id": tenant_id,
        "version": version,
        "requires_overlay_contract": ov.get("requires_overlay_contract", ">=1.0.0 <2.0.0"),
        "brand_config": brand_cfg,
        "overlays": overlays,
        "residency_demand": ov.get("residency_demand", "any"),
        "brand_audit_score": ov.get("brand_audit_score"),
    }


def _build_fabric_axis(fabric_endpoint=None) -> dict:
    """Axis 3 (vendor_fabric, EXTERNAL). Default: disabled (whole axis null-equivalent -> the
    instance routes local-only). When enabled, contract_version + base_url are required and
    residency defaults to the sovereignty-pin lan_only."""
    fab = dict(fabric_endpoint) if isinstance(fabric_endpoint, dict) else {}
    enabled = bool(fab.get("enabled", False))
    if not enabled:
        return {"enabled": False}
    if not fab.get("contract_version"):
        raise ValueError("fabric_endpoint.contract_version is required when enabled")
    if not fab.get("base_url"):
        raise ValueError("fabric_endpoint.base_url is required when enabled")
    node = {
        "enabled": True,
        "contract_version": fab.get("contract_version"),
        "base_url": fab.get("base_url"),
        "residency": fab.get("residency", "lan_only"),
        "posture": fab.get("posture", "pooled"),
    }
    if fab.get("discovery_url"):
        node["discovery_url"] = fab["discovery_url"]
    if fab.get("capability_min"):
        node["capability_min"] = fab["capability_min"]
    return node


# --------------------------------------------------------------------------- #
# A. write_instance_manifest -- bind the three axes + emit manifest + lock     #
# --------------------------------------------------------------------------- #
def manifest_path(tenant_id: str) -> Path:
    """Resolved (fail-closed) path of the tenant's instance.yaml under its runtime root."""
    return resolve_tenant_path(MANIFEST_NAME, surface="runtime", tenant_id=tenant_id)


def lock_path(tenant_id: str) -> Path:
    """Resolved (fail-closed) path of the tenant's instance.lock under its runtime root."""
    return resolve_tenant_path(LOCK_NAME, surface="runtime", tenant_id=tenant_id)


def write_instance_manifest(tenant_id, framework_version=None, tenant_overlay_ref=None,
                            fabric_endpoint=None, brand_audit_score=None):
    """Bind the THREE axes for `tenant_id` and write BOTH the manifest (intent) and the lock
    (resolved fact + content hashes) under the tenant root. The single entry point T6 specifies.

    Args:
      tenant_id          -- the tenant under HYBRID isolation (.cex/tenants/<tid>/).
      framework_version  -- axis 1: a version string OR a dict of framework fields. None ->
                            the deterministic repo source (archetypes/VERSION.yaml::cex_version).
      tenant_overlay_ref -- axis 2: a version string OR a dict of overlay fields.
      fabric_endpoint    -- axis 3: a dict; None/absent -> disabled (local-only routing).
      brand_audit_score  -- folds today's brand-audit score into the overlay lock node.

    Returns: (manifest_dict, lock_dict). Fail-closed: an INCOMPATIBLE cross-axis bind raises
    ValueError BEFORE any file is written (no half-written instance). Reuses resolve_tenant_path
    so the path can never escape the tenant root.
    """
    fw_axis = _build_framework_axis(framework_version)
    ov_axis = _build_overlay_axis(tenant_id, tenant_overlay_ref)
    if brand_audit_score is not None:
        ov_axis["brand_audit_score"] = brand_audit_score
    fab_axis = _build_fabric_axis(fabric_endpoint)

    # COMPAT gate (Part C step 6): evaluate the three predicates BEFORE writing. An incompatible
    # bind fails closed -- one party's bump cannot proceed if it breaks another party's contract.
    axes = _normalize_axes(fw_axis, ov_axis, fab_axis)
    compat = evaluate_compat(axes)
    if compat["status"] != "valid":
        raise ValueError(
            "instance bind INCOMPATIBLE (fail-closed, no write): " + "; ".join(compat["reasons"]))

    # MANIFEST (intent): the three axes + schema_version + instance_id. No lock block (the lock
    # is generated, never authored -- Part A.1).
    # The persisted overlay block keeps every field that feeds the hash (incl. residency_demand)
    # so a read-back round-trips to the SAME content_hash -- no false drift. brand_audit_score is
    # a lock-only fact (not part of the install identity), so it is dropped from the manifest.
    ov_manifest = {k: v for k, v in ov_axis.items() if k != "brand_audit_score"}
    manifest = {
        "schema_version": SCHEMA_VERSION,
        "instance_id": tenant_id,
        "framework": fw_axis,
        "tenant_overlay": ov_manifest,
        "fabric_endpoint": fab_axis,
    }

    # LOCK (fact): one resolved node per axis + per-axis content_hash + the frozen compat result.
    now = datetime.now(timezone.utc).isoformat()
    fw_node = dict(axes["framework"])
    fw_node["resolved_version"] = fw_axis["version"]
    fw_node["content_hash"] = _hash_obj(axes["framework"])

    ov_node = dict(axes["tenant_overlay"])
    ov_node["resolved_version"] = ov_axis["version"]
    ov_node["content_hash"] = _hash_obj(axes["tenant_overlay"])
    if ov_axis.get("brand_audit_score") is not None:
        ov_node["brand_audit_score"] = ov_axis["brand_audit_score"]

    fab_node = dict(axes["fabric_endpoint"])
    if fab_axis.get("enabled"):
        fab_node["resolved_contract_version"] = fab_axis.get("contract_version")
        fab_node["endpoint_fingerprint"] = _hash_obj({
            "base_url": fab_axis.get("base_url"),
            "capability_min": fab_axis.get("capability_min", {}),
        })

    lock = {
        "lock": {
            "locked_at": now,
            "schema_version": SCHEMA_VERSION,
            "bootstrap_version": BOOTSTRAP_VERSION,
            "framework_version_source": "archetypes/VERSION.yaml::cex_version",
            "nodes": {
                "framework": fw_node,
                "tenant_overlay": ov_node,
                "fabric_endpoint": fab_node,
            },
            "compat_resolved": {
                "framework_x_overlay": compat["framework_x_overlay"],
                "framework_x_fabric": compat["framework_x_fabric"],
                "overlay_x_fabric": compat["overlay_x_fabric"],
            },
            "status": "valid",
        }
    }

    mpath = manifest_path(tenant_id)
    lpath = lock_path(tenant_id)
    mpath.parent.mkdir(parents=True, exist_ok=True)
    with open(mpath, "w", encoding="utf-8") as fh:
        fh.write("# .cex/tenants/%s/%s -- CEX instance manifest (INTENT: 3 axes, version "
                 "ranges)\n" % (tenant_id, MANIFEST_NAME))
        fh.write("# Authored by cex_bootstrap. Schema: p06_is_instance_manifest.md\n")
        yaml.dump(manifest, fh, default_flow_style=False, sort_keys=False, allow_unicode=False)
    with open(lpath, "w", encoding="utf-8") as fh:
        fh.write("# .cex/tenants/%s/%s -- GENERATED by cex_bootstrap (do not hand-edit).\n"
                 % (tenant_id, LOCK_NAME))
        fh.write("# Resolved versions + content hashes (FACT). Drift detection re-hashes "
                 "these.\n")
        yaml.dump(lock, fh, default_flow_style=False, sort_keys=False, allow_unicode=False)
    return manifest, lock


# --------------------------------------------------------------------------- #
# B. read_instance_manifest + verify_instance_lock                            #
# --------------------------------------------------------------------------- #
def read_instance_manifest(tenant_id):
    """Return the tenant's manifest dict, or None when no manifest is bound (the clean
    'not bound' state -- never a crash). resolve_tenant_path keeps the read inside the root."""
    mpath = manifest_path(tenant_id)
    if not mpath.exists():
        return None
    try:
        return yaml.safe_load(mpath.read_text(encoding="utf-8")) or None
    except Exception:
        return None


def read_instance_lock(tenant_id):
    """Return the tenant's lock dict (the inner 'lock' block), or None when unlocked."""
    lpath = lock_path(tenant_id)
    if not lpath.exists():
        return None
    try:
        data = yaml.safe_load(lpath.read_text(encoding="utf-8")) or {}
        return data.get("lock")
    except Exception:
        return None


def is_manifest_bound(tenant_id) -> bool:
    """True iff a manifest is bound for this tenant (used by the optional --list-tenants row)."""
    return manifest_path(tenant_id).exists()


def verify_instance_lock(tenant_id):
    """Re-check the lock against the CURRENT axes (Part B.2) and return a drift report dict:

      {status, bound, drifted, incompatible, drift, reasons}

      - status 'not_bound'    : no manifest/lock -> the clean unbound state (bound=False).
      - status 'no_drift'     : every axis hash matches + the compat matrix still holds.
      - status 'drift_detected': mechanism 1 -- an axis content_hash changed vs the lock
                                 (a party edited an axis WITHOUT bumping its version). The
                                 'drift' list names each drifted axis + old/new hash.
      - status 'incompatible' : mechanism 2 -- a version bump moved an axis into an
                                 INCOMPATIBLE range. FAIL-CLOSED per the design.

    Read-only + cheap (the every-boot re-check). A missing manifest is the clean 'not bound'
    state, never an error."""
    manifest = read_instance_manifest(tenant_id)
    lock = read_instance_lock(tenant_id)
    if manifest is None or lock is None:
        return {"status": "not_bound", "bound": False, "drifted": False,
                "incompatible": False, "drift": [], "reasons": []}

    # Recompute the current axes from the manifest-on-disk, exactly as the lock was produced.
    current = _normalize_axes(
        manifest.get("framework", {}),
        manifest.get("tenant_overlay", {}),
        manifest.get("fabric_endpoint", {}),
    )

    # Mechanism 1: content-hash recompute per axis vs the locked hash.
    drift = []
    nodes = lock.get("nodes", {})
    hash_fields = {"framework": "content_hash", "tenant_overlay": "content_hash",
                   "fabric_endpoint": "endpoint_fingerprint"}
    for axis_name, field in hash_fields.items():
        if axis_name == "fabric_endpoint" and not current["fabric_endpoint"].get("enabled"):
            continue  # disabled fabric carries no fingerprint to compare
        locked_hash = nodes.get(axis_name, {}).get(field)
        if locked_hash is None:
            continue
        if axis_name == "fabric_endpoint":
            new_hash = _hash_obj({
                "base_url": current["fabric_endpoint"].get("base_url"),
                "capability_min": manifest.get("fabric_endpoint", {}).get("capability_min", {}),
            })
        else:
            new_hash = _hash_obj(current[axis_name])
        if new_hash != locked_hash:
            drift.append({"axis": axis_name, "locked_hash": locked_hash, "current_hash": new_hash})

    # Mechanism 2: re-evaluate the cross-axis compat matrix against the current axes.
    compat = evaluate_compat(current)
    incompatible = compat["status"] != "valid"

    if incompatible:
        status = "incompatible"            # fail-closed: named failing pair surfaced
    elif drift:
        status = "drift_detected"          # silent edit-without-bump surfaced
    else:
        status = "no_drift"
    return {
        "status": status,
        "bound": True,
        "drifted": bool(drift),
        "incompatible": incompatible,
        "drift": drift,
        "reasons": compat["reasons"],
    }


__all__ = [
    "framework_version",
    "write_instance_manifest",
    "read_instance_manifest",
    "read_instance_lock",
    "is_manifest_bound",
    "verify_instance_lock",
    "evaluate_compat",
    "version_satisfies",
    "manifest_path",
    "lock_path",
    "SCHEMA_VERSION",
]
