#!/usr/bin/env python3
# coding: utf-8
"""CEX Autonomous Capability Router (ACR) -- propose-into-handoff prerequisite layer.

The intent compiler already turns user_input into {kind, pillar, nucleus, verb,
confidence}. The handoff is already the autonomous mechanism (a nucleus boots from
it and works out-of-loop). MISSING (until now): a layer that, given the resolved
kind, AUTO-PLAYS the prerequisite capabilities and BAKES them into the handoff so
the booting nucleus receives them.

This module is that layer. It is ADDITIVE, offline-first, and degrades to a complete
no-op when the cexai package is absent OR the kind declares no autonomy. The 8F
pipeline and the 301 existing kinds are NEVER regressed.

Two public functions (signatures are STABLE -- tests import them):

    resolve_prerequisites(kind, verb, confidence, handoff_path) -> dict
        Plan only. Returns {kind, verb, gated, disabled, actions, reason}.
        - gated:    confidence < policy.min_confidence (defer to GDP, run nothing).
        - disabled: kill-switch active (env / global / per-kind autonomy.enabled=false).
        - actions:  [{action, reversible, satisfied, reason}, ...] in topo order.

    execute_prerequisites(kind, verb, confidence, handoff_path, *, dry_run=False,
                          mission_id=None) -> dict
        Plans (resolve), then runs each action in topo order, appends a
        "## Prerequisites (auto-resolved by ACR)" block to the handoff (idempotent),
        and returns a report dict. dry_run => plan + would-append, no side effects.

CLI:
    python _tools/cex_capability_router.py --preflight --nucleus n0X \
        --handoff PATH [--dry-run] [--json]

Safety gates (all mandatory):
  - confidence < min_confidence -> gated, run NOTHING, append a one-line GDP-defer note.
  - kill-switch: env CEX_ACR_DISABLE=1 OR policy.global_kill_switch OR per-kind
    autonomy.enabled=false -> complete no-op.
  - idempotency: the prerequisites header already present -> skip; an action whose
    satisfied_if_glob matches -> skip that action.
  - grid double-exec guard: best-effort per-mission lockfile + the idempotency glob.
  - observability: lazy cexai.governance.tracing.MissionTracer span; ALWAYS write a
    machine-readable audit jsonl (.cex/runtime/acr/{mission}.jsonl) + an audit table
    in the handoff.
  - P3 graduated-HITL: a REVERSIBLE action runs freely (as below). An action planned
    with reversible=False (an autonomy prerequisite flagged irreversible:true) is GATED
    through cexai.governance.hitl.FileApprovalGate. The gate is EMIT-AND-DEFER and
    NON-BLOCKING: it emits a pending approval request, SKIPS the action, and bakes a
    note into the handoff; it NEVER calls await_decision (which can block up to 24h).
    FAIL-CLOSED: gate unavailable (cexai absent) or verdict pending => the irreversible
    action is NOT run; only a recorded `approve` verdict lets a future run proceed.
  - P3 RBAC auto-flag: a deploy verb or a requires_live_tools kind sets a baked-in flag +
    a handoff note (the BOOTING nucleus enforces cexai.governance.rbac under its own
    principal -- the router NEVER calls enforce() at dispatch time, which is dev mode).
  - R-188 ambient-pip-shadow guard: every lazy `cexai` import below is preceded by
    _require_cexai_vendored(), which verifies a bare `import cexai` resolves under THIS
    repo's root (not a stray/ambient pip-installed `cexai`) before trusting it; a shadow
    is treated identically to "genuinely absent" (see _cexai_is_vendored).
  - R-189 ACTION_TABLE: adding a prerequisite action used to mean hand-syncing 3
    duplicated ladders (the EXECUTOR dispatch, the RENDERER detail sections, and the
    unknown-action fallback-error string). All 3 now read one module-level
    ACTION_TABLE (action_name -> executor + render callables); a new action is its
    _run_xxx() reflex plus ONE table row (see the ACTION_TABLE section below).

Reversible actions (run freely): spec_kit EMITS a reversible template + a read-only
analyze; external_context is a read-only gather; blueprint + reposynth are PROPOSE-ONLY
(they surface a REUSE suggestion and NEVER call blueprint apply_stack / reposynth
synthesize). P3 ships the HITL + RBAC MECHANISM + tests only -- it enables NO real
irreversible action (those stay propose-only until explicitly promoted).

ASCII-only per .claude/rules/ascii-code-rule.md.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
from collections.abc import Callable
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, NamedTuple

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent

# R-188: a second, NEVER-monkeypatched anchor for the ambient-pip-shadow guard
# (see _cexai_is_vendored below). Tests repoint the mutable `ROOT` at a tmp dir
# for handoff/policy isolation (tests/test_capability_router.py's `patched`
# fixture) -- the cexai vendored-check must stay anchored to the REAL on-disk
# repo this module lives in regardless of that, so it is captured separately.
_REPO_ROOT = HERE.parent

# Allow sibling _tools imports (cex_intent_resolver, cex_preflight_mcp) whether this
# module is run as a script or imported as a top-level module from a test.
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

KINDS_META_PATH = ROOT / ".cex" / "kinds_meta.json"
POLICY_PATH = ROOT / ".cex" / "capability_policy.json"
ACR_RUNTIME_DIR = ROOT / ".cex" / "runtime" / "acr"

PREREQ_HEADER = "## Prerequisites (auto-resolved by ACR)"

# Mirrors .cex/capability_policy.json -- used when the file is missing so the router
# is still well-defined offline. The file (when present) overrides this shallowly.
DEFAULT_POLICY: dict[str, Any] = {
    "version": "1.0",
    "global_kill_switch": False,
    "min_confidence": 0.60,
    "max_depth": 4,
    "actions": {
        "external_context": {"reversible": True, "impl": "preflight_mcp"},
        "spec_kit": {
            "reversible": True,
            "spec_dir": ".cex/runtime/specs/{nucleus}_{kind}",
            "satisfied_if_glob": ".cex/runtime/specs/{nucleus}_{kind}/spec.md",
            "cmd_scaffold": ["cexai", "spec-kit", "spec"],
            "cmd_check": ["cexai", "spec-kit", "analyze"],
        },
        # debt-c: surface the cexai F7 GOVERN gates (citation + reasoning_trace) --
        # which fire only in the headless cex_8f_runner -- to interactive dispatch by
        # baking their import paths into the handoff. Read-only probe (no gate call,
        # no heavy import); the booting nucleus runs them under its own F7.
        "f7_capability": {
            "reversible": True,
            "impl": "cexai F7 gates (citation + reasoning_trace)",
        },
    },
    "verb_overrides": {},
    # P3 graduated-HITL: irreversible actions emit a pending approval + skip (never block).
    "hitl": {
        "enabled": True,
        "approvals_dir": ".cexai/approvals",
        "requester": "acr",
    },
    # P3 RBAC: baked flag; the booting nucleus enforces under its principal.
    "rbac": {
        "flag_on_verbs": ["deploy"],
        "flag_on_requires_live_tools": True,
    },
}

# Status tokens (ASCII).
ST_DONE = "done"
ST_SKIPPED = "skipped"
ST_WOULD_RUN = "would-run"
ST_GATED = "gated"
ST_GATED_HITL = "gated-hitl"
ST_DISABLED = "disabled"
ST_NOOP = "noop"
ST_ERROR = "error"


def _log(msg: str) -> None:
    """Diagnostics to stderr (Article II); stdout stays machine-parseable."""
    print("[acr] %s" % msg, file=sys.stderr)


# ---------------------------------------------------------------------------
# Loaders
# ---------------------------------------------------------------------------

def _load_json(path: Path) -> dict[str, Any] | None:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None


def load_policy() -> dict[str, Any]:
    """Load capability_policy.json shallow-merged over DEFAULT_POLICY."""
    policy = json.loads(json.dumps(DEFAULT_POLICY))  # deep copy
    disk = _load_json(POLICY_PATH)
    if isinstance(disk, dict):
        for key, value in disk.items():
            if key == "actions" and isinstance(value, dict):
                merged = dict(policy.get("actions", {}))
                merged.update(value)
                policy["actions"] = merged
            else:
                policy[key] = value
    return policy


_kinds_meta_cache: dict[str, Any] | None = None


def load_kinds_meta() -> dict[str, Any]:
    """Load kinds_meta.json (cached). Empty dict on any error (never raises)."""
    global _kinds_meta_cache
    if _kinds_meta_cache is not None:
        return _kinds_meta_cache
    data = _load_json(KINDS_META_PATH)
    _kinds_meta_cache = data if isinstance(data, dict) else {}
    return _kinds_meta_cache


# ---------------------------------------------------------------------------
# Handoff parse
# ---------------------------------------------------------------------------

def _read_text(path: str | Path) -> str:
    try:
        return Path(path).read_text(encoding="utf-8", errors="replace")
    except Exception:
        return ""


def _frontmatter_block(text: str) -> str:
    """Return the YAML frontmatter block (between the first two '---' lines), or ''."""
    if not text.startswith("---"):
        return ""
    parts = text.split("\n")
    if not parts or parts[0].strip() != "---":
        return ""
    out: list[str] = []
    for line in parts[1:]:
        if line.strip() == "---":
            return "\n".join(out)
        out.append(line)
    # no closing fence -> not a valid frontmatter block
    return ""


def _fm_field(fm: str, name: str) -> str | None:
    """Extract a top-level scalar field from a frontmatter block."""
    m = re.search(r"(?m)^%s\s*:\s*(.+?)\s*$" % re.escape(name), fm)
    if not m:
        return None
    val = m.group(1).strip().strip("'\"")
    return val or None


def _title_and_head(text: str, n_lines: int = 20) -> str:
    """Title (first markdown heading) + first n body lines, frontmatter stripped."""
    body = text
    fm = _frontmatter_block(text)
    if fm:
        # drop the frontmatter region
        idx = text.find("\n---", 3)
        if idx != -1:
            body = text[idx + 4:]
    lines = [l for l in body.split("\n")]
    head = " ".join(l.lstrip("# ").strip() for l in lines[:n_lines] if l.strip())
    return head[:400]


def _infer_nucleus_from_kind(kind: str) -> str:
    """Infer the owning nucleus id (n0X) from kinds_meta llm_function. Default n07."""
    entry = load_kinds_meta().get(kind, {})
    fn = entry.get("llm_function", "")
    fn_to_nuc = {
        "BECOME": "n03", "INJECT": "n03", "PRODUCE": "n03",
        "CALL": "n05", "GOVERN": "n05",
    }
    return fn_to_nuc.get(fn, "n07")


def resolve_kind_from_handoff(handoff_path: str | Path) -> dict[str, Any]:
    """Resolve {kind, verb, confidence, nucleus, method} from a handoff file.

    Frontmatter 'kind:' is an explicit declaration (confidence 1.0). Absent that,
    fall back to cex_intent_resolver.resolve_intent over the title/body.
    """
    text = _read_text(handoff_path)
    fm = _frontmatter_block(text)

    nucleus = None
    verb = None
    if fm:
        nucleus = _fm_field(fm, "to") or _fm_field(fm, "nucleus")
        verb = _fm_field(fm, "verb")
        kind = _fm_field(fm, "kind")
        if kind:
            return {
                "kind": kind,
                "verb": verb or "create",
                "confidence": 1.0,
                "nucleus": (nucleus or _infer_nucleus_from_kind(kind)),
                "method": "frontmatter",
            }

    # Fall back to the intent resolver over the title/body.
    head = _title_and_head(text)
    try:
        from cex_intent_resolver import resolve_intent
        res = resolve_intent(head) if head else {}
    except Exception as exc:  # never break dispatch
        _log("intent resolver unavailable: %s" % exc)
        res = {}

    kind = res.get("kind")
    return {
        "kind": kind,
        "verb": verb or res.get("verb") or "create",
        "confidence": float(res.get("confidence") or 0.0),
        "nucleus": (nucleus or (res.get("nucleus") or "").lower()
                    or (_infer_nucleus_from_kind(kind) if kind else "n07")),
        "method": res.get("method", "intent"),
    }


# ---------------------------------------------------------------------------
# Prerequisite DAG (kinds) -- Kahn topo-sort with depth/cycle guard
# ---------------------------------------------------------------------------

def _autonomy(kind: str, kinds_meta: dict[str, Any]) -> dict[str, Any] | None:
    """Return the autonomy block for kind if it is an enabled dict, else None."""
    block = kinds_meta.get(kind, {}).get("autonomy")
    if isinstance(block, dict):
        return block
    return None


def topo_kinds(kind: str, kinds_meta: dict[str, Any], max_depth: int) -> list[str]:
    """Bounded dependency walk from kind over depends_on, returned dependencies-first.

    Only recurses into kinds that declare an autonomy block (the others are leaves --
    we do not expand the full 301-kind dependency graph). A visited-set + max_depth
    bound make cycles and pathological depth safe (never raises).
    """
    order: list[str] = []
    visited: set[str] = set()

    def visit(node: str, depth: int) -> None:
        if node in visited or depth > max_depth:
            return
        visited.add(node)
        entry = kinds_meta.get(node, {})
        deps = entry.get("depends_on") or []
        # Only expand dependencies that themselves carry an autonomy block; pure
        # structural deps (no autonomy) are leaves and need no further walk.
        for dep in deps:
            if isinstance(dep, str) and _autonomy(dep, kinds_meta) is not None:
                visit(dep, depth + 1)
        order.append(node)

    visit(kind, 0)
    return order


# ---------------------------------------------------------------------------
# Planning
# ---------------------------------------------------------------------------

def _kill_switch(kind: str, policy: dict[str, Any], kinds_meta: dict[str, Any]) -> str | None:
    """Return a non-empty reason string if the router is a complete no-op, else None."""
    if os.environ.get("CEX_ACR_DISABLE", "").strip() in ("1", "true", "True", "yes"):
        return "kill-switch: env CEX_ACR_DISABLE"
    if policy.get("global_kill_switch"):
        return "kill-switch: policy.global_kill_switch"
    block = kinds_meta.get(kind, {}).get("autonomy")
    if isinstance(block, dict) and block.get("enabled") is False:
        return "kill-switch: kind autonomy.enabled=false"
    return None


def _verb_in(action_def: dict[str, Any], verb: str, policy: dict[str, Any]) -> bool:
    """Does verb satisfy this prerequisite's when_verb (with policy.verb_overrides)?"""
    overrides = policy.get("verb_overrides", {}) or {}
    verb = overrides.get(verb, verb)
    when = action_def.get("when_verb")
    if not when:
        return True  # no constraint -> applies to any verb
    return verb in [overrides.get(v, v) for v in when]


def _satisfied(action_name: str, kind: str, nucleus: str, policy: dict[str, Any]) -> bool:
    """Idempotency: does a file already match the action's satisfied_if_glob?"""
    spec = policy.get("actions", {}).get(action_name, {})
    glob = spec.get("satisfied_if_glob")
    if not glob:
        return False
    rel = glob.format(nucleus=nucleus, kind=kind)
    try:
        matches = list(ROOT.glob(rel))
        return len(matches) > 0
    except Exception:
        return False


def _action_reversible(action_name: str, policy: dict[str, Any]) -> bool:
    return bool(policy.get("actions", {}).get(action_name, {}).get("reversible", True))


def resolve_prerequisites(
    kind: str | None,
    verb: str,
    confidence: float,
    handoff_path: str | Path,
) -> dict[str, Any]:
    """Plan the prerequisite actions for kind/verb. Pure -- no side effects.

    See module docstring for the return shape.
    """
    policy = load_policy()
    kinds_meta = load_kinds_meta()
    nucleus = _infer_nucleus_from_kind(kind) if kind else "n07"

    base = {
        "kind": kind,
        "verb": verb,
        "confidence": round(float(confidence or 0.0), 3),
        "nucleus": nucleus,
        "gated": False,
        "disabled": False,
        "actions": [],
        "reason": "",
    }

    if not kind:
        base["disabled"] = True
        base["reason"] = "no kind resolved from handoff"
        return base

    kill = _kill_switch(kind, policy, kinds_meta)
    if kill:
        base["disabled"] = True
        base["reason"] = kill
        return base

    # Plan the actions BEFORE the confidence gate so the report can show what WOULD
    # have run; execute_prerequisites enforces the gate (runs nothing when gated).
    actions: list[dict[str, Any]] = []

    # ACTION 0 -- external_context: driven by the kind's requires_external_context
    # meta flag (subsumes the legacy MCP gather). Independent of autonomy reflexes,
    # so it generalizes the old preflight to every external-context kind.
    if bool(kinds_meta.get(kind, {}).get("requires_external_context", False)):
        actions.append({
            "action": "external_context",
            "reversible": _action_reversible("external_context", policy),
            "satisfied": False,
            "reason": "kind requires_external_context",
        })

    # Autonomy reflexes -- walk the (bounded) dependency DAG dependencies-first and
    # collect each autonomy-enabled kind's verb-matching prerequisites.
    max_depth = int(policy.get("max_depth", 4))
    seen_actions: set[str] = {a["action"] for a in actions}
    for node in topo_kinds(kind, kinds_meta, max_depth):
        block = _autonomy(node, kinds_meta)
        if not block or block.get("enabled") is False:
            continue
        for prereq in block.get("prerequisites", []) or []:
            if not isinstance(prereq, dict):
                continue
            name = prereq.get("action")
            if not name or name in seen_actions:
                continue
            if not _verb_in(prereq, verb, policy):
                continue
            seen_actions.add(name)
            actions.append({
                "action": name,
                "reversible": (not bool(prereq.get("irreversible", False)))
                and _action_reversible(name, policy),
                "satisfied": _satisfied(name, kind, nucleus, policy),
                "reason": "autonomy.prerequisites (%s)" % node,
            })

    base["actions"] = actions

    if float(confidence or 0.0) < float(policy.get("min_confidence", 0.60)):
        base["gated"] = True
        base["reason"] = "deferred to GDP (low-confidence intent)"
        return base

    if not actions:
        base["reason"] = "no prerequisites for this kind/verb"
    else:
        base["reason"] = "%d prerequisite action(s) planned" % len(actions)
    return base


# ---------------------------------------------------------------------------
# R-188: ambient-pip-shadow guard for the 5 lazy `cexai` import sites below
# (mirrors R-007's fix for cex_distill.py's offline_import_smoke gate -- a
# proven bite: this exact dev env has an ambient/stale pip-installed `cexai`
# that can resolve for a bare `import cexai` independently of this repo's OWN
# vendored copy at ROOT/cexai/cexai/). An ImportError from "genuinely absent"
# and "present but shadowed" would otherwise be indistinguishable -- a shadow
# could silently run foreign/stale code under the trusted `cexai` name. The
# check: resolve a bare `import cexai`, then verify its origin lives under
# THIS repo's root (_REPO_ROOT). A regular package exposes `__file__`; some
# editable installs (observed in this exact dev env) surface `cexai` as a
# namespace package instead (`__file__` is None, `__path__` holds the search
# portions) -- both shapes are checked. Anything else (import fails, or
# resolves outside the repo) is treated as ABSENT, reusing the pre-existing
# ImportError degrade path at every call site below. Memoized: cexai's
# resolution cannot change mid-process, so the real check runs once.
# ---------------------------------------------------------------------------
_cexai_vendored_cache: bool | None = None


def _cexai_is_vendored() -> bool:
    """True iff a bare `import cexai` resolves under THIS repo's root (never an
    ambient pip-shadow). Never raises; any failure degrades to False (absent)."""
    global _cexai_vendored_cache
    if _cexai_vendored_cache is not None:
        return _cexai_vendored_cache
    vendored = False
    try:
        import cexai as _cexai_probe
        origins = []
        file_attr = getattr(_cexai_probe, "__file__", None)
        if file_attr:
            origins.append(file_attr)
        origins.extend(getattr(_cexai_probe, "__path__", None) or [])
        for origin in origins:
            try:
                if Path(origin).resolve().is_relative_to(_REPO_ROOT):
                    vendored = True
                    break
            except Exception:
                continue
    except Exception:
        vendored = False
    _cexai_vendored_cache = vendored
    return vendored


def _require_cexai_vendored() -> None:
    """Raise ImportError unless `cexai` is vendored under this repo (R-188).

    A one-line call added at the top of each `cexai`-importing try block below
    -- both "genuinely absent" and "present but ambient-shadowed" then fall
    through that site's EXISTING `except ImportError` (or `except Exception`)
    degrade path unchanged, so no site's reported status/reason text changes
    shape because of this guard.
    """
    if not _cexai_is_vendored():
        raise ImportError(
            "cexai not vendored under repo root (absent or ambient pip-shadow)")


# ---------------------------------------------------------------------------
# Action implementations (lazy cexai; never raise -- degrade + report)
# ---------------------------------------------------------------------------

def _run_external_context(nucleus: str, kind: str, task: str) -> dict[str, Any]:
    """ACTION 0: read-only external context gather (reuse cex_preflight_mcp)."""
    out = {"action": "external_context", "status": ST_DONE, "reason": "",
           "context_md": ""}
    try:
        from cex_preflight_mcp import gather_external_context
    except Exception as exc:  # sibling tool absent -> degrade
        out["status"] = ST_SKIPPED
        out["reason"] = "preflight_mcp unavailable: %s" % exc
        return out
    try:
        res = gather_external_context(nucleus=nucleus, kind=kind, task=task)
    except Exception as exc:
        out["status"] = ST_ERROR
        out["reason"] = "gather failed: %s" % exc
        return out
    if res.get("skipped"):
        out["status"] = ST_SKIPPED
        out["reason"] = res.get("skipped_reason", "skipped")
        return out
    if res.get("has_context"):
        out["context_md"] = res.get("context_md", "")
        out["reason"] = "gathered %d source(s), %d tokens" % (
            res.get("result_count", 0), res.get("tokens_used", 0))
    else:
        out["status"] = ST_SKIPPED
        out["reason"] = "no external context available (offline / no provider key)"
    return out


def _run_spec_kit(
    nucleus: str,
    kind: str,
    verb: str,
    policy: dict[str, Any],
    *,
    dry_run: bool,
) -> dict[str, Any]:
    """spec_kit reflex: emit a reversible spec template, then read-only analyze.

    Reuses the cexai spec-kit Python API directly (offline, no subprocess):
    templates.emit('spec') + analyze_feature_dir(dir). Degrades to a reported skip
    when cexai is absent.
    """
    out = {"action": "spec_kit", "status": ST_DONE, "reason": "",
           "spec_path": "", "verdict": "", "detail": ""}
    spec_cfg = policy.get("actions", {}).get("spec_kit", {})
    spec_dir_tmpl = spec_cfg.get("spec_dir", ".cex/runtime/specs/{nucleus}_{kind}")
    spec_dir = ROOT / spec_dir_tmpl.format(nucleus=nucleus, kind=kind)
    spec_file = spec_dir / "spec.md"
    out["spec_path"] = str(spec_file.relative_to(ROOT)).replace("\\", "/")

    if _satisfied("spec_kit", kind, nucleus, policy):
        out["status"] = ST_SKIPPED
        out["reason"] = "spec already exists (idempotent)"
        return out

    if dry_run:
        out["status"] = ST_WOULD_RUN
        out["reason"] = "would emit spec template + analyze"
        return out

    try:
        _require_cexai_vendored()  # R-188: never trust an ambient pip-shadow
        from cexai.distribution.spec_kit import templates as _sk_templates
        from cexai.distribution.spec_kit.analyze import analyze_feature_dir as _sk_analyze
    except ImportError:
        out["status"] = ST_SKIPPED
        out["reason"] = "cexai spec-kit not installed (non-blocking)"
        return out
    except Exception as exc:
        out["status"] = ST_ERROR
        out["reason"] = "cexai import failed: %s (non-blocking)" % exc
        return out

    try:
        spec_dir.mkdir(parents=True, exist_ok=True)
        spec_file.write_text(_sk_templates.emit("spec"), encoding="utf-8")
    except Exception as exc:
        out["status"] = ST_ERROR
        out["reason"] = "spec emit failed: %s" % exc
        return out

    try:
        report = _sk_analyze(str(spec_dir))
        counts = report.counts()
        out["verdict"] = report.verdict
        out["detail"] = "SEV-1=%d SEV-2=%d SEV-3=%d" % (
            counts.get("sev1", 0), counts.get("sev2", 0), counts.get("sev3", 0))
        out["reason"] = "scaffolded spec.md + analyzed (verdict %s)" % report.verdict
    except Exception as exc:
        out["verdict"] = "UNKNOWN"
        out["reason"] = "spec scaffolded; analyze failed: %s" % exc
    return out


def _name_tokens(name: str) -> set[str]:
    """Lowercased alphanumeric tokens (>= 4 chars) from a kind/feature name.

    Coarse + explainable -- the blueprint match is a SUGGESTION, not an auto-apply,
    so a conservative token overlap (drop short noise tokens like 'api') is enough.
    """
    return {t for t in re.split(r"[^a-z0-9]+", (name or "").lower()) if len(t) >= 4}


def _run_blueprint(
    nucleus: str,
    kind: str,
    policy: dict[str, Any],
    *,
    dry_run: bool,
) -> dict[str, Any]:
    """blueprint reflex (PROPOSE-ONLY): surface REUSE candidates from the cexai stack
    blueprints whose feature pillar/name overlaps this kind.

    A feature matches when the kind's pillar is in feature.pillars OR the feature_name
    shares a (>= 4-char) token with the kind name. Candidates are "<stack>/<feature>"
    refs (deterministic order, capped). This NEVER calls freeze.apply_stack -- apply is
    irreversible and lands behind HITL in P3. Degrades to a reported skip when cexai is
    absent; never raises.
    """
    out = {"action": "blueprint", "status": ST_DONE, "reason": "",
           "candidates": [], "detail": ""}
    # The match is READ-ONLY (it only reads packaged blueprint data), so it runs even
    # in dry_run -- only the status differs (would-run vs done) and NOTHING is written.
    # The proof block (### blueprint) is rendered from candidates in both modes.
    done = ST_WOULD_RUN if dry_run else ST_DONE
    skip = ST_WOULD_RUN if dry_run else ST_SKIPPED
    pillar = (load_kinds_meta().get(kind, {}) or {}).get("pillar") or ""

    try:
        _require_cexai_vendored()  # R-188: never trust an ambient pip-shadow
        from cexai.distribution.blueprints import catalog as _bp_catalog
        from cexai.distribution.blueprints.loader import load_features as _bp_load
    except ImportError:
        out["status"] = skip
        out["reason"] = "cexai blueprints not installed (non-blocking)"
        return out
    except Exception as exc:
        out["status"] = ST_ERROR
        out["reason"] = "cexai import failed: %s (non-blocking)" % exc
        return out

    cap = int(policy.get("actions", {}).get("blueprint", {}).get("max_candidates", 5))
    kind_tokens = _name_tokens(kind)
    candidates: list[str] = []
    try:
        for stack_id in _bp_catalog.STACK_IDS:
            try:
                if not _bp_catalog.get_stack(stack_id).applyable:
                    continue  # reference/protocol stacks are never apply-able
            except Exception:
                continue
            for feature in _bp_load(stack_id):
                pillar_match = bool(pillar) and pillar in (feature.pillars or ())
                name_match = bool(kind_tokens & _name_tokens(feature.feature_name))
                if pillar_match or name_match:
                    ref = "%s/%s" % (stack_id, feature.feature_name)
                    if ref not in candidates:
                        candidates.append(ref)
                if len(candidates) >= cap:
                    break
            if len(candidates) >= cap:
                break
    except Exception as exc:
        out["status"] = ST_ERROR
        out["reason"] = "blueprint match failed: %s (non-blocking)" % exc
        return out

    if not candidates:
        out["status"] = skip
        out["reason"] = "no blueprint feature matches pillar %s" % (pillar or "?")
        return out

    out["candidates"] = candidates
    out["status"] = done
    out["detail"] = "pillar=%s" % (pillar or "?")
    out["reason"] = ("matched %d applyable blueprint feature(s); propose-only "
                     "(apply is irreversible, P3 HITL)" % len(candidates))
    return out


def _run_reposynth(
    nucleus: str,
    kind: str,
    policy: dict[str, Any],
    *,
    dry_run: bool,
) -> dict[str, Any]:
    """reposynth reflex (PROPOSE-ONLY / READ-ONLY in P2): note whether a reverse-
    synthesis path is available for this kind.

    This NEVER calls a synthesize/write entrypoint -- synthesize is irreversible and
    lands behind HITL in P3. Availability is probed with importlib.util.find_spec so the
    heavy synthesizer module is not even imported. Degrades to a reported skip when
    cexai is absent; never raises.
    """
    out = {"action": "reposynth", "status": ST_SKIPPED, "reason": "",
           "available": False}
    if dry_run:
        out["status"] = ST_WOULD_RUN
        out["reason"] = "would surface reposynth availability (read-only; no synthesize)"
        return out
    try:
        import importlib.util
        spec = importlib.util.find_spec("cexai.tools.reposynth.synthesizer")
    except ImportError:
        out["reason"] = "cexai reposynth not installed (non-blocking)"
        return out
    except Exception as exc:
        out["status"] = ST_ERROR
        out["reason"] = "reposynth probe failed: %s (non-blocking)" % exc
        return out
    if spec is None:
        out["reason"] = "cexai reposynth not installed (non-blocking)"
        return out
    out["available"] = True
    out["reason"] = ("propose-only (P2): reposynth synthesize is irreversible, "
                     "deferred to P3 HITL")
    return out


def _run_memory_recall(
    nucleus: str,
    kind: str,
    task: str,
    policy: dict[str, Any],
    *,
    dry_run: bool,
) -> dict[str, Any]:
    """memory_recall reflex (READ-ONLY): recall the top-K related artifacts for the
    handoff's task text and bake them in so the booting nucleus starts with relevant
    context already assembled.

    The pipeline mirrors cex_8f_runner.py F3 (the cexai.memory.recall bridge): the
    TF-IDF retriever builds a candidate pool, then cexai.memory.recall re-ranks it via
    the vector substrate (offline, deterministic FakeEmbedder -- no live embedding
    call). Both layers are LAZY + degrade-never: retriever absent/empty -> ST_SKIPPED;
    cexai.memory absent -> fall back to the raw retriever top-K (still useful). NEVER
    raises -- read-only + reversible, so it does NOT pass through the P3 HITL gate.
    """
    out = {"action": "memory_recall", "status": ST_DONE, "reason": "", "related": []}
    mr_cfg = policy.get("actions", {}).get("memory_recall", {})
    top_k = int(mr_cfg.get("top_k", 5))
    pool = int(mr_cfg.get("candidate_pool", 10))
    # The recall is READ-ONLY (a retriever file-read + an offline FakeEmbedder re-rank --
    # no writes, no network), so it RUNS even in dry_run (mirrors _run_blueprint): only
    # the status differs (would-run vs done) and the handoff is never written in dry_run.
    done = ST_WOULD_RUN if dry_run else ST_DONE
    skip = ST_WOULD_RUN if dry_run else ST_SKIPPED

    # 1. Candidate pool via the TF-IDF retriever (mirror 8f_runner's semantic_candidates
    #    path). Retriever absent / no index / no candidates -> degrade to a skip.
    try:
        from cex_retriever import find_examples_for_kind
        from cex_retriever import load_index as _load_retriever_index
    except Exception as exc:  # sibling tool absent -> degrade
        out["status"] = skip
        out["reason"] = "retriever unavailable: %s (non-blocking)" % exc
        return out
    try:
        idx = _load_retriever_index()
        candidates = find_examples_for_kind(
            kind=kind, intent=task, index=idx, top_k=pool) if idx else []
    except Exception as exc:
        out["status"] = skip
        out["reason"] = "retriever failed: %s (non-blocking)" % exc
        return out
    if not candidates:
        out["status"] = skip
        out["reason"] = "no retriever index / no candidates"
        return out

    def _raw_top_k(reason: str) -> dict[str, Any]:
        out["related"] = [
            {"id": c.get("id") or c.get("title"),
             "path": c.get("path", ""),
             "score": round(float(c.get("score") or 0.0), 4)}
            for c in candidates[:top_k]
        ]
        out["status"] = done
        out["reason"] = "recalled %d related artifact(s) %s" % (
            len(out["related"]), reason)
        return out

    # 2. Re-rank via cexai.memory.recall (offline FakeEmbedder). cexai.memory absent ->
    #    fall back to the raw retriever top-K. Mirrors the cex_8f_runner.py F3 seam.
    intent_text = task or kind
    try:
        _require_cexai_vendored()  # R-188: never trust an ambient pip-shadow
        from cexai.memory import recall as _cexai_recall
        from cexai.memory._shared.types import MemoryRecord as _CexaiRecord
        from cexai.memory.vector import FakeEmbedder as _CexaiFakeEmbedder
    except ImportError:
        return _raw_top_k("via retriever (cexai.memory absent; raw top-K)")
    except Exception as exc:
        return _raw_top_k("via retriever (cexai.memory import failed: %s)" % exc)

    try:
        corpus = [
            _CexaiRecord(
                id=str(c.get("id") or c.get("title") or "cand-%d" % i),
                content=str(c.get("tldr") or c.get("title") or ""),
                kind=str(c.get("kind") or "unknown"),
                source_path=c.get("path"),
                timestamp="",
                metadata={},
            )
            for i, c in enumerate(candidates)
        ]
        reranked = _cexai_recall(
            intent_text, top_k=top_k, records=corpus,
            embedder=_CexaiFakeEmbedder())
    except Exception as exc:  # any recall error -> raw retriever fallback, never raise
        return _raw_top_k("via retriever (cexai.memory.recall failed: %s)" % exc)

    out["related"] = [
        {"id": r.get("id"),
         "path": r.get("source_path") or "",
         "score": round(float(r.get("score") or 0.0), 4)}
        for r in reranked[:top_k]
    ]
    out["status"] = done
    out["reason"] = ("recalled %d related artifact(s) via cexai.memory.recall "
                     "(offline re-rank)" % len(out["related"]))
    return out


# The cexai F7 GOVERN gates surfaced by the f7_capability reflex: (name, module,
# the exact import line the booting nucleus uses). Each gate exposes
# evaluate(frontmatter, body) -> result with .applies / .passed / .reason and is
# pure + offline + never raises (it runs under the nucleus's own F7).
_F7_GATES = (
    ("citation", "cexai.tools.research.citation_gate",
     "from cexai.tools.research.citation_gate import evaluate"),
    ("reasoning_trace", "cexai.distribution.skills.reasoning_gate",
     "from cexai.distribution.skills.reasoning_gate import evaluate"),
)


def _run_f7_capability(
    nucleus: str,
    kind: str,
    policy: dict[str, Any],
    *,
    dry_run: bool,
) -> dict[str, Any]:
    """f7_capability reflex (READ-ONLY): surface the cexai F7 GOVERN gates (citation
    + reasoning_trace) to interactive dispatch -- the debt-c gap.

    These gates fire automatically ONLY inside the headless cex_8f_runner; an
    interactive nucleus booting from a handoff never reaches them. This reflex bakes
    their availability + import paths into the handoff (mirroring how memory_recall
    bakes recalled artifacts in) so the booting nucleus CAN emit a citation /
    reasoning_trace as part of its OWN 8F F7 GOVERN. It does NOT call the gates and
    does NOT modify boot/dispatch control flow -- a handoff-level addition only.

    Availability is probed with importlib.util.find_spec (no heavy import, no gate
    call). The note is baked regardless of availability (the import path is still
    the contract); read-only + reversible -> runs freely, no P3 HITL. Never raises."""
    out = {"action": "f7_capability", "status": ST_DONE, "reason": "",
           "available": False, "gates": []}
    done = ST_WOULD_RUN if dry_run else ST_DONE
    try:
        import importlib.util
    except Exception as exc:  # essentially unreachable; degrade-never
        out["status"] = ST_ERROR
        out["reason"] = "importlib unavailable: %s (non-blocking)" % exc
        return out

    gates: list[dict[str, Any]] = []
    for name, module, import_line in _F7_GATES:
        try:
            # R-188 6th site (acceptance-caught): find_spec also resolves the
            # AMBIENT pip cexai 0.1.0.dev0 -- a cexai-dotted module must only
            # count as available when the vendored (in-repo) package is the
            # one that resolves, same contract as the 5 import sites above.
            if module == "cexai" or module.startswith("cexai."):
                present = _cexai_is_vendored() and \
                    importlib.util.find_spec(module) is not None
            else:
                present = importlib.util.find_spec(module) is not None
        except Exception:
            present = False  # a broken/partial cexai install -> treat as absent
        gates.append({"name": name, "module": module,
                      "import": import_line, "available": present})

    n_present = sum(1 for g in gates if g["available"])
    out["gates"] = gates
    out["available"] = n_present > 0
    out["status"] = done
    if n_present:
        out["reason"] = ("surfaced %d cexai F7 gate(s) to interactive F7 GOVERN "
                         "(emit citation/reasoning_trace)" % n_present)
    else:
        out["reason"] = ("cexai F7 gates not installed; import-path note baked "
                         "(non-blocking)")
    return out


# ---------------------------------------------------------------------------
# P3 governance -- HITL gate for irreversible actions (emit-and-defer, fail-closed)
# + RBAC auto-flag for deploy / live-tool handoffs.
# ---------------------------------------------------------------------------

def _resolve_watch(data: dict[str, Any]) -> str:
    """Resolve one HITL watch-file dict to approved | denied | pending.

    Mirrors cexai.governance.hitl.file_gate._resolve so the router reads a verdict
    WITHOUT calling the blocking await_decision: a persisted terminal status wins; a
    single `deny` vetoes; else `approved` once M DISTINCT approvers approved (M from the
    file's policy, default 1); else `pending`. (In the non-blocking dispatch path the
    file's `status` stays `pending` even after verdicts are recorded -- nobody calls
    await_decision -- so verdicts, not status, are the source of truth.)
    """
    status = data.get("status")
    if status in ("approved", "denied"):
        return status
    verdicts = data.get("verdicts", []) or []
    if any(v.get("verdict") == "deny" for v in verdicts):
        return "denied"
    approvers = {v.get("approver") for v in verdicts if v.get("verdict") == "approve"}
    required = int((data.get("policy", {}) or {}).get("approvers_required", 1) or 1)
    if len(approvers) >= required:
        return "approved"
    return "pending"


def _find_request(approvals_dir: Path, operation: str) -> dict[str, Any] | None:
    """Scan approvals_dir for a watch file whose `operation` matches; return its
    resolved state + request_id, or None when no file matches.

    Precedence across multiple matches is fail-closed: denied > approved > pending
    (a deny anywhere vetoes). Best-effort + never raises (corruption -> ignored)."""
    rank = {"denied": 3, "approved": 2, "pending": 1}
    best: tuple[str, str] | None = None
    try:
        files = sorted(approvals_dir.glob("*.json"))
    except Exception:
        return None
    for fpath in files:
        try:
            data = json.loads(fpath.read_text(encoding="utf-8"))
        except Exception:
            continue
        if data.get("operation") != operation:
            continue
        state = _resolve_watch(data)
        rid = data.get("request_id") or fpath.stem
        if best is None or rank[state] > rank[best[0]]:
            best = (state, rid)
    if best is None:
        return None
    return {"state": best[0], "request_id": best[1]}


def _gate_irreversible(
    mission: str,
    nucleus: str,
    kind: str,
    action_name: str,
    policy: dict[str, Any],
    *,
    dry_run: bool,
) -> dict[str, Any]:
    """HITL gate for one IRREVERSIBLE action (emit-and-defer, NON-BLOCKING, fail-closed).

    Returns a report dict with a `gate` key the caller switches on:
      - gate == "approved" -> a recorded `approve` exists; the caller RUNS the action.
      - gate in {"pending","denied","unavailable","would-request"} -> the caller does
        NOT run the action (it appends this result and continues).

    Deterministic operation = "acr:{mission}:{kind}:{action}" keys the approval. The
    cexai FileApprovalGate is lazy-imported (cexai-absent => fail-closed skip). We NEVER
    call await_decision / await_or_raise here -- those block up to 24h; this only reads
    prior verdicts and (when none) EMITS a pending request, then defers."""
    operation = "acr:%s:%s:%s" % (mission, kind, action_name)
    hitl_cfg = policy.get("hitl", {}) or {}
    approvals_rel = hitl_cfg.get("approvals_dir", ".cexai/approvals")
    requester = hitl_cfg.get("requester", "acr") or "acr"

    # Lazy cexai import FIRST: the approval mechanism IS cexai, so its absence is
    # fail-closed (skip) even if a verdict file somehow existed.
    try:
        _require_cexai_vendored()  # R-188: never trust an ambient pip-shadow
        from cexai.governance.hitl import FileApprovalGate
    except Exception as exc:  # ImportError or anything -> degrade, never raise
        return {
            "action": action_name, "status": ST_SKIPPED, "gate": "unavailable",
            "operation": operation,
            "reason": "HITL gate unavailable; irreversible action NOT auto-run "
                      "(fail-closed): %s" % exc,
        }

    try:
        approvals_dir = ROOT / approvals_rel
        existing = _find_request(approvals_dir, operation)
        if existing is not None and existing["state"] == "approved":
            return {
                "action": action_name, "status": ST_DONE, "gate": "approved",
                "operation": operation, "request_id": existing["request_id"],
                "reason": "HITL approved by human; running irreversible action",
            }
        if existing is not None and existing["state"] == "denied":
            return {
                "action": action_name, "status": ST_SKIPPED, "gate": "denied",
                "operation": operation, "request_id": existing["request_id"],
                "reason": "denied by human; irreversible action NOT run",
            }
        if dry_run:
            return {
                "action": action_name, "status": ST_WOULD_RUN, "gate": "would-request",
                "operation": operation,
                "reason": "irreversible; would emit a HITL approval request (no side effects)",
            }
        if existing is not None and existing["state"] == "pending":
            # A pending request was already emitted for this operation -> reuse it
            # (idempotent; do not pile up duplicate watch files).
            return {
                "action": action_name, "status": ST_GATED_HITL, "gate": "pending",
                "operation": operation, "request_id": existing["request_id"],
                "reason": "irreversible; HITL approval required; NOT auto-run "
                          "(pending request already emitted)",
            }
        gate = FileApprovalGate(approvals_dir=approvals_dir)
        req = gate.request(operation, requester)
        return {
            "action": action_name, "status": ST_GATED_HITL, "gate": "pending",
            "operation": operation, "request_id": req.request_id,
            "reason": "irreversible; HITL approval required; NOT auto-run "
                      "(emitted pending request; emit-and-defer)",
        }
    except Exception as exc:  # any IO / construction error -> fail-closed skip
        return {
            "action": action_name, "status": ST_SKIPPED, "gate": "unavailable",
            "operation": operation,
            "reason": "HITL gate error; irreversible action NOT auto-run "
                      "(fail-closed): %s" % exc,
        }


def _compute_rbac_flag(kind: str, verb: str, policy: dict[str, Any]) -> bool:
    """A baked-in RBAC flag: True when this handoff is a deploy / live-tool action.

    The booting nucleus enforces cexai.governance.rbac under its OWN principal; the
    router only FLAGS (dispatch time is dev mode -- no token, zero overhead)."""
    rbac_cfg = policy.get("rbac", {}) or {}
    flag_verbs = rbac_cfg.get("flag_on_verbs", ["deploy"]) or []
    flag_live = bool(rbac_cfg.get("flag_on_requires_live_tools", True))
    if verb in flag_verbs:
        return True
    if flag_live:
        meta = load_kinds_meta().get(kind, {}) or {}
        if bool(meta.get("requires_live_tools")):
            return True
    return False


# ---------------------------------------------------------------------------
# R-189 -- prerequisite ACTION_TABLE.
#
# Before this table, adding action "foo" meant 4 separately-maintained touch
# points: (1) write _run_foo() (the reflex itself -- unavoidable, real work),
# then hand-sync 3 DUPLICATED ladders that could (and did) drift: (2) an
# `elif name == "foo":` branch in the EXECUTOR (execute_prerequisites' action
# loop), (3) an `if ran.get("action") == "foo" and ...:` branch in the
# RENDERER (_render_block's per-action detail loop), and (4) "foo" spelled out
# in the EXECUTOR's hardcoded unknown-action fallback-error string. After this
# table: write _run_foo(), then add ONE ACTION_TABLE row -- the EXECUTOR, the
# RENDERER, and the fallback-error text all read this same table below.
#
# Each executor wrapper calls its _run_xxx() reflex BY NAME (not via a
# captured function reference) so `monkeypatch.setattr(acr, "_run_spec_kit",
# fake)` (used throughout tests/test_capability_router.py) keeps working
# exactly as before: Python resolves a bare name referenced inside a function
# body against the module's __dict__ at CALL time, so a later monkeypatch of
# the module-level name is honored even though ACTION_TABLE itself (the dict
# literal below) is only ever built once, at import time.
# ---------------------------------------------------------------------------

class _ActionCtx(NamedTuple):
    """Uniform call context: every action's executor wrapper takes exactly this
    one argument, regardless of which subset of (nucleus, kind, verb, task,
    policy, dry_run) its underlying _run_xxx() reflex actually needs."""
    nucleus: str
    kind: str
    verb: str
    task: str
    policy: dict[str, Any]
    dry_run: bool


class _ActionSpec(NamedTuple):
    """One ACTION_TABLE row: the executor callable the EXECUTOR dispatches to,
    and the render callable the RENDERER uses for that action's detail
    section. Both take/return the same shapes the pre-R-189 ladders did."""
    executor: Callable[[_ActionCtx], dict[str, Any]]
    render: Callable[[dict[str, Any]], list[str]]


def _exec_external_context(ctx: _ActionCtx) -> dict[str, Any]:
    return _run_external_context(ctx.nucleus, ctx.kind, ctx.task)


def _exec_spec_kit(ctx: _ActionCtx) -> dict[str, Any]:
    return _run_spec_kit(ctx.nucleus, ctx.kind, ctx.verb, ctx.policy, dry_run=ctx.dry_run)


def _exec_blueprint(ctx: _ActionCtx) -> dict[str, Any]:
    return _run_blueprint(ctx.nucleus, ctx.kind, ctx.policy, dry_run=ctx.dry_run)


def _exec_reposynth(ctx: _ActionCtx) -> dict[str, Any]:
    return _run_reposynth(ctx.nucleus, ctx.kind, ctx.policy, dry_run=ctx.dry_run)


def _exec_memory_recall(ctx: _ActionCtx) -> dict[str, Any]:
    return _run_memory_recall(ctx.nucleus, ctx.kind, ctx.task, ctx.policy, dry_run=ctx.dry_run)


def _exec_f7_capability(ctx: _ActionCtx) -> dict[str, Any]:
    return _run_f7_capability(ctx.nucleus, ctx.kind, ctx.policy, dry_run=ctx.dry_run)


def _render_spec_kit(ran: dict[str, Any]) -> list[str]:
    if not ran.get("spec_path"):
        return []
    out = ["### spec_kit", "- Spec scaffolded: `%s`" % ran["spec_path"]]
    if ran.get("verdict"):
        out.append("- Analyze verdict: %s (%s)" % (
            ran["verdict"], ran.get("detail", "")))
    out.append("")
    return out


def _render_blueprint(ran: dict[str, Any]) -> list[str]:
    if not ran.get("candidates"):
        return []
    out = [
        "### blueprint",
        "Why start from zero? These applyable stack features overlap this "
        "kind. PROPOSE-ONLY: nothing was applied -- `blueprint apply` is "
        "irreversible and stays behind P3 HITL.",
    ]
    stacks: list[str] = []
    for ref in ran["candidates"]:
        out.append("- REUSE candidate: `%s`" % ref)
        stack = ref.split("/", 1)[0]
        if stack not in stacks:
            stacks.append(stack)
    for stack in stacks:
        out.append("- Inspect: `cexai blueprint show %s`" % stack)
    out.append("")
    return out


def _render_reposynth(ran: dict[str, Any]) -> list[str]:
    if not ran.get("available"):
        return []
    return [
        "### reposynth",
        "- A reverse-synthesis path is available for this kind. "
        "PROPOSE-ONLY: `reposynth synthesize` is irreversible and stays "
        "behind P3 HITL.",
        "",
    ]


def _render_memory_recall(ran: dict[str, Any]) -> list[str]:
    if not ran.get("related"):
        return []
    out = [
        "### memory_recall",
        "Related (auto-recalled) -- read these before producing; the router "
        "pre-assembled them via the vector substrate (read-only, offline, "
        "bounded top-K).",
    ]
    for rel in ran["related"]:
        out.append("- `%s` (%s) -- score %s" % (
            rel.get("id", "?"), rel.get("path", "?"), rel.get("score", "?")))
    out.append("")
    return out


def _render_f7_capability(ran: dict[str, Any]) -> list[str]:
    if not ran.get("gates"):
        return []
    out = [
        "### f7_capability",
        "cexai F7 GOVERN gates are reachable from your F7 -- EMIT them as "
        "part of your 8F. They fire automatically only in the headless "
        "runner; in interactive dispatch YOU call them. Each is pure + "
        "offline + never raises: call `evaluate(frontmatter, body)` and "
        "treat `result.applies and not result.passed` as a HARD F7 fail "
        "(record the citation / reasoning_trace in the artifact otherwise).",
    ]
    for g in ran["gates"]:
        state = "available" if g.get("available") else "not installed"
        out.append("- %s (%s): `%s`" % (
            g.get("name", "?"), state, g.get("import", "?")))
    out.append("")
    return out


def _render_external_context(ran: dict[str, Any]) -> list[str]:
    if not ran.get("context_md"):
        return []
    return [ran["context_md"], ""]


# The single source of truth: action_name -> (executor, render). This dict's
# INSERTION ORDER is what the EXECUTOR's unknown-action fallback-error text is
# built from below (matching the pre-R-189 hardcoded string's order exactly);
# Python dicts preserve insertion order since 3.7, so this literal's order IS
# that text's order.
ACTION_TABLE: dict[str, _ActionSpec] = {
    "external_context": _ActionSpec(_exec_external_context, _render_external_context),
    "spec_kit": _ActionSpec(_exec_spec_kit, _render_spec_kit),
    "blueprint": _ActionSpec(_exec_blueprint, _render_blueprint),
    "reposynth": _ActionSpec(_exec_reposynth, _render_reposynth),
    "memory_recall": _ActionSpec(_exec_memory_recall, _render_memory_recall),
    "f7_capability": _ActionSpec(_exec_f7_capability, _render_f7_capability),
}


# ---------------------------------------------------------------------------
# Handoff append (idempotent) + audit
# ---------------------------------------------------------------------------

def _render_block(report: dict[str, Any]) -> str:
    """Render the '## Prerequisites (auto-resolved by ACR)' markdown block."""
    kind = report.get("kind")
    verb = report.get("verb")
    conf = report.get("confidence")
    lines: list[str] = [
        PREREQ_HEADER,
        "<!-- generated by cex_capability_router.py; kind=%s verb=%s confidence=%s -->"
        % (kind, verb, conf),
        "",
    ]

    if report.get("gated"):
        lines += [
            "Intent confidence %s < %s -> deferred to GDP (low-confidence intent)."
            % (conf, report.get("min_confidence", 0.60)),
            "No prerequisites were auto-run; surface a Guided Decision to the user "
            "before building.",
            "",
        ]
        return "\n".join(lines)

    if report.get("ran"):
        lines += [
            "The Autonomous Capability Router resolved the prerequisite capabilities for "
            "this kind and baked them in below. Execute them as part of your 8F pipeline.",
            "",
            "| action | status | reason |",
            "|--------|--------|--------|",
        ]
        for ran in report.get("ran", []):
            lines.append("| %s | %s | %s |" % (
                ran.get("action", "?"), ran.get("status", "?"),
                (ran.get("reason", "") or "").replace("|", "/")))
        lines.append("")
    else:
        lines += [
            "The Autonomous Capability Router found no auto-run prerequisites for this "
            "kind/verb; the governance flags below still apply.",
            "",
        ]

    # Per-action detail sections (ACTION_TABLE-driven; R-189 -- this used to be a
    # 6-way if-chain duplicating the EXECUTOR's action-name switch below).
    for ran in report.get("ran", []):
        spec = ACTION_TABLE.get(ran.get("action"))
        if spec is not None:
            lines += spec.render(ran)

    # P3 governance section -- HITL gate status (per gated action) + RBAC flag.
    gated_actions = [r for r in report.get("ran", []) if r.get("gate")]
    if gated_actions or report.get("rbac_flag"):
        lines.append("### governance")
        for r in gated_actions:
            gate = r.get("gate", "?")
            line = "- HITL: '%s' is IRREVERSIBLE -> %s" % (r.get("action", "?"), gate)
            if r.get("request_id"):
                line += " (request_id %s)" % r["request_id"]
            lines.append(line)
            if gate == "pending" and r.get("request_id"):
                lines.append(
                    "  - approve: record an `approve` verdict in "
                    "`.cexai/approvals/%s.json`, then re-dispatch (the action runs once "
                    "approved; fail-closed until then)." % r["request_id"])
        if report.get("rbac_flag"):
            lines.append(
                "- RBAC: this handoff is deploy/live-tool -> the booting nucleus MUST "
                "run under an authorized principal (cexai.governance.rbac); HITL "
                "approval recommended.")
        lines.append("")

    return "\n".join(lines)


def _append_block(handoff_path: str | Path, block: str) -> bool:
    """Append block to the handoff. Returns False if the header is already present
    (idempotent) or on any write error."""
    path = Path(handoff_path)
    text = _read_text(path)
    if PREREQ_HEADER in text:
        return False
    try:
        sep = "" if text.endswith("\n") else "\n"
        path.write_text(text + sep + "\n" + block + "\n", encoding="utf-8")
        return True
    except Exception as exc:
        _log("append failed: %s" % exc)
        return False


def _write_audit_jsonl(mission_id: str, report: dict[str, Any]) -> None:
    """Append one audit line to .cex/runtime/acr/{mission}.jsonl (cexai-absent
    fallback; also a durable local audit). Best-effort, never raises."""
    try:
        ACR_RUNTIME_DIR.mkdir(parents=True, exist_ok=True)
        line = {
            "ts": datetime.now(timezone.utc).isoformat(),
            "mission": mission_id,
            "kind": report.get("kind"),
            "verb": report.get("verb"),
            "confidence": report.get("confidence"),
            "gated": report.get("gated"),
            "disabled": report.get("disabled"),
            "appended": report.get("appended"),
            "actions": [
                {"action": r.get("action"), "status": r.get("status"),
                 "reason": r.get("reason")}
                for r in report.get("ran", [])
            ],
        }
        path = ACR_RUNTIME_DIR / ("%s.jsonl" % _safe_name(mission_id))
        with path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(line, ensure_ascii=True))
            handle.write("\n")
    except Exception as exc:
        _log("audit jsonl write skipped: %s" % exc)


def _trace_span(mission_id: str, report: dict[str, Any]) -> None:
    """Lazy cexai MissionTracer span for the acr.run (non-blocking observability)."""
    try:
        _require_cexai_vendored()  # R-188: never trust an ambient pip-shadow
        from cexai.governance.tracing.mission_tracer import MissionTracer
    except Exception:
        return  # cexai absent -> jsonl is the audit fallback
    try:
        tracer = MissionTracer(mission_id)
        span = tracer.start_span("acr.run", attrs={
            "kind": str(report.get("kind")),
            "verb": str(report.get("verb")),
            "confidence": float(report.get("confidence") or 0.0),
            "gated": bool(report.get("gated")),
            "disabled": bool(report.get("disabled")),
            "actions": ",".join(r.get("action", "") for r in report.get("ran", [])),
        })
        tracer.emit(tracer.end_span(span))
    except Exception as exc:
        _log("tracer span skipped: %s" % exc)


def _safe_name(value: str) -> str:
    return re.sub(r"[^A-Za-z0-9_.-]", "_", value or "adhoc")


def _mission_for(handoff_path: str | Path, mission_id: str | None) -> str:
    if mission_id:
        return mission_id
    text = _read_text(handoff_path)
    fm = _frontmatter_block(text)
    if fm:
        m = _fm_field(fm, "mission")
        if m:
            return m
    stem = Path(handoff_path).stem
    return stem or "adhoc"


# ---------------------------------------------------------------------------
# Execute
# ---------------------------------------------------------------------------

def execute_prerequisites(
    kind: str | None,
    verb: str,
    confidence: float,
    handoff_path: str | Path,
    *,
    dry_run: bool = False,
    mission_id: None | str = None,
) -> dict[str, Any]:
    """Plan + run prerequisites, append the handoff block, return a report.

    See module docstring. dry_run => plan + would-append, no side effects.
    """
    start = time.monotonic()
    policy = load_policy()
    plan = resolve_prerequisites(kind, verb, confidence, handoff_path)

    report: dict[str, Any] = dict(plan)
    report["dry_run"] = dry_run
    report["min_confidence"] = policy.get("min_confidence", 0.60)
    report["ran"] = []
    report["appended"] = False
    report["idempotent_skip"] = False
    mission = _mission_for(handoff_path, mission_id)
    report["mission"] = mission
    nucleus = plan.get("nucleus", "n07")

    # Kill-switch / no-kind -> complete no-op (do NOT touch the handoff). Computed
    # before rbac_flag so a disabled router is a TRUE no-op (no flag, no append).
    if plan.get("disabled"):
        report["elapsed_ms"] = int((time.monotonic() - start) * 1000)
        _log("disabled: %s" % plan.get("reason"))
        return report

    # P3 RBAC auto-flag: a deploy / live-tool handoff is FLAGGED (baked note only --
    # the booting nucleus enforces under its principal). A non-flagged kind keeps the
    # zero-regression byte-identical guarantee below.
    rbac_flag = _compute_rbac_flag(kind, verb, policy) if kind else False
    report["rbac_flag"] = rbac_flag

    # Idempotency: prerequisites block already present -> skip everything.
    if PREREQ_HEADER in _read_text(handoff_path):
        report["idempotent_skip"] = True
        report["reason"] = "prerequisites block already present (idempotent skip)"
        report["elapsed_ms"] = int((time.monotonic() - start) * 1000)
        return report

    # No prerequisites planned AND no RBAC flag -> complete no-op (byte-identical
    # handoff). This precedes the confidence gate: a defer-to-GDP note is only
    # meaningful when there is actually a prerequisite we are declining to run.
    # An RBAC-flagged handoff with zero actions still appends a governance-only note.
    if not plan.get("actions") and not rbac_flag:
        report["reason"] = "no prerequisites for this kind/verb (no-op)"
        report["elapsed_ms"] = int((time.monotonic() - start) * 1000)
        return report

    # Gated (low confidence, but prerequisites exist) -> run NOTHING, append only
    # the GDP-defer note.
    if plan.get("gated"):
        block = _render_block(report)
        if not dry_run:
            report["appended"] = _append_block(handoff_path, block)
            _write_audit_jsonl(mission, report)
            _trace_span(mission, report)
        report["elapsed_ms"] = int((time.monotonic() - start) * 1000)
        return report

    # Best-effort grid double-exec lock (idempotency header + satisfied glob are the
    # real guards; the lock just records contention).
    lock_path = ACR_RUNTIME_DIR / ("%s.lock" % _safe_name(mission))
    if not dry_run:
        try:
            ACR_RUNTIME_DIR.mkdir(parents=True, exist_ok=True)
            report["lock_contended"] = lock_path.exists()
            lock_path.write_text(
                "%s %s %s\n" % (datetime.now(timezone.utc).isoformat(), nucleus, kind),
                encoding="utf-8")
        except Exception:
            report["lock_contended"] = False

    task = _title_and_head(_read_text(handoff_path))
    # ACTION_TABLE-driven dispatch (R-189): ctx bundles the args every _run_xxx()
    # reflex might need; each executor wrapper picks the subset it actually uses.
    ctx = _ActionCtx(nucleus=nucleus, kind=kind, verb=verb, task=task,
                     policy=policy, dry_run=dry_run)

    try:
        for planned in plan.get("actions", []):
            name = planned.get("action")
            if planned.get("satisfied"):
                report["ran"].append({
                    "action": name, "status": ST_SKIPPED,
                    "reason": "already satisfied (idempotent)"})
                continue
            # P3 graduated-HITL: a reversible action runs freely (falls through). An
            # irreversible action is GATED first -- only a recorded `approve` lets it
            # run; pending / denied / unavailable => NOT run (append the gate result).
            if planned.get("reversible") is False:
                gate_res = _gate_irreversible(
                    mission, nucleus, kind, name, policy, dry_run=dry_run)
                if gate_res.get("gate") != "approved":
                    report["ran"].append(gate_res)
                    continue
                # approved -> fall through to the existing action impl below.
            spec = ACTION_TABLE.get(name)
            if spec is not None:
                report["ran"].append(spec.executor(ctx))
            else:
                report["ran"].append({
                    "action": name, "status": ST_SKIPPED,
                    "reason": "no implementation for action (supports %s)"
                              % ", ".join(ACTION_TABLE)})
    finally:
        if not dry_run:
            try:
                lock_path.unlink(missing_ok=True)
            except Exception:
                pass

    block = _render_block(report)
    if dry_run:
        report["would_append"] = block
    else:
        report["appended"] = _append_block(handoff_path, block)
        _write_audit_jsonl(mission, report)
        _trace_span(mission, report)

    report["elapsed_ms"] = int((time.monotonic() - start) * 1000)
    return report


# ---------------------------------------------------------------------------
# Preflight (CLI helper) -- resolve kind from handoff, then execute
# ---------------------------------------------------------------------------

def preflight(
    nucleus: str,
    handoff_path: str | Path,
    *,
    dry_run: bool = False,
) -> dict[str, Any]:
    """Dispatch-time entry: resolve the kind from the handoff, then execute.

    Returns the execute report (or a skip report when no handoff / no kind).
    """
    path = Path(handoff_path)
    if not path.is_file():
        return {"skipped": True, "reason": "handoff not found: %s" % handoff_path,
                "appended": False}

    resolved = resolve_kind_from_handoff(path)
    kind = resolved.get("kind")
    verb = resolved.get("verb", "create")
    confidence = float(resolved.get("confidence") or 0.0)

    if not kind:
        return {"skipped": True, "reason": "no kind resolved from handoff",
                "kind": None, "appended": False, "method": resolved.get("method")}

    # The CLI-provided nucleus wins (it knows the dispatch target); fall back to the
    # nucleus resolved from the handoff / kind.
    nuc = (nucleus or resolved.get("nucleus") or "n07").lower()
    report = execute_prerequisites(
        kind, verb, confidence, path, dry_run=dry_run,
        mission_id=None)
    report["nucleus"] = nuc
    report["resolve_method"] = resolved.get("method")
    return report


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def _print_human(report: dict[str, Any]) -> None:
    if report.get("skipped"):
        print("[acr] skipped: %s" % report.get("reason", ""))
        return
    if report.get("disabled"):
        print("[acr] no-op (disabled): %s" % report.get("reason", ""))
        return
    if report.get("idempotent_skip"):
        print("[acr] idempotent skip: prerequisites already present")
        return
    tag = "DRY-RUN" if report.get("dry_run") else "RUN"
    print("[acr] %s kind=%s verb=%s confidence=%s gated=%s appended=%s" % (
        tag, report.get("kind"), report.get("verb"), report.get("confidence"),
        report.get("gated"), report.get("appended")))
    for ran in report.get("ran", []):
        print("  - %-18s %-10s %s" % (
            ran.get("action", "?"), ran.get("status", "?"), ran.get("reason", "")))
    if report.get("dry_run") and report.get("would_append"):
        print("  (would append %d-char prerequisites block)" % len(report["would_append"]))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="CEX Autonomous Capability Router -- resolve prerequisites into a handoff")
    parser.add_argument("--preflight", action="store_true",
                        help="Resolve the handoff kind and bake prerequisites in")
    parser.add_argument("--nucleus", default="n07", help="Dispatch target nucleus id")
    parser.add_argument("--handoff", help="Path to the handoff file")
    parser.add_argument("--dry-run", action="store_true",
                        help="Plan + would-append only; no side effects")
    parser.add_argument("--json", action="store_true", help="Emit the report as JSON")
    args = parser.parse_args(argv)

    if not args.preflight:
        parser.print_help()
        return 2
    if not args.handoff:
        print("[acr] --handoff is required for --preflight", file=sys.stderr)
        return 2

    report = preflight(args.nucleus, args.handoff, dry_run=args.dry_run)

    if args.json:
        # context_md / would_append can be large; keep them out of the compact JSON.
        compact = {k: v for k, v in report.items() if k != "would_append"}
        if compact.get("ran"):
            compact["ran"] = [{k: v for k, v in r.items() if k != "context_md"}
                              for r in compact["ran"]]
        print(json.dumps(compact, ensure_ascii=True, indent=2))
    else:
        _print_human(report)

    # Exit 0 always for a clean plan/run/skip (never break dispatch); 0 even when
    # gated (the GDP defer is a successful, expected outcome).
    return 0


if __name__ == "__main__":
    try:
        from cex_agent_io import wrap_main

        def _main_wrapper(argv: list[str]) -> int:
            return main(argv)

        sys.exit(wrap_main(_main_wrapper, sys.argv[1:], label="cex_capability_router"))
    except ImportError:
        sys.exit(main())
