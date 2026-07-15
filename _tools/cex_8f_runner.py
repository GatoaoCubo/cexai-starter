#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
cex_8f_runner.py -- 8F Runner: Stateful artifact production pipeline.

Each function (F1-F8) produces state that the next CONSUMES.
Wave 1: F1 CONSTRAIN, F2 BECOME, F3 INJECT, F6 PRODUCE, F8 COLLABORATE.
Wave 2: + F4 REASON (LLM planning), F7 GOVERN (6 hard gates + retry loop).
Wave 3 adds: F5 CALL, multi-kind, proofs.

Usage:
  python cex_8f_runner.py "create a chunking config for markdown"
  python cex_8f_runner.py "create agent for sales" --execute
  python cex_8f_runner.py --kind chunk_strategy --dry-run
  python cex_8f_runner.py --list-kinds
  python cex_8f_runner.py "create eval" --step 3 --verbose
"""

import os
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

import argparse
import json
import re
import subprocess
import time
from dataclasses import dataclass, field
from pathlib import Path

import yaml

try:
    import importlib.util
    if importlib.util.find_spec("yaml") is None:
        raise ImportError
except ImportError:
    print("ERROR: PyYAML required. pip install pyyaml", file=sys.stderr)
    sys.exit(1)

try:
    _CEXAGENT_AVAILABLE = True
except ImportError:
    _CEXAGENT_AVAILABLE = False

# --- Imports from Motor + Intent ---

sys.path.insert(0, str(Path(__file__).resolve().parent))
from cex_8f_motor import (CEX_ROOT, OBJECT_TO_KINDS, classify_objects, fan_out,
                          generate_output, load_builder_map, load_kc_library,
                          lookup_kcs_for_kind, parse_intent)
from cex_intent import execute_prompt
from cex_shared import \
    extract_frontmatter_dict as _shared_extract_frontmatter_dict
from cex_shared import find_builder_dir as _shared_find_builder_dir
from cex_shared import load_iso as _shared_load_iso
from cex_shared import load_yaml
from cex_shared import strip_frontmatter as _shared_strip_frontmatter
from cex_shared import write_learning_record as _shared_write_learning_record

# --- Optional tools (degrade gracefully) ---
try:
    from cex_retriever import find_examples_for_kind
    from cex_retriever import find_similar as _find_similar
    from cex_retriever import load_index as load_retriever_index
    _RETRIEVER_AVAILABLE = True
except ImportError:
    _RETRIEVER_AVAILABLE = False

# Gitignore-aware safe commit (F8 COLLABORATE): partitions artifact paths into
# committable vs gitignored, NEVER force-adds, and reports `committed` honestly
# (no "nothing to commit" false-success). Single shared fix for the naive
# `git add <artifact> && git commit` pattern. See cex_git_safe.py.
try:
    from cex_git_safe import safe_artifact_commit as _safe_artifact_commit
    _GIT_SAFE_AVAILABLE = True
except ImportError:
    _GIT_SAFE_AVAILABLE = False

# Reuse gate (LEVERAGE_A4): advisory pre-build near-duplicate check. Flag-gated
# (CEX_REUSE_GATE) at the F3 call site; fail-open. Default OFF = byte-identical.
try:
    from cex_reuse_gate import check_reuse as _reuse_check
    from cex_reuse_gate import is_enabled as _reuse_enabled
    _REUSE_GATE_AVAILABLE = True
except ImportError:
    _REUSE_GATE_AVAILABLE = False

# Repo-map digest (R-304, R-292): OPTIONAL F3 seam over cex_repo_map.py's
# clean-room ast+pagerank ranked-symbol digest. Flag-gated (CEX_F3_REPO_MAP
# env var, or explicit with_repo_map= on EightFRunner) exactly like the reuse
# gate above; fail-open, default OFF = byte-identical to pre-R-304 runs. See
# repo_map_seam_enabled() below (defined after the id_pattern helpers).
try:
    import cex_repo_map as _repo_map_mod
    _REPO_MAP_AVAILABLE = True
except ImportError:
    _REPO_MAP_AVAILABLE = False

try:
    from cex_token_budget import TokenBudget as _TokenBudget
    from cex_token_budget import count_tokens
    _TOKEN_BUDGET_AVAILABLE = True
except ImportError:
    _TOKEN_BUDGET_AVAILABLE = False

try:
    from cex_gdp import GDPEnforcer as _GDPEnforcer
    from cex_gdp import NeedsUserDecision as _NeedsUserDecision
    _GDP_AVAILABLE = True
except ImportError:
    _GDP_AVAILABLE = False

try:
    from cex_memory import get_injection_context as _memory_inject
    _MEMORY_AVAILABLE = True
except ImportError:
    _MEMORY_AVAILABLE = False

try:
    from cex_output_formatter import validate_frontmatter as _validate_fm
    _FORMATTER_AVAILABLE = True
except ImportError:
    _FORMATTER_AVAILABLE = False

try:
    from cex_prompt_optimizer import \
        suggest_improvements as _suggest_improvements
    _OPTIMIZER_AVAILABLE = True
except ImportError:
    _OPTIMIZER_AVAILABLE = False

try:
    from cex_quality_monitor import save_snapshot as _save_snapshot
    _MONITOR_AVAILABLE = True
except ImportError:
    _MONITOR_AVAILABLE = False

try:
    from cex_query import query_builders as _query_builders
    _QUERY_AVAILABLE = True
except ImportError:
    _QUERY_AVAILABLE = False

try:
    from cex_provider_discovery import \
        discover_providers as _discover_providers
    _PROVIDER_AVAILABLE = True
except ImportError:
    _PROVIDER_AVAILABLE = False

try:
    from cex_theme import get_sin as _get_sin
    _THEME_AVAILABLE = True
except ImportError:
    _THEME_AVAILABLE = False

try:
    from cex_prompt_layers import get_layers as _get_prompt_layers
    _LAYERS_AVAILABLE = True
except ImportError:
    _LAYERS_AVAILABLE = False

try:
    from cex_skill_loader import get_skill_loader as _get_skill_loader
    _SKILL_LOADER_AVAILABLE = True
except ImportError:
    _SKILL_LOADER_AVAILABLE = False

try:
    from brand_inject import flatten as _flatten_brand
    from brand_inject import load_brand_config as _load_brand_config
    _BRAND_INJECT_AVAILABLE = True
except ImportError:
    _BRAND_INJECT_AVAILABLE = False

try:
    from cex_secretariat import classify_intent as _secretariat_classify
    _SECRETARIAT_AVAILABLE = True
except ImportError:
    _SECRETARIAT_AVAILABLE = False

try:
    from cex_8f_enforcer import mark_stage as _enforcer_mark
    _ENFORCER_AVAILABLE = True
except ImportError:
    _ENFORCER_AVAILABLE = False

try:
    from signal_writer import write_signal as _write_signal
    _SIGNAL_AVAILABLE = True
except ImportError:
    _SIGNAL_AVAILABLE = False

# F8 incremental-index tail (R-248 consumer half): keep the total index
# current after every successful save. Absent module is the ORDINARY
# degrade-never state (a checkout that has never run cex_total_index.py
# --build), not an error -- mirrors every other optional-tool block above.
try:
    from cex_total_index import INDEX_META_PATH as _TOTAL_INDEX_META_PATH
    from cex_total_index import update_single_file as _total_index_update_file
    _TOTAL_INDEX_AVAILABLE = True
except ImportError:
    _TOTAL_INDEX_AVAILABLE = False

# GDP Q4 (closed, docs/SPEC_CEXAI_TOTAL_HYDRATION_INDEX_2026_07_03.md Sec 5
# item 4): F8's incremental-index tail ships WARN-and-skip-on-slow -- a
# non-blocking soft budget, never a hard gate. Module-level constant (not a
# class attribute) so tests can monkeypatch it directly for a deterministic
# slow-path repro without a real sleep().
_TOTAL_INDEX_SOFT_BUDGET_SECONDS = 2.0

# Load .env for API keys
for _ep in [CEX_ROOT / ".env", CEX_ROOT.parent / "organization-core" / ".env"]:
    if _ep.exists():
        for _line in _ep.read_text().splitlines():
            if "=" in _line and not _line.startswith("#"):
                _k, _v = _line.split("=", 1)
                if _k.strip() not in os.environ:
                    os.environ[_k.strip()] = _v.strip()
        break

# --- Constants ---

BUILDER_DIR = CEX_ROOT / "archetypes" / "builders"

# Pillar directory names keyed by code (e.g. "P01" -> "P01_knowledge")
# Root P01-P12 dirs are now under N00_genesis/
PILLAR_DIRS = {}
_n00 = CEX_ROOT / "N00_genesis"
for d in sorted(_n00.glob("P[0-9][0-9]_*")):
    if d.is_dir():
        code = d.name[:3]  # e.g. "P01"
        PILLAR_DIRS[code] = "N00_genesis/" + d.name

# Builder spec prefix -> function mapping
ISO_TO_FUNCTION = {
    "bld_schema": "F1",
    "bld_config": "F1",
    "bld_model": "F2",
    "bld_knowledge": "F3",
    "bld_eval": "F3",
    "bld_memory": "F3",
    "bld_architecture": "F3",
    "bld_prompt": "F6",
    "bld_output": "F6",
    "bld_feedback": "F7",
    "bld_tools": "F5",
    "bld_orchestration": "F8",
}

ALL_ISO_PREFIXES = list(ISO_TO_FUNCTION.keys())

# Function labels for verbose output
F_LABELS = {
    "F1": "CONSTRAIN",
    "F2": "BECOME",
    "F3": "INJECT",
    "F4": "REASON",
    "F5": "CALL",
    "F6": "PRODUCE",
    "F7": "GOVERN",
    "F8": "COLLABORATE",
}

# --- RunState ---

@dataclass
class RunState:
    """Accumulated state across 8 functions."""

    intent: str = ""
    context: str = ""
    kind: str = ""
    pillar: str = ""
    builder_dir: Path | None = None

    # F1 CONSTRAIN
    constraints: dict = field(default_factory=dict)
    # F2 BECOME
    identity: dict = field(default_factory=dict)
    # F3 INJECT
    knowledge: dict = field(default_factory=dict)
    # F4 REASON (wave 2)
    reasoning: dict = field(default_factory=dict)
    # F5 CALL (wave 3)
    tool_results: dict = field(default_factory=dict)
    # F6 PRODUCE
    artifact: str = ""
    # F7 GOVERN (wave 2)
    verdict: dict = field(default_factory=dict)
    # F8 COLLABORATE
    result: dict = field(default_factory=dict)

    # Meta
    timings: dict = field(default_factory=dict)
    errors: list = field(default_factory=list)


# --- Helpers ---


# Delegates to cex_shared (single source of truth)
find_builder_dir = _shared_find_builder_dir
load_iso = _shared_load_iso
strip_frontmatter = _shared_strip_frontmatter
extract_frontmatter_dict = _shared_extract_frontmatter_dict


# R-127 deferred-lookup: process-lifetime cache for load_pillar_schema, keyed
# by pillar code. See the function's own docstring for the safety argument.
_PILLAR_SCHEMA_CACHE: dict[str, dict] = {}


def load_pillar_schema(pillar: str) -> dict:
    """Load _schema.yaml for a pillar.

    R-127 deferred-lookup (docs/IMPROVEMENT_REGISTER.md): memoized at module
    level for the life of the process. Pure function of `pillar` over an
    immutable repo file within a short-lived one-shot CLI invocation -- a
    cached read cannot return a stale value within a run. This pays off when
    main()'s multi-kind loop (kinds_to_run) resolves >1 kind that share a
    pillar: previously each EightFRunner instance re-read + re-parsed that
    pillar's _schema.yaml from scratch; now the whole process parses it once.

    NOTE: the returned dict (and any nested list it contains, e.g. a kind's
    frontmatter_required) is the SHARED cache entry -- callers must treat it
    as read-only. Audited 2026-07-11 (grep across this file): every caller
    only reads it (dict(...) copy, .get(), len(), join()) -- nothing mutates
    it in place.
    """
    if pillar in _PILLAR_SCHEMA_CACHE:
        return _PILLAR_SCHEMA_CACHE[pillar]
    dir_name = PILLAR_DIRS.get(pillar)
    result: dict = {}
    if dir_name:
        schema_path = CEX_ROOT / dir_name / "_schema.yaml"
        if schema_path.exists():
            try:
                result = load_yaml(schema_path)
            except Exception:
                result = {}
    _PILLAR_SCHEMA_CACHE[pillar] = result
    return result


def load_kind_schema(kind: str, pillar: str) -> dict:
    """Extract kind-specific constraints from pillar _schema.yaml."""
    return load_pillar_schema(pillar).get("kinds", {}).get(kind, {})


# --- R-264 CLASS GUARD: structurally-scoped id_pattern extraction -----------
#
# AF-1 postmortem (R-263 manifest, folded into R-264): the original H02
# extraction ran `re.search(r"Regex:\s*`([^`]+)`", body)` over the ENTIRE
# bld_schema ISO body, top-down, first-match-wins. Any later prose containing
# that literal shape -- a status note, a worked example, a changelog line --
# silently REBINDS the gate to a decoy (proven: our own 2026-07-04 status note
# broke prompt_template's H02 for ~3h until defused). The fix below scopes the
# search STRUCTURALLY to the '## ID Pattern' section only (heading -> next
# '## ' heading), so no prose anywhere else in the file can ever shadow the
# documented pattern again -- while degrading NEVER (a bld_schema with no
# '## ID Pattern' heading at all falls back to the original whole-body
# search, so nonstandard/legacy layouts are not silently broken).
_ID_PATTERN_HEADING_RE = re.compile(r"(?im)^##\s*id\s*pattern\s*$")
_NEXT_H2_HEADING_RE = re.compile(r"(?m)^##(?!#)")
_ID_PATTERN_REGEX_LINE_RE = re.compile(r"Regex:\s*`([^`]+)`")


def extract_id_pattern_section(body: str) -> str | None:
    """Isolate the '## ID Pattern' section of a bld_schema ISO body.

    Returns the section text starting just after the heading line, up to
    (but not including) the next '## ' (H2) heading -- or the rest of the
    body if the ID Pattern section is the last one. Returns None if the
    body has no '## ID Pattern' heading at all.
    """
    m = _ID_PATTERN_HEADING_RE.search(body)
    if not m:
        return None
    rest = body[m.end():]
    m2 = _NEXT_H2_HEADING_RE.search(rest)
    return rest[:m2.start()] if m2 else rest


def extract_id_pattern(body: str) -> str | None:
    """Extract a kind's H02 id_pattern regex from its bld_schema ISO body.

    Structurally scoped to the '## ID Pattern' section (see
    extract_id_pattern_section). Degrade-never: if the body has no such
    heading, falls back to the pre-R-264 whole-body search so kinds with a
    nonstandard/legacy bld_schema layout keep their existing behavior.
    """
    section = extract_id_pattern_section(body)
    haystack = section if section is not None else body
    m = _ID_PATTERN_REGEX_LINE_RE.search(haystack)
    return m.group(1) if m else None


# --- R-304: F3 repo-map digest seam (optional, additive, default OFF) ------
#
# Mirrors cex_reuse_gate.py's own flag contract exactly (FLAG_ENV + _TRUTHY +
# an is_enabled()-shaped resolver): env-var truthy check, OFF = byte-identical
# to pre-R-304 behavior. The one addition over that precedent is an explicit
# constructor override (EightFRunner(with_repo_map=True/False)) so tests and
# programmatic callers do not have to mutate process environment -- explicit
# argument wins, then env, then the OFF default (same precedence order as
# cex_reuse_gate.resolve_threshold's "explicit > env > default").
REPO_MAP_SEAM_ENV = "CEX_F3_REPO_MAP"
_REPO_MAP_SEAM_TRUTHY = frozenset({"1", "true", "yes", "on", "enabled"})

# Kept deliberately small: this is advisory context for an LLM prompt, not a
# full corpus dump. cex_repo_map.py's own scan over its documented default
# scopes (_tools/, cex_sdk/) takes several seconds (measured 2026-07-11:
# ~7s for ~900 files / ~19k symbols) -- acceptable for an explicit opt-in,
# never acceptable as a silent default, which is exactly why this seam stays
# OFF unless asked for.
_REPO_MAP_SEAM_TOP = 15
_REPO_MAP_SEAM_BUDGET_TOKENS = 800

# Process-lifetime cache for the seam's own report -- companion to R-127's
# "cache within a run": main()'s multi-kind loop (kinds_to_run) can construct
# several EightFRunner instances in one process; without this, each one that
# opts into the seam would re-pay the multi-second corpus scan independently.
# None = not yet computed this process; degrade-never on any lookup failure
# (see the try/except at the F3 call site) -- a failed scan is logged and
# skipped, never raised, and is NOT cached (retried on the next call).
_repo_map_report_cache: dict | None = None


def repo_map_seam_enabled(explicit: bool | None = None) -> bool:
    """True iff the F3 repo-map digest seam (R-304) is enabled.

    Precedence: explicit constructor arg (if not None) > env CEX_F3_REPO_MAP
    (truthy) > OFF. Default OFF -> F3 INJECT is byte-identical to pre-R-304
    runs (no import touched, no key added to state.knowledge).
    """
    if explicit is not None:
        return explicit
    return os.environ.get(REPO_MAP_SEAM_ENV, "").strip().lower() in _REPO_MAP_SEAM_TRUTHY


# --- R-336/DP2c: max_bytes -> max_tokens for execute_prompt calls ----------
#
# execute_prompt() gained a max_tokens parameter (GLM_BENCH_0712_EXEC DP2c) so
# the GLM/openwebui branch can be given a real cap instead of guessing --
# below the documented reasoning-budget floor a glm-5.2-family model spends
# its ENTIRE budget on reasoning and returns EMPTY content (p07_bm_glm_
# openwebui.md "Reasoning-budget gotcha", reproduced live twice). The
# artifact's own max_bytes constraint (already computed at F1 CONSTRAIN, see
# state.constraints) is the natural source: divide by cex_intent.py's
# documented _CHARS_PER_TOKEN=4 approximation, clamp to a safe range. This is
# a no-op for the ollama/claude branches (they do not read max_tokens at all
# -- byte-identical behavior, R-336 test 4d).
_MAX_TOKENS_FLOOR = 300     # GLM reasoning-budget floor (see comment above)
_MAX_TOKENS_CEILING = 8000  # matches cex_intent.py's existing hardcoded SDK caps


def _max_tokens_from_bytes(max_bytes) -> int:
    """Best-effort output-token cap derived from an artifact's max_bytes
    constraint. Returns 0 (unspecified -- execute_prompt's own per-branch
    default applies) when max_bytes is unknown/invalid."""
    if not max_bytes:
        return 0
    try:
        tokens = int(max_bytes) // 4
    except (TypeError, ValueError):
        return 0
    return max(_MAX_TOKENS_FLOOR, min(_MAX_TOKENS_CEILING, tokens))


# --- R-342: W5 escalation ladder for Mode B Stage 2 F7 floor-miss ----------
#
# Precedent to FOLLOW (pattern, not import): cex_mentor_swarm.py's
# ESCALATION_LADDER (haiku -> sonnet -> opus, opus terminal) and
# .claude/rules/model-economy.md (same climb direction: cheap -> Sonnet ->
# Opus, Opus terminal). This is a SEPARATE, self-contained ladder -- not an
# import of the swarm's module -- because Mode B Stage 2 can START on ANY
# model (an explicit --model / CEX_DECOMPOSE_STAGE2_MODEL override, or a GLM
# box model), not always the cheapest tier, so the swarm's provider-keyed
# "where does this producer sit on ITS OWN ladder" indexing does not apply.
#
# Rung ids resolve through cex_model_resolver.resolve_shorthand (the repo's
# single source of truth for model aliases -- reads .cex/config/
# nucleus_models.yaml::model_aliases) when importable; the literals below are
# the documented W5 fallback for a checkout where that import fails, so the
# ladder never silently stalls just because the resolver is unavailable.
_LADDER_FALLBACK_MODELS = {
    "sonnet": "claude-sonnet-4-6",
    "opus": "claude-opus-4-8",
}


def _resolve_ladder_rung(shorthand: str) -> str:
    """Resolve a W5 ladder rung shorthand ('sonnet'/'opus') to a model id.

    Degrade-never: any import/resolution error falls back to the documented
    W5 literal in _LADDER_FALLBACK_MODELS (never raises, never returns a
    falsy value for a known shorthand).
    """
    try:
        from cex_model_resolver import resolve_shorthand
        resolved = resolve_shorthand(shorthand)
        if resolved:
            return resolved
    except Exception:
        pass
    return _LADDER_FALLBACK_MODELS[shorthand]


# --- EightFRunner ---


class EightFRunner:
    """Stateful 8-function pipeline for artifact production."""

    def __init__(
        self,
        intent: str,
        kind: str | None = None,
        dry_run: bool = False,
        verbose: bool = False,
        output_dir: Path | None = None,
        context: str = "",
        model: str = "",
        update_path: str = "",
        force_rewrite: bool = False,
        mode: str = "auto",
        prompt_package_path: str = "",
        with_repo_map: bool | None = None,
    ):
        self.dry_run = dry_run
        self.verbose = verbose
        self.output_dir = output_dir
        self.model = model  # e.g. "ollama/qwen3:8b" or "claude-sonnet-4-6"
        self.update_path = update_path  # --update: path to existing artifact
        self.force_rewrite = force_rewrite  # --force: allow >60% rewrite
        self.prompt_package_path = prompt_package_path
        # R-342: set by _run_mode_b_generate every time it runs (both the
        # explicit --prompt-package Stage-2-only dispatch AND the auto-
        # continue Stage1->Stage2 path) -- lets F7's ladder escalation
        # re-invoke Stage 2 F6 against the SAME package on a stronger model
        # after a floor-miss. Stays None for Mode A (never set) -- the
        # ladder in f7_govern is gated on this being non-None, so Mode A
        # behavior is untouched.
        self._mode_b_pkg_path: Path | None = None
        # R-342: lazily built once per run by _mode_b_ladder_rungs() --
        # [starting_model, sonnet, opus] with duplicates collapsed. Index 0
        # is always the STARTING rung (the override, never a ceiling).
        self._ladder_rungs: list[str] | None = None
        self._ladder_idx = 0
        # R-304: explicit arg > env CEX_F3_REPO_MAP > OFF. See
        # repo_map_seam_enabled() for the full precedence contract.
        self.with_repo_map = repo_map_seam_enabled(with_repo_map)
        self.state = RunState(intent=intent, context=context)

        # Resolve mode: auto detects from model tier via cex_router_v2
        if mode == "auto" and model:
            try:
                from cex_router_v2 import UnsupportedTierError, get_mode
            except ImportError:
                self.mode = "A"
            else:
                try:
                    self.mode = get_mode(model)
                except UnsupportedTierError:
                    # R-011: model's tier is explicitly BLOCKED (mode: null
                    # in nucleus_models.yaml) -- fail closed, do NOT swallow
                    # into a silent Mode A fallback. Re-raise so dispatch
                    # refuses here instead of running a full 8F pipeline
                    # against a known-unsupported model.
                    raise
                except Exception:
                    self.mode = "A"
        else:
            self.mode = mode if mode in ("A", "B") else "A"

        nuc = os.environ.get("CEX_NUCLEUS", "n07")
        self.session_id = "%s_%s_%d" % (nuc, (kind or "auto"), int(time.time()))

        # Motor parse + classify
        self.parsed = parse_intent(intent)
        if kind:
            self.classified = classify_objects([kind])
        else:
            self.classified = classify_objects(self.parsed["objects"])

        # Set primary kind
        if self.classified:
            c = self.classified[0]
            self.state.kind = c["kind"]
            self.state.pillar = c["pillar"]
        else:
            self.state.kind = "generic"
            self.state.pillar = "P01"

        # Locate builder
        self.state.builder_dir = find_builder_dir(self.state.kind)
        self.kind_slug = self.state.kind.replace("-", "_")

        # Motor plan (for F3 KC injection)
        builder_map = load_builder_map()
        self.kc_library = load_kc_library()
        functions = fan_out(
            classified=self.classified,
            intent_lower=intent.lower(),
            quality=self.parsed["quality"],
            builder_map=builder_map,
            verb_action=self.parsed["verb_action"],
            kc_library=self.kc_library,
        )
        self.plan = generate_output(intent, self.parsed, self.classified, functions)

    def _log(self, fn: str, msg: str):
        if self.verbose:
            print(f"  [{fn}] {msg}", file=sys.stderr)

    def _state_summary(self, fn: str) -> str:
        """One-line summary of state after function fn completes."""
        s = self.state
        c, k, v = s.constraints, s.knowledge, s.verdict
        summaries: dict[str, str] = {
            "F1": lambda: "constraints: {" + ", ".join(filter(None, [
                f"max_bytes: {c['max_bytes']}" if c.get("max_bytes") else "",
                f"fields: {len(c.get('frontmatter_required', []))}",
                f"id_pattern: /{c['id_pattern']}/" if c.get("id_pattern") else "",
            ])) + "}",
            "F2": lambda: f"identity: {len(s.identity)} keys ({', '.join(list(s.identity)[:3])})",
            "F3": lambda: f"ISOs: {sum(1 for x in k.values() if x)}, KCs injected: {len(k.get('kc_domains', []))}",
            "F4": lambda: f"plan: {len(s.reasoning.get('plan', '').split())} words (model={s.reasoning.get('model_used', '?')})",
            "F5": lambda: f"tools: {len(s.tool_results.get('tools_available', []))}, existing: {len(s.tool_results.get('existing_artifacts', []))}, executed: {len(s.tool_results.get('tool_outputs', {}))}",
            "F6": lambda: f"artifact: {len(s.artifact.split()) if s.artifact else 0} words",
            "F7": lambda: (f"gates: {sum(1 for g in v.get('hard_gates', []) if g.get('passed'))}/{len(v.get('hard_gates', []))}, retries: {v.get('retries', 0)}" if v else "pending"),
            "F8": lambda: f"mode: {s.result.get('mode', '?')}, path: {s.result.get('path', 'none')}",
        }
        return summaries.get(fn, lambda: "")()

    def _timed(self, fn_name: str, func):
        """Run a function and record its timing."""
        t0 = time.perf_counter()
        ok = True
        try:
            func()
        except Exception as e:
            ok = False
            self.state.errors.append(f"{fn_name}: {e}")
            self._log(fn_name, f"ERROR: {e}")
        elapsed = (time.perf_counter() - t0) * 1000
        self.state.timings[fn_name] = round(elapsed, 1)
        if ok and _ENFORCER_AVAILABLE:
            stage = fn_name.split(".")[0]
            try:
                _enforcer_mark(self.session_id, stage, self.state.kind)
            except Exception:
                pass
        # Verbose timing line: [F1 CONSTRAIN] 12ms | summary
        base = fn_name.split(".")[0]  # strip .retryN suffix
        label = F_LABELS.get(base, "")
        summary = self._state_summary(base)
        if self.verbose:
            print(
                f"  [{fn_name} {label}] {elapsed:.1f}ms | {summary}",
                file=sys.stderr,
            )

    # -- F1 CONSTRAIN -------------------------------------------------------

    def f1_constrain(self) -> None:
        """Load _schema.yaml + bld_schema + bld_config -> state.constraints.

        T04: Token budget allocation at pipeline start.

        R-127 deferred-lookup (docs/IMPROVEMENT_REGISTER.md): bld_config's
        FULL body used to be read+retained unconditionally purely to (a)
        regex-extract max_bytes as a FALLBACK and (b) stash the raw body in
        constraints['config_rules'] -- a field audited 2026-07-11 (full-repo
        grep) to have ZERO consumers anywhere in this codebase. When the
        pillar's _schema.yaml already supplies max_bytes (true for 122/125
        schema-registered kinds, avg ~3.2KB/file, ~394KB in aggregate across
        the corpus -- measured 2026-07-11), that read produces nothing
        anyone uses, so it is now SKIPPED (self._f1_read_stats records the
        skip for an honest before/after count). The fallback path (pillar
        schema has no max_bytes -- 2/125 kinds today) is untouched: same
        read, same regex, same constraints. bld_schema is still read in
        full -- its id_pattern IS genuinely consumed downstream (F6, F7,
        Mode B's prompt package) -- only its dead full-body retention
        (constraints['_schema_body'], also zero consumers) is dropped:
        "read only the needed fields", not "read less".
        """
        self._f1_read_stats = {"files_read": 0, "bytes_read": 0, "files_skipped": 0}

        # Secretariat enhancement: if kind is generic/uncertain, try LLM classification
        if _SECRETARIAT_AVAILABLE and self.state.kind in ("generic", ""):
            try:
                sec_result = _secretariat_classify(self.state.intent)
                if sec_result.get("kind") and sec_result.get("confidence", 0) >= 0.6:
                    self.state.kind = sec_result["kind"]
                    self.state.pillar = sec_result.get("pillar", self.state.pillar)
                    self.state.builder_dir = _shared_find_builder_dir(self.state.kind)
                    self.kind_slug = self.state.kind.replace("-", "_")
                    self._log("F1", "secretariat resolved: kind=%s pillar=%s" % (
                        self.state.kind, self.state.pillar))
            except Exception as e:
                self._log("F1", "secretariat unavailable: %s" % e)

        # --- T04: Token budget ---
        if _TOKEN_BUDGET_AVAILABLE:
            try:
                budget = _TokenBudget()
                self.state.token_budget = budget
                self._log("F1", f"token budget: input={budget.input_limit} output={budget.output_limit}")
            except Exception:
                self.state.token_budget = None
        else:
            self.state.token_budget = None

        bdir = self.state.builder_dir
        kind = self.state.kind
        pillar = self.state.pillar

        # 1. Pillar schema constraints
        kind_schema = load_kind_schema(kind, pillar)
        constraints = dict(kind_schema.get("constraints", {}))
        # R-352: the kind THIS run was constrained to resolve, explicit in
        # constraints (not just state.kind) so any consumer that reads
        # state.constraints["kind"] (the shape docs/IMPROVEMENT_REGISTER.md
        # R-352 names) sees the real, authoritative, Stage-1-resolved value.
        # f7_govern's kind-drift check (below) prefers this key, falling back
        # to state.kind when absent (Mode B Stage-2-only dispatch, where F1
        # never runs in-process -- see _run_mode_b_generate's own docstring).
        constraints["kind"] = kind
        constraints["frontmatter_required"] = kind_schema.get("frontmatter_required", [])
        constraints["naming"] = kind_schema.get("naming", "")
        constraints["boundary"] = kind_schema.get("boundary", "")

        # 2. bld_schema -> id_pattern, field types
        if bdir:
            schema_text = load_iso(bdir, "bld_schema", self.kind_slug)
            if schema_text:
                body = strip_frontmatter(schema_text)
                # Extract ID pattern regex (R-264: scoped to the '## ID
                # Pattern' section, not whole-body prose -- see class guard
                # above extract_id_pattern / extract_id_pattern_section)
                extracted_id_pattern = extract_id_pattern(body)
                if extracted_id_pattern:
                    constraints["id_pattern"] = extracted_id_pattern
                self._f1_read_stats["files_read"] += 1
                self._f1_read_stats["bytes_read"] += len(schema_text)
                self._log("F1", f"bld_schema loaded ({len(schema_text)} chars)")

        # 3. bld_config -> naming rules, paths, size limits.
        #    R-127 deferred lookup: skip the read entirely when max_bytes is
        #    already resolved from the pillar schema (block 1 above) -- see
        #    this method's docstring for the safety argument.
        if bdir:
            if "max_bytes" in constraints:
                self._f1_read_stats["files_skipped"] += 1
                self._log(
                    "F1",
                    "bld_config SKIPPED (max_bytes already resolved from "
                    "pillar schema -- R-127 deferred lookup)",
                )
            else:
                config_text = load_iso(bdir, "bld_config", self.kind_slug)
                if config_text:
                    body = strip_frontmatter(config_text)
                    constraints["config_rules"] = body
                    # Extract max bytes from config if present
                    m = re.search(r"max\s+(\d+)\s*bytes", body, re.IGNORECASE)
                    if m:
                        constraints["max_bytes"] = int(m.group(1))
                    self._f1_read_stats["files_read"] += 1
                    self._f1_read_stats["bytes_read"] += len(config_text)
                    self._log("F1", f"bld_config loaded ({len(config_text)} chars)")

        self.state.constraints = constraints
        self._log("F1", f"constraints: {len(constraints)} keys")

    # -- F2 BECOME ----------------------------------------------------------

    def f2_become(self) -> None:
        """Load bld_model (merged identity + persona) -> state.identity."""
        bdir = self.state.builder_dir
        identity = {}

        if bdir:
            # Model ISO (merged manifest + system_prompt -> identity + persona)
            model_text = load_iso(bdir, "bld_model", self.kind_slug)
            if model_text:
                fm = extract_frontmatter_dict(model_text)
                identity["system_prompt"] = strip_frontmatter(model_text)
                identity["persona"] = fm.get("persona", "")
                identity["knowledge_boundary"] = fm.get("knowledge_boundary", "")
                identity["builder_name"] = fm.get("id", "")
                identity["domain"] = fm.get("domain", "")
                identity["pillar_boundary"] = strip_frontmatter(model_text)
                self._log("F2", f"bld_model loaded ({len(model_text)} chars)")

        # Schema boundary
        identity["kind_boundary"] = self.state.constraints.get("boundary", "")

        # Prompt optimizer: improvement hints from learning records
        if _OPTIMIZER_AVAILABLE:
            try:
                hints = _suggest_improvements(self.state.kind)
                if hints:
                    identity["optimizer_hints"] = hints
                    self._log("F2", f"prompt optimizer: {len(hints)} hints")
            except Exception as e:
                self._log("F2", f"prompt optimizer unavailable: {e}")

        self.state.identity = identity
        self._log("F2", f"identity: {list(identity.keys())}")

    # -- F3 INJECT ----------------------------------------------------------

    def f3_inject(self) -> None:
        """Assemble ALL context from files -- pure Python, zero subprocess.

        Single source of truth for context injection. Loads 14 source types
        unconditionally, plus 1 OPTIONAL default-OFF seam:
          1. Builder knowledge card (ISO)
          2. Dedicated kind KC (1:1 per kind)
          3. Cluster domain KCs (supplementary, max 2)
          4. Few-shot examples (ISO)
          5. Memory / persistent learnings (ISO)
          6. Architecture / patterns (ISO)
          7. Domain context (--context flag)
          8. Build memory (past performance via cex_memory)
          9. Semantic retrieval (TF-IDF via cex_retriever)
         10. Prompt layers (compiled pillar artifacts)
         11. Brand context (brand_config.yaml variables)
         12. Sin lens (nucleus identity from nucleus_sins.yaml)
         13. Skill loader ISOs (multi-source, priority-ordered)
         14. Shared skills (cross-builder skills from _shared/)
         15. Repo-map digest (R-304, OPTIONAL -- see repo_map_seam_enabled();
             default OFF, adds a ranked ast+pagerank symbol digest when on)
        """
        bdir = self.state.builder_dir
        knowledge: dict = {}

        # 1. Builder knowledge card
        if bdir:
            kc_text = load_iso(bdir, "bld_knowledge", self.kind_slug)
            if kc_text:
                knowledge["kc_builder"] = strip_frontmatter(kc_text)
                self._log("F3", "bld_knowledge loaded")

        # 2. Dedicated kind KC (primary -- 1:1 per kind)
        kind_kc_path = CEX_ROOT / "N00_genesis" / "P01_knowledge" / "library" / "kind" / f"kc_{self.kind_slug}.md"
        if kind_kc_path.exists():
            text = kind_kc_path.read_text(encoding="utf-8")
            body = strip_frontmatter(text)
            if body.strip():
                knowledge["kc_dedicated"] = body
                self._log("F3", f"dedicated kind KC loaded: kc_{self.kind_slug}.md")

        # 3. Cluster domain KCs from library (supplementary, max 2)
        kc_matches = lookup_kcs_for_kind(self.kc_library, self.state.kind, self.state.pillar)
        kc_domains = []
        for kc in kc_matches[:2]:
            kc_path = CEX_ROOT / kc["path"]
            if kc_path.exists():
                text = kc_path.read_text(encoding="utf-8")
                body = strip_frontmatter(text)
                if body.strip():
                    kc_domains.append(
                        f"### KC: {kc.get('title', kc.get('id', 'unknown'))}\n\n{body}"
                    )
        knowledge["kc_domains"] = kc_domains
        self._log("F3", f"KC-Domains matched: {len(kc_domains)}")

        # 4. Few-shot examples
        if bdir:
            ex_text = load_iso(bdir, "bld_eval", self.kind_slug)
            if ex_text:
                knowledge["few_shots"] = strip_frontmatter(ex_text)
                self._log("F3", "bld_eval loaded (examples section)")

        # 5. Memory (persistent learnings)
        if bdir:
            mem_text = load_iso(bdir, "bld_memory", self.kind_slug)
            if mem_text:
                knowledge["memory"] = strip_frontmatter(mem_text)
                self._log("F3", "bld_memory loaded")

        # 6. Architecture (patterns, dependencies)
        if bdir:
            arch_text = load_iso(bdir, "bld_architecture", self.kind_slug)
            if arch_text:
                knowledge["architecture"] = strip_frontmatter(arch_text)
                self._log("F3", "bld_architecture loaded")

        # 7. Domain context (from --context flag or nucleus seed)
        if self.state.context:
            knowledge["domain_context"] = self.state.context
            self._log("F3", f"domain context injected ({len(self.state.context)} chars)")

        # 8. Build memory injection (past performance for this kind)
        if _MEMORY_AVAILABLE:
            try:
                mem_context = _memory_inject(self.state.kind)
                if mem_context and mem_context.strip():
                    knowledge["build_memory"] = mem_context
                    self._log("F3", f"build memory injected ({len(mem_context)} chars)")
            except Exception as e:
                self._log("F3", f"build memory unavailable: {e}")

        # 9. Semantic retrieval (TF-IDF similar artifacts)
        semantic_candidates: list = []
        idx = None
        if _RETRIEVER_AVAILABLE:
            try:
                idx = load_retriever_index()
                if idx:
                    similar = find_examples_for_kind(
                        kind=self.state.kind,
                        intent=self.state.intent,
                        index=idx,
                        top_k=3,
                    )
                    if similar:
                        semantic_candidates = similar
                        parts = []
                        for s in similar:
                            parts.append(
                                f"- **{s['title']}** (kind={s['kind']}, "
                                f"score={s['score']:.3f}): {s.get('tldr', '')[:150]}"
                            )
                        knowledge["semantic_matches"] = "\n".join(parts)
                        self._log("F3", f"retriever: {len(similar)} semantic matches")
            except Exception as e:
                self._log("F3", f"retriever unavailable: {e}")

        # 9a. Reuse gate (LEVERAGE_A4) -- ADVISORY pre-build near-duplicate check.
        #     Flag-gated (CEX_REUSE_GATE, default OFF = byte-identical). Reuses the
        #     index already loaded in block 9; fail-open (check_reuse never raises).
        #     It PROPOSES reuse -- it never blocks the build. The proposal is surfaced
        #     into the F6 prompt so the producer can adapt rather than regenerate.
        if _REUSE_GATE_AVAILABLE and _reuse_enabled():
            try:
                rg = _reuse_check(
                    kind=self.state.kind,
                    intent=self.state.intent,
                    index=idx,  # reuse block-9 index; None -> check_reuse loads
                )
                if rg.get("decision") == "reuse":
                    tgt = rg.get("reuse_target") or {}
                    knowledge["reuse_proposal"] = (
                        "REUSE CANDIDATE (advisory, score=%.3f >= %.2f): %s -- %s\n"
                        "Prefer ADAPTING this existing artifact over regenerating."
                        % (rg.get("max_score", 0.0), rg.get("threshold", 0.85),
                           tgt.get("path", "?"), tgt.get("title", tgt.get("id", "?")))
                    )
                    self._log("F3", "REUSE PROPOSAL: %s (score=%.3f)"
                              % (tgt.get("path", "?"), rg.get("max_score", 0.0)))
                else:
                    self._log("F3", "reuse gate: no near-duplicate (max=%.3f) -> build"
                              % rg.get("max_score", 0.0))
            except Exception as e:
                self._log("F3", f"reuse gate skipped: {e}")

        # 9b. CEXAI memory recall bridge (v0.2-W3) -- a richer, semantic re-rank of
        #     the TF-IDF candidates above via the vector substrate
        #     (cexai.memory.recall). Imported LAZILY because the cexai package may
        #     not be installed in every runtime; on ImportError we log + continue so
        #     F3 NEVER breaks 8F for the 301 existing kinds. Offline + non-blocking:
        #     a deterministic FakeEmbedder keeps it model-free + fast (no live
        #     embedding call per build), and recall() itself degrades to TF-IDF if a
        #     production embedder is ever wired and unavailable. Mirrors the W4 F5
        #     cexai.llm seam exactly.
        if semantic_candidates:
            try:
                from cexai.memory import recall as _cexai_recall
                from cexai.memory._shared.types import MemoryRecord as _CexaiRecord
                from cexai.memory.vector import FakeEmbedder as _CexaiFakeEmbedder

                corpus = [
                    _CexaiRecord(
                        id=str(c.get("id") or c.get("title") or f"cand-{i}"),
                        content=str(c.get("tldr") or c.get("title") or ""),
                        kind=str(c.get("kind") or "unknown"),
                        source_path=c.get("path"),
                        timestamp="",
                        metadata={},
                    )
                    for i, c in enumerate(semantic_candidates)
                ]
                reranked = _cexai_recall(
                    self.state.intent,
                    top_k=len(corpus),
                    records=corpus,
                    embedder=_CexaiFakeEmbedder(),
                )
                if reranked:
                    knowledge["memory_recall"] = reranked
                    self._log(
                        "F3",
                        f"cexai.memory.recall: re-ranked {len(reranked)} candidate(s) "
                        f"via the vector substrate (non-blocking)",
                    )
            except ImportError:
                self._log("F3", "cexai.memory.recall: package not installed (non-blocking)")
            except Exception as e:
                self._log("F3", f"cexai.memory.recall failed: {e} (non-blocking)")

        # 10. Prompt layers (compiled pillar artifacts -- identity, guardrails, skills)
        if _LAYERS_AVAILABLE:
            try:
                layers = _get_prompt_layers()
                layer_data: dict = {}

                # Wire 1: Core identity
                identity_body = layers.get("p03_sp_cex_core_identity")
                if identity_body:
                    # Resolve {{INCLUDE}} directives
                    for inc_id in ["p03_ins_doing_tasks", "p03_ins_action_protocol"]:
                        inc_body = layers.get(inc_id)
                        if inc_body:
                            identity_body = identity_body.replace(
                                "{{INCLUDE " + inc_id + "}}", inc_body
                            )
                    identity_body = re.sub(
                        r"\{\{[A-Z_]+\}\}", "[runtime]", identity_body
                    )
                    layer_data["identity"] = identity_body

                # Wire 4: Guardrails
                guardrail_ids = layers.by_kind("guardrail")
                if guardrail_ids:
                    guardrail_parts = []
                    for gid in guardrail_ids:
                        g_body = layers.get(gid)
                        g_meta = layers.get_meta(gid)
                        if g_body:
                            title = g_meta.get("title", gid)
                            severity = g_meta.get("severity", "?")
                            guardrail_parts.append(
                                f"### {title} [severity={severity}]\n{g_body}"
                            )
                    if guardrail_parts:
                        layer_data["guardrails"] = "\n\n".join(guardrail_parts)

                # Wire 5: Verification protocol
                verify_body = layers.get("p03_sp_verification_agent")
                if verify_body:
                    layer_data["verification"] = verify_body

                # Wire 2-3: Behavioral + action skills
                skill_ids = layers.by_kind("skill")
                if skill_ids:
                    skill_parts = []
                    for sid in skill_ids:
                        s_body = layers.get(sid)
                        s_meta = layers.get_meta(sid)
                        if s_body:
                            title = s_meta.get("title", sid)
                            skill_parts.append(f"### {title}\n{s_body}")
                    if skill_parts:
                        layer_data["skills"] = "\n\n".join(skill_parts)

                if layer_data:
                    knowledge["prompt_layers"] = layer_data
                    self._log(
                        "F3",
                        f"prompt layers loaded: {list(layer_data.keys())}",
                    )
            except Exception as e:
                self._log("F3", f"prompt layers unavailable: {e}")

        # 11. Brand context (brand_config.yaml -- pure Python, no subprocess)
        if _BRAND_INJECT_AVAILABLE:
            try:
                brand_config_path = CEX_ROOT / ".cex" / "brand" / "brand_config.yaml"
                if brand_config_path.exists():
                    brand_cfg = _load_brand_config(brand_config_path)
                    if brand_cfg:
                        flat = _flatten_brand(brand_cfg)
                        real = {
                            k: v
                            for k, v in flat.items()
                            if v and not str(v).startswith("{{")
                        }
                        if real:
                            knowledge["brand_context"] = real
                            self._log("F3", f"brand context: {len(real)} variables")
            except Exception as e:
                self._log("F3", f"brand context unavailable: {e}")

        # 12. Sin lens (nucleus identity from nucleus_sins.yaml)
        if _THEME_AVAILABLE:
            try:
                nucleus = os.environ.get("CEX_NUCLEUS", "n03").lower()
                sin = _get_sin(nucleus)
                if sin:
                    knowledge["sin_lens"] = sin
                    self._log("F3", f"sin lens: {sin.get('virtue', '?')}")
            except Exception as e:
                self._log("F3", f"sin lens unavailable: {e}")

        # 13. Skill loader ISOs (multi-source, priority-ordered, dedup'd)
        if _SKILL_LOADER_AVAILABLE:
            try:
                loader = _get_skill_loader()
                isos = loader.load_builder(self.state.kind.replace("_", "-"))
                if isos:
                    # Count by source for logging
                    by_source = {}
                    for iso in isos:
                        by_source[iso.source] = by_source.get(iso.source, 0) + 1
                    knowledge["skill_loader_sources"] = by_source
                    self._log(
                        "F3",
                        f"skill loader: {len(isos)} ISOs from {dict(by_source)}",
                    )

                    # 14. Shared skills (cross-builder, from _shared/)
                    shared = [i for i in isos if i.source == "shared"]
                    if shared:
                        shared_parts = []
                        for s in shared:
                            shared_parts.append(f"### {s.name}\n{s.content[:2000]}")
                        knowledge["shared_skills"] = "\n\n".join(shared_parts)
                        self._log("F3", f"shared skills: {len(shared)}")
            except Exception as e:
                self._log("F3", f"skill loader unavailable: {e}")

        # 15. Repo-map digest (R-304 optional additive seam, default OFF --
        #     see repo_map_seam_enabled() near class EightFRunner for the
        #     flag contract). Injects a compact ranked-symbol digest from
        #     cex_repo_map.py's clean-room ast+pagerank extraction (R-292)
        #     over the tool's own documented default scopes (_tools/,
        #     cex_sdk/). Cached at module level (_repo_map_report_cache) so
        #     a multi-kind run (main()'s kinds_to_run loop) pays the
        #     multi-second corpus scan at most once per process -- companion
        #     to R-127's "cache within a run". Mode B's _write_prompt_package
        #     intentionally does NOT carry this field: it already excludes
        #     semantic_matches/reuse_proposal for the same reason (Mode B's
        #     package is a deliberately slimmed subset for a cheap generation
        #     model, not a mirror of the full F3 state).
        if self.with_repo_map and _REPO_MAP_AVAILABLE:
            try:
                global _repo_map_report_cache
                if _repo_map_report_cache is None:
                    _repo_map_report_cache = _repo_map_mod.build_report(
                        _repo_map_mod.ROOT,
                        list(_repo_map_mod.DEFAULT_SCOPES),
                        top=_REPO_MAP_SEAM_TOP,
                        budget_tokens=_REPO_MAP_SEAM_BUDGET_TOKENS,
                    )
                report = _repo_map_report_cache
                symbols = report.get("symbols") or []
                if symbols:
                    header = (
                        "Ranked symbol digest (%s, cex_repo_map.py R-292) over "
                        "%s -- %d files scanned, %d symbols total, top %d shown "
                        "(%d/%d tokens):"
                        % (
                            report.get("extraction_method", "ast+pagerank"),
                            ", ".join(report.get("scopes", [])),
                            report.get("files_scanned", 0),
                            report.get("symbol_count", 0),
                            len(symbols),
                            report.get("used_tokens", 0),
                            report.get("budget_tokens", 0),
                        )
                    )
                    lines = [header]
                    for s in symbols:
                        lines.append(
                            "- %s %s -- %s:%s (score=%.4f)"
                            % (
                                s.get("kind", "?"), s.get("name", "?"),
                                s.get("file", "?"), s.get("lineno", "?"),
                                s.get("score", 0.0),
                            )
                        )
                    knowledge["repo_map_digest"] = "\n".join(lines)
                    self._log(
                        "F3",
                        "repo-map digest injected (%d symbols, seam=ON)" % len(symbols),
                    )
            except Exception as e:
                self._log("F3", f"repo-map digest unavailable: {e} (non-blocking)")

        self.state.knowledge = knowledge
        self._log("F3", f"knowledge: {list(knowledge.keys())}")

    # -- F4 REASON ----------------------------------------------------------

    def _load_update_artifact(self) -> dict:
        """Load existing artifact for --update mode. Returns dict with keys:
        'path', 'content', 'frontmatter', 'body', 'sections'.
        Empty dict if file not found or unparseable.
        """
        if not self.update_path:
            return {}
        p = Path(self.update_path)
        if not p.is_absolute():
            p = CEX_ROOT / p
        if not p.exists():
            self._log("F4", f"[WARN] --update file not found: {p}")
            return {}
        try:
            content = p.read_text(encoding="utf-8")
        except Exception as e:
            self._log("F4", f"[WARN] --update read error: {e}")
            return {}
        fm = extract_frontmatter_dict(content)
        body = strip_frontmatter(content)
        # Parse sections: split on ## headings
        sections = {}
        current_heading = "_preamble"
        current_lines = []
        for line in body.split("\n"):
            if line.startswith("## "):
                if current_lines:
                    sections[current_heading] = "\n".join(current_lines)
                current_heading = line.strip()
                current_lines = []
            else:
                current_lines.append(line)
        if current_lines:
            sections[current_heading] = "\n".join(current_lines)
        return {
            "path": str(p),
            "content": content,
            "frontmatter": fm,
            "body": body,
            "sections": sections,
        }

    @staticmethod
    def _estimate_change_ratio(existing_body: str, new_plan: str) -> float:
        """Estimate how much of the existing artifact the plan would change.
        Returns a float 0.0-1.0 representing the fraction of change.
        Uses a simple line-level diff heuristic.
        """
        if not existing_body.strip():
            return 1.0
        existing_lines = set(
            line.strip() for line in existing_body.split("\n") if line.strip()
        )
        plan_lines = set(
            line.strip() for line in new_plan.split("\n") if line.strip()
        )
        if not existing_lines:
            return 1.0
        common = existing_lines & plan_lines
        total = len(existing_lines | plan_lines)
        if total == 0:
            return 0.0
        return 1.0 - (len(common) / total)

    def f4_reason(self) -> None:
        """LLM plans the artifact: fields, decisions, tradeoffs -> state.reasoning.

        T03: GDP gate -- if unresolved USER-scope decisions exist for this kind,
        raises NeedsUserDecision instead of proceeding (D2: raise = halt pipeline).

        --update mode: reads existing artifact first, produces a delta plan
        that preserves human edits and scores.
        """
        # --- T03: GDP gate ---
        if _GDP_AVAILABLE:
            try:
                gdp = _GDPEnforcer()
                pending = gdp.get_pending()
                for d in pending:
                    if d.kind == self.state.kind or d.scope.value == "GLOBAL":
                        self._log("F4", f"GDP BLOCKED: unresolved decision '{d.id}' ({d.scope.value})")
                        raise _NeedsUserDecision(d)
            except _NeedsUserDecision:
                raise
            except Exception as e:
                self._log("F4", f"GDP check skipped: {e}")

        # --- UPDATE MODE: load existing artifact for delta planning ---
        existing = self._load_update_artifact()
        if existing:
            self.state.reasoning["_update_existing"] = existing
            self._log("F4", f"update mode: loaded {existing['path']} "
                      f"({len(existing['sections'])} sections, "
                      f"{len(existing['body'])} chars)")

        # Compose reasoning prompt from accumulated state
        parts = []
        if existing:
            parts.append(
                "You are planning an UPDATE to an existing artifact. "
                "Think step-by-step about WHAT CHANGED vs the existing content. "
                "Preserve human edits, scores, and stable sections. "
                "Only modify sections that the intent requires changing."
            )
        else:
            parts.append("You are planning what artifact to produce. Think step-by-step.")
        parts.append(f"\n## Intent\n{self.state.intent}")
        parts.append(f"\n## Kind\n{self.state.kind} (pillar: {self.state.pillar})")

        # Identity context
        persona = self.state.identity.get("persona", "")
        if persona:
            parts.append(f"\n## Builder Persona\n{persona}")

        # Constraints summary
        c = self.state.constraints
        c_lines = []
        if c.get("id_pattern"):
            c_lines.append(f"- ID pattern: `{c['id_pattern']}`")
        if c.get("frontmatter_required"):
            c_lines.append(f"- Required frontmatter: {', '.join(c['frontmatter_required'])}")
        if c.get("max_bytes"):
            c_lines.append(f"- Max size: {c['max_bytes']} bytes")
        if c.get("boundary"):
            c_lines.append(f"- Boundary: {c['boundary']}")
        if c_lines:
            parts.append("\n## Constraints\n" + "\n".join(c_lines))

        # Knowledge summary (condensed)
        k = self.state.knowledge
        kc_count = len(k.get("kc_domains", []))
        if kc_count:
            parts.append(f"\n## Available Knowledge\n{kc_count} domain KCs available.")
        if k.get("kc_builder"):
            # First 300 chars of builder KC as context
            parts.append(f"\n## Builder KC (excerpt)\n{k['kc_builder'][:300]}...")

        # --- UPDATE MODE: inject existing artifact for delta planning ---
        if existing:
            fm_lines = []
            for fk, fv in sorted(existing["frontmatter"].items()):
                fm_lines.append(f"  {fk}: {fv}")
            parts.append(
                "\n## EXISTING ARTIFACT (preserve unless intent requires change)\n"
                "### Frontmatter\n```yaml\n"
                + "\n".join(fm_lines)
                + "\n```\n"
                "### Sections\n"
                + "\n".join(
                    f"- {heading} ({len(body.split())} words)"
                    for heading, body in existing["sections"].items()
                )
                + "\n\n### Full Body\n"
                + existing["body"][:3000]
            )
            if len(existing["body"]) > 3000:
                parts.append("... (truncated, original has "
                             f"{len(existing['body'])} chars)")

            parts.append(
                "\n## Task (UPDATE MODE)\n"
                "Plan a DELTA update to the existing artifact. List:\n"
                "1. Which frontmatter fields need updating (and new values)\n"
                "2. Which sections to ADD, MODIFY, or REMOVE\n"
                "3. Which sections to KEEP AS-IS (preserve human edits)\n"
                "4. Summary of changes vs existing\n"
                "Be concise (under 500 words). "
                "Preserve quality, tags, and scores from the original."
            )
        else:
            parts.append(
                "\n## Task\n"
                "Plan the artifact. List:\n"
                "1. Which frontmatter fields to include and their values\n"
                "2. Key decisions and tradeoffs\n"
                "3. Body structure outline\n"
                "Be concise (under 500 words)."
            )

        prompt = "\n".join(parts)

        if self.dry_run:
            self.state.reasoning = {"plan": prompt, "model_used": "dry-run"}
            self._log("F4", f"dry-run reasoning prompt ({len(prompt.split())} words)")
        else:
            # Token optimization: skip LLM reasoning if F3 found existing
            # artifacts of the same kind (template-first approach).
            # The plan is predictable: adapt from template structure.
            existing_count = len(self.state.knowledge.get("similar", []))
            kc_builder = self.state.knowledge.get("kc_builder", "")
            has_template = bool(kc_builder and len(kc_builder) > 200)

            # Ollama models: ALWAYS use deterministic plan (skip F4 LLM call)
            # Saves ~280s on weak hardware. F6 already sends full context.
            is_ollama = self.model and self.model.startswith("ollama/")

            if existing_count >= 1 and has_template or is_ollama:
                # Deterministic plan from template (saves ~5K tokens)
                c = self.state.constraints
                plan_lines = [
                    "## F4 Reasoning Plan (template-first, zero LLM tokens)",
                    f"Kind: {self.state.kind} | Pillar: {self.state.pillar}",
                    f"Approach: adapt from {existing_count} existing artifact(s)",
                    "",
                    "1. Frontmatter: id, kind, pillar, title, version, quality: null, "
                    "tags, tldr, domain, created, updated, density_score",
                    "2. Structure: follow output template sections",
                    "3. Content: domain-specific, no filler, density >= 0.85",
                    "4. Quality: target 9.0+, all hard gates PASS",
                ]
                if c.get("boundary"):
                    plan_lines.append(f"5. Boundary: {c['boundary']}")
                response = "\n".join(plan_lines)
                skip_reason = "ollama-skip" if is_ollama else "template-skip"
                self.state.reasoning = {"plan": response, "model_used": skip_reason}
                self._log("F4", f"deterministic plan ({skip_reason}, LLM skipped)")
            else:
                self._log("F4", "calling LLM for reasoning plan...")
                response = execute_prompt(
                    prompt, model_override=self.model,
                    max_tokens=_max_tokens_from_bytes(self.state.constraints.get("max_bytes")),
                )
                model_tag = self.model or "default"
                self.state.reasoning = {"plan": response, "model_used": model_tag}
                self._log("F4", f"reasoning plan received ({len(response)} chars)")

    # -- F5 CALL ------------------------------------------------------------

    def f5_call(self) -> None:
        """Load bld_tools spec, scan existing artifacts, EXECUTE active tools -> state.tool_results."""
        bdir = self.state.builder_dir
        tool_results = {
            "existing_artifacts": [],
            "tools_available": [],
            "tool_outputs": {},
            "enrichment_text": "",
        }

        # --- Phase 1: Parse bld_tools spec (backwards compat) ---
        if bdir:
            tools_text = load_iso(bdir, "bld_tools", self.kind_slug)
            if tools_text:
                body = strip_frontmatter(tools_text)
                for line in body.split("\n"):
                    line = line.strip()
                    if (
                        line.startswith("|")
                        and "---" not in line
                        and "Tool" not in line
                        and "Source" not in line
                    ):
                        cols = [c.strip() for c in line.split("|")[1:-1]]
                        if len(cols) >= 2 and cols[0]:
                            tool_results["tools_available"].append(
                                {
                                    "name": cols[0],
                                    "purpose": cols[1] if len(cols) > 1 else "",
                                    "status": cols[3] if len(cols) > 3 else "unknown",
                                }
                            )
                self._log(
                    "F5",
                    f"bld_tools loaded, {len(tool_results['tools_available'])} tools parsed",
                )

        # --- Phase 2: Scan existing artifacts in pillar examples dir ---
        pillar_dir_name = PILLAR_DIRS.get(self.state.pillar)
        if pillar_dir_name:
            examples_dir = CEX_ROOT / pillar_dir_name / "examples"
            if examples_dir.exists():
                kind_slug = self.state.kind.replace("-", "_")
                for f in sorted(examples_dir.glob(f"ex_{kind_slug}*.md")):
                    tool_results["existing_artifacts"].append(f.name)

        existing = tool_results["existing_artifacts"]
        if existing:
            self._log(
                "F5",
                f"WARNING: {len(existing)} similar artifact(s) exist: "
                + ", ".join(existing[:5]),
            )

        # --- Phase 3: Auto-execute tools for context enrichment ---
        intent = self.state.intent
        executed = 0

        # 3a. Retriever: find similar artifacts by TF-IDF
        if _RETRIEVER_AVAILABLE:
            try:
                idx = load_retriever_index()
                if idx:
                    results = _find_similar(intent, index=idx, top_k=3)
                    if results:
                        tool_results["tool_outputs"]["retriever"] = results
                        executed += 1
                        self._log("F5", f"retriever: {len(results)} similar artifacts found")
            except Exception as e:
                self._log("F5", f"retriever failed: {e} (non-blocking)")

        # 3b. Query: discover related builders by TF-IDF
        if _QUERY_AVAILABLE:
            try:
                builders = _query_builders(intent, top_k=3)
                if builders:
                    tool_results["tool_outputs"]["query"] = builders
                    executed += 1
                    self._log("F5", f"query: {len(builders)} related builders discovered")
            except Exception as e:
                self._log("F5", f"query failed: {e} (non-blocking)")

        # 3c. Memory: recall relevant build memories
        if _MEMORY_AVAILABLE:
            try:
                kind = self.state.kind
                memory_ctx = _memory_inject(kind)
                if memory_ctx and memory_ctx.strip():
                    tool_results["tool_outputs"]["memory"] = memory_ctx
                    executed += 1
                    self._log("F5", f"memory: context loaded for kind={kind}")
            except Exception as e:
                self._log("F5", f"memory failed: {e} (non-blocking)")

        # 3d. Provider discovery: check health
        if _PROVIDER_AVAILABLE:
            try:
                providers = _discover_providers(use_cache=True)
                if providers:
                    alive = sum(1 for p in providers.values() if p.get("status") == "OK")
                    tool_results["tool_outputs"]["providers"] = {
                        "alive": alive,
                        "total": len(providers),
                        "detail": {k: v.get("status", "?") for k, v in providers.items()},
                    }
                    executed += 1
                    self._log("F5", f"providers: {alive}/{len(providers)} alive")
            except Exception as e:
                self._log("F5", f"provider discovery failed: {e} (non-blocking)")

        # 3e. Brand config -- MOVED to F3 INJECT (pure Python, single source of truth)
        # F5 reads from F3 state if needed:
        if self.state.knowledge.get("brand_context"):
            tool_results["tool_outputs"]["brand"] = self.state.knowledge["brand_context"]
            executed += 1
            self._log("F5", "brand context: from F3 (already loaded)")

        # 3f. Sin lens -- MOVED to F3 INJECT (pure Python, single source of truth)
        if self.state.knowledge.get("sin_lens"):
            tool_results["tool_outputs"]["sin"] = self.state.knowledge["sin_lens"]
            executed += 1
            self._log("F5", "sin lens: from F3 (already loaded)")

        # 3g. CEXAI foundation LLM facade -- the canonical multi-provider call()
        #     interface (cexai.foundation.llm). Discovery via available_providers();
        #     generation flows through cexai.foundation.llm.call(LlmRequest) which
        #     returns a normalized LlmResponse across Anthropic/OpenAI/Google/Ollama.
        #     Imported LAZILY because the cexai package may not be installed in every
        #     runtime; on ImportError we log + continue so F5 NEVER breaks 8F for the
        #     301 existing kinds. Additive + non-blocking, exactly like the steps above.
        try:
            from cexai.foundation.llm import available_providers as _cexai_providers
            cexai_provider_names = list(_cexai_providers())
            if cexai_provider_names:
                tool_results["tool_outputs"]["cexai_llm"] = {
                    "providers": cexai_provider_names,
                    "count": len(cexai_provider_names),
                    "interface": "cexai.foundation.llm.call",
                }
                executed += 1
                self._log(
                    "F5",
                    f"cexai.llm: {len(cexai_provider_names)} provider(s) via canonical "
                    f"call() interface ({', '.join(cexai_provider_names)})",
                )
        except ImportError:
            self._log("F5", "cexai.llm: package not installed (non-blocking)")
        except Exception as e:
            self._log("F5", f"cexai.llm discovery failed: {e} (non-blocking)")

        # 3h. CEXAI memory recall -- surfaced from F3 INJECT (block 9b) into F5's
        #     enrichment, mirroring the brand/sin "read from F3 state" pattern (3e/3f).
        if self.state.knowledge.get("memory_recall"):
            tool_results["tool_outputs"]["memory_recall"] = self.state.knowledge["memory_recall"]
            executed += 1
            self._log("F5", "cexai.memory.recall: from F3 (already loaded)")

        # --- Phase 4: Build enrichment text for F6 injection ---
        if tool_results["tool_outputs"]:
            enrichments = []
            for tool_name, output in tool_results["tool_outputs"].items():
                if tool_name == "retriever" and isinstance(output, list):
                    lines = [f"### Similar Artifacts ({len(output)} matches)"]
                    for item in output[:3]:
                        lines.append(
                            f"- **{item.get('id', '?')}** ({item.get('kind', '?')}) "
                            f"score={item.get('score', 0):.2f} -- {item.get('tldr', '')[:120]}"
                        )
                    enrichments.append("\n".join(lines))
                elif tool_name == "query" and isinstance(output, list):
                    lines = [f"### Related Builders ({len(output)} discovered)"]
                    for item in output[:3]:
                        lines.append(
                            f"- **{item.get('builder_id', item.get('id', '?'))}** "
                            f"score={item.get('score', 0):.2f}"
                        )
                    enrichments.append("\n".join(lines))
                elif tool_name == "memory" and isinstance(output, str):
                    enrichments.append(f"### Build Memory\n{output[:2000]}")
                elif tool_name == "providers" and isinstance(output, dict):
                    enrichments.append(
                        f"### Provider Health\n"
                        f"{output.get('alive', 0)}/{output.get('total', 0)} providers alive"
                    )
                elif tool_name == "cexai_llm" and isinstance(output, dict):
                    enrichments.append(
                        f"### CEXAI LLM Interface\n"
                        f"Canonical multi-provider call: {output.get('interface', '?')}() "
                        f"-> normalized LlmResponse.\n"
                        f"{output.get('count', 0)} provider adapter(s): "
                        f"{', '.join(output.get('providers', []))}"
                    )
                elif tool_name == "brand" and isinstance(output, dict):
                    brand_name = output.get("identity", {}).get("name", "?")
                    enrichments.append(f"### Brand Context\nBrand: {brand_name}")
                elif tool_name == "sin" and isinstance(output, dict):
                    enrichments.append(
                        f"### Sin Lens\n"
                        f"Virtue: {output.get('virtue', '?')} | "
                        f"Tagline: {output.get('tagline', '?')}"
                    )
                elif tool_name == "memory_recall" and isinstance(output, list):
                    lines = [f"### Memory Recall ({len(output)} re-ranked via vector substrate)"]
                    for item in output[:3]:
                        marker = " [FALLBACK]" if item.get("fallback") else ""
                        lines.append(
                            f"- **{item.get('id', '?')}** ({item.get('kind', '?')}) "
                            f"score={item.get('score', 0):.2f}{marker}"
                        )
                    enrichments.append("\n".join(lines))
                else:
                    # Generic fallback
                    enrichments.append(
                        f"### {tool_name}\n{json.dumps(output, indent=2, default=str)[:2000]}"
                    )

            tool_results["enrichment_text"] = "\n\n".join(enrichments)

        self.state.tool_results = tool_results
        self._log(
            "F5",
            f"tools: {len(tool_results['tools_available'])}, "
            f"existing: {len(existing)}, "
            f"executed: {executed}, "
            f"enrichments: {len(tool_results['tool_outputs'])}",
        )

    # -- F6 PRODUCE ---------------------------------------------------------

    def f6_produce(self, retry_feedback: str = "") -> None:
        """Compose STRUCTURED prompt with labeled sections -> state.artifact."""
        sections = []

        # 0. PROMPT LAYERS (from F3 -- injected FIRST, before everything)
        k = self.state.knowledge
        pl = k.get("prompt_layers", {})
        if pl.get("identity"):
            sections.append(f"# CEX AGENT IDENTITY\n\n{pl['identity']}")
        if k.get("sin_lens"):
            sin = k["sin_lens"]
            sections.append(
                f"# IDENTITY LENS\n\n"
                f"Virtue: {sin.get('virtue', '?')} | "
                f"Tagline: {sin.get('tagline', '?')}"
            )
        if pl.get("guardrails"):
            sections.append(f"# GUARDRAILS\n\n{pl['guardrails']}")

        # 0b. BRAND CONTEXT (from F3)
        brand = k.get("brand_context")
        if brand and isinstance(brand, dict):
            brand_lines = [f"- {bk}: {bv}" for bk, bv in sorted(brand.items())
                           if not bk.startswith(("identity.", "archetype.", "voice.",
                                                 "audience.", "visual.", "positioning.",
                                                 "monetization."))]
            if brand_lines:
                sections.append("# BRAND CONTEXT\n\n" + "\n".join(brand_lines))

        # 0c. SHARED SKILLS (from F3)
        if k.get("shared_skills"):
            sections.append(f"# SHARED SKILLS\n\n{k['shared_skills']}")

        # 1. IDENTITY (from F2)
        sp = self.state.identity.get("system_prompt", "")
        if sp:
            sections.append(f"# IDENTITY\n\n{sp}")

        # 2. CONSTRAINTS (from F1)
        c = self.state.constraints
        constraint_lines = []
        if c.get("max_bytes"):
            constraint_lines.append(f"- Max body size: {c['max_bytes']} bytes")
        if c.get("id_pattern"):
            constraint_lines.append(f"- ID pattern: `{c['id_pattern']}`")
        if c.get("frontmatter_required"):
            constraint_lines.append(
                f"- Required frontmatter: {', '.join(c['frontmatter_required'])}"
            )
        if c.get("boundary"):
            constraint_lines.append(f"- Boundary: {c['boundary']}")
        if c.get("naming"):
            constraint_lines.append(f"- Naming: {c['naming']}")
        constraint_lines.append("- quality: null (NEVER self-score)")
        if constraint_lines:
            sections.append("# CONSTRAINTS\n\n" + "\n".join(constraint_lines))

        # 3. KNOWLEDGE (from F3)
        k = self.state.knowledge
        knowledge_parts = []
        if k.get("kc_builder"):
            knowledge_parts.append(f"## Builder Knowledge\n\n{k['kc_builder']}")
        for kc_domain in k.get("kc_domains", []):
            knowledge_parts.append(f"## Domain Knowledge\n\n{kc_domain}")
        if k.get("architecture"):
            knowledge_parts.append(f"## Architecture\n\n{k['architecture']}")
        if k.get("memory"):
            knowledge_parts.append(f"## Memory (Past Learnings)\n\n{k['memory']}")
        if k.get("domain_context"):
            knowledge_parts.append("## Domain Context\n\n" + k["domain_context"])
        if k.get("build_memory"):
            knowledge_parts.append(
                "## Build Memory (past performance)\n\n" + k["build_memory"]
            )
        if k.get("semantic_matches"):
            knowledge_parts.append(
                "## Similar Artifacts (semantic retrieval)\n\n" + k["semantic_matches"]
            )
        if k.get("reuse_proposal"):
            knowledge_parts.append(
                "## Reuse Proposal (advisory)\n\n" + k["reuse_proposal"]
            )
        if k.get("repo_map_digest"):
            knowledge_parts.append(
                "## Repo Map Digest (advisory, R-304)\n\n" + k["repo_map_digest"]
            )
        if knowledge_parts:
            sections.append("# KNOWLEDGE\n\n" + "\n\n".join(knowledge_parts))

        # 4. EXAMPLES (from F3)
        if k.get("few_shots"):
            sections.append(f"# EXAMPLES\n\n{k['few_shots']}")

        # 5. PLAN (from F4 reasoning)
        plan = self.state.reasoning.get("plan", "")
        if plan:
            sections.append(f"# PLAN\n\n{plan}")

        # 5b. TOOLS (from F5 call)
        tr = self.state.tool_results
        if tr.get("tools_available") or tr.get("existing_artifacts"):
            tool_lines = []
            if tr.get("tools_available"):
                tool_lines.append("## Available Tools")
                for t in tr["tools_available"]:
                    status = t.get("status", "")
                    tool_lines.append(f"- **{t['name']}**: {t['purpose']} [{status}]")
            if tr.get("existing_artifacts"):
                tool_lines.append(f"\n## Existing Artifacts ({len(tr['existing_artifacts'])})")
                for a in tr["existing_artifacts"][:5]:
                    tool_lines.append(f"- {a}")
                tool_lines.append(
                    "\n> NOTE: Similar artifacts exist. Ensure your output is "
                    "distinct and adds value."
                )
            sections.append("# TOOLS\n\n" + "\n".join(tool_lines))

        # 5b-extra. F5 AUTO-RETRIEVED CONTEXT (tool execution outputs)
        enrichment = tr.get("enrichment_text", "")
        if enrichment:
            sections.append("# AUTO-RETRIEVED CONTEXT (F5 CALL)\n\n" + enrichment)

        # 5c. OPTIMIZER HINTS (from F2 prompt_optimizer)
        hints = self.state.identity.get("optimizer_hints", [])
        if hints:
            sections.append(
                "# OPTIMIZER HINTS\n\n"
                "Based on past builds, pay attention to:\n"
                + "\n".join(f"- {h}" for h in hints)
            )

        # 6. PROMPT (bld_prompt body)
        bdir = self.state.builder_dir
        if bdir:
            prompt_text = load_iso(bdir, "bld_prompt", self.kind_slug)
            if prompt_text:
                sections.append(f"# PROMPT\n\n{strip_frontmatter(prompt_text)}")

        # 7. TEMPLATE (bld_output body)
        if bdir:
            tpl_text = load_iso(bdir, "bld_output", self.kind_slug)
            if tpl_text:
                sections.append(f"# TEMPLATE\n\n{strip_frontmatter(tpl_text)}")

        # 8. TASK (user intent)
        existing = self.state.reasoning.get("_update_existing", {})
        task_lines = [
            f"**Intent**: {self.state.intent}",
            f"**Kind**: {self.state.kind}",
            f"**Pillar**: {self.state.pillar}",
            f"**Verb**: {self.parsed.get('verb', 'cria')}"
            f" ({self.parsed.get('verb_action', 'create')})",
            "**Quality**: set quality: null (NEVER self-score)",
        ]
        if existing:
            task_lines.extend([
                "",
                "## UPDATE MODE RULES",
                "You are UPDATING an existing artifact, NOT creating from scratch.",
                "1. PRESERVE all sections not mentioned in the delta plan.",
                "2. KEEP existing frontmatter fields unless the plan says to change them.",
                "3. MERGE new content into existing sections -- do not drop content.",
                "4. Preserve quality: null from the original (NEVER self-score).",
                "5. Keep existing tags and add new ones if relevant.",
                "",
                "## EXISTING ARTIFACT TO UPDATE",
                existing.get("content", "")[:6000],
            ])
            if len(existing.get("content", "")) > 6000:
                task_lines.append(
                    "... (truncated, original has "
                    f"{len(existing['content'])} chars)"
                )
        task_lines.extend([
            "",
            "## CRITICAL OUTPUT RULES",
            "1. Output ONLY the artifact. NO preamble, NO explanation, NO tool calls.",
            "2. Start your response with exactly `---` on the first line.",
            "3. Then YAML frontmatter fields (id, kind, pillar, title, etc).",
            "4. Then `---` to close frontmatter.",
            "5. Then Markdown body with ## sections.",
            "6. Do NOT wrap in code fences (no ```yaml or ```markdown).",
            "7. Do NOT include any text before the opening `---`.",
        ])
        sections.append("# TASK\n\n" + "\n".join(task_lines))

        # 9. RETRY FEEDBACK (from F7, if retrying)
        if retry_feedback:
            sections.append(
                f"# RETRY FEEDBACK\n\n"
                f"Your previous output FAILED validation. Fix these issues:\n\n"
                f"{retry_feedback}"
            )

        prompt = "\n\n---\n\n".join(sections)

        # Ollama ultra-lite mode: aggressive prompt reduction for local models
        # Local models on weak hardware (4GB VRAM, CPU offload) need <3K tokens
        if self.model and self.model.startswith("ollama/"):
            keep_headers = {
                "# IDENTITY", "# CONSTRAINTS", "# INSTRUCTION",
                "# TEMPLATE", "# TASK",
            }
            lite_sections = []
            for sec in sections:
                header = sec.split("\n")[0].strip()
                if header in keep_headers:
                    # Truncate long sections to ~500 chars
                    if len(sec) > 600 and header not in ("# TASK",):
                        sec = sec[:600] + "\n[...truncated for local model...]"
                    lite_sections.append(sec)
            # Always include TASK (last)
            if not any(s.startswith("# TASK") for s in lite_sections):
                lite_sections.append(sections[-1])
            prompt = "\n\n---\n\n".join(lite_sections)
            self._log("F6", f"Ollama ultra-lite: {len(sections)} -> {len(lite_sections)} sections")

        # Token budget analysis (if available)
        token_count = len(prompt.split())  # fallback: word count
        if _TOKEN_BUDGET_AVAILABLE:
            token_count = count_tokens(prompt)
            self._log("F6", f"prompt: {token_count:,} tokens (tiktoken)")

        if self.dry_run:
            self.state.artifact = prompt
            self._log("F6", f"dry-run prompt composed ({token_count:,} tokens)")
        else:
            self._log("F6", f"executing prompt ({token_count:,} tokens) via {self.model or 'default'}...")
            response = execute_prompt(
                prompt, model_override=self.model,
                max_tokens=_max_tokens_from_bytes(self.state.constraints.get("max_bytes")),
            )
            self.state.artifact = response
            self._log("F6", f"LLM response received ({len(response)} chars)")

            # --- T04b: Token budget output check ---
            if getattr(self.state, "token_budget", None):
                try:
                    out_tokens = count_tokens(response) if _TOKEN_BUDGET_AVAILABLE else len(response.split())
                    limit = self.state.token_budget.output_limit
                    if limit and out_tokens > limit:
                        self._log("F6", f"WARN: output {out_tokens} tokens exceeds budget {limit}")
                except Exception:
                    pass

    # -- helpers: clean LLM output ------------------------------------------

    def _clean_llm_output(self, text: str) -> str:
        """Strip preamble, code fences, and tool calls from LLM output."""
        t = text.strip()

        # Strip everything before first --- (preamble, tool calls, etc.)
        idx = t.find("---\n")
        if idx > 0:
            t = t[idx:]
        elif idx < 0 and not t.startswith("---"):
            for marker in ["---\r\n", "---\n", "\n---"]:
                pos = t.find(marker)
                if pos >= 0:
                    t = t[pos:].lstrip("\n\r")
                    break

        # Strip code fences wrapping the whole thing
        bt = chr(96) * 3
        if t.startswith(bt):
            nl = t.find(chr(10))
            if nl > 0:
                t = t[nl + 1:]
            close = t.rfind(bt)
            if close > 0:
                t = t[:close].strip()

        # Ensure starts with ---
        if not t.startswith("---"):
            t = "---\n" + t

        return t

    # -- F7 GOVERN ----------------------------------------------------------

    def _mode_b_ladder_rungs(self) -> list[str]:
        """Lazily build + cache this run's Mode B escalation ladder (R-342).

        Rung 0 is always the STARTING model (self.model as resolved before
        this run began -- an override is the starting rung, never a ceiling,
        Fix Direction #2). Rungs 1..N are the fixed W5 targets that come
        AFTER the starting rung's own position: an unrecognized starting
        model (a GLM box model, empty/default, ollama, ...) is treated as
        below "sonnet" and gets the full sonnet -> opus climb; a starting
        model that already resolves to sonnet only gets opus; one that
        already resolves to opus gets nothing further (already terminal --
        no downgrade, no redundant re-run on the same tier).
        """
        if self._ladder_rungs is None:
            starting = self.model or ""
            s_low = starting.lower()
            rungs = [starting]
            if "opus" not in s_low:
                if "sonnet" not in s_low:
                    sonnet_id = _resolve_ladder_rung("sonnet")
                    if sonnet_id and sonnet_id not in rungs:
                        rungs.append(sonnet_id)
                opus_id = _resolve_ladder_rung("opus")
                if opus_id and opus_id not in rungs:
                    rungs.append(opus_id)
            self._ladder_rungs = rungs
        return self._ladder_rungs

    def f7_govern(self) -> None:
        """Validate artifact against 6 hard gates. Retry via F6 if fails (max 2).

        In --update mode, also checks if the diff exceeds 60% (effective rewrite).
        If >60% and --force not set, flags a warning in the verdict.
        """
        max_retries = 2
        retries = 0

        # Clean LLM output before validation
        self.state.artifact = self._clean_llm_output(self.state.artifact)

        # --- UPDATE MODE: rewrite ratio check ---
        existing = self.state.reasoning.get("_update_existing", {})
        if existing and existing.get("body"):
            new_body = strip_frontmatter(self.state.artifact)
            ratio = self._estimate_change_ratio(existing["body"], new_body)
            self._log("F7", f"update change ratio: {ratio:.1%}")
            if ratio > 0.6 and not self.force_rewrite:
                self._log(
                    "F7",
                    "[WARN] >60%% change detected -- this is effectively a "
                    "rewrite. Use --force to confirm."
                )
                self.state.verdict = {
                    "passed": False,
                    "hard_gates": [],
                    "issues": [
                        "UPDATE_REWRITE: %.0f%% of content changed (>60%% "
                        "threshold). This is effectively a rewrite, not an "
                        "update. Use --force to override." % (ratio * 100)
                    ],
                    "feedback": "",
                    "retries": 0,
                    "rewrite_ratio": ratio,
                }
                return

        while True:
            artifact = self.state.artifact
            hard_gates: list[dict] = []
            issues: list[str] = []

            def _gate(gate: str, check: str, passed: bool, fail_msg: str = "") -> None:
                hard_gates.append({"gate": gate, "check": check, "passed": passed})  # noqa: B023
                if not passed and fail_msg:
                    issues.append(fail_msg)  # noqa: B023

            fm = extract_frontmatter_dict(artifact)
            _gate("H01", "YAML frontmatter parses", bool(fm),
                  "H01: Frontmatter missing or invalid YAML")

            id_pattern = self.state.constraints.get("id_pattern", "")
            artifact_id = fm.get("id", "")
            h02 = bool(re.match(id_pattern, str(artifact_id))) if (id_pattern and artifact_id) else (not id_pattern)
            _gate("H02", "id matches id_pattern", h02,
                  f"H02: id '{artifact_id}' does not match pattern /{id_pattern}/")

            # R-352: kind-enforce. expected_kind prefers the explicit
            # state.constraints["kind"] (set by f1_constrain -- Mode A / Stage
            # 1) and falls back to state.kind (always populated at __init__,
            # including Mode B Stage-2-only dispatch where f1_constrain never
            # runs in-process). The Stage-1-constrained kind is AUTHORITATIVE
            # -- a model's own auto-declared frontmatter.kind is NEVER
            # accepted over it, matching docs/IMPROVEMENT_REGISTER.md R-352.
            artifact_kind = fm.get("kind", "")
            expected_kind = self.state.constraints.get("kind") or self.state.kind
            kind_matches = str(artifact_kind) == expected_kind if fm else True
            if fm and not kind_matches:
                self._log(
                    "F7",
                    "[KIND-DRIFT] modelo declarou '%s', constrangido '%s' -> "
                    "rejeitado" % (artifact_kind, expected_kind),
                )
            _gate("H03", "kind matches", kind_matches,
                  f"H03: kind '{artifact_kind}' != expected '{expected_kind}'")

            h04 = fm.get("quality") is None if fm else True
            _gate("H04", "quality is null", h04,
                  f"H04: quality must be null, got '{fm.get('quality')}'")

            required = self.state.constraints.get("frontmatter_required", [])
            missing = [f for f in required if f not in fm] if fm else list(required)
            _gate("H05", "required fields present", len(missing) == 0,
                  f"H05: Missing required fields: {', '.join(missing)}")

            max_bytes = self.state.constraints.get("max_bytes")
            body_size = len(strip_frontmatter(artifact).encode("utf-8"))
            _gate("H06", "body <= max_bytes", body_size <= int(max_bytes) if max_bytes else True,
                  f"H06: Body {body_size} bytes > max {max_bytes} bytes")

            # CEXAI citation gate (v0.4-W2) -- additive, lazy, non-blocking.
            # 11 US P2 / SC-002 / V11-F2: an artifact that reuses welib content
            # verbatim or as a >= 50-word paraphrase MUST carry a Citation; an
            # uncited direct-reuse HARD-FAILS F7. Imported LAZILY because the cexai
            # package may not be installed in every runtime; the gate is added ONLY
            # when the artifact carries the welib direct-reuse signal (result.applies)
            # -- so when cexai is absent OR there is no reuse signal, the hard_gates
            # list is byte-identical to today and F7 is unchanged for the 301 existing
            # kinds. Mirrors the v0.2 F3/F5 cexai seams (lazy import, guard, never
            # break 8F).
            try:
                from cexai.tools.research.citation_gate import \
                    evaluate as _cexai_citation_eval
                _cg = _cexai_citation_eval(fm, strip_frontmatter(artifact))
                if _cg.applies:
                    _gate(
                        "CEXAI_CITATION",
                        "welib direct-reuse carries a Citation",
                        _cg.passed,
                        f"CEXAI_CITATION: {_cg.reason}",
                    )
                    self._log(
                        "F7",
                        f"cexai citation gate: applies={_cg.applies} "
                        f"passed={_cg.passed} -- {_cg.reason}",
                    )
            except ImportError:
                self._log("F7", "cexai citation gate: package not installed (non-blocking)")
            except Exception as e:
                self._log("F7", f"cexai citation gate failed: {e} (non-blocking)")

            # CEXAI reasoning_trace gate (v0.5-W2) -- additive, lazy, non-blocking.
            # 13 SC-005 / FR-012: a COMPILER-INITIATED skill install MUST emit a
            # non-empty reasoning_trace; its absence HARD-FAILS F7 GOVERN. Imported
            # LAZILY because the cexai package may not be installed in every runtime;
            # the gate is added ONLY when the artifact carries the compiler-initiated
            # skill-install signal (result.applies) -- so when cexai is absent OR there
            # is no install signal, the hard_gates list is byte-identical to today and
            # F7 is unchanged for the 301 existing kinds (an ordinary skill kind carries
            # no compiler initiator, so it does not trigger either). Mirrors the v0.4-W2
            # citation gate above (lazy import, guard, broad-except, never break 8F).
            try:
                from cexai.distribution.skills.reasoning_gate import \
                    evaluate as _cexai_reasoning_eval
                _rg = _cexai_reasoning_eval(fm, strip_frontmatter(artifact))
                if _rg.applies:
                    _gate(
                        "CEXAI_REASONING_TRACE",
                        "compiler-initiated skill install emits a reasoning_trace",
                        _rg.passed,
                        f"CEXAI_REASONING_TRACE: {_rg.reason}",
                    )
                    self._log(
                        "F7",
                        f"cexai reasoning_trace gate: applies={_rg.applies} "
                        f"passed={_rg.passed} -- {_rg.reason}",
                    )
            except ImportError:
                self._log("F7", "cexai reasoning_trace gate: package not installed (non-blocking)")
            except Exception as e:
                self._log("F7", f"cexai reasoning_trace gate failed: {e} (non-blocking)")

            # Output formatter validation (jsonschema-based, soft -- non-blocking)
            soft_warnings: list[str] = []
            if _FORMATTER_AVAILABLE and fm:
                try:
                    fm_results = _validate_fm(fm, self.state.kind)
                    for r in fm_results:
                        if not r.get("passed"):
                            soft_warnings.append(f"S_{r['rule']}: {r['message']}")
                    self._log("F7", f"formatter: {len(fm_results)} rules, {len(soft_warnings)} warnings")
                except Exception as e:
                    self._log("F7", f"formatter unavailable: {e}")

            all_passed = all(g["passed"] for g in hard_gates)

            if all_passed:
                self.state.verdict = {
                    "passed": True,
                    "hard_gates": hard_gates,
                    "soft_warnings": soft_warnings,
                    "issues": [],
                    "feedback": "",
                    "retries": retries,
                }
                # R-342: record which model actually produced the passing
                # artifact whenever the W5 ladder climbed at least one rung
                # (self.model IS that model already -- escalation mutates it
                # in place). Absent on every non-escalated run (byte-identical
                # verdict shape to pre-R-342).
                if self._ladder_idx > 0:
                    self.state.verdict["escalation_path"] = list(
                        self._ladder_rungs[: self._ladder_idx + 1]
                    )
                self._log("F7", f"PASSED all {len(hard_gates)} hard gates (retries={retries})"
                           + (f", {len(soft_warnings)} soft warnings" if soft_warnings else ""))
                break

            # Gates failed
            retries += 1
            feedback = "HARD GATE FAILURES:\n" + "\n".join(f"- {i}" for i in issues)

            if retries <= max_retries:
                self._log("F7", f"FAILED ({len(issues)} issues), retry {retries}/{max_retries}")
                # Retry: call f6_produce with feedback
                self._timed(
                    f"F6.retry{retries}", lambda fb=feedback: self.f6_produce(retry_feedback=fb)
                )
                # Clean output after retry
                self.state.artifact = self._clean_llm_output(self.state.artifact)
                continue

            # R-342: same-model retries exhausted. Mode B Stage 2 (a known
            # prompt_package on disk, self._mode_b_pkg_path) escalates to the
            # next W5 ladder rung instead of giving up -- re-running F6
            # against the SAME package on a stronger model. Mode A, and any
            # Mode B run that never produced via a package, are UNCHANGED:
            # this block is a no-op and the old give-up verdict below fires
            # exactly as before (byte-identical happy/give-up path).
            if self.mode == "B" and self._mode_b_pkg_path is not None:
                rungs = self._mode_b_ladder_rungs()
                if self._ladder_idx + 1 < len(rungs):
                    prior_model = self.model or "default"
                    self._ladder_idx += 1
                    self.model = rungs[self._ladder_idx]
                    self._log(
                        "F7",
                        "[LADDER] floor-miss on %s after %d retries -> "
                        "escalating to %s" % (prior_model, max_retries, self.model),
                    )
                    pkg_path = self._mode_b_pkg_path
                    self._timed(
                        "F6.ladder%d" % self._ladder_idx,
                        lambda p=pkg_path: self._run_mode_b_generate(p),
                    )
                    self.state.artifact = self._clean_llm_output(self.state.artifact)
                    retries = 0
                    continue

            # Max retries exhausted (ladder unavailable, inactive, or itself
            # exhausted at the terminal rung) -> save as draft with issues.
            # Honest FAIL: no publication below the floor, no infinite loop
            # (the ladder is finite -- see _mode_b_ladder_rungs).
            self.state.verdict = {
                "passed": False,
                "hard_gates": hard_gates,
                "issues": issues,
                "feedback": feedback,
                "retries": retries,
            }
            if self._ladder_idx > 0:
                self.state.verdict["escalation_path"] = list(
                    self._ladder_rungs[: self._ladder_idx + 1]
                )
            self._log("F7", f"FAILED after {max_retries} retries: {issues}")
            break

    # -- Learning Record -----------------------------------------------------

    def _write_learning_record(self) -> None:
        """Capture build outcome as learning_record (delegates to cex_shared)."""
        _shared_write_learning_record(
            kind=self.state.kind,
            intent=self.state.intent,
            verdict=self.state.verdict,
            timings=self.state.timings,
            builder_dir=self.state.builder_dir,
            logger=self._log,
        )

    # -- F8 COLLABORATE -----------------------------------------------------

    def f8_collaborate(self) -> None:
        """Save artifact to file, compile -> state.result."""
        # Write learning record (pre-save, captures build outcome regardless)
        if not self.dry_run:
            self._write_learning_record()

        if self.dry_run:
            # In dry-run, just report the prompt
            out_path = None
            if self.output_dir:
                out_path = Path(self.output_dir) / f"{self.state.kind}_prompt.md"
                out_path.parent.mkdir(parents=True, exist_ok=True)
                out_path.write_text(self.state.artifact, encoding="utf-8")
                self._log("F8", f"prompt saved to {out_path}")

            self.state.result = {
                "path": str(out_path) if out_path else None,
                "compiled": False,
                "committed": False,
                "mode": "dry-run",
                "prompt_words": len(self.state.artifact.split()),
            }
        else:
            # Execute mode: save artifact
            # --- UPDATE MODE: write back to original path ---
            existing = self.state.reasoning.get("_update_existing", {})
            if existing and existing.get("path"):
                out_path = Path(existing["path"])
                out_dir = out_path.parent
                self._log("F8", f"update mode: overwriting {out_path}")
            else:
                out_dir = self.output_dir or (
                    CEX_ROOT / PILLAR_DIRS.get(self.state.pillar, "N00_genesis/P01_knowledge") / "examples"
                )
                out_dir = Path(out_dir)
                out_dir.mkdir(parents=True, exist_ok=True)

                # Generate filename: try to extract id from artifact, fallback to intent slug
                fm_pre = extract_frontmatter_dict(self.state.artifact)
                artifact_id = fm_pre.get("id", "") if fm_pre else ""
                if artifact_id and re.match(r"^[a-z0-9_]+$", str(artifact_id)):
                    filename = f"{artifact_id}.md"
                else:
                    slug = re.sub(r"[^a-z0-9]+", "_", self.state.intent.lower()).strip("_")[:40]
                    filename = f"{self.state.pillar.lower()}_{self.state.kind}_{slug}.md"
                out_path = out_dir / filename

            # Clean code fences from LLM output (safety net -- F7 already cleans)
            art = self._clean_llm_output(self.state.artifact)
            self.state.artifact = art
            out_path.write_text(art, encoding="utf-8")
            self._log("F8", f"artifact saved to {out_path}")

            # Try compile
            compiled = False
            try:
                compile_script = CEX_ROOT / "_tools" / "cex_compile.py"
                if compile_script.exists():
                    subprocess.run(
                        [sys.executable, str(compile_script), str(out_path)],
                        capture_output=True,
                        timeout=30,
                    )
                    compiled = True
            except Exception as e:
                self._log("F8", f"compile skipped: {e}")

            # Re-index after creation (full cycle)
            indexed = False
            try:
                index_script = CEX_ROOT / "_tools" / "cex_index.py"
                if index_script.exists():
                    subprocess.run(
                        [sys.executable, str(index_script)],
                        capture_output=True,
                        timeout=60,
                    )
                    indexed = True
                    self._log("F8", "index rebuilt")
            except Exception as e:
                self._log("F8", f"index skipped: {e}")

            # Auto-commit if gates passed -- gitignore-aware (see cex_git_safe).
            # The naive `git add <path> && git commit` swallowed two failures:
            # (A) a gitignored landing path (.cex/runtime/, **/compiled/, _docs/,
            # _reports/, P10_memory instance files) errored, and (B) "nothing to
            # commit" still set committed=True. safe_artifact_commit partitions
            # ignored paths out (kept on disk, never force-added) and reports
            # `committed` honestly.
            committed = False
            if self.state.verdict.get("passed"):
                # Candidate paths: the artifact + its compiled/ sibling if any.
                commit_paths = [out_path]
                compiled_dir = out_path.parent / "compiled"
                if compiled_dir.exists():
                    commit_paths.append(compiled_dir)
                msg = f"[8F] {self.state.kind}: {self.state.intent[:60]}"
                if _GIT_SAFE_AVAILABLE:
                    res = _safe_artifact_commit(commit_paths, msg)
                    committed = bool(res.get("committed"))
                    if committed:
                        self._log("F8", "auto-committed to git")
                    elif res.get("skipped_ignored"):
                        # Intentionally ephemeral: the file stays on disk for the
                        # collector / N07 to read directly. NOT a failure.
                        self._log(
                            "F8",
                            "commit skipped (gitignored, on disk): "
                            + str(res.get("reason", "")),
                        )
                    else:
                        self._log(
                            "F8",
                            "no commit: " + str(res.get("reason", "")),
                        )
                else:
                    # Fallback if the helper is unavailable: stay HONEST -- only
                    # claim committed=True on a real (non-empty) commit.
                    try:
                        subprocess.run(
                            ["git", "add", "--", str(out_path)],
                            capture_output=True, timeout=10,
                        )
                        cp = subprocess.run(
                            ["git", "commit", "-m", msg, "--", str(out_path)],
                            capture_output=True, timeout=10, text=True,
                        )
                        out = ((cp.stdout or "") + (cp.stderr or "")).lower()
                        committed = (
                            cp.returncode == 0 and "nothing to commit" not in out
                        )
                        if committed:
                            self._log("F8", "auto-committed to git")
                        else:
                            self._log("F8", "no commit (nothing staged)")
                    except Exception as e:
                        self._log("F8", f"auto-commit skipped: {e}")

            # Signal completion
            signaled = False
            if _SIGNAL_AVAILABLE and committed:
                try:
                    nuc = os.environ.get("CEX_NUCLEUS", "n03")
                    _write_signal(nuc, "complete", 8.0,
                                  mission=os.environ.get("CEX_MISSION", ""))
                    signaled = True
                    self._log("F8", f"signal sent: {nuc} complete")
                except Exception as e:
                    self._log("F8", f"signal skipped: {e}")

            # Quality monitor: track build in snapshot
            monitored = False
            if _MONITOR_AVAILABLE and self.state.verdict.get("passed"):
                try:
                    _save_snapshot([{
                        "path": str(out_path),
                        "kind": self.state.kind,
                        "pillar": self.state.pillar,
                        "score": 8.0,  # baseline; peer review adjusts later
                    }])
                    monitored = True
                    self._log("F8", "quality snapshot updated")
                except Exception as e:
                    self._log("F8", f"quality monitor skipped: {e}")

            # NotebookLM auto-upload for knowledge_card artifacts
            notebooklm_uploaded = False
            if committed and self.state.kind == "knowledge_card":
                try:
                    nlm_config_path = CEX_ROOT / ".cex" / "config" / "notebooklm_notebooks.yaml"
                    if nlm_config_path.exists():
                        nlm_cfg = yaml.safe_load(
                            nlm_config_path.read_text(encoding="utf-8")
                        ) or {}
                        if nlm_cfg.get("publish_mode") == "auto":
                            nlm_tool = CEX_ROOT / "_tools" / "cex_notebooklm.py"
                            if nlm_tool.exists():
                                nlm_result = subprocess.run(
                                    [sys.executable, str(nlm_tool),
                                     "--upload", str(out_path)],
                                    capture_output=True, text=True, timeout=120,
                                )
                                if nlm_result.returncode == 0:
                                    notebooklm_uploaded = True
                                    self._log("F8", "NotebookLM auto-upload OK")
                                else:
                                    self._log(
                                        "F8",
                                        "NotebookLM upload failed: "
                                        + nlm_result.stderr[:200],
                                    )
                except Exception as e:
                    self._log("F8", f"NotebookLM upload skipped: {e}")

            # F8 tail: keep the total index incrementally current (R-248
            # consumer half). Non-blocking -- see _update_total_index_tail's
            # docstring for the GDP Q4 WARN-and-skip-on-slow contract. Runs
            # last, regardless of compile/commit/signal/monitor/notebooklm
            # outcome above: the save itself (out_path.write_text, earlier
            # in this branch) already succeeded by the time we reach here.
            self._update_total_index_tail(out_path)

            self.state.result = {
                "path": str(out_path),
                "compiled": compiled,
                "indexed": indexed,
                "committed": committed,
                "signaled": signaled,
                "monitored": monitored,
                "notebooklm": notebooklm_uploaded,
                "mode": "execute",
            }

    # -- F8 tail: total-index incremental update (R-248 consumer half) ------

    def _update_total_index_tail(self, path: Path) -> None:
        """Non-blocking F8 tail: keep the total index (R-245..R-248,
        docs/SPEC_CEXAI_TOTAL_HYDRATION_INDEX_2026_07_03.md Sec 3.1/4.1)
        incrementally current after a successful artifact save, via
        cex_total_index.update_single_file -- the same primitive its own
        `--update-file` CLI verb calls.

        GDP Q4 (closed, spec Sec 5 item 4: "ship with a WARN-and-skip-on-slow
        fallback (degrade-never)"): this call must NEVER fail or slow down a
        build. Any exception, OR wall-clock over the soft budget
        (`_TOTAL_INDEX_SOFT_BUDGET_SECONDS`), logs exactly one [WARN] line
        via the runner's existing `self._log` convention and returns; by the
        time this method runs, the artifact save has ALREADY succeeded and
        is never rolled back or reported as failed because of this step.
        Absent module / absent index -> SILENT skip (the ordinary, expected
        state for a repo that has not run `cex_total_index.py --build` yet
        -- this tail only MAINTAINS an already-built index, it never
        bootstraps one from a single file).
        """
        if not _TOTAL_INDEX_AVAILABLE:
            return  # cex_total_index.py not importable -- silent skip
        try:
            if not _TOTAL_INDEX_META_PATH.exists():
                return  # no total index built yet -- silent skip (ordinary state)
        except OSError:
            return

        t0 = time.perf_counter()
        try:
            _total_index_update_file(str(path))
        except Exception as e:
            self._log("F8", f"[WARN] total-index update skipped: {e}")
            return
        elapsed = time.perf_counter() - t0
        if elapsed > _TOTAL_INDEX_SOFT_BUDGET_SECONDS:
            self._log(
                "F8",
                "[WARN] total-index update exceeded soft budget "
                f"({elapsed:.2f}s > {_TOTAL_INDEX_SOFT_BUDGET_SECONDS}s) -- "
                "continuing (GDP Q4: WARN-and-skip-on-slow, save never blocked)",
            )
        else:
            self._log("F8", f"total-index updated ({elapsed:.3f}s)")

    # -- Mode B: prompt package write/read ------------------------------------

    def _write_prompt_package(self) -> Path:
        """Stage 1 output: write F1-F4 state as a prompt_package .md file."""
        pkg_dir = CEX_ROOT / ".cex" / "runtime" / "packages"
        pkg_dir.mkdir(parents=True, exist_ok=True)

        c = self.state.constraints
        k = self.state.knowledge
        identity = self.state.identity

        fm_lines = [
            "---",
            "package_type: f6_prompt_package",
            "task_id: %s" % self.session_id,
            "target_kind: %s" % self.state.kind,
            "target_pillar: %s" % self.state.pillar,
            "target_nucleus: %s" % os.environ.get("CEX_NUCLEUS", "n07"),
        ]
        pillar_dir = PILLAR_DIRS.get(self.state.pillar, "N00_genesis/P01_knowledge")
        slug = re.sub(r"[^a-z0-9]+", "_", self.state.intent.lower()).strip("_")[:40]
        target_path = "%s/%s_%s.md" % (pillar_dir, self.state.pillar.lower(), slug)
        fm_lines.append("target_path: %s" % target_path)

        iso_count = sum(1 for v in k.values() if v and isinstance(v, str))
        fm_lines.append("builder_isos_loaded: %d" % iso_count)
        fm_lines.append("context_sources: %d" % len(k.get("kc_domains", [])))
        fm_lines.append("density_target: 0.85")
        fm_lines.append("max_bytes: %s" % c.get("max_bytes", 8192))
        # 8F decompose schema (matches tpl_prompt_package.md):
        fm_lines.append("stage: 1")
        fm_lines.append(
            "stage_2_model_hint: %s"
            % os.environ.get("CEX_DECOMPOSE_STAGE2_MODEL", "claude-haiku-4-5-20251001")
        )
        fm_lines.append("mode: B")
        fm_lines.append("---")

        body_parts = []

        sp = identity.get("system_prompt", "")
        if sp:
            body_parts.append("## IDENTITY (from F2 BECOME)\n\n%s" % sp[:2000])

        constraint_lines = []
        if c.get("max_bytes"):
            constraint_lines.append("- Max body size: %s bytes" % c["max_bytes"])
        if c.get("id_pattern"):
            constraint_lines.append("- ID pattern: `%s`" % c["id_pattern"])
        if c.get("frontmatter_required"):
            constraint_lines.append(
                "- Required frontmatter: %s" % ", ".join(c["frontmatter_required"])
            )
        if c.get("boundary"):
            constraint_lines.append("- Boundary: %s" % c["boundary"])
        constraint_lines.append("- quality: null (NEVER self-score)")
        if constraint_lines:
            body_parts.append("## CONSTRAINTS (from F1)\n\n" + "\n".join(constraint_lines))

        ctx_parts = []
        if k.get("kc_builder"):
            ctx_parts.append("### Builder knowledge:\n%s" % k["kc_builder"][:1500])
        for kc_d in k.get("kc_domains", [])[:3]:
            ctx_parts.append("### Domain knowledge:\n%s" % str(kc_d)[:1000])
        if k.get("domain_context"):
            ctx_parts.append("### Injected context:\n%s" % k["domain_context"][:1500])
        if ctx_parts:
            body_parts.append("## CONTEXT (from F3 INJECT)\n\n" + "\n\n".join(ctx_parts))

        plan = self.state.reasoning.get("plan", "")
        if plan:
            body_parts.append("## PLAN (from F4 REASON)\n\n%s" % plan[:2000])

        bdir = self.state.builder_dir
        if bdir:
            tpl_text = load_iso(bdir, "bld_output", self.kind_slug)
            if tpl_text:
                body_parts.append(
                    "## TEMPLATE (generate this artifact)\n\n%s"
                    % strip_frontmatter(tpl_text)[:3000]
                )

        task_lines = [
            "**Intent**: %s" % self.state.intent,
            "**Kind**: %s" % self.state.kind,
            "**Pillar**: %s" % self.state.pillar,
            "**Quality**: set quality: null (NEVER self-score)",
            "",
            "## CRITICAL OUTPUT RULES",
            "1. Output ONLY the artifact. NO preamble, NO explanation.",
            "2. Start with exactly `---` on the first line.",
            "3. Then YAML frontmatter (id, kind, pillar, title, version, quality: null, tags).",
            "4. Then `---` to close frontmatter.",
            "5. Then Markdown body with ## sections.",
            "6. Do NOT wrap in code fences.",
        ]
        body_parts.append("## TASK\n\n" + "\n".join(task_lines))

        content = "\n".join(fm_lines) + "\n\n" + "\n\n".join(body_parts) + "\n"
        pkg_filename = "pp_%s_%s.md" % (self.state.kind, self.session_id)
        pkg_path = pkg_dir / pkg_filename
        pkg_path.write_text(content, encoding="utf-8")
        self._log("pkg", "prompt_package written: %s (%d bytes)" % (pkg_path.name, len(content)))
        return pkg_path

    def _run_mode_b_generate(self, pkg_path: Path) -> None:
        """Stage 2: read prompt_package, call cheap model for F6 only."""
        # R-342: remember the package path so F7's ladder escalation can
        # re-invoke this SAME method (against the SAME package) on a
        # stronger model after a floor-miss. Set unconditionally -- harmless
        # idempotent overwrite when this is itself an escalation re-run.
        self._mode_b_pkg_path = pkg_path
        pkg_content = pkg_path.read_text(encoding="utf-8")

        target_path = ""
        tp_match = re.search(r"^target_path:\s*(.+)$", pkg_content, re.MULTILINE)
        if tp_match:
            target_path = tp_match.group(1).strip()

        # R-336/DP2c: recover max_bytes from the package header -- F1 never
        # ran in THIS process for a --stage 2-only dispatch, so self.state.
        # constraints is empty here; the package (written by _write_prompt_
        # package's "max_bytes: %s" line) is the only source available.
        max_bytes_val = 0
        mb_match = re.search(r"^max_bytes:\s*(\d+)$", pkg_content, re.MULTILINE)
        if mb_match:
            max_bytes_val = int(mb_match.group(1))

        body_start = pkg_content.find("---", 3)
        if body_start > 0:
            prompt = pkg_content[body_start + 3:].strip()
        else:
            prompt = pkg_content

        self._log("F6.B", "Mode B generate: sending package to %s" % (self.model or "default"))

        if self.dry_run:
            self.state.artifact = prompt
            self.state.result = {
                "mode": "dry-run",
                "pipeline_mode": "B",
                "prompt_package": str(pkg_path),
                "prompt_words": len(prompt.split()),
            }
        else:
            response = execute_prompt(
                prompt, model_override=self.model,
                max_tokens=_max_tokens_from_bytes(max_bytes_val),
            )
            self.state.artifact = response
            self._log("F6.B", "response received (%d chars)" % len(response))

            if target_path and not self.output_dir:
                tp = CEX_ROOT / target_path
                self.output_dir = str(tp.parent)

    # -- run() pipeline -----------------------------------------------------

    def run(self, stop_at: int | None = None) -> RunState:
        """Execute pipeline based on mode.

        Mode A (monolithic): F1->F2->F3->F4->F5->F6->F7->F8
        Mode B (decomposed):
          Stage 1 (first pass): F1->F2->F3->F4 -> write prompt_package
          Stage 2 (--execute):  read package -> F6 -> F7 -> F8
        """
        if self.mode == "B":
            return self._run_mode_b(stop_at)
        return self._run_mode_a(stop_at)

    def _run_mode_a(self, stop_at: int | None = None) -> RunState:
        """Mode A: monolithic F1-F8 (unchanged behavior)."""
        steps = [
            ("F1", self.f1_constrain),
            ("F2", self.f2_become),
            ("F3", self.f3_inject),
            ("F4", self.f4_reason),
            ("F5", self.f5_call),
            ("F6", self.f6_produce),
            ("F7", self.f7_govern),
            ("F8", self.f8_collaborate),
        ]

        for step_num, (name, func) in enumerate(steps, 1):
            self._timed(name, func)
            if stop_at and step_num >= stop_at:
                self._log("run", "stopped at step %d (--step %d)" % (step_num, stop_at))
                break

        return self.state

    def _run_mode_b(self, stop_at: int | None = None) -> RunState:
        """Mode B: decomposed pipeline."""
        if self.prompt_package_path:
            pkg = Path(self.prompt_package_path)
            if not pkg.exists():
                self.state.errors.append("prompt_package not found: %s" % pkg)
                return self.state

            self._log("run.B", "Stage 2: generating from package %s" % pkg.name)
            self._timed("F6.B", lambda: self._run_mode_b_generate(pkg))

            if not self.dry_run:
                self._timed("F7", self.f7_govern)
                self._timed("F8", self.f8_collaborate)
        else:
            stage1_steps = [
                ("F1", self.f1_constrain),
                ("F2", self.f2_become),
                ("F3", self.f3_inject),
                ("F4", self.f4_reason),
            ]
            for step_num, (name, func) in enumerate(stage1_steps, 1):
                self._timed(name, func)
                if stop_at and step_num >= stop_at:
                    self._log("run.B", "stopped at step %d" % step_num)
                    return self.state

            pkg_path = self._write_prompt_package()
            self.state.result = {
                "mode": "stage1",
                "pipeline_mode": "B",
                "prompt_package": str(pkg_path),
                "prompt_words": len(pkg_path.read_text(encoding="utf-8").split()),
            }
            self._log("run.B", "Stage 1 complete. Package: %s" % pkg_path)

            if not self.dry_run:
                self._log("run.B", "Stage 2: auto-generating from package")
                self._timed("F6.B", lambda: self._run_mode_b_generate(pkg_path))
                self._timed("F7", self.f7_govern)
                self._timed("F8", self.f8_collaborate)

        return self.state


# --- CLI: list-kinds ---


def list_kinds():
    """Print all available kinds grouped by pillar."""
    by_pillar: dict[str, list[tuple[str, str]]] = {}
    seen = set()
    for _keyword, kinds_list in sorted(OBJECT_TO_KINDS.items()):
        for kind, pillar, fn in kinds_list:
            key = (kind, pillar)
            if key not in seen:
                seen.add(key)
                by_pillar.setdefault(pillar, []).append((kind, fn))

    print("\n=== CEX Kinds (8F Runner) ===\n")
    for pillar in sorted(by_pillar.keys()):
        kinds = sorted(by_pillar[pillar], key=lambda x: x[0])
        print(f"\n  {pillar}:")
        for kind, fn in kinds:
            bdir = find_builder_dir(kind)
            has = "+" if bdir else " "
            print(f"    {has} {kind:<30s} [{fn}]")
    print(f"\n  Total: {len(seen)} kinds")
    print("  + = builder exists in archetypes/builders/\n")


# --- CLI: banner ---


def print_banner(state: RunState, elapsed_ms: float) -> None:
    """Print compact run summary."""
    sep = "=" * 70
    mode = "DRY-RUN" if state.result.get("mode") == "dry-run" else "EXECUTE"
    c, k, v = state.constraints, state.knowledge, state.verdict
    lines = [
        f"\n{sep}",
        f"  CEX 8F Runner | {state.kind} | {state.pillar} | {mode}",
        sep,
        f"  Intent:  {state.intent}",
        f"  Builder: {state.builder_dir or 'NONE'}",
    ]
    c_parts = ([f"max={c['max_bytes']}b"] if c.get("max_bytes") else [])
    if c.get("frontmatter_required"):
        c_parts.append(f"fm={len(c['frontmatter_required'])} fields")
    if c_parts:
        lines.append(f"  Constrain: {', '.join(c_parts)}")
    k_parts = [label for key, label in [("kc_builder", "builder-KC"), ("few_shots", "examples"), ("memory", "memory")] if k.get(key)]
    if k.get("kc_domains"):
        k_parts.insert(1, f"{len(k['kc_domains'])} KCs")
    if k.get("build_memory"):
        k_parts.append("memory")
    if k.get("semantic_matches"):
        k_parts.append("retriever")
    if k.get("repo_map_digest"):
        k_parts.append("repo-map")
    if k_parts:
        lines.append(f"  Knowledge: {', '.join(k_parts)}")
    if state.artifact:
        lines.append(f"  Artifact: {len(state.artifact.split())} words")
    if v:
        g = v.get("hard_gates", [])
        ok = sum(1 for x in g if x.get("passed"))
        lines.append(f"  Verdict:  {'PASS' if v.get('passed') else 'FAIL'} ({ok}/{len(g)} gates, {v.get('retries', 0)} retries)")
        lines.extend(f"    ! {issue}" for issue in v.get("issues", []))
    if state.result.get("path"):
        lines.append(f"  Output:   {state.result['path']}")
    if state.timings:
        lines.append(f"  Timing:   {' | '.join(f'{tk}={tv}ms' for tk, tv in state.timings.items())} | total={elapsed_ms:.0f}ms")
    lines.extend(f"  ! ERROR: {err}" for err in state.errors)
    lines.append(sep)
    print("\n".join(lines))


# --- Main ---


NUC_DIRS = {
    "N01": "N01_intelligence", "N02": "N02_marketing", "N03": "N03_engineering",
    "N04": "N04_knowledge", "N05": "N05_operations", "N06": "N06_commercial",
    "N07": "N07_admin",
}
NUC_DOMAINS = {
    "N01": "research, intelligence, papers, benchmarks",
    "N02": "copywriting, ads, campaigns, social media",
    "N03": "meta-construction, 8F pipeline, scaffolding",
    "N04": "RAG, embeddings, chunking, taxonomy",
    "N05": "testing, CI/CD, deployment, monitoring",
    "N06": "pricing, sales funnels, monetization",
    "N07": "orchestration, dispatch, quality validation",
}
KIND_TO_SUBDIR = {
    "agent": "agents", "knowledge_card": "knowledge", "dispatch_rule": "orchestration",
    "workflow": "orchestration", "quality_gate": "feedback", "embedding_config": "knowledge",
    "rag_source": "knowledge", "chunk_strategy": "knowledge", "retriever_config": "knowledge",
    "checkpoint": "memory", "spawn_config": "orchestration", "prompt_template": "prompts",
    "action_prompt": "prompts", "system_prompt": "prompts", "scoring_rubric": "quality",
    "signal": "orchestration", "dag": "orchestration", "handoff": "orchestration",
    "fallback_chain": "agents", "pattern": "architecture", "agent_card": "architecture",
}


def _resolve_nucleus(nucleus: str, kind_override: str | None, intent: str) -> tuple[str, str]:
    """Resolve nucleus output dir and domain context."""
    nuc = nucleus.upper()
    if nuc not in NUC_DIRS:
        return "", ""
    kind_for_dir = kind_override or ""
    if not kind_for_dir:
        parsed = parse_intent(intent)
        if parsed.get("objects"):
            kind_for_dir = parsed["objects"][0]
    subdir = KIND_TO_SUBDIR.get(kind_for_dir, "artifacts")
    output_dir = str(CEX_ROOT / NUC_DIRS[nuc] / subdir)
    ctx = f"Nucleus: {nuc} ({NUC_DIRS[nuc]}). Domain: {NUC_DOMAINS.get(nuc, '')}. All content must be specific to this nucleus domain."
    return output_dir, ctx


def _default_nucleus_from_env(explicit_nucleus: str | None) -> str:
    """R-094 fix: which nucleus (if any) `main()` should fall back to when the caller did NOT
    pass `--nucleus` explicitly.

    Before this, an absent `--nucleus`/`--output-dir` always fell through to the pillar-only
    default (`PILLAR_DIRS.get(pillar, "N00_genesis/P01_knowledge")` in f8_collaborate) -- even when
    the calling PROCESS was itself a booted nucleus session. Every `boot/n0X*.ps1` sets
    `CEX_NUCLEUS=N0X` in its environment (verified: `boot/n01.ps1:102`, ..., `boot/n07.ps1` and the
    codex/gemini/litellm/ollama siblings) -- see `N01_intelligence/P10_memory/procedural_memory_n01.md`'s
    R-094 finding for the file:line evidence (`cex_8f_runner.py` PILLAR_DIRS/`_resolve_nucleus`
    ~line 1893-1895 / ~2439-2452) that a plain `/build` call with no `--nucleus` silently wrote into
    `N00_genesis/P01_knowledge/examples/` instead of the booted nucleus's own tree.

    Returns the upper-cased nucleus code (e.g. "N01") to feed into `_resolve_nucleus`, or "" when no
    fallback should apply:
      - `explicit_nucleus` already given -> "" (caller has an explicit value, nothing to add).
      - `CEX_NUCLEUS` unset/blank -> "" (unchanged legacy default: N00_genesis).
      - `CEX_NUCLEUS=N07` -> "" (N07 is the orchestrator and never builds directly, RACI matrix;
        it is also the value EVERY tenant boot script hardcodes for its single in-session-persona
        process -- so this fallback deliberately does NOT change tenant-persona routing behavior;
        that residual gap needs a command/prompt-layer fix, not a code default, and stays open).
      - anything else not in NUC_DIRS (unset/garbage) -> "" (degrade-never).
      - a real N01-N06 value -> that value (the actual fix: a booted nucleus process calling this
        runner directly, without remembering --nucleus, now lands in ITS OWN tree).
    """
    if explicit_nucleus:
        return ""
    env_val = os.environ.get("CEX_NUCLEUS", "").strip().upper()
    if not env_val or env_val == "N07" or env_val not in NUC_DIRS:
        return ""
    return env_val


def main() -> None:
    parser = argparse.ArgumentParser(description="cex_8f_runner.py -- 8F Stateful Artifact Pipeline")
    parser.add_argument("intent", nargs="?", help="Natural language intent")
    parser.add_argument("--kind", help="Override kind classification (skip Motor)")
    parser.add_argument("--dry-run", action="store_true", help="Preview prompt without LLM (default)")
    parser.add_argument("--execute", action="store_true", help="Call LLM to produce artifact")
    parser.add_argument("--list-kinds", action="store_true", help="Print all available kinds")
    parser.add_argument("--verbose", action="store_true", help="Show per-F details")
    parser.add_argument("--step", type=int, metavar="N", help="Stop after function N (1-8)")
    parser.add_argument("--output-dir", metavar="DIR", help="Save outputs to this directory")
    parser.add_argument("--nucleus", metavar="N0X", help="Target nucleus (e.g. N01, N05)")
    parser.add_argument("--context", metavar="TEXT", help="Domain context to inject")
    parser.add_argument("--context-file", metavar="FILE", help="Read domain context from file (safer than --context for untrusted content)")
    parser.add_argument("--model", metavar="MODEL",
                        help="Model override (e.g. 'ollama/qwen3:8b', 'claude-sonnet-4-6')")
    parser.add_argument("--update", metavar="FILE",
                        help="Diff-aware update: read existing artifact, produce delta merge "
                             "preserving human edits and scores")
    parser.add_argument("--force", action="store_true",
                        help="Allow >60%% rewrite in --update mode (bypass rewrite guard)")
    parser.add_argument("--mode", choices=["auto", "A", "B"], default="auto",
                        help="8F pipeline mode: A=monolithic F1-F8, B=decomposed (F6 only from prompt package), auto=detect from model tier")
    parser.add_argument("--prompt-package", metavar="FILE",
                        help="Path to pre-compiled prompt_package for Mode B Stage 2 (skip F1-F4)")
    parser.add_argument("--stage", type=int, choices=[1, 2, 3], default=None,
                        help="Decomposed stage selector for cex_decompose.py: "
                             "1=write prompt_package (F1-F4 only), "
                             "2=consume prompt_package and run F6, "
                             "3=F7+F8 only (deterministic).")
    parser.add_argument("--with-repo-map", action="store_true", default=None,
                        help="R-304: inject a ranked-symbol digest (cex_repo_map.py, "
                             "ast+pagerank) into F3 INJECT. Default OFF (also settable "
                             "via env CEX_F3_REPO_MAP=1). Adds several seconds (corpus scan "
                             "over _tools/, cex_sdk/) -- advisory only, never load-bearing.")
    args = parser.parse_args()

    # --- --stage selector: maps to --mode B + --step (Mode B already exists) ---
    # Stage 1 -> Mode B, stop after F4 (--step 4), produce prompt_package, no execute
    # Stage 2 -> Mode B with --prompt-package present, --execute, run F6+F7+F8
    # Stage 3 -> deterministic (F7+F8 only); covered by cex_decompose stage_3 function,
    #           but if invoked here we degrade to: do nothing if no artifact context,
    #           or run F7+F8 on the prior session state (advanced use)
    if args.stage is not None:
        # Decomposed stages always imply Mode B
        args.mode = "B"
        if args.stage == 1:
            # F1-F4 then write prompt_package. Do NOT set args.step here:
            # _run_mode_b uses an early-return on stop_at that fires before
            # the write_prompt_package() call. Letting the loop run through
            # all 4 stage1_steps falls through to the write naturally.
            # The dry_run guard at line ~1956 prevents Stage 2 auto-execution.
            pass
        elif args.stage == 2:
            if not args.prompt_package:
                print("ERROR: --stage 2 requires --prompt-package FILE", file=sys.stderr)
                sys.exit(2)
            if not args.execute:
                args.execute = True
        elif args.stage == 3:
            # Stage 3 is deterministic (F7+F8): cex_decompose.py invokes tools directly.
            # When called here without prompt_package or artifact, just print a notice
            # (cex_decompose orchestrates the real Stage 3 via cex_doctor + cex_compile).
            print("[8f_runner] --stage 3 is a no-op here; cex_decompose.py runs F7+F8 deterministically via tools.", file=sys.stderr)
            sys.exit(0)

    if args.list_kinds:
        list_kinds()
        return
    if not args.intent and not args.kind and not args.prompt_package:
        # Stage 2 dispatch flows pass --prompt-package without an intent;
        # the runner derives target_kind from the package frontmatter.
        parser.print_help()
        sys.exit(1)

    # Stage 2: hydrate kind/intent from prompt_package frontmatter when
    # the dispatcher passed only --prompt-package. Without this, downstream
    # parse_intent() runs on "create None" and the EightFRunner ends up with
    # kind=None which breaks classification + output path resolution.
    if args.prompt_package and not args.kind and not args.intent:
        try:
            pkg_text = Path(args.prompt_package).read_text(encoding="utf-8")
            tk_match = re.search(r"^target_kind:\s*(\S+)", pkg_text, re.MULTILINE)
            if tk_match:
                args.kind = tk_match.group(1).strip()
            tn_match = re.search(r"^# Task for \S+:\s*(.+)$", pkg_text, re.MULTILINE)
            if tn_match:
                args.intent = tn_match.group(1).strip()
        except (OSError, UnicodeDecodeError):
            pass

    intent = args.intent or f"create {args.kind}"
    context = args.context or ""
    if not context and args.context_file:
        with open(args.context_file, encoding="utf-8") as f:
            context = f.read()
    if args.nucleus:
        output_dir, nuc_context = _resolve_nucleus(args.nucleus, args.kind, intent)
        if not args.output_dir:
            args.output_dir = output_dir
        if not context:
            context = nuc_context
    elif not args.output_dir:
        # R-094: no explicit --nucleus/--output-dir -- fall back to CEX_NUCLEUS (set by every
        # boot/n0X*.ps1) so a booted nucleus session invoking this runner directly still lands in
        # its OWN tree instead of silently defaulting to N00_genesis. See
        # _default_nucleus_from_env's docstring for the full contract (N07/tenant-persona
        # excluded on purpose).
        env_nucleus = _default_nucleus_from_env(args.nucleus)
        if env_nucleus:
            output_dir, nuc_context = _resolve_nucleus(env_nucleus, args.kind, intent)
            if output_dir:
                args.output_dir = output_dir
                if not context:
                    context = nuc_context

    parsed = parse_intent(intent)
    classified = classify_objects(parsed["objects"]) if not args.kind else []
    if len(classified) > 1:
        print(f"\n  Multi-kind detected: {len(classified)} kinds")
        for i, c in enumerate(classified):
            print(f"    [{i + 1}] {c['kind']} (pillar={c['pillar']})")
    kinds_to_run = [c["kind"] for c in classified] if len(classified) > 1 else [args.kind]

    for kind_i, kind in enumerate(kinds_to_run):
        if len(kinds_to_run) > 1:
            print(f"\n{'#' * 70}\n  Multi-kind [{kind_i + 1}/{len(kinds_to_run)}]: {kind}\n{'#' * 70}")
        runner = EightFRunner(
            intent=intent, context=context, kind=kind,
            dry_run=not args.execute, verbose=args.verbose, output_dir=args.output_dir,
            model=getattr(args, "model", "") or "",
            update_path=getattr(args, "update", "") or "",
            force_rewrite=getattr(args, "force", False),
            mode=args.mode,
            prompt_package_path=getattr(args, "prompt_package", "") or "",
            with_repo_map=getattr(args, "with_repo_map", None),
        )
        t0 = time.perf_counter()
        state = runner.run(stop_at=args.step)
        print_banner(state, (time.perf_counter() - t0) * 1000)
        if state.artifact:
            if state.result.get("mode") == "dry-run":
                print(f"--- STRUCTURED PROMPT (8F) ---\n\n{state.artifact}\n\n--- END ({len(state.artifact.split())} words) ---")
            else:
                print(f"--- ARTIFACT ---\n\n{state.artifact[:2000]}")
                if len(state.artifact) > 2000:
                    print(f"\n... (truncated, full: {len(state.artifact)} chars)")


if __name__ == "__main__":
    try:
        from cex_agent_io import wrap_main

        def _main_wrapper(argv):
            sys.argv = [sys.argv[0]] + argv
            main()
            return 0

        sys.exit(wrap_main(_main_wrapper, sys.argv[1:], label="cex_8f_runner"))
    except ImportError:
        main()
