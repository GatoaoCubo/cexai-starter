#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""CEX Doctor v3.0 -- 12-Pillar ISO Architecture + Density + Completeness.

Usage:
  python _tools/cex_doctor.py          # diagnose only
  python _tools/cex_doctor.py --fix    # diagnose + auto-fix naming issues

R-162 CHECK REGISTRY WIRING (2026-07-03, ADDITIVE):
  The default run also executes the typed pluggable check registry
  (_tools/cex_check_registry.py -- 16 plugins today, growing per R-162) and
  prints its findings in a trailing "CHECK REGISTRY (advisory)" section.
  Degrade-never: any import/execution error in the registry pass is swallowed
  -- the doctor's own 12-pillar checks are never affected by it.

R-162 PROMOTION (2026-07-12, GDP-closed -- see
docs/FOUNDER_DESK_R162_PROMOTION_CALL_2026_07_12.md):
  The founder promoted exactly 7 zero-legacy-debt plugins from advisory to
  BLOCKING, DEFAULT-ON (see PROMOTED_PLUGINS below for the frozen set + the
  full rationale). The fold is SET-scoped, not severity-scoped: a failing
  PROMOTED plugin flips the exit code regardless of its declared severity
  (e.g. counter_gate is MEDIUM and still folds); a failing NON-promoted
  plugin never folds by default, regardless of severity (e.g. registry_drift
  is HIGH but carries known, counted legacy debt the founder chose not to
  enforce yet -- it stays advisory). Three flags govern the registry pass's
  effect on the exit code:
    (default, no flag)  fold the exit code iff a PROMOTED plugin is failing
                         (see PROMOTED_PLUGINS) -- default-on since 2026-07-12
    --plugins-strict     ADDITIONALLY fold ANY failing BLOCKING/HIGH finding
                          into the exit code, promoted or not (pre-existing,
                          UNCHANGED severity-scoped opt-in escalation -- e.g.
                          this still flips on registry_drift's known debt)
    --no-plugins-strict  ESCAPE HATCH: force the registry pass back to pure
                          advisory-only (never folds, overrides both of the
                          above) -- the 1-line rollback the brief promises
    --json                additionally print a trailing JSON block with a
                          "check_registry" summary + findings key (does not
                          replace the normal text report)
"""

import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Any

import yaml

# R-196 backport: reuse cex_shared's line-anchored frontmatter helpers instead of
# the local `.index("---", 3)` substring scan (which mistakes a '---' occurring
# INSIDE a value, a table divider, or a horizontal rule for the closing fence).
sys.path.insert(0, str(Path(__file__).resolve().parent))
from cex_shared import _frontmatter_close_index, parse_frontmatter

ROOT = Path(__file__).resolve().parent.parent
BUILDERS_DIR = ROOT / "archetypes" / "builders"
LIBRARY_DIR = ROOT / "N00_genesis" / "P01_knowledge" / "library"
FIX_MODE = "--fix" in sys.argv
# R-162: module-level fallback mirrors FIX_MODE's pattern above, for callers that
# invoke main() directly (e.g. `import cex_doctor; cex_doctor.main()`) without
# going through _doctor_cli()'s argparse pass. Both default to False/off.
PLUGINS_STRICT = "--plugins-strict" in sys.argv
JSON_MODE = "--json" in sys.argv
# R-162 PROMOTION (2026-07-12): same module-level-fallback pattern as PLUGINS_STRICT
# above -- the --no-plugins-strict escape hatch. See PROMOTED_PLUGINS and
# _check_promoted_fold_exit() further down for the full mechanic.
NO_PLUGINS_STRICT = "--no-plugins-strict" in sys.argv

# -- Constants ----------------------------------------------------------------

EXPECTED_KINDS = [
    "architecture",
    "config",
    "eval",
    "feedback",
    "knowledge",
    "memory",
    "model",
    "orchestration",
    "output",
    "prompt",
    "schema",
    "tools",
]
EXPECTED_COUNT = len(EXPECTED_KINDS)  # 12
# =============================================================================
# Size gate -- strategic limits aligned with multi-runtime token economy
# =============================================================================
#
# DECISION: 8 KiB regular / 10 KiB prompt ISOs
#
# Multi-runtime safety analysis:
#   Smallest practical runtime context = 32K tokens (Ollama mid-tier setups).
#   Fixed overhead (system prompt + .claude/rules + reasoning buffer) ~= 10K.
#   Available for ISO loading: ~22K tokens.
#   Typical 8F peak load: 6-8 ISOs simultaneously.
#
# At 8 KiB / ~2K tokens per ISO:
#   - 10 ISOs fit in 22K window (covers peak load with margin)
#   - Aligned with Anthropic/OpenAI ~2K-token system-prompt guidance
#   - User mods get ~1 KiB headroom over current 3.9 KiB avg
#
# Distribution context (3,647 ISOs, post-v1.0.0):
#   p50 = 3,536B | p95 = 6,180B | p99 = 6,778B | max = 7,941B
#
# 8 KiB limit catches only true outliers (>8KB) while accommodating
# natural growth as kinds are enriched and users extend artifacts.
#
# bld_prompt_*.md gets 10 KiB because reasoning_trace + workflow_primitive
# legitimately need more room for trace examples / chain-of-thought blocks.
#
# History: started at 6,144B (rigid, flagged 144 normal files); bumped to
# 7,168B during v1.0.0 self-eval; settled at 8,192B after multi-runtime
# token budget analysis.
# =============================================================================
MAX_BYTES = 8192          # 8 KiB regular ISOs (~2K tokens)
MAX_BYTES_PROMPT = 10240  # 10 KiB prompt ISOs (~2.5K tokens)

# Old ISO names that should no longer exist (migration residue check)
OLD_ISO_NAMES = [
    "manifest", "system_prompt", "instruction", "knowledge_card",
    "output_template", "quality_gate", "examples", "collaboration",
]
# Density floor calibrated against actual distribution (3,646 ISOs):
#   p5 = 0.803 | p10 = 0.815 | p50 = 0.882 | min = 0.773
# Floor 0.75 catches truly sparse files (>25% blank lines) while accommodating
# standard markdown style (blank lines before headers, around code blocks,
# before Related Artifacts table). At 0.75: zero files flagged, gate stays
# meaningful for future bloat detection.
MIN_DENSITY = 0.75
NAMING_RE = re.compile(r"^bld_[a-z][a-z0-9_]+_[a-z][a-z0-9_]+\.md$")

# -- Helpers ------------------------------------------------------------------


def get_frontmatter(path: Path) -> dict[str, Any] | None:
    """Return parsed YAML frontmatter dict, or None if missing/invalid.

    R-196: delegates to cex_shared.parse_frontmatter (line-anchored close-fence
    scan) instead of `text.index("---", 3)`, which closed on the first '---'
    SUBSTRING anywhere -- including one embedded inside a quoted value or a
    markdown table divider -- truncating or corrupting the parsed frontmatter.
    """
    try:
        text = path.read_text(encoding="utf-8", errors="ignore")
        return parse_frontmatter(text)
    except Exception:
        pass
    return None


def calc_density(path: Path) -> float:
    """Return density ratio (0.0-1.0): content lines / total lines.

    Filler = empty lines, whitespace-only, bare separators (---).
    Frontmatter block is excluded from calculation.
    """
    try:
        text = path.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return 0.0

    # Strip frontmatter (R-196: line-anchored close-fence scan, not a '---'
    # substring search -- see get_frontmatter's docstring for the failure mode
    # this replaces).
    body = text
    if text.startswith("---"):
        end = _frontmatter_close_index(text)
        if end >= 0:
            body = text[end + 3 :].lstrip("\n")

    lines = body.splitlines()
    if not lines:
        return 0.0

    content = 0
    for line in lines:
        stripped = line.strip()
        if stripped and stripped != "---":
            content += 1

    return content / len(lines)


def extract_topic_from_dir(dirname: str) -> str:
    """Convert builder dir name to expected topic suffix.

    'agent-builder' -> 'agent'
    'knowledge-card-builder' -> 'knowledge_card'
    'agent-package-builder' -> 'agent_package'
    """
    name = dirname
    if name.endswith("-builder"):
        name = name[: -len("-builder")]
    elif name.endswith("_builder"):
        name = name[: -len("_builder")]
    return name.replace("-", "_")


def expected_filename(kind: str, topic: str) -> str:
    return f"bld_{kind}_{topic}.md"


def parse_bld_filename(filename: str) -> tuple[str, str] | None:
    """Parse bld_{kind}_{topic}.md -> (kind, topic) or None."""
    if not filename.startswith("bld_") or not filename.endswith(".md"):
        return None
    stem = filename[4:-3]  # strip bld_ and .md
    # Match against known kinds (longest first to handle multi-word kinds)
    for kind in sorted(EXPECTED_KINDS, key=len, reverse=True):
        if stem.startswith(kind + "_"):
            topic = stem[len(kind) + 1 :]
            return (kind, topic)
    return None


# -- Checks -------------------------------------------------------------------


class CheckResult:
    def __init__(self, builder_name: str) -> None:
        self.name = builder_name
        self.naming = "PASS"
        self.density = "PASS"
        self.max_bytes = "PASS"
        self.completeness = "PASS"
        self.frontmatter = "PASS"
        self.h_related = "PASS"
        self.details = []

    @property
    def overall(self) -> str:
        statuses = [self.naming, self.density, self.max_bytes, self.completeness, self.frontmatter, self.h_related]
        if "FAIL" in statuses:
            return "FAIL"
        warn_count = statuses.count("WARN")
        if warn_count >= 3:
            return "FAIL"
        if warn_count > 0:
            return "WARN"
        return "PASS"


def check_builder(builder_dir: Path) -> CheckResult:
    """Run all checks on a single builder directory."""
    r = CheckResult(builder_dir.name)
    topic = extract_topic_from_dir(builder_dir.name)

    # Gather all bld_*.md files
    bld_files = sorted(builder_dir.glob("bld_*.md"))
    bld_names = {f.name for f in bld_files}

    # -- CHECK 1: 13-file completeness ----------------------------------------
    expected = {expected_filename(k, topic) for k in EXPECTED_KINDS}
    missing = expected - bld_names
    extra = bld_names - expected

    if missing:
        r.completeness = "FAIL"
        r.details.append(
            f"  missing {len(missing)}: {', '.join(sorted(missing)[:3])}"
            + (f" +{len(missing) - 3}" if len(missing) > 3 else "")
        )
    if extra:
        # Extra files might be naming issues, not necessarily wrong
        pass

    actual_count = len(bld_files)
    if actual_count != EXPECTED_COUNT and not missing:
        r.completeness = "WARN"
        r.details.append(f"  has {actual_count} bld_*.md (expected {EXPECTED_COUNT})")

    # -- CHECK 2: Naming ------------------------------------------------------
    naming_issues = []
    fix_renames = []
    for f in bld_files:
        if not NAMING_RE.match(f.name):
            naming_issues.append(f.name)
            continue
        parsed = parse_bld_filename(f.name)
        if not parsed:
            naming_issues.append(f"{f.name} (unknown kind)")
        elif parsed[1] != topic:
            naming_issues.append(f"{f.name} (topic '{parsed[1]}' != '{topic}')")
            # Potential fix: rename to correct topic
            correct = expected_filename(parsed[0], topic)
            fix_renames.append((f, builder_dir / correct))

    if naming_issues:
        r.naming = "WARN"
        for ni in naming_issues[:3]:
            r.details.append(f"  naming: {ni}")

    if FIX_MODE and fix_renames:
        for src, dst in fix_renames:
            if not dst.exists():
                src.rename(dst)
                r.details.append(f"  FIXED: {src.name} -> {dst.name}")

    # -- CHECK 3: Density -----------------------------------------------------
    # Compare with 2-decimal rounding so files that DISPLAY as min-threshold
    # don't fail due to floating-point noise (e.g. 0.7796 displays as 0.78
    # but raw float < 0.78 fails the gate -- pure UX inconsistency).
    low_density = []
    for f in bld_files:
        d = calc_density(f)
        if round(d, 2) < MIN_DENSITY:
            low_density.append((f.name, d))

    if low_density:
        r.density = "WARN" if len(low_density) <= 3 else "FAIL"
        for fname, d in low_density[:3]:
            r.details.append(f"  density: {fname} = {d:.2f} (min {MIN_DENSITY})")

    # -- CHECK 4: Max bytes ---------------------------------------------------
    oversized = []
    for f in bld_files:
        size = f.stat().st_size
        limit = MAX_BYTES_PROMPT if f.name.startswith("bld_prompt_") else MAX_BYTES
        if size > limit:
            oversized.append((f.name, size, limit))

    if oversized:
        r.max_bytes = "WARN"
        for fname, sz, limit in oversized[:3]:
            r.details.append(f"  size: {fname} = {sz}B (max {limit})")

    # -- CHECK 5a: Old ISO residue (migration check) --------------------------
    old_residue = []
    for f in bld_files:
        parsed = parse_bld_filename(f.name)
        if parsed and parsed[0] in OLD_ISO_NAMES:
            old_residue.append(f.name)
    if old_residue:
        r.completeness = "FAIL"
        for of in old_residue[:3]:
            r.details.append(f"  old-iso: {of} (should be migrated)")

    # -- CHECK 6: Frontmatter -------------------------------------------------
    missing_fm = []
    for f in bld_files:
        fm = get_frontmatter(f)
        if fm is None:
            missing_fm.append(f.name)
        else:
            # Check required fields
            req = {"id", "kind", "pillar"}
            has = set(fm.keys()) if isinstance(fm, dict) else set()
            lacking = req - has
            if lacking:
                missing_fm.append(f"{f.name} (missing: {', '.join(lacking)})")

    if missing_fm:
        r.frontmatter = "FAIL" if len(missing_fm) > 3 else "WARN"
        for mf in missing_fm[:3]:
            r.details.append(f"  frontmatter: {mf}")

    # -- CHECK 7: Related cross-references ------------------------------------
    low_related = []
    for f in bld_files:
        fm = get_frontmatter(f)
        related = []
        if isinstance(fm, dict):
            raw = fm.get("related", [])
            if isinstance(raw, list):
                related = raw
        count = len(related)
        if count < 3:
            low_related.append((f.name, count))

    if low_related:
        r.h_related = "WARN"
        for fname, cnt in low_related[:3]:
            r.details.append(
                f"  h_related: {fname} has {cnt} related entries (min 3)"
            )
        if len(low_related) > 3:
            r.details.append(f"  h_related: +{len(low_related) - 3} more")

    return r


# -- KC Library Checks --------------------------------------------------------

# All 98 CEX kinds (12 pillars)
ALL_KINDS = [
    "action_prompt",
    "agent",
    "api_client",
    "audio_tool",
    "axiom",
    "benchmark",
    "boot_config",
    "knowledge_index",
    "browser_tool",
    "bugloop",
    "chain",
    "checkpoint",
    "chunk_strategy",
    "cli_tool",
    "code_executor",
    "component_map",
    "computer_use",
    "constraint_spec",
    "context_doc",
    "daemon",
    "dag",
    "db_connector",
    "decision_record",
    "diagram",
    "discovery_questions",
    "dispatch_rule",
    "document_loader",
    "e2e_eval",
    "embedding_config",
    "entity_memory",
    "enum_def",
    "env_config",
    "eval_dataset",
    "fallback_chain",
    "feature_flag",
    "few_shot_example",
    "formatter",
    "function_def",
    "glossary_entry",
    "golden_test",
    "guardrail",
    "handoff",
    "handoff_protocol",
    "hook",
    "input_schema",
    "instruction",
    "interface",
    "agent_package",
    "knowledge_card",
    "landing_page",
    "learning_record",
    "lens",
    "lifecycle_rule",
    "llm_judge",
    "mcp_server",
    "memory_scope",
    "memory_summary",
    "mental_model",
    "model_card",
    "naming_rule",
    "notifier",
    "optimizer",
    "output_validator",
    "parser",
    "path_config",
    "pattern",
    "permission",
    "plugin",
    "prompt_template",
    "prompt_version",
    "quality_gate",
    "rag_source",
    "rate_limit_config",
    "red_team_eval",
    "regression_check",
    "response_format",
    "retriever",
    "retriever_config",
    "reward_signal",
    "router",
    "runtime_rule",
    "runtime_state",
    "schedule",
    "scoring_rubric",
    "search_tool",
    "secret_config",
    "session_state",
    "signal",
    "smoke_eval",
    "spawn_config",
    "system_prompt",
    "type_def",
    "unit_eval",
    "validation_schema",
    "validator",
    "vision_tool",
    "webhook",
    "workflow",
]


def check_kc_library() -> dict[str, Any]:
    """Check KC Library health: sources, domains, kind KCs, feeds_kinds, origins."""
    sources_dir = LIBRARY_DIR / "sources"
    domain_dir = LIBRARY_DIR / "domain"

    sources = sorted(sources_dir.glob("src_*.md")) if sources_dir.exists() else []
    domains = sorted(domain_dir.glob("kc_*.md")) if domain_dir.exists() else []
    # Also check _reference/ for archived cluster KCs
    ref_dir = domain_dir / "_reference"
    if ref_dir.exists():
        domains = sorted(ref_dir.glob("kc_*.md"))
    # Check dedicated kind KCs
    kind_dir = LIBRARY_DIR / "kind"
    kind_kcs = sorted(kind_dir.glob("kc_*.md")) if kind_dir.exists() else []

    issues = []

    # Check each domain KC for feeds_kinds and origin
    covered_kinds = set()
    for kc_path in domains:
        fm = get_frontmatter(kc_path)
        if fm is None:
            issues.append(f"  {kc_path.name}: no frontmatter")
            continue

        feeds = fm.get("feeds_kinds", [])
        if not feeds:
            issues.append(f"  {kc_path.name}: feeds_kinds empty")
        else:
            for kind in feeds:
                # Only strip P##_ prefix, keep real kind names as-is
                if len(kind) > 3 and kind[0] == "P" and kind[1:3].isdigit() and kind[3] == "_":
                    clean = kind[4:]  # P04_tools -> tools
                else:
                    clean = kind
                covered_kinds.add(clean)

        origin = fm.get("origin")
        if origin:
            # Check origin source exists
            origin_file = sources_dir / f"{origin}.md"
            if origin in ("manual", "distill_self_kc_carry"):
                continue  # manual origin is valid (no source file needed); distill_self_kc_carry
                # is the distill engine's synthesized self-KC origin (R-329, no source file either)
            if not origin_file.exists():
                issues.append(f"  {kc_path.name}: origin '{origin}' not found")

    # Dedicated per-kind KCs (kc_{kind}.md under library/kind/) also count as coverage for
    # that kind -- a tenant that carries kc_knowledge_card.md has knowledge_card covered even
    # if no domain-cluster KC declares feeds_kinds: [knowledge_card]. Previously this glob
    # (kind_kcs, above) was computed but never merged into covered_kinds, so any repo whose
    # coverage came entirely from per-kind KCs (e.g. a LEAN tenant distill) reported 0/N kinds
    # covered even with real KCs on disk.
    for kc_path in kind_kcs:
        stem = kc_path.stem  # "kc_{kind}"
        if stem.startswith("kc_"):
            covered_kinds.add(stem[len("kc_"):])

    kind_coverage = len(covered_kinds & set(ALL_KINDS))

    return {
        "sources": len(sources),
        "domains": len(domains),
        "kind_kcs": len(kind_kcs),
        "kinds_covered": kind_coverage,
        "kinds_total": len(ALL_KINDS),
        "issues": issues,
    }


# -- Shared Defaults Check ----------------------------------------------------

REQUIRED_SHARED_DEFAULTS = [
    "bld_tools_default.md",
    "bld_eval_default.md",
    "bld_config_default.md",
    "bld_memory_default.md",
    "bld_feedback_default.md",
    "bld_orchestration_default.md",
    "bld_architecture_default.md",
]


def check_podcast_manifests() -> list[str]:
    """Validate tour manifests under _courses/video_series/manifests/.

    Two families are enforced:
      - manifest_ep*.yaml    -> podcast episodes (require episode_id)
      - manifest_teach*.yaml -> /teach live-class lessons (no episode_id)

    Both share anchor + companion validation, plus the v1.1.0 optional
    `interaction` block (type/prompt/options/goto). Existing manifests
    without `interaction` remain valid (backward-compatible).

    Returns a list of human-readable issue strings (empty = clean).
    No-op when the manifests directory is absent.
    """
    issues: list[str] = []
    manifests_dir = ROOT / "_courses" / "video_series" / "manifests"
    if not manifests_dir.is_dir():
        return issues
    schema_path = manifests_dir / "_schema.yaml"
    if not schema_path.exists():
        issues.append(f"manifests/: missing _schema.yaml")
    heading_re = re.compile(r"^#{1,6}\s+(.+?)\s*$", re.MULTILINE)

    def headings_in(p: Path) -> set[str]:
        try:
            return set(heading_re.findall(p.read_text(encoding="utf-8", errors="ignore")))
        except Exception:
            return set()

    valid_interaction_types = ("choose_path", "poll", "open_qa")

    def _validate_interaction(interaction, prefix: str) -> list[str]:
        """Validate an anchor's optional `interaction` block (schema v1.1.0)."""
        out: list[str] = []
        if not isinstance(interaction, dict):
            out.append(f"{prefix}: interaction must be a mapping")
            return out
        itype = interaction.get("type")
        if itype not in valid_interaction_types:
            out.append(
                f"{prefix}: interaction.type must be one of "
                f"choose_path|poll|open_qa (got {itype!r})"
            )
        prompt = interaction.get("prompt")
        if not isinstance(prompt, str) or not prompt.strip():
            out.append(f"{prefix}: interaction.prompt must be a non-empty string")
        options = interaction.get("options")
        # choose_path and poll REQUIRE options; open_qa allows them but doesn't require.
        if itype in ("choose_path", "poll"):
            if not isinstance(options, list) or len(options) < 1:
                out.append(
                    f"{prefix}: interaction.options must be a non-empty list for type={itype}"
                )
                return out
        if options is None:
            return out
        if not isinstance(options, list):
            out.append(f"{prefix}: interaction.options must be a list when present")
            return out
        for i, opt in enumerate(options):
            opt_prefix = f"{prefix}: interaction.options[{i}]"
            if not isinstance(opt, dict):
                out.append(f"{opt_prefix} must be a mapping")
                continue
            label = opt.get("label")
            if not isinstance(label, str) or not label.strip():
                out.append(f"{opt_prefix}.label must be a non-empty string")
            if "goto" not in opt:
                out.append(
                    f"{opt_prefix} missing 'goto' (use null to continue linearly)"
                )
            else:
                goto = opt["goto"]
                if goto is not None and not isinstance(goto, str):
                    out.append(f"{opt_prefix}.goto must be a string or null")
        return out

    def _validate_manifest(mf: Path, required_keys: tuple) -> list[str]:
        """Validate one manifest file. Shared body for ep + teach globs."""
        out: list[str] = []
        try:
            data = yaml.safe_load(mf.read_text(encoding="utf-8")) or {}
        except Exception as e:
            out.append(f"manifests/{mf.name}: parse error: {e}")
            return out
        if not isinstance(data, dict):
            out.append(f"manifests/{mf.name}: top-level is not a mapping")
            return out
        for k in required_keys:
            if k not in data:
                out.append(f"manifests/{mf.name}: missing required key '{k}'")
        anchors = data.get("anchors") or []
        if len(anchors) < 3:
            out.append(f"manifests/{mf.name}: needs at least 3 anchors (have {len(anchors)})")
        script = data.get("script")
        script_path = ROOT / script if script else None
        if script and (not script_path or not script_path.exists()):
            out.append(f"manifests/{mf.name}: script path missing: {script}")
        script_headings = headings_in(script_path) if script_path and script_path.exists() else set()
        seen_files: set[str] = set()
        for ai, a in enumerate(anchors):
            if not isinstance(a, dict):
                continue
            sh = a.get("script_heading")
            if sh and script_headings and sh not in script_headings:
                out.append(f"manifests/{mf.name}: script_heading not found: '{sh}'")
            for c in (a.get("companion") or []):
                cf = c.get("file") if isinstance(c, dict) else None
                ch = c.get("heading") if isinstance(c, dict) else None
                if not cf:
                    out.append(f"manifests/{mf.name}: companion missing 'file'")
                    continue
                seen_files.add(cf)
                cpath = ROOT / cf
                if not cpath.exists():
                    out.append(f"manifests/{mf.name}: companion file missing: {cf}")
                elif ch and ch not in headings_in(cpath):
                    out.append(f"manifests/{mf.name}: companion heading not found in {cf}: '{ch}'")
            interaction = a.get("interaction")
            if interaction is not None:
                out.extend(
                    _validate_interaction(interaction, f"manifests/{mf.name}: anchor[{ai}]")
                )
        if len(seen_files) < 2:
            out.append(f"manifests/{mf.name}: needs at least 2 distinct companion files (have {len(seen_files)})")
        return out

    # Podcast episodes: episode_id required (existing behavior preserved).
    for mf in sorted(manifests_dir.glob("manifest_ep*.yaml")):
        issues.extend(_validate_manifest(mf, ("id", "episode_id", "script", "anchors")))
    # Teach lessons: no episode_id; same anchor + companion + interaction rules.
    for mf in sorted(manifests_dir.glob("manifest_teach*.yaml")):
        issues.extend(_validate_manifest(mf, ("id", "script", "anchors")))
    return issues


def check_shared_defaults() -> list[str]:
    """Verify _shared/ has the 7 required default files."""
    shared_dir = BUILDERS_DIR / "_shared"
    issues = []
    if not shared_dir.exists():
        issues.append("_shared/ directory missing")
        return issues
    for fname in REQUIRED_SHARED_DEFAULTS:
        if not (shared_dir / fname).exists():
            issues.append(f"_shared/{fname} missing")
    return issues


# -- Signal-Without-Deliverable Gate ------------------------------------------


def check_signal_deliverables(signals_dir: str = None) -> list:
    """Check that every 'complete' signal has a corresponding artifact on disk.

    Returns list of violations: {'nucleus': ..., 'signal': ..., 'verdict': 'FAIL'}.
    This catches the 'signal without deliverable' pattern observed in
    STRESS_TEST (Haiku 4/6 signaled complete but wrote nothing).
    """
    if signals_dir is None:
        signals_dir = str(ROOT / ".cex" / "runtime" / "signals")

    violations = []
    signals_path = Path(signals_dir)
    if not signals_path.exists():
        return violations

    for sig_file in signals_path.glob("signal_*.json"):
        try:
            data = json.loads(sig_file.read_text(encoding='utf-8'))
        except Exception:
            continue

        if data.get('status') != 'complete':
            continue

        nucleus = data.get('nucleus', '')
        mission = data.get('mission', '')

        # Check git log for commits by this nucleus since signal
        try:
            nuc_upper = nucleus.upper()
            result = subprocess.run(
                ['git', 'log', '--oneline', '--since=30 minutes ago', '--all'],
                capture_output=True, text=True, timeout=10,
                cwd=str(ROOT)
            )
            commits = [l for l in result.stdout.strip().split('\n')
                       if f'[{nuc_upper}]' in l]
            has_commit = len(commits) > 0
        except Exception:
            has_commit = False

        if not has_commit:
            violations.append({
                'nucleus': nucleus,
                'signal': sig_file.name,
                'quality_score': data.get('quality_score', 'n/a'),
                'mission': mission,
                'verdict': 'FAIL',
                'reason': 'Signal complete but no git commit found',
            })

    return violations


# -- Vocabulary KC Check (--vocab) --------------------------------------------
#
# Per .claude/rules/ubiquitous-language.md, every nucleus N01-N07 MUST hold
# a controlled vocabulary KC at:
#     N0X_<domain>/P01_knowledge/kc_<domain>_vocabulary.md
#
# This check confirms each present nucleus directory has at least one
# vocabulary KC. It does NOT auto-create missing files -- the doctor only
# reports.
#
# N00_genesis is exempt (canonical taxonomy lives there; no domain vocab
# needed).


def _domain_for_nucleus_dir(nuc_dir: Path, oss: dict) -> str:
    """Return the canonical domain slug for a nucleus directory.

    Priority: oss_defaults.nucleus_domains[n0X] > directory suffix.
    e.g. 'N01_intelligence' -> 'intelligence' (from oss) or fallback to
    the directory suffix after the underscore.
    """
    name = nuc_dir.name
    nuc_id = name[:3].lower()  # 'n01'
    nucleus_domains = (oss or {}).get("nucleus_domains") or {}
    cfg_domain = nucleus_domains.get(nuc_id)
    if cfg_domain:
        return cfg_domain
    # Fallback: directory suffix after first underscore.
    if "_" in name:
        return name.split("_", 1)[1]
    return ""


def _load_oss_defaults() -> dict:
    """Lazy load .cex/config/oss_defaults.yaml. Empty dict on any error."""
    path = ROOT / ".cex" / "config" / "oss_defaults.yaml"
    if not path.exists():
        return {}
    try:
        with path.open("r", encoding="utf-8") as f:
            return yaml.safe_load(f) or {}
    except Exception:
        return {}


def check_vocab_kcs() -> tuple[list[dict], int, int]:
    """Verify each N01-N07 nucleus has a vocabulary KC.

    Returns (results, ok_count, fail_count) where each result dict has:
        nucleus, dir, expected_path, status ('OK'|'FAIL'), found_path|None
    """
    oss = _load_oss_defaults()
    results: list[dict] = []
    ok = 0
    fail = 0

    # Find N01_*..N07_* directories. N00 is intentionally exempt.
    nucleus_dirs = []
    for child in sorted(ROOT.iterdir()):
        if not child.is_dir():
            continue
        if not re.match(r"^N0[1-7]_[a-z]", child.name):
            continue
        nucleus_dirs.append(child)

    if not nucleus_dirs:
        return ([{
            "nucleus": "?",
            "dir": "(none found)",
            "expected_path": "",
            "status": "FAIL",
            "found_path": None,
            "reason": "no N01_*..N07_* nucleus directories detected at repo root",
        }], 0, 1)

    for nuc_dir in nucleus_dirs:
        nuc_id = nuc_dir.name[:3].upper()
        domain = _domain_for_nucleus_dir(nuc_dir, oss)
        kb_dir = nuc_dir / "P01_knowledge"
        expected_basename = f"kc_{domain}_vocabulary.md" if domain else "kc_<domain>_vocabulary.md"
        expected_path = kb_dir / expected_basename if domain else None

        # Acceptance: the expected path exists, OR any kc_*_vocabulary.md
        # file exists in P01_knowledge/ (e.g. N07 has both
        # kc_admin_vocabulary.md and kc_orchestration_vocabulary.md and
        # either is acceptable).
        found_path: Path | None = None
        if expected_path is not None and expected_path.exists():
            found_path = expected_path
        elif kb_dir.exists():
            candidates = sorted(kb_dir.glob("kc_*_vocabulary.md"))
            if candidates:
                found_path = candidates[0]

        if found_path is not None:
            results.append({
                "nucleus": nuc_id,
                "dir": nuc_dir.name,
                "expected_path": (
                    str(expected_path.relative_to(ROOT))
                    if expected_path is not None else ""
                ),
                "status": "OK",
                "found_path": str(found_path.relative_to(ROOT)),
            })
            ok += 1
        else:
            results.append({
                "nucleus": nuc_id,
                "dir": nuc_dir.name,
                "expected_path": (
                    str(expected_path.relative_to(ROOT))
                    if expected_path is not None else ""
                ),
                "status": "FAIL",
                "found_path": None,
            })
            fail += 1

    return (results, ok, fail)


def print_vocab_report(results: list[dict], ok: int, fail: int) -> None:
    """Render the --vocab report to stdout."""
    print("=" * 72)
    print("CEX Doctor -- Vocabulary KC Check (.claude/rules/ubiquitous-language.md)")
    print(f"Root: {ROOT}")
    print("=" * 72)
    print()
    for r in results:
        tag = "[OK]" if r["status"] == "OK" else "[FAIL]"
        nuc = r["nucleus"]
        nuc_dir = r["dir"]
        if r["status"] == "OK":
            found = r.get("found_path") or "(found)"
            base = Path(found).name
            print(f"  {tag} {nuc_dir} -- {base} exists")
        else:
            expected = r.get("expected_path") or "(unknown)"
            base = Path(expected).name if expected else "kc_<domain>_vocabulary.md"
            print(f"  {tag} {nuc_dir} -- {base} MISSING")
    print()
    print(f"Vocabulary: {ok} OK / {fail} FAIL")
    print("=" * 72)


# -- Open Variables (Article XIX / ADR 022) ----------------------------------
#
# Standalone audit mirroring --vocab. SCOPED to cexai/ + cexai-specs/ typed
# artifacts ONLY (a .md whose frontmatter declares kind:). Legacy CEX paths
# (N0X_*/, archetypes/, ...) are NEVER scanned -- they predate the mandate.
#
# Two structural exclusions keep the audit honest (see ADR + the Layer-2 test
# cexai/tests/governance/test_article_xix_open_vars.py -- keep these in sync):
#   * compiled/ trees      -- vendored / auto-generated (same skip as the
#                             builder doctor + run_validate_all).
#   * OPEN_VARS_LEGACY_BASELINE -- pre-Round-20 artifacts grandfathered per
#                             ADR 022 Layer 3 (CONDITIONAL until v1.5). RATCHET:
#                             may only shrink; NEW violations still FAIL.

OPEN_VARS_SCOPE_ROOTS = ("cexai", "cexai-specs")

OPEN_VARS_LEGACY_BASELINE = frozenset({
    "cexai-specs/18_aitmpl_stack/analyze.md",
    "cexai-specs/18_aitmpl_stack/constitution.md",
    "cexai-specs/18_aitmpl_stack/plan.md",
    "cexai-specs/18_aitmpl_stack/spec.md",
    "cexai-specs/18_aitmpl_stack/tasks.md",
    "cexai-specs/_decisions/adr_020_compiler_activation_protocol.md",
    "cexai-specs/_decisions/adr_023_recon_layer.md",
    "cexai-specs/_revisions/proposed_kcs/kc_chatterbox_tts.md",
    "cexai-specs/_revisions/proposed_kcs/kc_dspy.md",
    "cexai-specs/_revisions/proposed_kcs/kc_langgraph.md",
    "cexai-specs/_revisions/proposed_kcs/kc_moneyprinterturbo.md",
    "cexai-specs/_revisions/research_prior_art_landscape.md",
    "cexai-specs/_revisions/rubric_intent_resolution.md",
    "cexai-specs/_revisions/spec_auto_research_triangulation.md",
    "cexai-specs/_revisions/spec_knowledge_distillation.md",
    "cexai-specs/_revisions/spec_open_variables_protocol.md",
    "cexai-specs/_revisions/spec_prompt_compiler.md",
    "cexai-specs/_revisions/spec_recon_phase.md",
    "cexai-specs/_revisions/spec_verticalize_protocol.md",
})

_OPEN_VARS_TOP_KEY = re.compile(r"^([A-Za-z_][\w-]*):")


def _open_vars_frontmatter_keys(text: str) -> set[str] | None:
    """Top-level (column-0) frontmatter keys, or None if no frontmatter. Same
    dependency-free probe as the Layer-2 governance test."""
    if not text.startswith("---"):
        return None
    end = text.find("\n---", 3)
    if end < 0:
        return None
    keys: set[str] = set()
    for line in text[3:end].splitlines():
        if not line or line[0].isspace() or line.lstrip().startswith("#"):
            continue
        m = _OPEN_VARS_TOP_KEY.match(line)
        if m:
            keys.add(m.group(1))
    return keys


def check_open_vars() -> tuple[dict, int, int]:
    """Audit Article XIX compliance for CEXAI typed artifacts.

    Returns (report, ok, fail):
      report = {compliant:int, legacy:int, compiled_skipped:int, violations:[rel,...]}
      ok     = compliant count
      fail   = number of NEW violations (typed, not compiled, not baselined,
               missing open_vars:). Exit 0 iff fail == 0.
    """
    compliant = 0
    legacy = 0
    compiled_skipped = 0
    violations: list[str] = []

    # Ship-safety: only scan scope roots that actually exist on disk. When a root
    # is excluded from the ship (e.g. cexai-specs/ on the public repo), it is
    # dropped here -- the audit degrades to the remaining roots, never crashes.
    # The hardcoded OPEN_VARS_LEGACY_BASELINE below is a pure string filter, so an
    # absent cexai-specs/ simply matches nothing (no FS access on the baseline).
    scanned_roots = [b for b in OPEN_VARS_SCOPE_ROOTS if (ROOT / b).is_dir()]

    for base in scanned_roots:
        root = ROOT / base
        for md in root.rglob("*.md"):
            rel = md.relative_to(ROOT).as_posix()
            if "compiled" in rel.split("/"):
                compiled_skipped += 1
                continue
            try:
                text = md.read_text(encoding="utf-8", errors="replace")
            except OSError:
                continue
            keys = _open_vars_frontmatter_keys(text)
            if not keys or "kind" not in keys:
                continue  # plain doc -- not a typed artifact
            if "open_vars" in keys:
                compliant += 1
            elif rel in OPEN_VARS_LEGACY_BASELINE:
                legacy += 1
            else:
                violations.append(rel)

    report = {
        "compliant": compliant,
        "legacy": legacy,
        "compiled_skipped": compiled_skipped,
        "violations": sorted(violations),
        "scanned_roots": scanned_roots,
    }
    return (report, compliant, len(violations))


def print_open_vars_report(report: dict, ok: int, fail: int) -> None:
    """Render the --open-vars report to stdout."""
    print("=" * 72)
    print("CEX Doctor -- Open Variables Check (Article XIX / ADR 022, scoped)")
    print(f"Root: {ROOT}")
    scope = " + ".join("%s/" % r for r in report.get("scanned_roots", [])) or "(none present)"
    print(f"Scope: {scope} typed artifacts (kind:) -- legacy paths never scanned")
    print("=" * 72)
    print()
    print(f"  [OK]   {ok} typed artifact(s) declare open_vars:")
    print(f"  [i]    {report['legacy']} pre-Round-20 legacy artifact(s) grandfathered (ADR 022 L3)")
    print(f"  [i]    {report['compiled_skipped']} compiled/vendored artifact(s) skipped")
    if report["violations"]:
        print()
        print(f"  {len(report['violations'])} NEW violation(s) -- declare open_vars: (even []):")
        for rel in report["violations"]:
            print(f"    [FAIL] {rel}")
    print()
    print(f"Open Variables: {ok} OK / {fail} FAIL")
    print("=" * 72)


# -- Model literal gate (--models) : plan opus_latest_dynamic (W1 T9) ---------
# A hardcoded full model version slug (claude-(opus|sonnet|haiku)-N-N) in CEX's
# functional code is a regression: it pins a stale model and silently defeats
# the dynamic `*_latest` alias mechanism (.cex/config/nucleus_models.yaml::
# model_aliases). This gate FAILs on any NEW literal in the scanned surfaces
# outside the permanent allowed buckets and the ratchet baseline below.
#
# Scope = CEX's OWN functional surfaces only. Markdown / docs are intentionally
# OUT of scope (they cite versions for historical / audit / capability context
# and are swept by cex_model_updater.py --propagate, not this gate). Vendored
# trees (.venv*, node_modules), compiled/, worktrees/, and out-of-tree packages
# (cex_sdk/, examples/, cexai/) are not scanned -- they are separately owned.
MODELS_LITERAL_RE = re.compile(r"claude-(?:opus|sonnet|haiku)-\d+-\d+")
MODELS_SCAN_ROOTS = ("_tools", "boot", ".cex/config")
MODELS_SCAN_EXTS = (".py", ".ps1", ".sh", ".yaml", ".yml")

# Permanent allowed buckets -- literals here are BY DESIGN (never flagged):
#  - config source of truth (model_aliases + tiers + preflight pin versions),
#  - the resolution core (the ONE place a baseline const is permitted -- DP4),
#  - version-catalog / pricing / hygiene tools (version-aware by nature),
#  - test fixtures + per-runtime pin configs (their job IS to name a model).
MODELS_ALLOWED_FILES = frozenset({
    ".cex/config/nucleus_models.yaml",
    ".cex/config/nucleus_models.template.yaml",
    # resolution core (baseline const + local shorthand fallback live here)
    "_tools/cex_model_resolver.py",
    "_tools/cex_boot_pipeline.py",
    "boot/_shared/resolve_model.ps1",
    "boot/_shared/claude_boot.sh",
    # version catalog / pricing / hygiene (intentional version references)
    "_tools/cex_cost_tracker.py",
    "_tools/cex_token_budget.py",
    "_tools/cex_provider_discovery.py",
    "_tools/cex_model_updater.py",
    "_tools/cex_hygiene.py",
    "_tools/cex_release_check.py",
})
MODELS_ALLOWED_DIR_PREFIXES = ("_tools/tests/", ".cex/config/runtimes/")

# Legacy baseline -- functional files that STILL carry a literal pending
# migration to resolve_model() (plan opus_latest_dynamic: T5/T7/T8 + the
# one-shot --propagate sweep). RATCHET: this set may only SHRINK. Do NOT add
# entries -- a NEW literal outside the allowed buckets above MUST fail the gate.
# Remove an entry once its file migrates to the resolver.
MODELS_LEGACY_BASELINE = frozenset({
    "_tools/cex_8f_runner.py",
    "_tools/cex_auto_run.py",
    "_tools/cex_benchmark_ollama.py",
    "_tools/cex_fts5_search.py",
    "_tools/cex_intent.py",
    "_tools/cex_iso_serve.py",
    "_tools/cex_mission_dispatch.py",
    "_tools/cex_model_bench.py",
    "_tools/cex_preflight.py",
    "_tools/cex_quota_check.py",
    "_tools/cex_run.py",
    "_tools/cex_showoff_smoke.py",
    "_tools/cex_translate.py",
    "_tools/cex_user_model.py",
    # -- Removed by OPUS_LATEST_DYNAMIC W2a (N05), migrated to resolve_*() --
    #    cex_8f_motor.py, cex_cli_resolver.py, cex_decompose.py, cex_router.py,
    #    cex_router_v2.py, cex_skill_distill.py, cex_stress_runner.py (22 -> 15).
})


def check_model_literals() -> tuple[dict, int, int]:
    """Scan CEX functional surfaces for hardcoded model version literals.

    Returns (report, ok, fail):
      report = {allowed, baselined, baseline_total, stale_baseline:[rel,...],
                violations:[rel,...]}
      ok     = count of files whose literals are in a permanent allowed bucket
      fail   = number of NEW violations (literal outside allowed buckets AND not
               in MODELS_LEGACY_BASELINE). Exit 0 iff fail == 0.
    """
    allowed = 0
    baselined = 0
    hit_baseline: set[str] = set()
    violations: list[str] = []

    for base in MODELS_SCAN_ROOTS:
        root = ROOT / base
        if not root.exists():
            continue
        candidates = root.rglob("*") if root.is_dir() else [root]
        for path in candidates:
            if not path.is_file() or path.suffix not in MODELS_SCAN_EXTS:
                continue
            rel = path.relative_to(ROOT).as_posix()
            segs = set(rel.split("/"))
            if segs & {"compiled", ".git", "worktrees", "node_modules", "__pycache__"}:
                continue
            try:
                text = path.read_text(encoding="utf-8", errors="replace")
            except OSError:
                continue
            if not MODELS_LITERAL_RE.search(text):
                continue
            if (rel in MODELS_ALLOWED_FILES
                    or any(rel.startswith(p) for p in MODELS_ALLOWED_DIR_PREFIXES)):
                allowed += 1
            elif rel in MODELS_LEGACY_BASELINE:
                baselined += 1
                hit_baseline.add(rel)
            else:
                violations.append(rel)

    # Baseline entries that no longer match (file migrated/deleted) -- the
    # ratchet has slack to tighten. Reported as info, never a failure.
    stale = sorted(MODELS_LEGACY_BASELINE - hit_baseline)

    report = {
        "allowed": allowed,
        "baselined": baselined,
        "baseline_total": len(MODELS_LEGACY_BASELINE),
        "stale_baseline": stale,
        "violations": sorted(violations),
    }
    return (report, allowed, len(violations))


def print_model_literals_report(report: dict, ok: int, fail: int) -> None:
    """Render the --models report to stdout."""
    print("=" * 72)
    print("CEX Doctor -- Model Literal Gate (plan: opus_latest_dynamic)")
    print(f"Root: {ROOT}")
    print("Scope: _tools/ boot/ .cex/config/  (.py/.ps1/.sh/.yaml)")
    print("Pattern: claude-(opus|sonnet|haiku)-N-N outside allowed buckets")
    print("=" * 72)
    print()
    print(f"  [OK]   {ok} file(s) with by-design literals "
          "(config / resolver core / pricing / tests)")
    print(f"  [i]    {report['baselined']}/{report['baseline_total']} legacy-baseline "
          "file(s) still carry a literal (migration debt: T5/T7/T8 + --propagate)")
    if report["stale_baseline"]:
        print(f"  [i]    {len(report['stale_baseline'])} baseline entry(ies) now clean "
              "-- safe to remove from MODELS_LEGACY_BASELINE:")
        for rel in report["stale_baseline"]:
            print(f"           - {rel}")
    if report["violations"]:
        print()
        print(f"  {len(report['violations'])} NEW violation(s) -- route the model "
              "through resolve_model()/resolve_shorthand, never hardcode:")
        for rel in report["violations"]:
            print(f"    [FAIL] {rel}")
    print()
    print(f"Model Literals: {ok} OK / {fail} FAIL")
    print("=" * 72)


# -- Wikilink gate (MAX_LEVERAGE P2.3: gate every F7, any topology) ------------
#
# The W2 wikilink gate (cex_wikilink_gate) used to run ONLY on the cheap decompose
# path (cex_decompose.stage_3). P2.3 wires it into the universal doctor every
# nucleus already runs in F7/F8, so NO produced artifact ships with a fabricated
# [[link]], regardless of topology (solo Mode A / swarm / manual build).
#
# Scope discipline (why this can't regress the 302/0/0 builder gate): the live
# corpus carries pre-existing fabricated links (measured: several N04 KCs fail).
# Gating the WHOLE corpus in the default run would explode it. So:
#   * the DEFAULT run gates ONLY git-STAGED .md (the F8 commit set -- the
#     artifacts actually entering the corpus). A clean tree stages no .md -> the
#     gate is a no-op -> the builder Result line stays 302 PASS | 0 WARN | 0 FAIL.
#   * the explicit `--wikilinks [PATHS]` flag gates given paths (or the staged
#     set) for targeted / CI / test use.
# Degrade-never: any git / import failure -> the gate is skipped, never crashes
# the doctor.

_WIKILINK_SKIP_DIRS = {".git", ".obsidian", "__pycache__", "node_modules",
                       ".cex", ".pytest_cache", ".mypy_cache", "compiled"}


def _git_staged_md() -> list[Path]:
    """Return git-STAGED .md artifact paths (the F8 commit set). [] on any error.

    Staged = `git diff --cached --name-only --diff-filter=ACM -- '*.md'`. These are
    the artifacts a nucleus is about to commit in F8 COLLABORATE -- exactly the set
    that must not ship a fabricated wikilink. Degrade-never: a non-repo / missing
    git / subprocess error yields [] so the default doctor is unaffected.
    """
    try:
        proc = subprocess.run(
            ["git", "diff", "--cached", "--name-only", "--diff-filter=ACM",
             "--", "*.md"],
            cwd=str(ROOT), capture_output=True, encoding="utf-8",
            errors="replace", timeout=15,
        )
    except (OSError, subprocess.SubprocessError):
        return []
    if proc.returncode != 0:
        return []
    out: list[Path] = []
    for line in (proc.stdout or "").splitlines():
        rel = line.strip()
        if not rel or not rel.endswith(".md"):
            continue
        parts = Path(rel).parts
        if any(seg in _WIKILINK_SKIP_DIRS for seg in parts):
            continue
        fp = ROOT / rel
        if fp.exists():
            out.append(fp)
    return out


def check_wikilinks(paths: list[Path] | None = None) -> tuple[list[dict], int, int]:
    """Gate the wikilinks of produced artifacts via cex_wikilink_gate (W2).

    paths=None -> gate the git-STAGED .md set (the default-run / F8 scope). An
    explicit list overrides discovery (used by --wikilinks PATHS and by tests).

    Returns (results, ok, fabricated_count) where each result is
    {path, ok, fabricated:list[str]}. A target RESOLVES iff some .md declares it
    as a frontmatter `^id:` on disk; any unresolved [[target]] is FABRICATED.
    Degrade-never: if the gate module cannot be imported, returns ([], 0, 0).
    """
    try:
        from cex_wikilink_gate import gate as _wl_gate
    except Exception:  # pragma: no cover - module ships beside the doctor
        return [], 0, 0
    targets = _git_staged_md() if paths is None else list(paths)
    results: list[dict] = []
    ok = 0
    fab = 0
    for p in targets:
        pp = Path(p)
        if not pp.exists():
            continue
        try:
            clean, fabricated = _wl_gate(str(pp))
        except Exception:
            continue
        try:
            rel = str(pp.resolve().relative_to(ROOT)).replace("\\", "/")
        except ValueError:
            rel = str(pp)
        results.append({"path": rel, "ok": clean, "fabricated": fabricated})
        if clean:
            ok += 1
        else:
            fab += 1
    return results, ok, fab


def print_wikilink_report(results: list[dict], ok: int, fab: int,
                          scope: str = "staged") -> None:
    """Print the wikilink-gate section (mirrors the other doctor sub-checks)."""
    if not results:
        print("Wikilink Gate (%s): no produced artifact to gate" % scope)
        return
    for r in results:
        if not r["ok"]:
            print("  [FAIL] %s -- %d fabricated: %s"
                  % (r["path"], len(r["fabricated"]), ", ".join(r["fabricated"])))
    print("Wikilink Gate (%s): %d clean / %d fabricated" % (scope, ok, fab))


# -- Check Registry (R-162 keystone-to-gate wiring) ----------------------------
#
# Wires _tools/cex_check_registry.py's typed pluggable CheckPlugin registry into
# the doctor as an ADDITIVE pass. See module docstring at the top of this file
# for the full contract. This section owns: run+summarize the registry, resolve
# a finding's severity, the two exit-code folds (severity-scoped --plugins-strict
# + the SET-scoped R-162 PROMOTION default-on fold below), and render the
# human-readable report -- mirroring the check_wikilinks() / print_wikilink_report()
# pair immediately above.
_CHECK_REGISTRY_EMPTY_SUMMARY = {
    "evaluated_checks": 0,
    "successful_checks": 0,
    "unsuccessful_checks": 0,
    "success_percent": 100.0,
}

# R-162 PROMOTION (GDP-closed 2026-07-12 -- founder star-rec accepted verbatim; see
# docs/FOUNDER_DESK_R162_PROMOTION_CALL_2026_07_12.md + docs/IMPROVEMENT_REGISTER.md
# row R-162). These 7 plugins were zero-legacy-debt clean on the day of the call and
# are promoted from advisory to BLOCKING, DEFAULT-ON. This is a SET, not a severity
# threshold: membership alone decides the fold (see _check_promoted_fold_exit below),
# so a MEDIUM-severity member like counter_gate still folds, while a HIGH-severity
# non-member like registry_drift (217+193 known kind-registry drift on the call date)
# stays advisory until its own legacy debt is cleaned to zero. The other 9 registered
# plugins stay advisory: 5 carry counted legacy debt (registry_drift,
# handoff_context_doctor, identity_doctor, reference_doctor, runtime_cap_doctor) until
# each is cleaned; 3 are by-design non-gates (index_freshness, hydration_doctor,
# memory_doctor) permanently. compiled_name_doctor was registered the same day as the
# original promotion (commit f6fa38fd6f) but AFTER the brief was written, so it was
# deliberately NOT auto-promoted by inference; the founder then EXPLICITLY promoted it
# in a second same-day GDP call (2026-07-12, "pode incluir o compiled_name_doctor nos
# promovidos") once its own legacy debt hit zero (R-330 closed the 3 residual
# collisions, commit fbc260c181) -- the set is now 8, still a closed founder
# enumeration, never inferred growth. Declared ONCE, here, as data -- never scattered
# across per-plugin ifs. Rollback is the --no-plugins-strict escape hatch below
# (1 line, see _check_promoted_fold_exit).
PROMOTED_PLUGINS = frozenset({
    "counter_gate",
    "schema_doctor",
    "provenance_doctor",
    "frontmatter_doctor",
    "license_doctor",
    "trace_auditor",
    "tenant_honesty",
    "compiled_name_doctor",
})


def check_registry_advisory() -> tuple[list, dict]:
    """Run the R-162 typed check registry and return (findings, summary).

    Degrade-never: any import or execution error in cex_check_registry yields
    ([], zero-evaluated summary) -- the doctor's own 12-pillar checks above are
    never affected by a registry-side failure.
    """
    try:
        from cex_check_registry import run_registry, summarize
    except Exception:
        return [], dict(_CHECK_REGISTRY_EMPTY_SUMMARY)
    try:
        findings = run_registry(ROOT)
        return findings, summarize(findings)
    except Exception:
        return [], dict(_CHECK_REGISTRY_EMPTY_SUMMARY)


def _check_registry_severity(finding) -> str:
    """Best-effort severity lookup for one CheckFinding. Degrade-never: an
    import error (or an unregistered plugin_id) resolves to OBSERVATION."""
    try:
        from cex_check_registry import severity_for
        return severity_for(finding)
    except Exception:
        return "OBSERVATION"


def _check_registry_fold_exit(findings: list, strict: bool) -> bool:
    """Pure helper: True iff --plugins-strict is set AND at least one registry
    finding is a failing BLOCKING/HIGH severity. Extracted out of main() so the
    exit-code fold can be unit-tested directly (synthetic findings) without
    driving the full 308-builder scan. strict=False (the default) always
    returns False -- this is what keeps the default-flags exit code untouched.
    """
    if not strict or not findings:
        return False
    return any(
        (not f.ok) and _check_registry_severity(f) in ("BLOCKING", "HIGH")
        for f in findings
    )


def _check_promoted_fold_exit(findings: list, disabled: bool = False) -> bool:
    """Pure helper: True iff at least one PROMOTED_PLUGINS finding is failing.

    R-162 PROMOTION (2026-07-12): this is the DEFAULT-ON fold -- unlike
    _check_registry_fold_exit above (opt-in via --plugins-strict, SEVERITY-scoped:
    any failing BLOCKING/HIGH plugin), this check runs UNCONDITIONALLY on every
    default doctor invocation and is SET-scoped: only membership in
    PROMOTED_PLUGINS can fold the exit code, regardless of the finding's declared
    severity (e.g. counter_gate is MEDIUM and still folds; registry_drift is HIGH
    but is NOT promoted, so it never folds here). Pass disabled=True (wired from
    the --no-plugins-strict escape hatch) to force this back to pure-advisory --
    always returns False -- the 1-line rollback the brief promises. Mirrors
    _check_registry_fold_exit's own extraction rationale: unit-testable directly
    with synthetic findings, no live-repo coupling, no full 308-builder scan.
    """
    if disabled or not findings:
        return False
    return any(
        (not f.ok) and f.plugin_id in PROMOTED_PLUGINS
        for f in findings
    )


def print_check_registry_report(findings: list, summary: dict) -> None:
    """Render the '=== CHECK REGISTRY (advisory) ===' section.

    ADVISORY ONLY: printing this section never changes fail_count or the
    doctor's exit code by itself -- see main() for the --plugins-strict fold.
    """
    print("=" * 72)
    print("CHECK REGISTRY (advisory) -- typed pluggable keystone checks (R-162)")
    print("=" * 72)
    if not findings:
        print("  (no plugins registered, or registry unavailable -- see "
              "_tools/cex_check_registry.py)")
    else:
        for f in findings:
            sev = _check_registry_severity(f)
            tag = "OK" if f.ok else ("FAIL[%s]" % sev)
            print("  [%s] %s: %s" % (tag, f.plugin_id, f.message))
    print("-" * 72)
    print(
        "%(successful_checks)d/%(evaluated_checks)d checks passed "
        "(%(success_percent).1f%%)" % summary
    )
    print("=" * 72)


# -- Main ---------------------------------------------------------------------


def main() -> None:
    print("=" * 72)
    print("CEX Doctor v3.0 -- 12-Pillar ISO Architecture + Density + Completeness")
    print(f"Root: {ROOT}")
    print(f"Mode: {'DIAGNOSE + FIX' if FIX_MODE else 'DIAGNOSE ONLY'}")
    print("=" * 72)
    print()

    # Discover builder dirs
    builder_dirs = sorted(
        d
        for d in BUILDERS_DIR.iterdir()
        if d.is_dir() and not d.name.startswith("_") and not d.name.startswith(".") and d.name != "compiled"
    )

    if not builder_dirs:
        print("ERROR: No builder directories found in archetypes/builders/")
        sys.exit(1)

    print(f"Found {len(builder_dirs)} builder directories\n")

    results = []
    for bd in builder_dirs:
        results.append(check_builder(bd))

    # -- Summary Table --------------------------------------------------------
    pass_count = sum(1 for r in results if r.overall == "PASS")
    warn_count = sum(1 for r in results if r.overall == "WARN")
    fail_count = sum(1 for r in results if r.overall == "FAIL")

    # Column headers
    hdr = f"{'Builder':<35} {'Name':>5} {'Dens':>5} {'Size':>5} {'12ok':>5} {'YAML':>5} {'Rel':>5} {'ALL':>5}"
    print(hdr)
    print("-" * len(hdr))

    for r in results:

        def sym(s: str) -> str:
            return {"PASS": "ok", "WARN": "~~", "FAIL": "XX"}[s]

        line = (
            f"{r.name:<35} {sym(r.naming):>5} {sym(r.density):>5} "
            f"{sym(r.max_bytes):>5} {sym(r.completeness):>5} "
            f"{sym(r.frontmatter):>5} {sym(r.h_related):>5} {sym(r.overall):>5}"
        )
        print(line)

    print("-" * len(hdr))
    print(f"{'TOTAL':<35} {pass_count:>3} ok  {warn_count:>3} ~~  {fail_count:>3} XX")
    print()

    # -- Detail section (only non-PASS) ---------------------------------------
    failures = [r for r in results if r.overall != "PASS"]
    if failures:
        print("DETAILS (non-PASS builders):")
        print()
        for r in failures:
            print(f"[{r.overall}] {r.name}:")
            for d in r.details:
                print(d)
            print()

    # -- Aggregate stats ------------------------------------------------------
    print("=" * 72)
    total_files = sum(len(list(bd.glob("bld_*.md"))) for bd in builder_dirs)
    total_bytes = sum(f.stat().st_size for bd in builder_dirs for f in bd.glob("bld_*.md"))
    densities = []
    for bd in builder_dirs:
        for f in bd.glob("bld_*.md"):
            densities.append(calc_density(f))
    avg_density = sum(densities) / len(densities) if densities else 0

    oversized_total = sum(
        1
        for bd in builder_dirs
        for f in bd.glob("bld_*.md")
        if f.stat().st_size
        > (MAX_BYTES_PROMPT if f.name.startswith("bld_prompt_") else MAX_BYTES)
    )
    fm_missing_total = sum(
        1 for bd in builder_dirs for f in bd.glob("bld_*.md") if get_frontmatter(f) is None
    )

    print(f"Builders:       {len(builder_dirs)}")
    print(f"Total files:    {total_files} (expected {len(builder_dirs) * EXPECTED_COUNT})")
    print(f"Total size:     {total_bytes / 1024:.1f} KB")
    print(f"Avg density:    {avg_density:.2f}")
    print(
        f"Oversized:      {oversized_total} files (>{MAX_BYTES}B std, >{MAX_BYTES_PROMPT}B prompts)"
    )
    print(f"No frontmatter: {fm_missing_total} files")
    print(f"Result:         {pass_count} PASS | {warn_count} WARN | {fail_count} FAIL")
    print("=" * 72)

    # -- KC Library Health ----------------------------------------------------
    print()
    kc = check_kc_library()
    print(
        f"KC Library: {kc['sources']} sources, {kc['domains']} domains, "
        f"{kc['kinds_covered']}/{kc['kinds_total']} kinds covered"
    )
    if kc["issues"]:
        print(f"KC Issues ({len(kc['issues'])}):")
        for issue in kc["issues"][:10]:
            print(issue)
    print("=" * 72)

    # -- Shared Defaults Check ------------------------------------------------
    shared_issues = check_shared_defaults()
    if shared_issues:
        print()
        print(f"Shared Defaults ({len(shared_issues)} issues):")
        for si in shared_issues:
            print(f"  [WARN] {si}")
        print("=" * 72)

    # -- Podcast Manifests Check (ADVISORY) -----------------------------------
    # This block validates media-asset manifests (storyboards / companion KCs /
    # cexai modules under _courses/video_series/). It is ADVISORY: missing media
    # assets are a content-pipeline concern, NOT a builder-health regression.
    # The process exit code reflects the builder-health CORE only (fail_count),
    # so a dangling media manifest never poisons CI / the doctor gate. Output
    # stays fully visible (reported as WARN) so the issues remain actionable.
    manifest_issues = check_podcast_manifests()
    if manifest_issues:
        print()
        print(f"Podcast Manifests ({len(manifest_issues)} issues) [ADVISORY -- "
              "does not affect exit code]:")
        for mi in manifest_issues:
            print(f"  [WARN] {mi}")
        print("=" * 72)
    elif (ROOT / "_courses" / "video_series" / "manifests").is_dir():
        print()
        print("Podcast Manifests: all manifests valid")
        print("=" * 72)

    # -- Wikilink Gate (staged artifacts) -- MAX_LEVERAGE P2.3 ----------------
    # Gates ONLY git-STAGED .md (the F8 commit set), so the leverage gate rides
    # the doctor call every nucleus already makes in F7/F8 -- no produced
    # artifact ships with a fabricated [[link]], any topology. A CLEAN TREE
    # stages no .md, so this is a no-op and the builder Result line above stays
    # 302 PASS | 0 WARN | 0 FAIL. A staged artifact with a fabricated link FAILS
    # the doctor (contributes to the exit code only -- the builder count is
    # untouched). Degrade-never: any error -> gate skipped, doctor unaffected.
    wl_fab = 0
    try:
        wl_results, wl_ok, wl_fab = check_wikilinks()  # None -> staged set
        if wl_results:
            print()
            print_wikilink_report(wl_results, wl_ok, wl_fab, scope="staged")
            print("=" * 72)
    except Exception:
        wl_fab = 0

    # -- Check Registry (ADVISORY + R-162 PROMOTION) -- keystone-to-gate wiring
    # ADDITIVE pass: registry findings are always REPORTED here. Whether they
    # affect the exit code is governed by 3 independent knobs (full contract in
    # the module docstring):
    #   cr_promoted_fail  DEFAULT-ON since the 2026-07-12 GDP promotion: folds
    #                     iff a PROMOTED_PLUGINS member is failing -- SET-scoped,
    #                     not severity-scoped. Before that date the registry pass
    #                     never folded the exit code without an explicit flag.
    #   cr_strict_fail    opt-in via --plugins-strict (pre-existing, UNCHANGED):
    #                     folds iff ANY failing BLOCKING/HIGH finding exists,
    #                     promoted or not (e.g. still catches registry_drift).
    #   NO_PLUGINS_STRICT escape hatch via --no-plugins-strict: forces BOTH of
    #                     the above to False -- pure-advisory rollback, one line.
    cr_findings, cr_summary = check_registry_advisory()
    print()
    print_check_registry_report(cr_findings, cr_summary)

    cr_strict_fail = _check_registry_fold_exit(
        cr_findings, PLUGINS_STRICT and not NO_PLUGINS_STRICT)
    cr_promoted_fail = _check_promoted_fold_exit(
        cr_findings, disabled=NO_PLUGINS_STRICT)

    if JSON_MODE:
        print()
        print(json.dumps(
            {
                "check_registry": cr_summary,
                "check_registry_findings": [f.to_dict() for f in cr_findings],
            },
            indent=2, ensure_ascii=False,
        ))

    sys.exit(1 if (fail_count > 0 or wl_fab > 0 or cr_strict_fail or cr_promoted_fail) else 0)


def _doctor_cli():
    """CLI entry point with verb help and agent-io support."""
    # Article Sec 2.1: per-verb help.
    VERB_HELP = {
        "check":   "Read-only diagnostic across all builders. Verifies naming, "
                   "density, size, frontmatter, 12P completeness, related links. "
                   "rc=0 if all PASS, 1 if any FAIL. Default verb.",
        "summary": "Same diagnostic as `check` but with --agent-io applied "
                   "automatically: output captured, truncated to 200 lines, "
                   "[exit:N | Xms] tail emitted. Use this from agent contexts.",
        "fix":     "Diagnostic + auto-fix naming issues (renames misspelled files "
                   "to canonical form). DESTRUCTIVE: makes git-trackable changes. "
                   "Review the diff before committing.",
    }
    try:
        from cex_agent_io import maybe_print_verb_help
        if maybe_print_verb_help(sys.argv[1:], VERB_HELP):
            sys.exit(0)
    except ImportError:
        pass

    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    # Positional verb (v1.2.0+ canonical form): check (default, read-only),
    # summary (alias for check), fix (sets --fix). Flag --fix preserved.
    parser.add_argument("verb", nargs="?", default="check",
                        choices=("check", "summary", "fix"),
                        help="Subcommand (default: check). Try `tool <verb> --help`.")
    parser.add_argument("--fix", action="store_true", help="Diagnose and auto-fix naming issues.")
    parser.add_argument("--plugins-strict", action="store_true",
                        help="R-162: fold BLOCKING/HIGH findings from the typed check "
                             "registry (_tools/cex_check_registry.py) into the doctor's "
                             "exit code (fail-closed), promoted or not (e.g. still folds "
                             "on registry_drift's known legacy debt). ADDITIONAL to the "
                             "default-on PROMOTED_PLUGINS fold (R-162 PROMOTION, "
                             "2026-07-12) -- leaving this unset does NOT disable that "
                             "default; see --no-plugins-strict. Applies to check/summary/"
                             "fix verbs only.")
    parser.add_argument("--no-plugins-strict", action="store_true",
                        help="R-162 PROMOTION (2026-07-12, GDP-closed -- see "
                             "docs/FOUNDER_DESK_R162_PROMOTION_CALL_2026_07_12.md): escape "
                             "hatch / 1-line rollback for the now-default-on "
                             "PROMOTED_PLUGINS exit-code fold. Forces the check registry "
                             "pass back to pure-advisory-only (never changes fail_count or "
                             "the exit code), overriding BOTH the default promotion fold "
                             "AND --plugins-strict if both are passed together. Applies to "
                             "check/summary/fix verbs only.")
    parser.add_argument("--json", action="store_true",
                        help="R-162: in addition to the normal text report, print a "
                             "trailing JSON block with a 'check_registry' summary + "
                             "findings key (does not replace the text output). Applies "
                             "to check/summary/fix verbs only.")
    parser.add_argument("--signals", action="store_true",
                        help="Check that every 'complete' signal has a matching deliverable. "
                             "Catches signal-without-deliverable pattern (Haiku failure mode).")
    parser.add_argument("--vocab", action="store_true",
                        help="Validate per-nucleus vocabulary KC presence "
                             "(.claude/rules/ubiquitous-language.md). "
                             "Standalone check: exits 0 if all 7 nuclei N01-N07 "
                             "have a kc_<domain>_vocabulary.md, else 1. "
                             "Does NOT run the full builder doctor when set.")
    parser.add_argument("--open-vars", action="store_true",
                        help="Validate Article XIX (Open Variables Mandate) for "
                             "CEXAI typed artifacts (ADR 022). Standalone check: "
                             "scans cexai/ + cexai-specs/ .md whose frontmatter has "
                             "kind: and asserts open_vars: is declared. Compiled/"
                             "vendored trees + a frozen pre-Round-20 legacy baseline "
                             "are skipped. Exits 0 if no NEW violations, else 1. "
                             "Does NOT run the full builder doctor when set.")
    parser.add_argument("--models", action="store_true",
                        help="Scan CEX functional code (_tools/ boot/ "
                             ".cex/config/) for hardcoded "
                             "claude-(opus|sonnet|haiku)-N-N model literals "
                             "outside the allowed buckets (model_aliases / "
                             "resolver core / pricing / tests) + a ratchet "
                             "baseline. FAILs on any NEW literal so a stale "
                             "model pin cannot be reintroduced (plan "
                             "opus_latest_dynamic). Standalone: does NOT run "
                             "the full builder doctor when set.")
    parser.add_argument("--agent-io", action="store_true",
                        help="Capture output, truncate to 200 lines / 50 KiB, "
                             "append [exit:N | Xms] metadata. v1.3.0+ agent-friendly mode.")
    parser.add_argument("--wikilinks", nargs="*", metavar="PATH", default=None,
                        help="MAX_LEVERAGE P2.3: gate produced artifacts' wikilinks "
                             "via cex_wikilink_gate (W2). With PATHs, gate those "
                             "files; with no PATH, gate the git-staged .md set. A "
                             "fabricated [[link]] (target id not declared on disk) "
                             "exits 1. Standalone: does NOT run the full builder "
                             "doctor when set, so it is a cheap pre-commit / F7 gate "
                             "for ANY topology, not just decompose.")
    args, _ = parser.parse_known_args()

    # --wikilinks: standalone W2 gate over produced artifacts (P2.3). Does not run
    # the full builder doctor, so any F7/F8/pre-commit hook can call it cheaply.
    if args.wikilinks is not None:
        wl_paths = [Path(p) for p in args.wikilinks] if args.wikilinks else None
        scope = "given" if args.wikilinks else "staged"
        results, ok, fab = check_wikilinks(wl_paths)
        print_wikilink_report(results, ok, fab, scope=scope)
        sys.exit(0 if fab == 0 else 1)

    # --signals: standalone check, does not run full doctor
    if args.signals:
        violations = check_signal_deliverables()
        if not violations:
            print("[OK] No signal-without-deliverable violations found.")
            sys.exit(0)
        else:
            print("[FAIL] %d signal(s) without deliverable:" % len(violations))
            for v in violations:
                print("  %s: %s (%s) -- %s" % (
                    v['nucleus'], v['signal'], v['quality_score'], v['reason']))
            sys.exit(1)

    # --vocab: standalone check, does not run full doctor
    if args.vocab:
        results, ok, fail = check_vocab_kcs()
        print_vocab_report(results, ok, fail)
        sys.exit(0 if fail == 0 else 1)

    # --open-vars: standalone check (Article XIX), does not run full doctor.
    # Kept OUT of the default builder doctor so the default run stays 301 PASS.
    if args.open_vars:
        report, ok, fail = check_open_vars()
        print_open_vars_report(report, ok, fail)
        sys.exit(0 if fail == 0 else 1)

    # --models: standalone model-literal gate (plan opus_latest_dynamic), does
    # not run the full builder doctor. Kept opt-in so the default run is cheap.
    if args.models:
        report, ok, fail = check_model_literals()
        print_model_literals_report(report, ok, fail)
        sys.exit(0 if fail == 0 else 1)


    # Positional verb -> set fix mode if needed.
    global FIX_MODE, PLUGINS_STRICT, JSON_MODE, NO_PLUGINS_STRICT
    FIX_MODE = args.fix or (args.verb == "fix")
    # R-162: advisory-by-default check-registry pass, opted into strict/json below.
    # R-162 PROMOTION (2026-07-12): the PROMOTED_PLUGINS fold is default-on (no
    # flag needed); --no-plugins-strict is the escape hatch that disables it (and
    # --plugins-strict too, if both are passed -- see _check_promoted_fold_exit).
    PLUGINS_STRICT = args.plugins_strict
    NO_PLUGINS_STRICT = args.no_plugins_strict
    JSON_MODE = args.json

    # `summary` verb implies --agent-io (read-only short-form output).
    use_agent_io = args.agent_io or (args.verb == "summary")

    if use_agent_io:
        # Article Sec 3.1 + 3.4: capture output, truncate, append metadata.
        import io as _io
        import time as _time
        try:
            from cex_agent_io import agent_print, truncate_or_file
        except Exception:
            agent_print = truncate_or_file = None

        if agent_print is not None:
            buf = _io.StringIO()
            old_stdout, sys.stdout = sys.stdout, buf
            t0 = _time.time()
            rc = 0
            try:
                main()
            except SystemExit as e:
                rc = e.code if isinstance(e.code, int) else 0
            finally:
                sys.stdout = old_stdout
            captured = buf.getvalue()
            display, _full = truncate_or_file(captured, label="doctor")
            agent_print(stdout=display, exit_code=rc, started_at=t0)
            sys.exit(rc)

    main()


if __name__ == "__main__":
    try:
        from cex_agent_io import wrap_main

        def _main_wrapper(argv):
            sys.argv = [sys.argv[0]] + argv
            _doctor_cli()
            return 0

        sys.exit(wrap_main(_main_wrapper, sys.argv[1:], label="cex_doctor"))
    except ImportError:
        _doctor_cli()
