#!/usr/bin/env python3
# -*- coding: ascii -*-
"""CEX Check Registry -- typed, pluggable keystone-check system (R-162 first mechanization).

R-162 asks for the first slice of "cex_doctor v2": a typed pluggable check registry that
mechanizes N07's repeated manual keystone checks into re-runnable, JSON-emitting plugins. This
file is that first slice: a CheckPlugin dataclass + registry + JSON/CI-friendly runner, plus EIGHT
real plugins that mechanize keystones this session already ran by hand (counter_gate = R-018's
class; registry_drift = R-158's class; schema_doctor = R-157/R-171's class; provenance_doctor =
the S5 falsified-pointer class; frontmatter_doctor = R-155/R-196's class; index_freshness =
R-248's doctor-side freshness WARN; hydration_doctor = R-249/R-250's per-nucleus-per-pillar
gap-measurement class; handoff_context_doctor = R-097/R-128's Phase-0-context-before-dispatch
class).

2026-07-03 growth pass (same R-162 mission, second slice): added schema_doctor,
provenance_doctor, frontmatter_doctor -- three keystone-to-gate mechanizations plus an R-212 fix
to registry_drift (it used to re-derive the kinds_meta/TYPE_TO_TPL/Motor set-diff a second time
even though it already imported cex_kind_register; it now CALLS cex_kind_register.validate()
itself -- captures its stdout report and adapts it into structured findings -- so there is one
parser for that diff, not two).

2026-07-04 growth pass (same R-162 mission, third slice): added index_freshness -- the DOCTOR
half of R-248 (docs/SPEC_CEXAI_TOTAL_HYDRATION_INDEX_2026_07_03.md Sec 3.1 "Freshness contract").
The indexer cell already landed the CLI/library half in _tools/cex_total_index.py
(`--check-fresh` exit 0 fresh / 3 stale, `--rebuild-if-stale`); this plugin imports and reuses
those primitives (`_read_index_meta`, `_max_corpus_mtime`) rather than re-deriving corpus-mtime
math a second time, and layers exactly one additional rule on top: WARN (severity=MEDIUM, never
BLOCKING/HIGH) once the corpus has been ahead of the last build for more than 24h -- per GDP Q4,
closed 2026-07-03 (.cex/runtime/decisions/decision_manifest_total_hydration_2026_07_03.yaml
"freshness_latency": ship WARN-and-skip-on-slow, never block a save/build on index rebuild).

2026-07-04 growth pass (same R-162 mission, fourth slice): added hydration_doctor -- R-249/R-250
(spec Sec 3.2 "STREAM B -- HYDRATION-ENGINE" + Sec 4.1 WAVE 3). Generalizes R-167's proven method
(disk-audit -> rank uneven cells -> promote from a REAL >=2x-usage exemplar, never mass-synthesize)
from 1 pillar (P03) / 1 nucleus (N07) to the full 12-pillar x 7-operational-nucleus grid, by
composing the spec's 4 named signals (density-measurement coverage, file-count unevenness, stub
markers, 8f:/related: coordinate coverage) into one ranked table. Reads ONLY the total index
_tools/cex_total_index.py already builds (`_load_l1_payload`) for the corpus-wide file list; ONE
additional targeted read pass (scoped to the ~3.1k paths the index already places inside a
canonical N00-N07 nucleus/pillar directory -- never a corpus rescan) fills in the frontmatter
fields/body text the L1 record itself does not persist (density_score/8f/related, [preencher]/
TODO). Per GDP Q3, closed 2026-07-03 (same decision manifest, "prompt_loadouts_scope"): measure
ALL nuclei, but only N07 is fill-eligible this cycle. Companion new thin CLI wrapper:
_tools/cex_hydration_doctor.py --audit (writes docs/HYDRATION_MAP.md, prints the top-10).

2026-07-05 growth pass (fifth slice): added handoff_context_doctor -- register rows R-097/R-128
(docs/IMPROVEMENT_REGISTER.md), a paired finding: "No doctor/lint check verifies a N06 handoff
for external-context-required kinds actually received Phase-0 context before dispatch." Reuses
_tools/cex_preflight_mcp.py's own requires_external_context() lookup (one parser of the
kinds_meta.json flag, same precedent as schema_doctor/registry_drift) and scans N06's own
.cex/runtime/handoffs/*_n06.md + n06_task.md files for the fixed "## External Context
(pre-compiled by N07 via MCP)" heading cex_preflight_mcp.assemble_external_context emits. Live-
verified against this repo the day it was added: .cex/runtime/handoffs/CAPGEN_n06.md declares
kind=content_monetization (requires_external_context=true) and has zero "External Context"
occurrences -- a real reproduction of the gap, not a theoretical one. MEDIUM severity (same
never-folds-into---ci contract as index_freshness/hydration_doctor): .cex/runtime/ is
gitignored/ephemeral, so a clean checkout degrades to "nothing to check", never a false BLOCKING
gate on repo state.

Mechanic transplant (clean-room, CONCEPTS ONLY -- no source code copied; both source licenses are
permissive and double-verified, see the 3 kc_oss_* dossiers this session produced for full
evidence + citations):

  - Ruff (astral-sh/ruff, MIT -- verified via LICENSE + pyproject.toml `license = "MIT"`):
    a rule CODE is a category-PREFIX + digits (E501 -> pycodestyle "501"; F401 -> pyflakes "401"),
    and a JSON-format diagnostic carries a `code` + `message` + `url` plus a fix `applicability`
    tier (Safe / Unsafe / Display -- "Display" means "shown, never auto-applied"). CheckPlugin
    borrows the typed-code(id)-plus-severity shape; `fix_hint` mirrors Ruff's safest "Display"
    applicability tier ON PURPOSE -- this transplant ships NO autofix, only advisory text, per the
    reversible/read-only scope of this task.
  - pre-commit (pre-commit/pre-commit, MIT -- verified via LICENSE + setup.cfg `license = MIT`):
    `MANIFEST_HOOK_DICT` is a cfgv-validated declarative hook CONTRACT -- required fields
    (id/name/entry/language) plus optional-with-defaults fields (files/exclude/types/always_run/
    stages/fail_fast/pass_filenames/...). CheckPlugin.selector borrows this "declare what you run
    against, validated once at registration" shape, adapted to CEXAI's need (a Callable[[Path],
    bool] gate over repo STATE, not a glob/regex over a staged-file list -- CEXAI checks inspect
    registries and managed-region text, not per-file diffs).
  - Great Expectations (great-expectations/great_expectations, Apache-2.0 -- verified via LICENSE
    + setup.py `license="Apache-2.0"` + OSI classifier): `ExpectationValidationResult` is the
    per-check result shape (success / result / meta / exception_info); `ExpectationSuiteValidationResult`
    aggregates many of those into suite-level statistics (successful_expectations /
    unsuccessful_expectations / evaluated_expectations / success_percent), computed by summing each
    result's `.success` boolean. CheckFinding + this module's `summarize()` borrow that
    per-check-result-plus-suite-aggregate shape.

Boundary (binding): this file does NOT edit cex_doctor.py, cex_score.py, or cex_distill.py. It is
new, additive, read-only infrastructure. Wiring it INTO cex_doctor.py as a real plugin-discovery
pass is R-162's stated NEXT step, explicitly left to a future /mission (per this task's own
instructions) -- tonight's deliverable is the typed registry + 2 real plugins + tests + a live
dogfood run against this repo, proven to work standalone.

Usage:
    python _tools/cex_check_registry.py            # human-readable table
    python _tools/cex_check_registry.py --json      # machine-readable findings (all plugins)
    python _tools/cex_check_registry.py --ci        # exit 1 if any BLOCKING/HIGH finding fails
    python _tools/cex_check_registry.py --list      # list registered plugins (id/severity/hint)
    python _tools/cex_check_registry.py --plugin counter_gate   # run one plugin only

ASCII-only (enforced repo-wide for .py, see .claude/rules/ascii-code-rule.md).
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, List, Optional, Tuple

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT / "_tools") not in sys.path:
    sys.path.insert(0, str(ROOT / "_tools"))

# Severity Matrix -- matches .claude/rules/8f-reasoning.md verbatim (this module does not invent
# a parallel severity vocabulary; it reuses the one every nucleus already reads).
VALID_SEVERITIES: Tuple[str, ...] = ("BLOCKING", "HIGH", "MEDIUM", "OBSERVATION")


@dataclass(frozen=True)
class CheckFinding:
    """One concrete result from running a CheckPlugin against a repo root.

    The Great-Expectations-ExpectationValidationResult analog: `ok` is the success bool,
    `message` is the human-readable reason, `detail` is a free-form JSON-serializable payload
    (mirrors GE's `result` dict -- e.g. the drift/gap list a plugin found). A plugin's `run()`
    returns a LIST of these (usually 1, but a check MAY fan out -- e.g. one finding per missing
    kind -- the same one-diagnostic-per-violation shape Ruff uses)."""
    plugin_id: str
    ok: bool
    message: str
    detail: Optional[dict] = None

    def to_dict(self) -> dict:
        d = {"plugin_id": self.plugin_id, "ok": self.ok, "message": self.message}
        if self.detail is not None:
            d["detail"] = self.detail
        return d


@dataclass(frozen=True)
class CheckPlugin:
    """One pluggable keystone check -- the typed unit R-162 asks for.

    `selector(root)` gates whether this plugin applies to the current repo (pre-commit's
    MANIFEST_HOOK_DICT declarative-gate analog; defaults to always-on, matching
    R-164's CarryEntry.when precedent of "every entry ships unconditional today, the hook exists
    so a future conditional plugin does not require touching the engine loop"). `run(root)`
    executes the check and returns `List[CheckFinding]`. `fix_hint` is ADVISORY TEXT ONLY -- see
    module docstring (Ruff "Display"-tier posture, no autofix in this transplant)."""
    id: str
    severity: str
    description: str
    run: Callable[[Path], List[CheckFinding]]
    fix_hint: str = ""
    selector: Callable[[Path], bool] = lambda root: True

    def __post_init__(self) -> None:
        if self.severity not in VALID_SEVERITIES:
            raise ValueError(
                "CheckPlugin %r: invalid severity %r (must be one of %s)"
                % (self.id, self.severity, VALID_SEVERITIES)
            )
        if not self.id:
            raise ValueError("CheckPlugin.id must be non-empty")
        if not callable(self.run):
            raise ValueError("CheckPlugin %r: run must be callable" % self.id)


# --------------------------------------------------------------------------------------------- #
# Plugin 1: counter_gate -- mechanization of R-018's class (badge/managed-region number-drift).
# Wraps the EXISTING, already-correct cex_stats.py engine (compute() + _iter_text_files() +
# _scan_drift()) -- this plugin does not reimplement the drift-detection regex/logic, it re-derives
# structured findings from the same public functions `python cex_stats.py --check` already calls,
# so there is exactly one source of truth for "what counts as drift" (cex_stats.py itself).
#
# TENANT-HONESTY FIX (R-162 tail, see Plugin 15 tenant_honesty below for the full rationale):
# cex_stats is NOT in _tools/cex_distill.py's FROZEN_TOOLS_CORE (live-verified 2026-07-12 --
# a distilled tenant repo does not carry this Central-only tool). The import below used to be
# unguarded, so a tenant's own doctor run would raise ModuleNotFoundError here and -- back when
# run_registry() had no per-plugin isolation -- would have silently lost EVERY sibling plugin's
# finding too (cex_doctor.py's check_registry_advisory() catches an exception at the outer
# run_registry() call and degrades the WHOLE advisory tail to empty). run_registry() now DOES
# isolate each plugin's own crash (R-335, docs/IMPROVEMENT_REGISTER.md -- see run_registry()'s
# own docstring), so that specific total-collapse risk is a defense-in-depth backstop today,
# not a live exposure -- but this import stays guarded regardless: an expected "not carried in
# this tenant" condition should degrade to a clean ok=True "unavailable" finding, not a noisy
# synthetic plugin_crashed one. Now wrapped in the SAME try/except-degrade-never idiom
# index_freshness/hydration_doctor/runtime_cap_doctor/memory_doctor already use for their own
# Central-only-tool dependency.
# --------------------------------------------------------------------------------------------- #
def _run_counter_gate(root: Path) -> List[CheckFinding]:
    try:
        import cex_stats  # local import: keeps this module importable even if cex_stats ever moves
    except Exception as e:
        return [
            CheckFinding(
                plugin_id="counter_gate", ok=True,
                message=(
                    "cex_stats unavailable (%s) -- degrade-never, skipped (e.g. a distilled "
                    "tenant that does not carry this Central-only tool)" % e
                ),
                detail={"state": "unavailable"},
            )
        ]

    stats = cex_stats.compute()
    drifts: List[dict] = []
    for rel, ap in cex_stats._iter_text_files(root):
        try:
            text = cex_stats._read_text(ap)
        except (OSError, UnicodeDecodeError):
            continue
        if "cex:stat:" not in text and "badge/" not in text:
            continue
        for key, found, expected in cex_stats._scan_drift(text, stats):
            drifts.append({"file": rel, "key": key, "found": found, "expected": expected})

    if drifts:
        return [
            CheckFinding(
                plugin_id="counter_gate",
                ok=False,
                message="%d managed stat value(s) drifted from compute()" % len(drifts),
                detail={"stats": stats, "drift": drifts},
            )
        ]
    return [
        CheckFinding(
            plugin_id="counter_gate",
            ok=True,
            message="all managed regions + badges match compute()",
            detail={"stats": stats},
        )
    ]


# --------------------------------------------------------------------------------------------- #
# Plugin 2: registry_drift -- mechanization of R-158's class (kinds_meta vs TYPE_TO_TPL vs Motor).
#
# R-212 fix (2026-07-03): this used to import cex_kind_register (ckr) and then RE-DERIVE the same
# kinds_meta/TYPE_TO_TPL/Motor set-diff ckr.validate() already computes -- two parsers of the same
# three registries, guaranteed to drift from each other the moment either one is edited alone.
# It now CALLS ckr.validate() itself (the ONE parser) and adapts its printed report into
# structured findings, instead of re-parsing TYPE_TO_TPL/MOTOR_PY a second time. validate() only
# prints + returns an int exit code (no structured return value) and this cell does not own
# cex_kind_register.py, so stdout-capture + adapt is the only zero-duplication reuse available;
# the regex below parses validate()'s OWN fixed-format report lines (`  kinds_meta:  N kinds`,
# `  [GAP] Missing in TYPE_TO_TPL: [...]`), not the registries themselves.
#
# TENANT-HONESTY FIX (R-162 tail, see Plugin 15 tenant_honesty below): cex_kind_register is NOT in
# FROZEN_TOOLS_CORE (live-verified 2026-07-12) -- a distilled tenant does not carry it. Same
# unguarded-import-crashes-the-whole-registry risk as counter_gate above; now wrapped.
# --------------------------------------------------------------------------------------------- #
def _run_registry_drift(root: Path) -> List[CheckFinding]:
    import ast
    import contextlib
    import io
    import re as _re

    try:
        import cex_kind_register as ckr  # local import, same reasoning as counter_gate
    except Exception as e:
        return [
            CheckFinding(
                plugin_id="registry_drift", ok=True,
                message=(
                    "cex_kind_register unavailable (%s) -- degrade-never, skipped (e.g. a "
                    "distilled tenant that does not carry this Central-only tool)" % e
                ),
                detail={"state": "unavailable"},
            )
        ]

    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        ckr.validate()
    report = buf.getvalue()

    def _count(label: str) -> int:
        m = _re.search(r"^\s*%s:\s*(\d+)" % _re.escape(label), report, _re.MULTILINE)
        return int(m.group(1)) if m else 0

    def _gap(label: str) -> List[str]:
        m = _re.search(
            r"^\s*\[GAP\] Missing in %s: (\[.*\])\s*$" % _re.escape(label), report, _re.MULTILINE
        )
        if not m:
            return []
        try:
            parsed = ast.literal_eval(m.group(1))
        except (ValueError, SyntaxError):
            return []
        return list(parsed) if isinstance(parsed, list) else []

    counts = {
        "kinds_meta": _count("kinds_meta"),
        "type_to_tpl": _count("TYPE_TO_TPL"),
        "motor": _count("Motor"),
    }
    gap_ttt = _gap("TYPE_TO_TPL")
    gap_motor = _gap("Motor")

    if gap_ttt or gap_motor:
        return [
            CheckFinding(
                plugin_id="registry_drift",
                ok=False,
                message=(
                    "registries out of sync: %d kind(s) missing in TYPE_TO_TPL, "
                    "%d kind(s) missing in Motor" % (len(gap_ttt), len(gap_motor))
                ),
                detail={"counts": counts, "missing_in_type_to_tpl": gap_ttt, "missing_in_motor": gap_motor},
            )
        ]
    return [
        CheckFinding(
            plugin_id="registry_drift",
            ok=True,
            message="kinds_meta / TYPE_TO_TPL / Motor all in sync",
            detail={"counts": counts},
        )
    ]


# --------------------------------------------------------------------------------------------- #
# Plugin 3: schema_doctor -- mechanization of the R-157 (flattened-indent) / R-171 (silent 0-kind
# map) class. Reuses cex_compile.py's own LP_DIRS constant (the 12 canonical pillar dirs) and its
# load_schema() function -- same YAML the compiler itself loads at build time -- so a schema that
# is flattened/mis-indented (fails to parse) OR one that parses but no longer maps any kind to a
# machine_format (silently drops every kind from compilation) is caught here BEFORE a build
# depends on it, instead of only being noticed downstream as "the compiler silently produced 0
# kinds for this pillar".
# --------------------------------------------------------------------------------------------- #
def _run_schema_doctor(root: Path) -> List[CheckFinding]:
    import yaml

    import cex_compile as cc  # local import, same reasoning as counter_gate

    broken: List[dict] = []
    counts: dict = {}
    for lp in cc.LP_DIRS:
        pillar_dir = root / lp
        schema_path = pillar_dir / "_schema.yaml"
        if not schema_path.exists():
            broken.append({"pillar_dir": lp, "reason": "schema file missing: %s" % schema_path})
            continue
        try:
            mapped = cc.load_schema(pillar_dir)
        except (OSError, UnicodeDecodeError, yaml.YAMLError) as e:
            broken.append({"pillar_dir": lp, "reason": "failed to parse: %s" % e})
            continue
        counts[lp] = len(mapped)
        if len(mapped) == 0:
            broken.append(
                {"pillar_dir": lp, "reason": "parsed OK but mapped 0 kinds (R-171 class)"}
            )

    if broken:
        return [
            CheckFinding(
                plugin_id="schema_doctor",
                ok=False,
                message="%d of %d pillar schema(s) broken" % (len(broken), len(cc.LP_DIRS)),
                detail={"counts": counts, "broken": broken},
            )
        ]
    return [
        CheckFinding(
            plugin_id="schema_doctor",
            ok=True,
            message="all %d pillar schemas parse and map >0 kinds" % len(cc.LP_DIRS),
            detail={"counts": counts},
        )
    ]


# --------------------------------------------------------------------------------------------- #
# Plugin 4: provenance_doctor -- mechanization of the S5 falsified-pointer lesson (a claimed
# provenance/origin field that names a path but the path does not actually exist). Scoped to
# .cex/kinds_meta.json to stay deterministic + fast (per the mission's explicit scope
# instruction) rather than crawling every artifact's frontmatter in the repo. Checks TWO shapes:
# (1) the known path-pointer fields (`builder` -> archetypes/builders/<slug>/, `sdk_module` ->
# cex_sdk/<dotted path>.py or a package dir); (2) ANY string field (including `upstream_source`)
# whose VALUE itself looks like a bare repo-relative file path (contains a path separator and
# ends in a known file extension) -- most `upstream_source` values today are prose spec
# citations ("OTel GenAI semconv v1.37 + C2PA v2.3"), not paths, and are correctly left unchecked
# by design; only a value that actually NAMES a path is held to "must resolve".
# --------------------------------------------------------------------------------------------- #
_PATH_LIKE_RE = re.compile(r"^[\w./-]+\.(md|py|ya?ml|json|txt)$")


def _resolve_kind_pointer(root: Path, field: str, value: object) -> Optional[Path]:
    """Return the repo-relative Path a kinds_meta field value points at, or None if this
    field/value does not name a resolvable path (nothing for provenance_doctor to check)."""
    if not isinstance(value, str) or not value.strip():
        return None
    v = value.strip()
    if field == "builder":
        return root / "archetypes" / "builders" / v
    if field == "sdk_module":
        rel = v.replace(".", "/")
        as_file = root / (rel + ".py")
        return as_file if as_file.exists() else root / rel / "__init__.py"
    if _PATH_LIKE_RE.match(v):
        return root / v
    return None


def _run_provenance_doctor(root: Path) -> List[CheckFinding]:
    import json as _json

    meta_path = root / ".cex" / "kinds_meta.json"
    if not meta_path.exists():
        return [
            CheckFinding(
                plugin_id="provenance_doctor",
                ok=False,
                message="kinds_meta.json not found at %s" % meta_path,
            )
        ]
    try:
        meta = _json.loads(meta_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, ValueError) as e:
        return [
            CheckFinding(
                plugin_id="provenance_doctor",
                ok=False,
                message="kinds_meta.json failed to parse: %s" % e,
            )
        ]

    broken: List[dict] = []
    checked = 0
    for kind in sorted(meta):
        entry = meta[kind]
        if not isinstance(entry, dict):
            continue
        for field in sorted(entry):
            candidate = _resolve_kind_pointer(root, field, entry[field])
            if candidate is None:
                continue
            checked += 1
            if not candidate.exists():
                broken.append(
                    {"kind": kind, "field": field, "value": entry[field], "resolved": str(candidate)}
                )

    if broken:
        return [
            CheckFinding(
                plugin_id="provenance_doctor",
                ok=False,
                message=(
                    "%d kinds_meta pointer(s) resolve to a missing path (of %d checked)"
                    % (len(broken), checked)
                ),
                detail={"checked": checked, "broken": broken},
            )
        ]
    return [
        CheckFinding(
            plugin_id="provenance_doctor",
            ok=True,
            message="all %d resolvable kinds_meta path-pointer(s) exist" % checked,
            detail={"checked": checked},
        )
    ]


# --------------------------------------------------------------------------------------------- #
# Plugin 5: frontmatter_doctor -- mechanization of the R-155 / R-196 class (a frontmatter
# close-delimiter mis-detected by a naive substring scan instead of the line-anchored helper).
# Reuses cex_shared.py's own parse_frontmatter_diagnostic() + _frontmatter_close_index() -- the
# SAME line-anchored helper every other tool in the repo relies on (R-155) -- to (a) confirm
# frontmatter actually parses, and (b) prove, file by file, that a naive `text.find("---", 3)`
# substring scan (the OLD pre-R-155 method: matches the FIRST "---" occurrence anywhere, even
# inside a quoted value or a markdown table divider) lands on the SAME index the line-anchored
# helper does. Any divergence means this file is a live landmine for the old method's bug class
# recurring -- a regression guard, not just a one-time audit.
#
# Scoped to N00_genesis/ + archetypes/builders/ (~5,000 .md files) for determinism + speed
# (a "sample scan" per the mission instruction, not a full-repo crawl of every tenant/docs .md).
# templates/tpl_*.md are excluded on purpose: they carry {{PLACEHOLDER}} frontmatter by design
# (not concrete artifacts) and are EXPECTED to fail YAML parsing.
# --------------------------------------------------------------------------------------------- #
def _run_frontmatter_doctor(root: Path) -> List[CheckFinding]:
    import cex_shared as csh  # local import, same reasoning as counter_gate

    sample_roots = [root / "N00_genesis", root / "archetypes" / "builders"]
    candidates: List[Path] = []
    for base in sample_roots:
        if base.exists():
            candidates.extend(sorted(base.rglob("*.md")))

    scanned = 0
    parse_failures: List[dict] = []
    close_mismatches: List[dict] = []
    for f in candidates:
        rel = f.relative_to(root).as_posix()
        if "/templates/" in rel or f.name.startswith("tpl_"):
            continue  # template scaffolds: {{PLACEHOLDER}} frontmatter by design, not artifacts
        try:
            text = f.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        stripped = text.strip()
        if not stripped.startswith("---"):
            continue
        scanned += 1

        fm, reason = csh.parse_frontmatter_diagnostic(text)
        if fm is None:
            parse_failures.append({"file": rel, "reason": reason})

        anchored = csh._frontmatter_close_index(stripped)
        naive = stripped.find("---", 3)  # R-196 class: old substring scan, no line anchor
        if anchored != naive:
            close_mismatches.append({"file": rel, "anchored_index": anchored, "naive_index": naive})

    issues = parse_failures or close_mismatches
    if issues:
        return [
            CheckFinding(
                plugin_id="frontmatter_doctor",
                ok=False,
                message=(
                    "%d frontmatter parse failure(s), %d close-delimiter mismatch(es) "
                    "(of %d scanned)" % (len(parse_failures), len(close_mismatches), scanned)
                ),
                detail={
                    "scanned": scanned,
                    "parse_failures": parse_failures,
                    "close_mismatches": close_mismatches,
                },
            )
        ]
    return [
        CheckFinding(
            plugin_id="frontmatter_doctor",
            ok=True,
            message=(
                "%d artifact(s) scanned: frontmatter parses + close-delimiter detection matches "
                "the line-anchored helper" % scanned
            ),
            detail={"scanned": scanned},
        )
    ]


# --------------------------------------------------------------------------------------------- #
# Plugin 6: index_freshness -- R-248's DOCTOR-SIDE half of the freshness contract (spec
# docs/SPEC_CEXAI_TOTAL_HYDRATION_INDEX_2026_07_03.md Sec 3.1; GDP-closed 2026-07-03,
# .cex/runtime/decisions/decision_manifest_total_hydration_2026_07_03.yaml "freshness_latency":
# ship WARN-and-skip-on-slow, never block a save/build on an index rebuild).
#
# The indexer cell already landed the CLI/library half in _tools/cex_total_index.py
# (`--check-fresh` exit 0 fresh / 3 stale, `--rebuild-if-stale`). This plugin does NOT
# reimplement that staleness math -- it imports and reuses cex_total_index's own primitives
# (`_read_index_meta`, `_max_corpus_mtime`) and layers exactly ONE additional rule on top: the
# doctor only WARNs once the corpus has been ahead of the last build for MORE THAN 24 HOURS.
# `--check-fresh` itself has NO grace period by design (it flags "any tracked file newer than
# built_at" for its own stricter CLI contract); the doctor's ADVISORY tail wants a coarser,
# less-noisy signal so routine same-day edits do not manufacture daily WARN churn.
#
# `root` is accepted (matching every other plugin's Callable[[Path], ...] shape) but UNUSED --
# same precedent as registry_drift: cex_total_index.py's helpers are hardcoded to their own
# module's repo root (like cex_kind_register's KINDS_META/TYPE_TO_TPL/MOTOR_PY), not
# root-parameterized, so tests isolate this plugin by monkeypatching cex_total_index's
# functions directly (see TestIndexFreshnessPlugin), exactly like TestRegistryDriftPlugin
# monkeypatches cex_kind_register's path constants instead of threading a root through.
#
# THREE STATES (mission-mandated; none BLOCKING/HIGH -- see the CHECK_REGISTRY entry below,
# severity=MEDIUM, so this plugin can NEVER fail cex_doctor.py's exit code, even under
# --plugins-strict: _check_registry_fold_exit only folds BLOCKING/HIGH):
#   1. ABSENT -- .cex/total_index/index_meta.json does not exist yet. Ordinary pre-first-build
#      state (mirrors cex_intent_resolver's own lazy-loader degrade-never posture: "not built
#      yet" is not an error) -- ok=True, an informational note, never a WARN.
#   2. FRESH  -- present, and the corpus's newest tracked-file mtime is within 24h of built_at
#      (or not ahead of it at all) -- ok=True.
#   3. STALE  -- present, and the corpus's newest mtime leads built_at by >24h -- ok=False. This
#      renders via the registry's own "FAIL[MEDIUM]" tag (cex_check_registry.py/cex_doctor.py's
#      shared print convention, unchanged by this plugin), but MEDIUM severity means it NEVER
#      folds into the doctor's exit code, default OR --plugins-strict -- the advisory-only
#      contract this mission requires. Message carries the age (hours) + the exact rebuild
#      one-liner.
# An unusable built_at (corrupt/unparseable index_meta.json) degrades into the SAME stale bucket
# (mirrors cex_total_index.cmd_check_fresh's own choice: "no usable built_at -- treating as
# stale"). Any OTHER unexpected error (cex_total_index fails to import, its internals raise
# something not already handled) degrades to an "unavailable" ok=True bucket instead --
# degrade-never: an infra hiccup in an ADVISORY plugin must never manufacture a false WARN. A
# crash here is ALSO no longer a total-collapse risk for the other plugins' findings even without
# this plugin's own degrade-never posture -- run_registry() gained generic per-plugin exception
# isolation (R-335, see its own docstring) -- but this plugin still prefers to degrade to a clean
# "unavailable" ok=True finding rather than lean on that generic safety net.
#
# R-334 FIX (docs/IMPROVEMENT_REGISTER.md): trusting index_meta.json's own `built_at` field alone
# is NOT sufficient -- live-reproduced on this repo 2026-07-12: `built_at` read 0.9h old (i.e.
# "fresh" by the ORIGINAL built_at-only logic below) while l1_documents.json's and
# l2_subdocuments.json's own on-disk mtimes were 8 DAYS old (last actually rewritten 07-04/05) --
# "index_meta touched by something else" without the heavy files themselves being rebuilt. A
# stale slug was found live in l1 as a direct consequence: indexed content had silently diverged
# from the corpus while the doctor reported clean. This plugin therefore now ALSO stats each HEAVY
# index file directly -- sourced from cex_total_index's own `L1_PATH`/`L2_PATH` constants (never
# re-derived, same reuse-not-reimplement precedent as `_read_index_meta`/`_max_corpus_mtime`
# above) -- and reports the STALEST of {built_at, l1_documents.json mtime, l2_subdocuments.json
# mtime} against the corpus's newest tracked mtime. A heavy file that does not exist yet on disk
# degrades to a "not_built" per-file marker (never a crash, never treated as 0.0-age-fresh) and is
# simply excluded from the stalest-of comparison; L0 (`l0_patterns.json`) is NOT included here --
# it is O(316) kind-pattern reads, not O(corpus), and the register row scopes "heavy" to L1/L2
# specifically. The existing built_at-vs-corpus math is preserved byte-for-byte as ONE of the
# three signals now compared (never removed), so a genuinely stale built_at is still caught
# exactly as before -- this is a superset fix, not a replacement.
# --------------------------------------------------------------------------------------------- #
_INDEX_STALE_HOURS = 24.0

# R-334: the heavy per-file indices this plugin fronts, beyond index_meta.json's own self-reported
# built_at -- (label, cex_total_index module attribute name) so tests can monkeypatch
# `cex_total_index.L1_PATH`/`L2_PATH` exactly like TestIndexFreshnessPlugin already monkeypatches
# `_read_index_meta`/`_max_corpus_mtime` on the same module object.
_HEAVY_INDEX_FILE_ATTRS: Tuple[Tuple[str, str], ...] = (
    ("l1_documents.json", "L1_PATH"),
    ("l2_subdocuments.json", "L2_PATH"),
)


def _index_freshness_age_hours(built_ts: float, newest_mtime: float) -> float:
    """Hours by which the corpus's newest tracked-file mtime leads `built_ts`; never negative
    (0.0 whenever the index is not behind the corpus at all). Pure function -- unit-testable
    without touching disk; mirrors the comparison cex_total_index.cmd_check_fresh already makes
    (`newest > built_ts`), expressed as a MAGNITUDE (hours) rather than a bool, since the doctor
    needs the 24h threshold cmd_check_fresh itself does not apply."""
    return max(0.0, newest_mtime - built_ts) / 3600.0


def _index_freshness_finding(
    ok: bool, state: str, message: str,
    age_hours: Optional[float] = None, built_at: Optional[str] = None,
    extra: Optional[dict] = None,
) -> CheckFinding:
    """Shared CheckFinding shape for all index_freshness states below. `extra` (R-334) merges
    additional detail keys (e.g. per-heavy-file ages) -- optional, additive, never overrides
    state/age_hours/built_at (callers that need those keys pass them via the named params
    above, not through extra)."""
    detail: dict = {"state": state}
    if age_hours is not None:
        detail["age_hours"] = age_hours
    if built_at is not None:
        detail["built_at"] = built_at
    if extra:
        detail.update(extra)
    return CheckFinding(plugin_id="index_freshness", ok=ok, message=message, detail=detail)


def _heavy_index_file_ages(ti, newest_mtime: float) -> "OrderedDict[str, dict]":
    """Per-heavy-file staleness (R-334): stats each heavy index file's OWN on-disk mtime --
    sourced from cex_total_index's `L1_PATH`/`L2_PATH` constants via getattr (so a test's
    `monkeypatch.setattr(ti, "L1_PATH", ...)` is honored) -- rather than trusting
    index_meta.json's self-reported `built_at`, which can be refreshed independently of the
    heavy files themselves (see the R-334 module comment above `_INDEX_STALE_HOURS`). Returns
    an ordered {label: {"age_hours": float}} or {label: {"state": "not_built"}} map; never
    raises (a missing/unreadable heavy file degrades to "not_built" for that one entry only,
    degrade-never, matching this plugin's existing posture for every other failure mode)."""
    from collections import OrderedDict

    ages: "OrderedDict[str, dict]" = OrderedDict()
    for label, attr_name in _HEAVY_INDEX_FILE_ATTRS:
        path = getattr(ti, attr_name, None)
        if path is None:
            ages[label] = {"state": "not_built"}
            continue
        try:
            heavy_mtime = path.stat().st_mtime
        except Exception:
            ages[label] = {"state": "not_built"}
            continue
        ages[label] = {"age_hours": round(_index_freshness_age_hours(heavy_mtime, newest_mtime), 2)}
    return ages


def _run_index_freshness(root: Path) -> List[CheckFinding]:
    try:
        import cex_total_index as ti  # local import, same reasoning as counter_gate
    except Exception as e:
        return [_index_freshness_finding(
            True, "unavailable",
            "total index tooling unavailable (%s) -- degrade-never, treated as "
            "pre-first-build" % e,
        )]

    try:
        meta = ti._read_index_meta()
    except Exception as e:
        return [_index_freshness_finding(
            True, "unavailable",
            "total index metadata unreadable (%s) -- degrade-never, treated as "
            "pre-first-build" % e,
        )]

    if meta is None:
        return [_index_freshness_finding(
            True, "absent",
            "total index not built yet (ordinary pre-first-build state) -- run: "
            "python _tools/cex_total_index.py --build",
        )]

    built_at = meta.get("built_at") if isinstance(meta, dict) else None
    from datetime import datetime  # local import, same reasoning as counter_gate

    try:
        built_ts = datetime.fromisoformat(built_at).timestamp()
    except (TypeError, ValueError):
        return [_index_freshness_finding(
            False, "unusable",
            "total index metadata has no usable built_at (%r) -- treating as stale; run: "
            "python _tools/cex_total_index.py --rebuild-if-stale" % (built_at,),
            built_at=built_at if isinstance(built_at, str) else None,
        )]

    try:
        newest = ti._max_corpus_mtime()
    except Exception as e:
        return [_index_freshness_finding(
            True, "unavailable",
            "could not compute corpus mtime (%s) -- degrade-never, skipping freshness check "
            "this run" % e,
        )]

    meta_age_hours = _index_freshness_age_hours(built_ts, newest)

    # R-334: ALSO compare against each HEAVY file's own on-disk mtime -- never trust built_at
    # alone (see the module comment above _INDEX_STALE_HOURS for the live-reproduced bug this
    # closes). `heavy_signal` stays False when built_at itself is at least as stale as every
    # heavy file AND every heavy file exists -- the ORDINARY, healthy state -- in which case the
    # reported message/detail shape is BYTE-IDENTICAL to the pre-R-334 built_at-only shape (a
    # true no-op for the common case: a fresh build always writes L1/L2 no later than it stamps
    # built_at, so heavy_age <= meta_age in the healthy state). Enrichment (extra detail keys +
    # "stalest source" wording) fires ONLY when there is something genuinely worth surfacing: a
    # heavy file that OUT-STALES built_at, or a heavy file that does not exist yet -- exactly the
    # R-334 divergence class, never the everyday case.
    heavy_ages = _heavy_index_file_ages(ti, newest)
    stalest_hours = meta_age_hours
    stalest_source = "index_meta.json (built_at)"
    heavy_signal = False
    for label, info in heavy_ages.items():
        heavy_age = info.get("age_hours")
        if heavy_age is None:
            heavy_signal = True  # a heavy file is missing/not yet built -- worth surfacing
            continue
        if heavy_age > stalest_hours:
            stalest_hours = heavy_age
            stalest_source = label
            heavy_signal = True

    is_stale = stalest_hours > _INDEX_STALE_HOURS

    if not heavy_signal:
        # Ordinary, healthy case -- identical to the pre-R-334 built_at-only message/detail.
        if is_stale:
            return [_index_freshness_finding(
                False, "stale",
                "total index stale by %.1fh (>%.0fh) -- run: python _tools/cex_total_index.py "
                "--rebuild-if-stale" % (stalest_hours, _INDEX_STALE_HOURS),
                age_hours=round(stalest_hours, 2), built_at=built_at,
            )]
        return [_index_freshness_finding(
            True, "fresh",
            "total index fresh (age %.1fh, built_at=%s)" % (stalest_hours, built_at),
            age_hours=round(stalest_hours, 2), built_at=built_at,
        )]

    # A heavy file genuinely out-stales built_at, or is missing/not yet built -- the R-334
    # divergence this fix exists to catch. Enrich message + detail.
    extra = {
        "meta_age_hours": round(meta_age_hours, 2),
        "heavy_files": dict(heavy_ages),
        "stalest_source": stalest_source,
    }
    if is_stale:
        return [_index_freshness_finding(
            False, "stale",
            "total index stale by %.1fh (>%.0fh; stalest source: %s) -- run: python "
            "_tools/cex_total_index.py --rebuild-if-stale"
            % (stalest_hours, _INDEX_STALE_HOURS, stalest_source),
            age_hours=round(stalest_hours, 2), built_at=built_at, extra=extra,
        )]
    return [_index_freshness_finding(
        True, "fresh",
        "total index fresh (age %.1fh, built_at=%s, stalest source: %s)"
        % (stalest_hours, built_at, stalest_source),
        age_hours=round(stalest_hours, 2), built_at=built_at, extra=extra,
    )]


# --------------------------------------------------------------------------------------------- #
# Plugin 7: hydration_doctor -- R-249/R-250 (HYDRATION-ENGINE, spec
# docs/SPEC_CEXAI_TOTAL_HYDRATION_INDEX_2026_07_03.md Sec 3.2 "STREAM B" + Sec 4.1 WAVE 3; GDP-closed
# 2026-07-03, .cex/runtime/decisions/decision_manifest_total_hydration_2026_07_03.yaml
# "prompt_loadouts_scope": "Wave 3 = measure the per-nucleus-per-pillar thinness map... for ALL, but
# FILL only N07 this cycle"). Generalizes R-167's method (disk-audit -> rank uneven cells -> promote
# from a REAL >=2x-usage exemplar, never mass-synthesize) from 1 pillar (P03) / 1 nucleus (N07) to
# the full 12-pillar x 7-operational-nucleus grid, by composing the FOUR signals the spec names
# (Sec 3.2 Mechanism, numbered 1-4 there; s1-s4 here) into one ranked nucleus x pillar table.
#
# MEASUREMENT, NOT GATING (mission-mandated): this plugin NEVER fails/warns cex_doctor.py's exit
# code (severity=MEDIUM below, same posture as index_freshness) and its own `ok` is unconditionally
# True whenever the measurement completes -- the interesting output is the ranked `detail` payload,
# not a pass/fail boolean. `ok` deliberately does NOT encode "is N07 still the thinnest nucleus" --
# that would make this check start WARNing the moment a future hydration wave actually fixes N07,
# a perverse incentive. The R-167-reproduction sanity gate this mission requires is verified ONCE,
# by a dedicated LIVE regression test against the real repo (TestHydrationDoctorLiveSanity in
# test_cex_check_registry.py) -- not baked into the plugin's per-run ok/fail semantics.
#
# ONE-SCAN PRINCIPLE (spec Sec 3.1): reads ONLY cex_total_index's already-built L1 payload
# (.cex/total_index/l1_documents.json via `cex_total_index._load_l1_payload`) for the corpus-wide
# file list + tier/kind/pillar -- signal s2 (file-count unevenness) is fully computable from that
# alone, no disk re-read needed. Signals s1 (density_score coverage) / s3 (stub markers) / s4 (8f:/
# related: coverage) need frontmatter fields and body text the L1 record does NOT persist (see
# cex_total_index._build_l1_record -- it captures path/id/tier/kind/pillar/nucleus/title/tldr/
# headings/mtime only, nothing else). The spec explicitly sanctions exactly one exception to "read
# the index, never rescan the corpus" for this: ONE additional targeted read pass over ONLY the
# (few-thousand) paths the index already told us sit inside a canonical N00-N07 nucleus/pillar
# directory -- never a rescan of the full ~12k-file tracked corpus.
#
# NUCLEUS FROM PATH, NOT FRONTMATTER (mission-mandated): an L1 record's own `nucleus` field is
# frontmatter-sourced and sparsely populated (frequently None even on well-formed Tier-A records --
# verified live: N07_admin/P01_knowledge/kc_admin.md's own L1 record carries `"nucleus": null`).
# `nucleus` is therefore DERIVED from the path's own directory prefix instead, via the canonical
# NUCLEUS_DIRS whitelist below (never a loose regex-only match) -- this is also what correctly
# skips the stray `N03_builder/` directory flagged by R-168 with zero special-casing: it is not
# one of the 8 canonical nucleus dirs, so no path under it is ever bucketed (live-verified: 0 hits).
#
# N05 CYBERSEC EXEMPTION (spec Sec 3.2 signal 4, "explicitly exempted via a documented constant"):
# N05_operations/cybersec(_distilled)/ is an externally-derived research corpus (3,589 files, live-
# verified) living as a SIBLING top-level directory to N05_operations' 12 pillar dirs -- it already
# structurally falls outside the N0X_.../P0Y_.../ path shape this plugin buckets by (cybersec files
# are not nested under any P0Y_ pillar dir), so no signal here silently drags on cybersec content.
# N05_CYBERSEC_EXEMPT_PREFIXES makes that exclusion a DOCUMENTED, VISIBLE decision instead of an
# accidental byproduct of the path regex: every run tallies + reports how many files were exempted
# (never silent), guarding against a future path-shape change accidentally re-including them.
# --------------------------------------------------------------------------------------------- #

NUCLEUS_DIRS: dict = {
    "N00": "N00_genesis", "N01": "N01_intelligence", "N02": "N02_marketing",
    "N03": "N03_engineering", "N04": "N04_knowledge", "N05": "N05_operations",
    "N06": "N06_commercial", "N07": "N07_admin",
}
OPERATIONAL_NUCLEI: tuple = ("N01", "N02", "N03", "N04", "N05", "N06", "N07")
PILLAR_CODES: tuple = tuple("P%02d" % i for i in range(1, 13))

# See "N05 CYBERSEC EXEMPTION" above. Documented, visible, never silent.
N05_CYBERSEC_EXEMPT_PREFIXES: tuple = (
    "N05_operations/cybersec/", "N05_operations/cybersec_distilled/",
)

_NUCLEUS_PILLAR_PATH_RE = re.compile(r"^(N0[0-7]_[A-Za-z]+)/(P\d{2})_[A-Za-z_]+/")
_DIR_TO_NUCLEUS_CODE = {v: k for k, v in NUCLEUS_DIRS.items()}
_PREENCHER_MARKER = "[preencher]"
_TODO_MARKER_RE = re.compile(r"\bTODO\b")
_HYDRATION_SIGNAL_WEIGHT = 0.25  # equal 25% weight per signal -- see _composite_severity docstring


def _bucket_l1_docs(l1_docs: list) -> dict:
    """Group L1 doc records by (nucleus_code, pillar_code) -- the mission's own read: "L1 docs
    carry path/kind/pillar/tier; derive nucleus from the path prefix N0X_*/; skip non-nucleus
    paths". A path's nucleus segment must be one of the 8 canonical NUCLEUS_DIRS values (not just
    any N0[0-7]_-shaped prefix) -- this is what skips the stray `N03_builder/` directory (R-168)
    with zero special-casing: it simply never appears as a dict value here, so no path under it is
    ever matched."""
    buckets: dict = {}
    for doc in l1_docs:
        path = doc.get("path") or ""
        m = _NUCLEUS_PILLAR_PATH_RE.match(path)
        if not m or m.group(1) not in _DIR_TO_NUCLEUS_CODE:
            continue
        cell = (_DIR_TO_NUCLEUS_CODE[m.group(1)], m.group(2))
        buckets.setdefault(cell, []).append(doc)
    return buckets


def _count_cybersec_exempt(l1_docs: list) -> int:
    return sum(
        1 for d in l1_docs
        if any((d.get("path") or "").startswith(p) for p in N05_CYBERSEC_EXEMPT_PREFIXES)
    )


def _pillar_medians(buckets: dict) -> dict:
    """Per-pillar median file count across the 7 OPERATIONAL nuclei only (N00 deliberately
    excluded from the comparison set: it is the archetype/master baseline every other nucleus is
    modeled after, consistently 5-10x larger per pillar -- including it would inflate every
    pillar's median and mark nearly every N01-N07 cell as "thin" relative to the archetype, diluting
    exactly the signal that should isolate N07 as uniquely thin among its OPERATIONAL peers, which
    is how R-167 itself framed the comparison: N01:10 N02:16 N03:13 N04:10 N05:8 N06:11 N07:2, with
    N00:71 cited only as extra context, never as part of the "uneven" comparison set)."""
    import statistics

    medians: dict = {}
    for pillar in PILLAR_CODES:
        vals = [len(buckets.get((n, pillar), [])) for n in OPERATIONAL_NUCLEI]
        medians[pillar] = float(statistics.median(vals)) if vals else 0.0
    return medians


def _clamp01(x: float) -> float:
    return max(0.0, min(1.0, x))


def _severity_s2_uneven(count: int, pillar_median: float) -> float:
    """s2 (file-count unevenness, spec signal 2): how far BELOW the cross-(operational-nucleus)
    median this cell's raw file count sits, as a 0..1 fraction (0 = at/above median, 1 = zero files
    against a nonzero median). Generalizes R-167's own by-hand P03 comparison to every pillar."""
    if pillar_median <= 0:
        return 0.0
    return _clamp01(1.0 - (count / pillar_median))


def _severity_s1_density_gap(typed_count: int, density_measured: int) -> float:
    """s1 (density-measurement coverage, spec signal 1): share of this cell's TYPED artifacts with
    NO density_score at all (numeric, non-null -- a present-but-null value, mirroring this repo's
    own `quality: null` convention, still counts as unmeasured). An empty cell (typed_count == 0)
    contributes 0.0 here (not 1.0): the absence-of-content problem is already captured by s2; this
    signal is specifically about EXISTING artifacts that have never been measured -- "unmeasured
    != thin", per the spec's own explicit instruction not to conflate the two."""
    if typed_count <= 0:
        return 0.0
    return _clamp01(1.0 - (density_measured / typed_count))


def _severity_s3_stub_markers(file_count: int, preencher_files: int, todo_files: int) -> float:
    """s3 (stub markers, spec signal 3): share of this cell's files (typed + governance -- the
    spec frames the 21/225 file counts repo-wide, not typed-only) carrying an unintentional
    `[preencher]` and/or bare-word `TODO` marker. A file with both markers counts once in each
    tally (matching the spec's own per-marker file-count framing), so this can slightly exceed a
    strict union fraction in a pathological case -- _clamp01 keeps the reported severity bounded."""
    if file_count <= 0:
        return 0.0
    return _clamp01((preencher_files + todo_files) / file_count)


def _severity_s4_coord_gap(typed_count: int, coord_ok: int) -> float:
    """s4 (coordinate coverage, spec signal 4): share of this cell's TYPED artifacts missing EITHER
    `8f:` or `related:` (both required for coord_ok) -- the N05 cybersec tree never reaches this
    function at all (see N05 CYBERSEC EXEMPTION above), so its 1.9%-8f-coverage does not need a
    second, separate exclusion here."""
    if typed_count <= 0:
        return 0.0
    return _clamp01(1.0 - (coord_ok / typed_count))


def _composite_severity(s1: float, s2: float, s3: float, s4: float) -> float:
    """Composite = equal-weighted mean of the 4 signals (documented in docs/HYDRATION_MAP.md too,
    where the ranked table is sorted worst-first by this value). Deliberately simple/auditable,
    NOT tuned toward any nucleus's rank -- the mission's own sanity gate (N07 thinnest-overall +
    N07 dominance of the s2 SIGNAL specifically) is checked against s2 and raw per-nucleus totals
    directly (see compute_hydration_report's `sanity` block), independent of this composite's
    weighting, so there is no temptation to fudge weights to force a result."""
    return round(_HYDRATION_SIGNAL_WEIGHT * (s1 + s2 + s3 + s4), 4)


def _scan_cell_body_signals(root: Path, cell_docs: list) -> dict:
    """ONE read pass over every doc already bucketed into ONE (nucleus, pillar) cell -- the
    "targeted pass over N0*_ tracked .md paths from the index list" the mission sanctions, scoped
    by the caller to ONLY the ~3.1k paths _bucket_l1_docs already matched (never the full ~11.9k-
    doc L1 corpus). Tier-B (no `kind:`) files are still read for the s3 stub-marker scan (spec Sec
    3.2 signal 3 is framed repo-wide, not typed-only) but never contribute to s1/s4 (both spec-
    scoped to TYPED artifacts). A file that no longer exists / is unreadable degrades to
    "unreadable" -- excluded from every count, never raises (the L1 index may legitimately be a
    few commits older than the working tree)."""
    import cex_shared as csh  # local import, same reasoning as every other plugin in this module

    typed_count = density_measured = coord_ok = preencher_files = todo_files = unreadable = 0
    for doc in cell_docs:
        abs_path = root / doc.get("path", "")
        try:
            text = abs_path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            unreadable += 1
            continue
        body = csh.strip_frontmatter(text)
        if _PREENCHER_MARKER in body:
            preencher_files += 1
        if _TODO_MARKER_RE.search(body):
            todo_files += 1
        if doc.get("tier") == "A":
            typed_count += 1
            fm = csh.parse_frontmatter(text) or {}
            if isinstance(fm.get("density_score"), (int, float)):
                density_measured += 1
            if bool(fm.get("8f")) and bool(fm.get("related")):
                coord_ok += 1
    return {
        "file_count": len(cell_docs), "typed_count": typed_count,
        "density_measured": density_measured, "coord_ok": coord_ok,
        "preencher_files": preencher_files, "todo_files": todo_files,
        "unreadable": unreadable,
    }


def _peer_kind_pattern(buckets: dict, pillar: str, exclude_nucleus: str, top_n: int = 3) -> list:
    """Best-effort, INDEX-ONLY signal for the Wave-fill shortlist: which `kind`s populate this
    SAME pillar across the OTHER operational nuclei, most-common first. This is a candidate
    POINTER for a future fill wave, NOT a verified >=2x-real-usage exemplar in the R-167 sense --
    that verification is Wave 3 fill work, explicitly out of scope for this measure-only cell."""
    from collections import Counter

    counter: Counter = Counter()
    for nucleus in OPERATIONAL_NUCLEI:
        if nucleus == exclude_nucleus:
            continue
        for doc in buckets.get((nucleus, pillar), []):
            if doc.get("tier") == "A" and doc.get("kind"):
                counter[doc["kind"]] += 1
    return counter.most_common(top_n)


def compute_hydration_report(root: Path) -> dict:
    """THE shared computation R-249/R-250 mandate be ONE implementation with two entrypoints (this
    plugin's `run`, and cex_hydration_doctor.py's --audit CLI -- "make it a thin wrapper importing
    the plugin logic"). See the Plugin 7 module comment above for the full architecture: L1-only
    for s2, one targeted read pass for s1/s3/s4, path-derived nucleus, documented N05-cybersec
    exemption.

    Returns {"available": False, "reason": ...} if the total index has never been built (ordinary
    pre-first-build state, degrade-never -- mirrors index_freshness's own "absent" bucket), else
    {"available": True, "index_built_at", "cells" (sorted worst-first by composite severity, ALL
    8 nuclei x 12 pillars = 96 rows), "cybersec_exempt", "operational_totals", "sanity",
    "wave_fill_shortlist"}.
    """
    try:
        import cex_total_index as ti  # local import, same reasoning as index_freshness
    except Exception as e:
        return {"available": False, "reason": "cex_total_index unavailable (%s)" % e}

    try:
        l1 = ti._load_l1_payload()
    except Exception as e:
        return {"available": False, "reason": "L1 payload unreadable (%s)" % e}

    if not l1 or not l1.get("docs"):
        return {
            "available": False,
            "reason": "total index L1 layer not built yet -- run: "
                      "python _tools/cex_total_index.py --build",
        }

    docs = l1["docs"]
    buckets = _bucket_l1_docs(docs)
    cybersec_exempt_count = _count_cybersec_exempt(docs)
    medians = _pillar_medians(buckets)

    cells = []
    for nucleus_code in NUCLEUS_DIRS:
        for pillar in PILLAR_CODES:
            cell_docs = buckets.get((nucleus_code, pillar), [])
            agg = _scan_cell_body_signals(root, cell_docs)
            s1 = _severity_s1_density_gap(agg["typed_count"], agg["density_measured"])
            s2 = _severity_s2_uneven(agg["file_count"], medians.get(pillar, 0.0))
            s3 = _severity_s3_stub_markers(agg["file_count"], agg["preencher_files"], agg["todo_files"])
            s4 = _severity_s4_coord_gap(agg["typed_count"], agg["coord_ok"])
            cells.append({
                "nucleus": nucleus_code, "pillar": pillar,
                "file_count": agg["file_count"], "typed_count": agg["typed_count"],
                "density_measured": agg["density_measured"], "coord_ok": agg["coord_ok"],
                "preencher_files": agg["preencher_files"], "todo_files": agg["todo_files"],
                "unreadable": agg["unreadable"],
                "pillar_median": medians.get(pillar, 0.0),
                "s1_density_gap": round(s1, 4), "s2_uneven": round(s2, 4),
                "s3_stub": round(s3, 4), "s4_coord_gap": round(s4, 4),
                "severity": _composite_severity(s1, s2, s3, s4),
                "fill_eligible": nucleus_code == "N07",
                "is_archetype_baseline": nucleus_code == "N00",
            })

    cells.sort(key=lambda c: c["severity"], reverse=True)

    operational_totals = {
        n: sum(c["file_count"] for c in cells if c["nucleus"] == n) for n in OPERATIONAL_NUCLEI
    }
    thinnest = min(operational_totals, key=operational_totals.get) if operational_totals else None
    s2_ranked = sorted(
        (c for c in cells if c["nucleus"] in OPERATIONAL_NUCLEI),
        key=lambda c: c["s2_uneven"], reverse=True,
    )
    n07_in_top10_s2 = sum(1 for c in s2_ranked[:10] if c["nucleus"] == "N07")

    fill_candidates = sorted(
        (c for c in cells if c["fill_eligible"]), key=lambda c: c["severity"], reverse=True,
    )
    wave_fill_shortlist = [
        {
            "nucleus": c["nucleus"], "pillar": c["pillar"], "file_count": c["file_count"],
            "pillar_median": c["pillar_median"], "severity": c["severity"],
            "candidate_kinds": _peer_kind_pattern(buckets, c["pillar"], exclude_nucleus="N07"),
        }
        for c in fill_candidates[:5]
    ]

    return {
        "available": True,
        "index_built_at": l1.get("built_at"),
        "cells": cells,
        "cybersec_exempt": {
            "prefixes": list(N05_CYBERSEC_EXEMPT_PREFIXES),
            "files_skipped": cybersec_exempt_count,
        },
        "operational_totals": operational_totals,
        "sanity": {
            "thinnest_operational_nucleus": thinnest,
            "n07_is_thinnest": thinnest == "N07",
            "n07_cells_in_top10_s2": n07_in_top10_s2,
        },
        "wave_fill_shortlist": wave_fill_shortlist,
    }


def _run_hydration_doctor(root: Path) -> List[CheckFinding]:
    report = compute_hydration_report(root)
    if not report.get("available"):
        return [CheckFinding(
            plugin_id="hydration_doctor", ok=True,
            message="hydration measurement unavailable: %s" % report.get("reason"),
            detail={"state": "unavailable", "reason": report.get("reason")},
        )]
    top = report["cells"][:10]
    worst = top[0] if top else None
    message = (
        "measured %d nucleus x pillar cells; worst=%s/%s severity=%.3f; "
        "N07 thinnest-operational-nucleus=%s (%d/10 top s2 cells are N07)"
        % (
            len(report["cells"]),
            worst["nucleus"] if worst else "-", worst["pillar"] if worst else "-",
            worst["severity"] if worst else 0.0,
            report["sanity"]["n07_is_thinnest"],
            report["sanity"]["n07_cells_in_top10_s2"],
        )
    )
    return [CheckFinding(
        plugin_id="hydration_doctor", ok=True, message=message,
        detail={
            "index_built_at": report["index_built_at"],
            "top10": top,
            "cybersec_exempt": report["cybersec_exempt"],
            "operational_totals": report["operational_totals"],
            "sanity": report["sanity"],
        },
    )]


# --------------------------------------------------------------------------------------------- #
# Plugin 8: handoff_context_doctor -- register rows R-097/R-128 (a paired finding: R-097 is the
# GAP framing, R-128 the actionable OTIMIZAR framing -- both name the SAME missing check, N06
# card, owner N06/N05). "No doctor/lint check verifies a N06 handoff for external-context-required
# kinds actually received Phase-0 context before dispatch."
#
# Phase-0 (`.claude/rules/dispatch-depth.md` "External Context Section (PREFLIGHT_EXPANSION)"):
# N07 pre-compiles external context for any dispatch whose target `kind` has
# `requires_external_context: true` in `.cex/kinds_meta.json` (79/316 kinds today, ~25%) and bakes
# it into the handoff under a FIXED heading (`_tools/cex_preflight_mcp.py`
# `assemble_external_context`, ~line 414: "## External Context (pre-compiled by N07 via MCP)").
# This plugin reuses that SAME `requires_external_context()` lookup (no second parser of
# kinds_meta's flag -- same "one source of truth" precedent as schema_doctor wrapping
# cex_compile.load_schema / registry_drift wrapping cex_kind_register.validate) and scans N06's
# own handoff files for the fixed heading.
#
# SCOPE (matches the row literally -- N06 only; the mechanism is nucleus-agnostic and
# `_nucleus_handoff_paths` takes `nucleus` as a parameter, so widening to N01-N07 later is a
# one-line change at the call site, not a rewrite):
#   Source: .cex/runtime/handoffs/*_n06.md + n06_task.md -- the two naming conventions
#   n07-orchestrator.md's Dispatch Workflow documents ("{MISSION}_{nucleus}.md" for the mission
#   handoff, "n0X_task.md" for the boot-script-read copy).
#   Target kind: the handoff's OWN frontmatter `kind:` field -- the same structured field every
#   handoff in the live corpus already carries (verified live against this repo, 2026-07-05:
#   `.cex/runtime/handoffs/CAPGEN_n06.md` declares `kind: content_monetization`, which IS
#   requires_external_context=true, and the file demonstrably has ZERO "External Context"
#   occurrences -- a REAL, live reproduction of this exact register-row gap, not a theoretical
#   one; this plugin correctly flags it the first time it runs).
#
# MEASUREMENT-STYLE, MEDIUM severity (same posture as index_freshness/hydration_doctor/
# provenance_doctor/counter_gate): `.cex/runtime/` is gitignored + ephemeral -- a clean checkout
# has NO handoffs at all, so this can never be a BLOCKING gate on repo state; it degrades to an
# "nothing to check" ok=True the instant no N06 handoff exists. When a handoff DOES exist and DOES
# name a requires_external_context kind, a missing heading is a genuine, actionable finding (never
# folds into --ci's exit code at MEDIUM, same contract as its 4 MEDIUM siblings).
# --------------------------------------------------------------------------------------------- #
_HANDOFF_KIND_RE = re.compile(r"^kind:\s*(\S+)\s*$", re.MULTILINE)
_EXTERNAL_CONTEXT_HEADING = "## External Context"


def _nucleus_handoff_paths(root: Path, nucleus: str) -> List[Path]:
    """Every `.cex/runtime/handoffs/*.md` file that belongs to `nucleus` (e.g. "n06") -- the two
    naming conventions n07-orchestrator.md's Dispatch Workflow documents: `{MISSION}_{nucleus}.md`
    and the boot-read `{nucleus}_task.md` copy. Sorted for deterministic output. Degrade-never: an
    absent handoffs dir returns []."""
    hdir = root / ".cex" / "runtime" / "handoffs"
    if not hdir.is_dir():
        return []
    suffix = "_%s.md" % nucleus
    exact = "%s_task.md" % nucleus
    return sorted(
        p for p in hdir.glob("*.md")
        if p.is_file() and (p.name.endswith(suffix) or p.name == exact)
    )


def _handoff_declared_kind(text: str) -> Optional[str]:
    """Extract the frontmatter `kind:` value from a handoff's YAML block (a bare, unquoted scalar
    -- every handoff in the live corpus writes it that way, e.g. `kind: knowledge_card`). Returns
    None when absent (a non-build handoff, e.g. a self-review/audit task -- this check correctly
    has nothing to say about those)."""
    m = _HANDOFF_KIND_RE.search(text)
    return m.group(1) if m else None


def _run_handoff_context_doctor(root: Path) -> List[CheckFinding]:
    # TENANT-HONESTY FIX (R-162 tail, see Plugin 15 tenant_honesty below): cex_preflight_mcp is
    # NOT in FROZEN_TOOLS_CORE (live-verified 2026-07-12 -- a distilled tenant does not carry it).
    # Same unguarded-import-crashes-the-whole-registry risk as counter_gate/registry_drift; now
    # wrapped in the SAME degrade-never idiom.
    try:
        import cex_preflight_mcp as pf  # local import, same reasoning as counter_gate
    except Exception as e:
        return [
            CheckFinding(
                plugin_id="handoff_context_doctor", ok=True,
                message=(
                    "cex_preflight_mcp unavailable (%s) -- degrade-never, skipped (e.g. a "
                    "distilled tenant that does not carry this Central-only tool)" % e
                ),
                detail={"state": "unavailable"},
            )
        ]

    nucleus = "n06"
    paths = _nucleus_handoff_paths(root, nucleus)
    if not paths:
        return [CheckFinding(
            plugin_id="handoff_context_doctor", ok=True,
            message=(
                "no %s handoff files present (ordinary state -- .cex/runtime/ is "
                "gitignored/ephemeral)" % nucleus
            ),
            detail={"state": "absent", "nucleus": nucleus},
        )]

    checked = 0
    violations: List[dict] = []
    for p in paths:
        try:
            text = p.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        kind = _handoff_declared_kind(text)
        if not kind:
            continue
        try:
            needs_context = pf.requires_external_context(kind)
        except Exception:
            continue
        if not needs_context:
            continue
        checked += 1
        if _EXTERNAL_CONTEXT_HEADING not in text:
            violations.append({
                "handoff": p.relative_to(root).as_posix(),
                "kind": kind,
            })

    if violations:
        return [CheckFinding(
            plugin_id="handoff_context_doctor",
            ok=False,
            message=(
                "%d of %d %s handoff(s) targeting a requires_external_context kind are missing "
                "the Phase-0 '%s' section"
                % (len(violations), checked, nucleus, _EXTERNAL_CONTEXT_HEADING)
            ),
            detail={"checked": checked, "scanned_handoffs": len(paths), "violations": violations},
        )]
    return [CheckFinding(
        plugin_id="handoff_context_doctor",
        ok=True,
        message=(
            "%d %s handoff(s) scanned, %d targeting a requires_external_context kind -- all carry "
            "the Phase-0 external-context section" % (len(paths), nucleus, checked)
        ),
        detail={"scanned_handoffs": len(paths), "checked": checked},
    )]


# --------------------------------------------------------------------------------------------- #
# Plugin 9: identity_doctor -- mechanization of the R-040/R-109..R-111/R-116 recurring class
# ("identity" drift: two things that should be ONE authoritative copy/name diverge or duplicate)
# plus this week's R-263 (id-rename sweep) / R-288 (dual nucleus_def copies) / R-289 (unlabeled
# Regex line = H02 dormant) arcs. Two checks over the TYPED-ARTIFACT corpus:
#
#   (a) id-vs-pattern mismatch, OPT-IN per kind. The w8c output_template lesson PROVED
#       id-equals-filename-stem is NOT a universal CEXAI convention (0/18 there, deliberate) -- so
#       this check never invents a pattern for a kind that has not explicitly published one. The
#       check SET is derived from bld_schema ISOs that carry a LABELED '## ID Pattern' -> 'Regex:
#       `...`' section -- the live H02 lane (see .claude/rules/8f-reasoning.md's H02 note + R-264's
#       extract_id_pattern, IMPORTED from cex_8f_runner below, never copied). A kind whose
#       bld_schema has no such labeled section (167/317 kinds, live-measured) is simply ABSENT from
#       the pattern map -- its artifacts are never checked, by construction, matching R-289's own
#       "unlabeled Regex line = H02 dormant for that kind" precedent exactly.
#   (b) duplicate id: the SAME `id:` frontmatter value in 2+ typed-artifact files -- the R-023..
#       R-029/R-116/R-288 identity-duplication disease class (nucleus_def/agent_card twins living
#       at P02_model AND a stale P08_architecture copy, now cured for all 8 nuclei per R-288's
#       2026-07-07 close).
#
# SCOPE (both checks share ONE definition of "typed-artifact corpus", reusing -- not re-deriving --
# the SAME nucleus/pillar path convention Plugin 7 (hydration_doctor) already established above in
# this file: _NUCLEUS_PILLAR_PATH_RE + N05_CYBERSEC_EXEMPT_PREFIXES):
#   - Only paths matching N0X_.../P0Y_.../ (the canonical nucleus/pillar tree) are in scope. This
#     is what keeps the 5602-mismatch/93-duplicate NAIVE repo-wide numbers (measured during this
#     mission's own research pass) down to a real, actionable 1204/13 -- the naive scan drowns in
#     `.claude/commands/*.md` (kind: instruction, a command-definition namespace, not an 8F
#     artifact), the N05 cybersec/cybersec_distilled externally-derived corpus (already documented
#     as exempt for the exact same reason hydration_doctor exempts it), and `.cex/experiments/`
#     stress-test fixtures.
#   - '/templates/' dirs + 'tpl_'-prefixed files: EXCLUDED, same convention frontmatter_doctor
#     established above (placeholder {{PLACEHOLDER}} scaffolds, not concrete artifacts).
#   - '/examples/' dirs + 'ex_'-prefixed files: EXCLUDED (NEW exclusion, this plugin). Live-
#     verified: N00_genesis/P01_knowledge/examples/ex_knowledge_card_prompt_caching.md's own id is
#     literally "ex_knowledge_card_prompt_caching" -- deliberately NOT the p01_kc_ production
#     prefix, because these are illustrative teaching examples for builders (referenced from
#     bld_knowledge ISOs), not artifacts subject to production id discipline.
#   - `.claude/agents/*.md` mirrors: NOT special-cased -- VERIFIED live (0/321 files carry an
#     `id:` frontmatter key at all; they use `name:` instead) that they never enter either scan by
#     construction, so no exclusion rule was needed for them.
#   - `compiled/` directories: gitignored repo-wide (`.gitignore` line `**/compiled/`), so they
#     never appear in `git ls-files` and are already absent from the tracked-file list this plugin
#     reads.
#
# SEVERITY (registered plugin severity is MEDIUM -- see CHECK_REGISTRY entry below -- even though
# the task framing this plugin mechanizes calls (a) "MEDIUM" and (b) "HIGH"). CheckPlugin has ONE
# severity per plugin (severity_for() resolves purely from `_BY_ID[plugin_id].severity`); this
# module does not add a per-finding severity-override mechanism, because doing so would silently
# change what `--plugins-strict` folds on THIS repo today (13 real duplicate-id groups + 1204 real
# pattern mismatches already exist, live-measured) -- promoting either sub-check to a real
# HIGH-folding severity is a quality-gate POLICY call, the same kind of decision the R-162 register
# row itself leaves open ("promotion of counter_gate/registry_drift to blocking (GDP call)"), not
# something a build cell decides unilaterally. Registering the WHOLE plugin HIGH would immediately
# fold --plugins-strict red on (a)'s known, accepted 33-55%-class legacy drift (R-263) -- exactly
# the "a BLOCKING would light everything red" outcome this mission was told to avoid. Each
# violation entry in `detail` instead carries an INFORMATIONAL `severity_class` string
# ("MEDIUM" for pattern mismatches, "HIGH" for duplicate ids) documenting the task's stated intent
# for a human reader (or a future dedicated split into 2 plugins), without wiring it into the fold.
# --------------------------------------------------------------------------------------------- #

_IDENTITY_SCAN_EXCLUDE_SEGMENTS: tuple = ("/templates/", "/examples/")


def _identity_scan_skip(rel: str) -> bool:
    """True if `rel` (repo-relative, forward-slashed) is OUT OF SCOPE for identity_doctor's
    typed-artifact scan. See the Plugin 9 module comment above for the full rationale per rule."""
    if not _NUCLEUS_PILLAR_PATH_RE.match(rel):
        return True
    if any(rel.startswith(p) for p in N05_CYBERSEC_EXEMPT_PREFIXES):
        return True
    if any(seg in rel for seg in _IDENTITY_SCAN_EXCLUDE_SEGMENTS):
        return True
    name = rel.rsplit("/", 1)[-1]
    if name.startswith("tpl_") or name.startswith("ex_"):
        return True
    return False


def _iter_typed_md_files(root: Path) -> List[str]:
    """Sorted, in-scope, repo-relative .md paths under the canonical N0X_.../P0Y_.../ tree.

    Degrade-never: tries `git ls-files` first (via cex_stats._git_tracked, same reuse precedent as
    counter_gate); if git is unavailable (e.g. a bare tmp_path fixture with no .git), falls back to
    an on-disk rglob -- same idiom cex_stats._iter_text_files already uses for the identical
    reason. TENANT-HONESTY FIX (R-162 tail, see Plugin 15 tenant_honesty below): cex_stats itself
    is NOT in FROZEN_TOOLS_CORE (live-verified 2026-07-12 -- a distilled tenant does not carry it)
    -- a bare `import cex_stats` here would raise before ever reaching the git-unavailable
    fallback this docstring already promises, so the import + call are now inside the SAME
    try/except that extends this function's own existing degrade-never contract to cover "module
    missing", not just "git missing".
    """
    tracked: List[str] = []
    try:
        import cex_stats  # local import, same reasoning as counter_gate

        tracked = cex_stats._git_tracked(root)
    except Exception:
        tracked = []  # falls through to the on-disk rglob below, same as "git unavailable"

    if tracked:
        rels = [r.replace("\\", "/") for r in tracked if r.lower().endswith(".md")]
    else:
        rels = [
            str(p.relative_to(root)).replace("\\", "/")
            for p in root.rglob("*.md") if p.is_file()
        ]
    return sorted(rel for rel in rels if not _identity_scan_skip(rel))


def _kind_id_patterns(root: Path) -> Tuple[dict, List[dict]]:
    """{kind: compiled_pattern} for every kind whose bld_schema ISO carries a LABELED '## ID
    Pattern' Regex line -- via cex_8f_runner.extract_id_pattern, IMPORTED (not copied), the ONE
    live H02 extraction lane (R-264's structurally-scoped extractor). A kind with no labeled
    pattern is simply absent from the returned dict (opt-in by construction -- see module comment).

    Root-parameterized (unlike cex_shared.find_builder_dir/load_iso, which are hardcoded to the
    real repo's archetypes/builders/ and so cannot be redirected at a tmp_path fixture) -- this
    function does its OWN root-relative path join so tmp_path tests can plant a synthetic builder
    dir and get real coverage of the pattern-extraction path, not just a monkeypatch.

    Returns (patterns, compile_errors) -- compile_errors lists any kind whose extracted Regex
    string failed `re.compile` (degrade-never: skipped, never crashes the plugin; live-measured
    0/150 labeled kinds hit this today).
    """
    from cex_8f_runner import extract_id_pattern  # import, not copy -- per the mission fence
    import cex_shared as csh  # local import, same reasoning as counter_gate

    meta_path = root / ".cex" / "kinds_meta.json"
    try:
        kinds = sorted(json.loads(meta_path.read_text(encoding="utf-8")))
    except (OSError, UnicodeDecodeError, ValueError):
        return {}, []

    patterns: dict = {}
    compile_errors: List[dict] = []
    for kind in kinds:
        dir_slug = kind.replace("_", "-")
        bdir = root / "archetypes" / "builders" / ("%s-builder" % dir_slug)
        if not bdir.is_dir():
            continue
        schema_path = bdir / ("bld_schema_%s.md" % kind)
        if not schema_path.exists():
            candidates = sorted(bdir.glob("bld_schema_*.md"))
            if not candidates:
                continue
            schema_path = candidates[0]
        try:
            text = schema_path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue

        body = csh.strip_frontmatter(text)
        pattern_str = extract_id_pattern(body)
        if not pattern_str:
            continue
        try:
            patterns[kind] = re.compile(pattern_str)
        except re.error as e:
            compile_errors.append({"kind": kind, "pattern": pattern_str, "error": str(e)})
    return patterns, compile_errors


# --------------------------------------------------------------------------------------------- #
# R-314 EXEMPT-BY-CONVENTION (DP4 APPROVED -- decision_manifest_publication_2026_07_10.yaml +
# decision_manifest_r307_exec_2026_07_10.yaml). The R-307 lane-4 id-rename sweep tried to rename
# 383 knowledge_card ids toward the labeled p01_kc_ pattern above; 191 of them were REVERTED by the
# build's OWN sanity check -- live breakage proved 4 sub-populations are LOAD-BEARING FILENAME
# CONVENTIONS (some OTHER tool constructs/globs the exact current filename by kind name) and a 5th
# is structurally PATTERN-INADMISSIBLE (no rename under the CURRENT labeled pattern can ever
# satisfy it). See commit af9552aaaf and docs/IMPROVEMENT_REGISTER.md row R-314 for the incident
# this constant mechanizes.
#
# Each entry is {population, kind, matcher(rel, art_id) -> bool, citation} -- narrowly scoped to
# the population actually proven load-bearing/inadmissible (never a broad heuristic), so this
# constant only ever REMOVES real mismatches from the counted total for a documented, cited reason
# -- it never invents a new pass condition. Full narrative + per-population table:
# archetypes/builders/knowledge-card-builder/bld_schema_knowledge_card.md's "Naming Conventions
# (load-bearing filename populations)" section -- a bidirectional cross-reference: that section
# names this constant, this constant names that section.
#
# GOVERNANCE (never silent -- see _run_identity_doctor below): an id matched here is REMOVED from
# `pattern_mismatches` (the counted violation total) but recorded in a sibling
# `exempted_by_convention` field with a per-population breakdown, on every JSON/human/CI run.
# Duplicate-id detection (identity_doctor's OTHER check) is COMPLETELY UNCHANGED by this constant
# -- it is never consulted there; see the `duplicate_ids` block below, built from the same raw
# `id_to_files` index this constant never touches.
#
# Live-verified 2026-07-10 (this constant's own authoring pass): the 6 matchers below are mutually
# exclusive over the real corpus today (zero files match more than one) and their combined count
# matches the register row's own per-population figures (156 + 26 + 8 + 6 + 1 + 5 = 202).
# --------------------------------------------------------------------------------------------- #

_BARE_KC_ID_RE = re.compile(r"^kc_[a-z][a-z0-9_]*$")
_KC_OSS_ID_RE = re.compile(r"^kc_oss_[a-z0-9_]+$")
_KC_LENS_ID_RE = re.compile(r"^kc_lens_[a-z0-9_]+$")
_KC_VOCABULARY_ID_RE = re.compile(r"^kc_[a-z0-9_]+_vocabulary$")
_KC_8F_ID_RE = re.compile(r"^kc_8f_[a-z0-9_]+$")

EXEMPT_ID_CONVENTIONS: tuple = (
    {
        "population": "library_kind_bare_kc",
        "kind": "knowledge_card",
        "matcher": (lambda rel, art_id: (
            rel.startswith("N00_genesis/P01_knowledge/library/kind/")
            and bool(_BARE_KC_ID_RE.match(art_id))
        )),
        "citation": (
            "cex_8f_motor.load_kc_library() globs library/kind/kc_*.md by FILENAME "
            "(KC_KIND_PATH.glob('kc_*.md')); ~14 _tools modules construct this same path from the "
            "registered kind name. R-307 lane-4 proved this live: the glob dropped 322->166 files "
            "mid-execute when these were renamed; reverted at commit af9552aaaf."
        ),
    },
    {
        "population": "kc_oss_star",
        "kind": "knowledge_card",
        "matcher": (lambda rel, art_id: bool(_KC_OSS_ID_RE.match(art_id))),
        "citation": (
            "license_doctor (Plugin 10, this file, _run_license_doctor) globs "
            "N01_intelligence/P01_knowledge/kc_oss_*.md by filename."
        ),
    },
    {
        "population": "kc_lens_star",
        "kind": "knowledge_card",
        "matcher": (lambda rel, art_id: bool(_KC_LENS_ID_RE.match(art_id))),
        "citation": (
            "cex_teach_lesson.py's LENS_DIR constructs N04_knowledge/P01_knowledge/"
            "kc_lens_{lens}.md by filename for every mentor lesson lookup."
        ),
    },
    {
        "population": "kc_vocabulary",
        "kind": "knowledge_card",
        "matcher": (lambda rel, art_id: bool(_KC_VOCABULARY_ID_RE.match(art_id))),
        "citation": (
            "cex_distill._carry_vocabulary_kcs() globs N0X_*/P01_knowledge/kc_*_vocabulary.md by "
            "filename -- the controlled-vocabulary-KC path .claude/rules/ubiquitous-language.md "
            "itself documents."
        ),
    },
    {
        "population": "kc_competitor_hermes",
        "kind": "knowledge_card",
        "matcher": (lambda rel, art_id: art_id == "kc_competitor_hermes"),
        "citation": (
            "cex_hygiene.py's R09 third-party-narrative rule hardcodes this exact filename in its "
            "EXCLUDE_FILES set."
        ),
    },
    {
        "population": "kc_8f_digit_leading",
        "kind": "knowledge_card",
        "matcher": (lambda rel, art_id: bool(_KC_8F_ID_RE.match(art_id))),
        "citation": (
            "Structurally pattern-inadmissible, not just load-bearing: the labeled H02 pattern "
            "requires a LETTER immediately after the p01_kc_ prefix ([a-z]); '8f' (the 8F pipeline "
            "shorthand -- .claude/rules/8f-reasoning.md) starts with a digit, so no rename under "
            "the CURRENT pattern can ever admit it -- verified live: "
            "re.match(r'^p01_kc_[a-z][a-z0-9_]+$', 'p01_kc_8f_mode_a') is False."
        ),
    },
)


def _match_exempt_convention(kind: str, rel: str, art_id: str) -> Optional[str]:
    """R-314: return the EXEMPT_ID_CONVENTIONS population name whose `kind` matches and whose
    `matcher(rel, art_id)` is True, else None. First match wins -- live-verified zero overlap
    across the 6 registered populations today, so match order is not load-bearing in practice."""
    for entry in EXEMPT_ID_CONVENTIONS:
        if entry["kind"] == kind and entry["matcher"](rel, art_id):
            return entry["population"]
    return None


def _run_identity_doctor(root: Path) -> List[CheckFinding]:
    import cex_shared as csh  # local import, same reasoning as counter_gate

    patterns, compile_errors = _kind_id_patterns(root)

    id_to_files: dict = {}
    pattern_mismatches: List[dict] = []
    exempted_by_convention: List[dict] = []
    scanned = 0
    for rel in _iter_typed_md_files(root):
        try:
            text = (root / rel).read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        if not text.lstrip().startswith("---"):
            continue
        fm = csh.parse_frontmatter(text)
        if not fm:
            continue
        scanned += 1
        art_id = fm.get("id")
        kind = fm.get("kind")
        if isinstance(art_id, str) and art_id.strip():
            id_to_files.setdefault(art_id.strip(), []).append(rel)
        if isinstance(kind, str) and isinstance(art_id, str) and kind in patterns:
            if not patterns[kind].match(art_id):
                # R-314: a governed skip removes this from the COUNTED total but never drops it
                # silently -- see EXEMPT_ID_CONVENTIONS above. Duplicate-id detection (id_to_files,
                # already populated above this block) never consults this exemption.
                population = _match_exempt_convention(kind, rel, art_id)
                if population is not None:
                    exempted_by_convention.append(
                        {"file": rel, "kind": kind, "id": art_id, "population": population}
                    )
                else:
                    pattern_mismatches.append(
                        {"file": rel, "kind": kind, "id": art_id, "pattern": patterns[kind].pattern}
                    )

    duplicate_ids = [
        {"id": art_id, "files": files, "count": len(files)}
        for art_id, files in sorted(id_to_files.items())
        if len(files) > 1
    ]

    from collections import Counter

    by_kind = Counter(m["kind"] for m in pattern_mismatches)
    by_population = Counter(e["population"] for e in exempted_by_convention)
    ok = not pattern_mismatches and not duplicate_ids
    message = (
        "%d typed artifact(s) scanned across %d labeled-pattern kind(s): %d id/pattern "
        "mismatch(es) (+%d exempted by convention, R-314), %d duplicate id group(s)"
        % (
            scanned, len(patterns), len(pattern_mismatches), len(exempted_by_convention),
            len(duplicate_ids),
        )
    )
    return [CheckFinding(
        plugin_id="identity_doctor",
        ok=ok,
        message=message,
        detail={
            "scanned": scanned,
            "labeled_kinds": len(patterns),
            "pattern_compile_errors": compile_errors,
            "pattern_mismatches": {
                "severity_class": "MEDIUM",  # R-263 class: known, accepted legacy drift
                "count": len(pattern_mismatches),
                "by_kind": dict(by_kind.most_common()),
                "sample": pattern_mismatches[:50],
                "exempted_by_convention": {
                    # R-314: governed skip, NEVER silent -- see EXEMPT_ID_CONVENTIONS above.
                    "count": len(exempted_by_convention),
                    "by_population": dict(by_population.most_common()),
                },
            },
            "duplicate_ids": {
                "severity_class": "HIGH",  # R-023/R-116/R-288 identity-duplication disease class
                "count": len(duplicate_ids),
                "groups": duplicate_ids,
            },
        },
    )]


# --------------------------------------------------------------------------------------------- #
# Plugin 10: license_doctor -- mechanization of the "stream G" SPDX gate, the OSS-assimilation
# license discipline this session's kc_oss_* wave applied by hand (see the module docstring's
# "Mechanic transplant" section above -- Ruff/pre-commit/Great-Expectations were all re-verified
# license-clean before any clean-room mechanic transplant). Two checks:
#
#   (a) ALLOWLIST GATE: every N01_intelligence/P01_knowledge/kc_oss_*.md (26 today, live-measured
#       -- grows over time) must DECLARE its subject's license, and at least one declared value
#       must be a permissive, transplant-authorizing license (MIT / Apache-2.0 / BSD-2-Clause /
#       BSD-3-Clause / CC-BY-4.0 / ISC / Unlicense).
#   (b) COPYLEFT GATE: a copyleft-or-source-available token (AGPL / SSPL / GPL-2.0 / GPL-3.0 /
#       BUSL / Commons Clause / PolyForm) may APPEAR (e.g. kc_oss_spree.md's own core-vs-module
#       SPLIT, or a "no AGPL/SSPL/BUSL exposure" clearance sentence) but ONLY alongside an explicit
#       reference-only/negation marker in the SAME neighborhood of text -- an unmarked occurrence
#       is a HIGH-class finding (a license-vs-marketing gap slipping through undocumented).
#   (c) _tools/*.py HEADER SCAN (cheap grep-class, MEDIUM): a top-of-file boilerplate license
#       header (`Licensed under the ...`, `SPDX-License-Identifier: ...`, GPL preamble text) is a
#       signal a whole FILE was vendored/adapted under a license that is not this repo's own
#       Apache-2.0 (see LICENSE at repo root) -- worth a human's attention even when benign (e.g. a
#       permissive Apache-2.0 vendor file), so any hit is reported, not just copyleft ones.
#
# LICENSE-DECLARATION CONVENTION (derived from reading the REAL corpus, not assumed -- there is NO
# frontmatter `license:` field anywhere in this corpus; every file declares it in the BODY, and NOT
# in one single format. Three conventions coexist today, live-verified across all 26 files):
#   1. `license_status: "CONFIRMED GREEN -- <NAME>, ..."` inside a fenced ```yaml block under a
#      '## Quick Reference' heading (majority convention, ~15 files).
#   2. `license: <NAME> (SPDX) -- verified Nx (...)` + `license_gate: PASS -- ...` (and per-repo
#      variants like kc_oss_autogen.md's `license_autogen:`/`license_ag2:`), same fenced block.
#   3. A markdown table under a '## License' / '## License Gate' (optionally numbered, e.g.
#      graphiti's '## 1. License Gate (PASS)') heading, with rows like '| SPDX id | `Apache-2.0` |
#      ... |' or '| License file | ... |' (kc_oss_graphiti.md, kc_oss_letta.md).
# Given 3 real, live conventions (not the single one a first guess might assume), this plugin scans
# a NARROW but ROBUST window -- the '## Quick Reference' fenced block PLUS the '## License'/'##
# License Gate' section body, concatenated -- rather than trying to parse one exact key or table
# shape. This is what correctly classifies all 3 conventions without inventing a 4th schema.
#
# SEVERITY: registered plugin severity is MEDIUM (see CHECK_REGISTRY entry below), matching every
# other FIRST-SLICE, not-yet-battle-tested advisory plugin in this file (provenance_doctor,
# index_freshness, hydration_doctor, handoff_context_doctor) rather than the 3 zero-legacy-debt
# HIGH gates (registry_drift/schema_doctor/frontmatter_doctor). The task's own framing calls the
# copyleft gate "HIGH" and the header scan "MEDIUM"; both are carried as an INFORMATIONAL
# `severity_class` string per violation bucket in `detail` (same posture as identity_doctor above,
# for the identical reason: CheckPlugin has one severity per plugin, and promoting either
# sub-check to a real HIGH-folding gate is a policy call left open, not decided here). Live-
# measured against this repo today: 0 violations in any of the 3 sub-checks -- a genuinely clean
# first run, not a suppressed one (see the false-positive fixes documented inline below: a naive
# first pass over the real corpus DID flag "No AGPL/SSPL/BUSL exposure" clearance sentences and a
# PolyForm-mentioned-twice case as violations; both were real false positives, fixed by the
# negation-window and any-occurrence-marked logic below, not by narrowing the token list).
# --------------------------------------------------------------------------------------------- #

_LICENSE_QUICKREF_HEADING_RE = re.compile(r"(?im)^##\s*quick reference\s*$")
# Matches '## License', '## License Gate', or a numbered/annotated variant like
# '## 1. License Gate (PASS)' (kc_oss_graphiti.md's real heading) -- NOT anchored to end-of-line,
# unlike the Quick Reference heading above, because this one legitimately carries trailing text.
_LICENSE_SECTION_HEADING_RE = re.compile(r"(?im)^##\s*(?:\d+\.\s*)?license(?:\s+gate)?\b")
_LICENSE_NEXT_H2_RE = re.compile(r"(?m)^##(?!#)")
_LICENSE_QUICKREF_FENCE_RE = re.compile(r"```(?:[a-zA-Z]*)\n(.*?)```", re.DOTALL)
_LICENSE_DECL_LINE_RE = re.compile(r"(?im)^\s*license\w*\s*:\s*(.+)$")

_LICENSE_ALLOWLIST: tuple = (
    "mit", "apache-2.0", "apache license", "bsd-2-clause", "bsd-3-clause",
    "cc-by-4.0", "isc license", "unlicense",
)
_LICENSE_FLAGGED: tuple = (
    "agpl", "sspl", "gpl-2.0", "gpl-3.0", "gnu general public license",
    "busl", "commons clause", "polyform",
)
# Explicit reference-only/caveat markers -- checked in an 80-char window around a flagged token
# (e.g. "AGPL-3.0 RED", "PolyForm ... non-OSI, entirely avoided").
_LICENSE_MARKER_RE = re.compile(
    r"\b(red|reference-only|reference only|avoided|non-osi|rejected|"
    r"not transplanted|nothing transplanted|gated|enterprise license|commercial license)\b",
    re.IGNORECASE,
)
# Negation immediately before a flagged token -- e.g. "No AGPL/SSPL/BUSL exposure." (a fixed
# clearance sentence reused verbatim across several kc_oss_* files this wave produced). Checked in
# a tighter 25-char pre-window (wide enough to span a '/'-joined token list's later members).
_LICENSE_NEGATION_PRE_RE = re.compile(r"\bno\b", re.IGNORECASE)

_TOOLS_HEADER_SCAN_LINES = 40
_TOOLS_LICENSE_HEADER_RE = re.compile(
    r"licensed under the|SPDX-License-Identifier|this program is free software|"
    r"under the gnu general public license",
    re.IGNORECASE,
)


def _license_section_after_heading(body: str, heading_re: "re.Pattern") -> str:
    """Text from just after `heading_re`'s matched line to the next '## ' (H2) heading, or the
    rest of the body if it is the last section. Empty string if the heading is absent."""
    m = heading_re.search(body)
    if not m:
        return ""
    rest = body[m.end():]
    m2 = _LICENSE_NEXT_H2_RE.search(rest)
    return rest[:m2.start()] if m2 else rest


def _license_scan_scope(body: str) -> str:
    """The narrow text window license_doctor scans for a kc_oss_* file's OWN declared license:
    the fenced code block under '## Quick Reference' (conventions 1+2 above) concatenated with the
    '## License'/'## License Gate' section body (convention 3) -- see the Plugin 10 module comment
    for why BOTH are read rather than picking exactly one."""
    parts = []
    qr_section = _license_section_after_heading(body, _LICENSE_QUICKREF_HEADING_RE)
    if qr_section:
        fence = _LICENSE_QUICKREF_FENCE_RE.search(qr_section)
        parts.append(fence.group(1) if fence else qr_section)
    lic_section = _license_section_after_heading(body, _LICENSE_SECTION_HEADING_RE)
    if lic_section:
        parts.append(lic_section)
    return "\n".join(parts)


def _license_token_hit(text: str, token: str) -> bool:
    return re.search(r"\b" + re.escape(token) + r"\b", text, re.IGNORECASE) is not None


def _classify_kc_oss_license(body: str) -> dict:
    """Classify one kc_oss_*.md file's declared license against the allowlist/copyleft gates.

    `flagged_unmarked` is computed PER TOKEN, not per raw text occurrence: if a flagged token
    appears multiple times in the scan scope (e.g. once in a short Quick Reference summary line
    WITH an adjacent marker, once again in a longer prose '## License' paragraph without one), the
    file is credited as long as AT LEAST ONE occurrence is properly marked -- matching
    kc_oss_openhands.md's real shape (PolyForm mentioned twice; the summary line marks it, a later
    prose sentence restates it without repeating the caveat inline).
    """
    scope = _license_scan_scope(body)
    declaration_lines = [m.group(1).strip() for m in _LICENSE_DECL_LINE_RE.finditer(scope)]
    allowed_hits = sorted({tok for tok in _LICENSE_ALLOWLIST if _license_token_hit(scope, tok)})

    flagged_unmarked: List[dict] = []
    for tok in _LICENSE_FLAGGED:
        occurrences = list(re.finditer(r"\b" + re.escape(tok) + r"\b", scope, re.IGNORECASE))
        if not occurrences:
            continue
        any_marked = False
        first_unmarked_context = ""
        for m in occurrences:
            pre = scope[max(0, m.start() - 25): m.start()]
            window = scope[max(0, m.start() - 80): m.end() + 80]
            if _LICENSE_NEGATION_PRE_RE.search(pre) or _LICENSE_MARKER_RE.search(window):
                any_marked = True
                break
            if not first_unmarked_context:
                first_unmarked_context = window.strip().replace("\n", " ")
        if not any_marked:
            flagged_unmarked.append({"token": tok, "context": first_unmarked_context})

    return {
        "declared": bool(scope.strip()),
        "declaration_lines": declaration_lines,
        "allowlisted": allowed_hits,
        "flagged_unmarked": flagged_unmarked,
    }


def _scan_tools_license_headers(root: Path) -> List[dict]:
    """Cheap grep-class scan: top _TOOLS_HEADER_SCAN_LINES lines of every _tools/*.py file
    (top-level only, matching the mission's literal '_tools/*.py' scope -- not _tools/tests/ or
    _tools/distill/) for boilerplate license-header phrasing. Degrade-never: an absent _tools/
    dir or an unreadable file is skipped, never raised.

    "new-ish" (per the task) is approximated as "every _tools/*.py file that exists today" -- a
    per-file git-log call to bucket by true age would defeat the "cheap" requirement this check is
    scoped to; this is documented here as a deliberate simplification, not silently assumed.
    """
    tools_dir = root / "_tools"
    if not tools_dir.is_dir():
        return []
    hits: List[dict] = []
    for f in sorted(tools_dir.glob("*.py")):
        try:
            text = f.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        head = "\n".join(text.splitlines()[:_TOOLS_HEADER_SCAN_LINES])
        m = _TOOLS_LICENSE_HEADER_RE.search(head)
        if m:
            hits.append({"file": f.relative_to(root).as_posix(), "matched": m.group(0)})
    return hits


def _run_license_doctor(root: Path) -> List[CheckFinding]:
    import cex_shared as csh  # local import, same reasoning as counter_gate

    kc_dir = root / "N01_intelligence" / "P01_knowledge"
    kc_files = sorted(kc_dir.glob("kc_oss_*.md")) if kc_dir.is_dir() else []

    missing_declaration: List[str] = []
    not_allowlisted: List[dict] = []
    copyleft_violations: List[dict] = []
    for f in kc_files:
        try:
            text = f.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue

        body = csh.strip_frontmatter(text)
        info = _classify_kc_oss_license(body)
        rel = f.relative_to(root).as_posix()
        if not info["declared"]:
            missing_declaration.append(rel)
        elif not info["allowlisted"]:
            not_allowlisted.append({"file": rel, "declaration_lines": info["declaration_lines"]})
        if info["flagged_unmarked"]:
            copyleft_violations.append({"file": rel, "hits": info["flagged_unmarked"]})

    header_hits = _scan_tools_license_headers(root)

    ok = not (missing_declaration or not_allowlisted or copyleft_violations or header_hits)
    message = (
        "%d kc_oss_* file(s) checked: %d missing a license declaration, %d w/o an allowlisted "
        "license, %d w/ an unmarked copyleft token; %d _tools/*.py header hit(s)"
        % (len(kc_files), len(missing_declaration), len(not_allowlisted),
           len(copyleft_violations), len(header_hits))
    )
    return [CheckFinding(
        plugin_id="license_doctor",
        ok=ok,
        message=message,
        detail={
            "kc_oss_files_checked": len(kc_files),
            "allowlist_gate": {
                "severity_class": "MEDIUM",
                "missing_declaration": missing_declaration,
                "not_allowlisted": not_allowlisted,
            },
            "copyleft_gate": {
                "severity_class": "HIGH",
                "violations": copyleft_violations,
            },
            "tools_header_scan": {
                "severity_class": "MEDIUM",
                "hits": header_hits,
            },
        },
    )]


# --------------------------------------------------------------------------------------------- #
# Plugin 11: reference_doctor -- mechanization of the R-160 class ("dead-reference detector") /
# R-162's own "wikilinks/refs quebrados" framing, generalized from R-160's tenant-carry-specific
# scope (dead references inside CARRIED skills/PM) into an ongoing REPO-WIDE measurement over
# Central's own typed-artifact corpus -- the same generalize-a-sweep-into-a-permanent-check move
# Plugin 9 (identity_doctor) already made for R-263.
#
# REUSE, not reimplementation: imports `cex_wikilink_gate.py` -- the EXISTING Benchmark-2-mandated
# `[[target]]` grounding gate (`build_id_index()` scans every .md under root for a frontmatter
# `^id: target$` declaration; `check_text()` reports any body `[[target]]` whose normalized target
# has no such declaration). cex_doctor.py already wires this SAME module via its `--wikilinks`
# flag, but that call is scoped to STAGED/GIVEN paths only (a pre-commit-style F7 gate over
# freshly PRODUCED artifacts). This plugin is the complementary thing every other keystone-to-gate
# plugin in this file already is: an ongoing repo-wide health measurement, re-runnable any time --
# not just at commit time for new artifacts.
#
# SCOPE: reuses Plugin 9's OWN `_iter_typed_md_files()` -- the SAME canonical N0X_.../P0Y_.../
# typed-artifact tree (git-tracked only, templates/examples/N05-cybersec exempt) -- rather than a
# naive whole-repo walk. MEASURED LIVE both ways during this plugin's own authoring pass: a raw
# `cex_wikilink_gate.py --all .` sweep over the ENTIRE repo (including `.cex/runtime/` ephemeral
# handoffs, `.claude/agents/*.md` mirrors, docs/, CHANGELOG.md, ...) found 3877/12837 files failing
# (30%, 5269 fabricated targets) -- drowned in exactly the class of noise Plugin 9's own module
# comment describes for a naive id-pattern scan. Scoped to the SAME canonical tree Plugin 9 already
# established, the count drops to a real, actionable 218/2540 files (416 fabricated targets) -- a
# live, non-trivial finding, not manufactured noise (e.g. N00_genesis/P02_model/nucleus_def_n00.md
# links `[[8f-reasoning]]` / `[[n07-orchestrator]]` -- real cross-references to `.claude/rules/*.md`
# governance docs, which carry no frontmatter `id:` and so cannot resolve under the id-decl model
# cex_wikilink_gate implements; disclosed via the `resolvable_universe` note in the finding detail,
# not hidden -- this is an honest measurement of the CURRENT id-decl-only resolution mechanism, not
# a claim every listed target is a typo).
#
# The id INDEX itself (what a link resolves AGAINST) stays repo-wide (`build_id_index(root)`,
# unscoped) -- a typed artifact may legitimately link to an id declared outside the canonical
# nucleus/pillar tree (a `docs/` spec, a `_docs/compiled/` catalog) and narrowing the resolution
# universe would manufacture false fabrication findings; only the SOURCE scan (which files' own
# [[links]] get checked) is scoped -- the same "scan a bounded sample, resolve against the full
# picture" split frontmatter_doctor already uses.
# --------------------------------------------------------------------------------------------- #
def _run_reference_doctor(root: Path) -> List[CheckFinding]:
    import cex_wikilink_gate as wg  # local import, same reasoning as counter_gate

    id_index = wg.build_id_index(root)
    rels = _iter_typed_md_files(root)  # reuse Plugin 9's canonical typed-artifact scope

    scanned = 0
    broken: List[dict] = []
    for rel in rels:
        try:
            text = (root / rel).read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        scanned += 1
        link_ok, fabricated = wg.check_text(text, id_index)
        if not link_ok:
            broken.append({"file": rel, "fabricated": fabricated, "count": len(fabricated)})

    total_fabricated = sum(b["count"] for b in broken)
    if broken:
        return [CheckFinding(
            plugin_id="reference_doctor",
            ok=False,
            message=(
                "%d of %d typed artifact(s) carry >=1 unresolved [[wikilink]] (%d fabricated "
                "target(s) total, against a %d-id repo-wide index)"
                % (len(broken), scanned, total_fabricated, len(id_index))
            ),
            detail={
                "scanned": scanned,
                "id_index_size": len(id_index),
                "files_with_broken_links": len(broken),
                "total_fabricated": total_fabricated,
                "resolvable_universe": (
                    "targets are checked against every repo .md frontmatter 'id:' declaration "
                    "(cex_wikilink_gate.build_id_index) -- a target naming a non-id-bearing file "
                    "(e.g. a .claude/rules/*.md governance doc, which declares no id:) is reported "
                    "as unresolved under this mechanism, same as cex_doctor.py's --wikilinks gate"
                ),
                "sample": broken[:50],
            },
        )]
    return [CheckFinding(
        plugin_id="reference_doctor",
        ok=True,
        message=(
            "%d typed artifact(s) scanned: every [[wikilink]] resolves against the %d-id "
            "repo-wide index" % (scanned, len(id_index))
        ),
        detail={"scanned": scanned, "id_index_size": len(id_index)},
    )]


# --------------------------------------------------------------------------------------------- #
# Plugin 12: runtime_cap_doctor -- mechanization of the R-003/audit#3 class ("`content` capability
# enabled with no generator -> structural ModuleNotFoundError precondition", fixed at the CRASH
# level by w7b's fail-closed `sdk_unavailable` refusal, but the underlying DECLARATION gap -- a
# capability card that has no structured generator and so depends on the generic cex_sdk build
# path -- was never itself measured). Two independent, non-mutually-exclusive checks over every
# card in the versioned base catalog (`_docs/compiled/cexai_capability_catalog.yaml`, read via
# `cex_capability_registry.base_capabilities()` -- the SAME accessor the dashboard/runtime use):
#
#   (a) UNRESOLVABLE KIND: the card's `kind` does not exist in `.cex/kinds_meta.json` at all -- a
#       structural break no environment can ever resolve (HIGH-class, informational only -- see
#       the identity_doctor/license_doctor precedent below for why severity stays MEDIUM overall).
#   (b) NO GENERATOR: neither the capability SLUG nor its `kind` has a registered structured
#       generator (`capability_generators.get_generator`, the SAME slug-then-kind resolution order
#       `cex_run_capability._resolve_structured_generator` uses) -- the card falls through to the
#       generic `cex_sdk.agent.cex_agent.CEXAgent` build path, the EXACT R-003 precondition. Valid
#       by design in Central (which always carries cex_sdk/) -- but a distilled tenant may not
#       (sdk_choice=cexai_packaged default), so this is a real, worth-surfacing risk signal, not a
#       hard break.
#
# Live-measured against this repo (this plugin's own authoring pass): 21 base capability cards, 2
# with an unresolvable kind (`funnel_diag` -> kind `tool_card`, `research_universe` -> kind
# `research_universe` -- neither is in kinds_meta.json's 318 registered kinds), 3 with no generator
# (`content` -> knowledge_card, `pesquisa_produto` -> knowledge_card, `research_universe` -- the
# last one fails BOTH checks). `content` is a VERBATIM live reproduction of the R-003 register
# row's own named example, still true today -- the crash was fixed, the declaration gap was not.
#
# MEDIUM severity (never folds -- same "advisory por default" contract as every sibling plugin):
# promoting either sub-check to HIGH/BLOCKING is the same quality-gate POLICY call identity_doctor
# and license_doctor already left open for their own split checks, not decided unilaterally here.
# Each violation entry's bucket carries an informational `severity_class` string instead (per the
# same precedent). Degrade-never: an absent/broken catalog or capability_generators import yields
# an ok=True "unavailable" finding, never a crash of this or any sibling plugin's findings.
# --------------------------------------------------------------------------------------------- #
def _run_runtime_cap_doctor(root: Path) -> List[CheckFinding]:
    import json as _json

    import cex_capability_registry as creg  # local import, same reasoning as counter_gate

    try:
        import capability_generators as cg  # local import, same reasoning as counter_gate
    except Exception as e:
        return [CheckFinding(
            plugin_id="runtime_cap_doctor", ok=True,
            message="capability_generators unavailable (%s) -- degrade-never, skipped" % e,
            detail={"state": "unavailable"},
        )]

    meta_path = root / ".cex" / "kinds_meta.json"
    try:
        kinds_meta = _json.loads(meta_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, ValueError):
        kinds_meta = {}

    try:
        caps = creg.base_capabilities()
    except Exception as e:
        return [CheckFinding(
            plugin_id="runtime_cap_doctor", ok=True,
            message="capability catalog unreadable (%s) -- degrade-never, skipped" % e,
            detail={"state": "unavailable"},
        )]

    unresolvable_kind: List[dict] = []
    no_generator: List[dict] = []
    for c in caps:
        card = {"capability": c.capability, "kind": c.kind, "nucleus": c.nucleus}
        if c.kind not in kinds_meta:
            unresolvable_kind.append(dict(card))
        gen = cg.get_generator(c.capability) or cg.get_generator(c.kind)
        if gen is None:
            no_generator.append(dict(card))

    ok = not unresolvable_kind and not no_generator
    message = (
        "%d capability card(s) checked: %d declare a kind not in kinds_meta.json (unresolvable), "
        "%d have no structured generator (fall to the generic cex_sdk build path -- R-003 class)"
        % (len(caps), len(unresolvable_kind), len(no_generator))
    )
    return [CheckFinding(
        plugin_id="runtime_cap_doctor",
        ok=ok,
        message=message,
        detail={
            "checked": len(caps),
            "unresolvable_kind": {
                "severity_class": "HIGH",
                "count": len(unresolvable_kind),
                "entries": unresolvable_kind,
            },
            "no_generator": {
                "severity_class": "MEDIUM",
                "count": len(no_generator),
                "entries": no_generator,
            },
        },
    )]


# --------------------------------------------------------------------------------------------- #
# Plugin 13: memory_doctor -- mechanization of the R-162 row's own "P10 learning_records/promote
# backlog health" candidate: a keystone-to-gate wrap of `cex_memory_promote.py` (R-153, PM-3 v2 --
# the reinforcement/memory-consolidation loop). REUSE, not reimplementation: calls
# `cex_memory_promote.promote(apply=False)` -- the tool's OWN read-only "ledger-only" entrypoint
# (its docstring: "writes NOTHING"; the ONLY write call, `_write_if_changed`, is gated strictly
# behind `if apply and decision in ("ADD", "UPDATE")` inside `promote()` itself, never reached
# here) -- rather than re-deriving lesson-grouping/fuzzy-merge/decision logic a second time.
#
# "Backlog" = every (tier-1+tier-2-merged) lesson group that reached `min_count` (default 2, the
# tool's own default, reused unchanged) AND whose `decide_action()` verdict is ADD (no
# `pm_promoted_{key}.md` draft exists yet) or UPDATE (a draft exists but new source_records have
# arrived since) -- i.e. recurring lessons not yet turned into a reviewable procedural_memory
# addendum. A NONE-decision group (already fully cited) or a below-min_count group is not backlog.
#
# Live-measured against this repo (this plugin's own authoring pass): 217 learning_records read (0
# skipped), 6 lesson groups total, 1 at/above min_count=2, that ONE group is decision=ADD (a real,
# small, genuinely-unpromoted backlog, not a manufactured example): `knowledge_card::
# retried_then_pass` (2 records, nucleus=n04, target=N04_knowledge/P10_memory/
# pm_promoted_knowledge_card_retried_then_pass.md).
#
# MEDIUM severity (never folds -- same "advisory por default" contract as every sibling plugin): a
# non-empty backlog is an ORDINARY, expected steady state for a PROPOSE-ONLY loop
# (cex_memory_promote.py never auto-applies; a human/nucleus reviews + runs --apply on their own
# cadence) -- never a repo-health BLOCKING/HIGH condition, only a useful "N lessons are waiting"
# surface for N07's own periodic sweep. Degrade-never: an unimportable cex_memory_promote or a
# promote() exception yields an ok=True "unavailable" finding, never a crash.
# --------------------------------------------------------------------------------------------- #
def _run_memory_doctor(root: Path) -> List[CheckFinding]:
    try:
        import cex_memory_promote as mp  # local import, same reasoning as counter_gate
    except Exception as e:
        return [CheckFinding(
            plugin_id="memory_doctor", ok=True,
            message="cex_memory_promote unavailable (%s) -- degrade-never, skipped" % e,
            detail={"state": "unavailable"},
        )]

    # Root-scoped kinds_meta (not cex_memory_promote's own hardcoded-to-the-real-repo default)
    # -- same precedent as every other plugin in this file (e.g. provenance_doctor). Without this,
    # promote()'s nucleus resolution would silently read the REAL repo's kinds_meta.json even when
    # `root` is a synthetic tmp_path fixture, decoupling the target path this plugin computes from
    # the one a caller passing the SAME `root` to promote() directly would get.
    meta_path = root / ".cex" / "kinds_meta.json"
    try:
        kinds_meta = json.loads(meta_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, ValueError):
        kinds_meta = {}

    records_dir = root / ".cex" / "learning_records"
    try:
        result = mp.promote(
            records_dir=records_dir, apply=False, root=root, kinds_meta=kinds_meta,
        )
    except Exception as e:
        return [CheckFinding(
            plugin_id="memory_doctor", ok=True,
            message="promote() failed (%s) -- degrade-never, skipped" % e,
            detail={"state": "unavailable"},
        )]

    backlog = [entry for entry in result["promoted"] if entry.get("decision") in ("ADD", "UPDATE")]
    ok = not backlog
    message = (
        "%d learning_record(s) read (%d skipped) -> %d lesson group(s) (%d below min_count=%d); "
        "%d group(s) awaiting promotion (decision=ADD/UPDATE)"
        % (
            result["records_read"], len(result["records_skipped"]), result["groups_total"],
            len(result["below_threshold"]), result["min_count"], len(backlog),
        )
    )
    return [CheckFinding(
        plugin_id="memory_doctor",
        ok=ok,
        message=message,
        detail={
            "records_read": result["records_read"],
            "records_skipped": len(result["records_skipped"]),
            "groups_total": result["groups_total"],
            "min_count": result["min_count"],
            "below_threshold": len(result["below_threshold"]),
            "backlog": [
                {
                    "key": entry["key"], "decision": entry["decision"], "count": entry["count"],
                    "nucleus": entry["nucleus"], "target": entry["target"],
                }
                for entry in backlog
            ],
        },
    )]


# --------------------------------------------------------------------------------------------- #
# Plugin 14: trace_auditor -- mechanization of R-009 ("Ollama-grid 'usable' reports never
# cross-check the real tool-call trace -- fabrication reproduced directly in sampled output").
#
# R-009 was fixed AT THE SOURCE (commit b4eb1e8695, w7e): _tools/cex_ollama_grid.py's own
# is_usable() is now evidence-based fail-closed -- a report only counts as usable when its
# .trace.json-sidecar-derived `reads` count (appended by the RUNNER per tool call it actually
# executed, never model-inflatable) clears `require_reads`, closing 3 fail-open paths (a 3rd
# done() accepted after the anti-fab rejection cap, text-only no_tool_call answers, and
# forced_synthesis after an all-list_dir loop with 0 real reads).
#
# What "mechanize the keystone" means here: the fix lives in is_usable() itself, but nothing
# re-verifies, ON AN ONGOING BASIS, that a wave_report.json's own top-level `usable` COUNT (the
# number a human/N07 reads off a grid run's summary) actually MATCHES a fresh recomputation of
# is_usable() over that SAME report's own recorded per-nucleus fields (bytes/reason/reads). This
# is the "judges verify by execution, not by reading prose" Honesty Spine
# (.claude/rules/n07-orchestrator.md Mode W section) applied to the ollama-grid self-report
# specifically: a wave_report.json is itself a CLAIM (produced by a subprocess this doctor did not
# supervise), and this plugin re-derives the verdict from the SAME ground-truth fields the claim
# was built from, using the CANONICAL is_usable() (imported, never re-implemented -- same "one
# source of truth" precedent as every sibling plugin in this file).
#
# REUSE: imports cex_ollama_grid.is_usable directly. Scans every _reports/**/wave_report.json that
# has a `results` dict (the headless-agentic-grid shape this file's own read_trace/is_usable pair
# produces) -- a wave_report.json lacking `results` (e.g. the windowed cex_grid_test.py-produced
# shape; live-verified: _reports/gridtest_leverage_map/ollama-llama/wave_report.json carries
# commits/committed/files/timed_out instead) is a DIFFERENT report family this plugin has nothing
# to say about, and is skipped, not misread.
#
# LEGACY-SHAPE HONESTY (live-verified against this repo's own _reports/, none tracked in git --
# `_reports/` is gitignored repo-wide per .gitignore, so every file here is local run debris, not
# a governed artifact): all 8 on-disk `results`-shaped wave_report.json files predate commit
# b4eb1e8695's "wave_report records the gate" change and carry NO `require_reads` key at all.
# Recomputing is_usable() against a legacy report needs SOME require_reads value; guessing one and
# silently treating a mismatch as a live finding would manufacture a false "fabrication" claim
# against reports the current code no longer even produces this way. This plugin therefore reports
# missing `require_reads`/`min_bytes` as its OWN bucket (`legacy_shape`, informational, never
# counted as a mismatch) -- never silently guesses, never mis-flags. A report that DOES carry both
# keys (i.e. produced by the fixed harness, going forward) is fully re-verified, and any mismatch
# between its claimed `usable` and a fresh is_usable() recomputation is the real, ongoing "gates
# that lie" regression this plugin exists to catch the 6th time (R-009's own docstring already
# counts 5 prior kills of the same disease class).
#
# DEGRADE-NEVER: absent _reports/ dir, an unparseable wave_report.json, a failed cex_ollama_grid
# import, or a per-nucleus record shaped without the fields is_usable() needs, all fold into an
# informational/skipped bucket -- never a crash of this or any sibling plugin's findings (same
# posture as index_freshness/hydration_doctor).
# --------------------------------------------------------------------------------------------- #
def _run_trace_auditor(root: Path) -> List[CheckFinding]:
    try:
        import cex_ollama_grid as og  # local import, same reasoning as counter_gate
    except Exception as e:
        return [CheckFinding(
            plugin_id="trace_auditor", ok=True,
            message="cex_ollama_grid unavailable (%s) -- degrade-never, skipped" % e,
            detail={"state": "unavailable"},
        )]

    reports_dir = root / "_reports"
    if not reports_dir.is_dir():
        return [CheckFinding(
            plugin_id="trace_auditor", ok=True,
            message=(
                "no _reports/ directory present (ordinary state -- _reports/ is "
                "gitignored/ephemeral, same posture as .cex/runtime/)"
            ),
            detail={"state": "absent"},
        )]

    wave_paths = sorted(reports_dir.rglob("wave_report.json"))
    skipped_other_shape = 0
    legacy_shape: List[dict] = []
    audited = 0
    mismatches: List[dict] = []
    for p in wave_paths:
        rel = p.relative_to(root).as_posix()
        try:
            wave = json.loads(p.read_text(encoding="utf-8", errors="replace"))
        except (OSError, UnicodeDecodeError, ValueError):
            skipped_other_shape += 1
            continue
        if not isinstance(wave, dict) or not isinstance(wave.get("results"), dict):
            skipped_other_shape += 1  # a different wave_report family (e.g. windowed grid shape)
            continue

        results = wave["results"]
        min_bytes = wave.get("min_bytes")
        if "require_reads" not in wave or not isinstance(min_bytes, (int, float)):
            legacy_shape.append({
                "report": rel, "claimed_usable": wave.get("usable"), "count": len(results),
            })
            continue

        require_reads = wave["require_reads"]
        try:
            recomputed = sum(
                1 for rec in results.values()
                if isinstance(rec, dict) and og.is_usable(rec, min_bytes, require_reads)
            )
        except (KeyError, TypeError):
            skipped_other_shape += 1  # per-nucleus records lack the fields is_usable() needs
            continue

        audited += 1
        claimed = wave.get("usable")
        if claimed != recomputed:
            mismatches.append({
                "report": rel, "claimed_usable": claimed, "recomputed_usable": recomputed,
                "min_bytes": min_bytes, "require_reads": require_reads, "count": len(results),
            })

    ok = not mismatches
    message = (
        "%d wave_report.json(s) found under _reports/ (%d skipped/other-shape, %d legacy "
        "pre-R-009-fix shape w/o require_reads, %d re-audited via is_usable() recomputation); "
        "%d usable-count mismatch(es) (claimed vs re-derived from the SAME on-disk trace fields)"
        % (len(wave_paths), skipped_other_shape, len(legacy_shape), audited, len(mismatches))
    )
    return [CheckFinding(
        plugin_id="trace_auditor",
        ok=ok,
        message=message,
        detail={
            "wave_reports_found": len(wave_paths),
            "skipped_other_shape": skipped_other_shape,
            "legacy_shape": legacy_shape,
            "audited": audited,
            "mismatches": mismatches,
        },
    )]


# --------------------------------------------------------------------------------------------- #
# Plugin 15: tenant_honesty -- mechanization of the R-162 row's own "tenant-mode honesty (S7)"
# core-upgrade line, generalizing the SAME "kill self-certification" ethos R-007's S7 stream
# applied to cex_distill.py's verify() step (docs/IMPROVEMENT_REGISTER.md R-007: doctor-status was
# hardcoded, import-smoke was a text-grep proxy, not real execution) to THIS registry itself, when
# it runs INSIDE a distilled tenant repo rather than Central.
#
# THE CONCRETE GAP (found by this plugin's own authoring pass, not assumed): 4 of this file's OWN
# local imports were UNGUARDED (no try/except) around a tool module that _tools/cex_distill.py's
# FROZEN_TOOLS_CORE allowlist (the 60-module set every distilled tenant carries, live-verified
# against cex_distill.py 2026-07-12) does NOT include -- cex_stats (counter_gate + the shared
# _iter_typed_md_files helper identity_doctor/reference_doctor both call), cex_kind_register
# (registry_drift), and cex_preflight_mcp (handoff_context_doctor). AT THE TIME this plugin was
# authored, run_registry() had NO per-plugin isolation (a plain for-loop calling plugin.run()
# directly), so ANY ONE of these raising ModuleNotFoundError in an environment that genuinely
# lacks the tool (a lean tenant, by design, per cex_distill.py's own module-carry contract) would
# silently blank EVERY OTHER plugin's finding too -- cex_doctor.py's check_registry_advisory()
# catches the exception at the OUTER run_registry() call, per its own docstring ("any import or
# execution error in cex_check_registry yields ([], zero-evaluated summary)"). The doctor's ENTIRE
# advisory tail would silently vanish to "(no plugins registered, or registry unavailable...)",
# not just the 4 Central-only-dependent ones. This is the disease class the row names precisely:
# "doctor/registry must not assert Central-only expectations... as failures, and must not claim
# surfaces that were not carried" -- here it is WORSE than a false FAIL, it is a silent, total
# collapse of every advisory signal a tenant's own doctor run would otherwise have gotten for
# free. Companion fix (same authoring pass, see each site's own inline comment): all 4 sites now
# wrap their import in the SAME try/except-degrade-never idiom already used by index_freshness/
# hydration_doctor/runtime_cap_doctor/memory_doctor (4 sibling plugins added AFTER counter_gate/
# registry_drift were first written) -- counter_gate/registry_drift/handoff_context_doctor degrade
# to an ok=True "unavailable" finding; _iter_typed_md_files degrades to the rglob fallback its OWN
# docstring already promised for the "no .git" case, now also covering "no cex_stats module".
#
# UPDATE (R-335, docs/IMPROVEMENT_REGISTER.md): run_registry() itself has since gained generic
# per-plugin exception isolation (see its own docstring) -- a plugin that raises for ANY reason,
# not just the 3 named imports above, now yields a synthetic plugin_crashed finding instead of
# blanking the tail. This plugin's own value is now complementary rather than the last line of
# defense: it PROACTIVELY names which sibling would fail a tenant-context run (a diagnostic run
# BEFORE any real doctor invocation needs to hit that crash), whereas run_registry()'s isolation
# is a passive, always-on safety net that fires only when a real crash actually occurs.
#
# TENANT DETECTION (per the mission's own instruction: follow cex_distill.py's OWN idiom, `.cex/`
# tenant markers, not a new invented mechanism): `.cex/distill/distillation_manifest.yaml` is the
# file cex_distill.py's own emit-manifest write step (cex_distill.py, ~line 8920) writes into the
# OUTPUT tree as the LAST step of every real (non-dry-run) distill run -- present in every
# distilled tenant, absent from Central by construction (Central is the SOURCE, never a distill
# OUTPUT; live-verified: this repo's own `.cex/` has no `distill/` subdirectory at all).
#
# WHAT THIS PLUGIN ACTUALLY ASSERTS (a detection + skip/re-scope layer, NOT a rewrite of the other
# 14 plugins): outside a distilled tenant (Central, or an undetectable environment), there is
# nothing tenant-specific to assert -- ok=True, informational, mirrors every sibling "absent"
# bucket. INSIDE a distilled tenant, this plugin calls every OTHER registered plugin's OWN
# run(root) directly (never run_registry() itself -- that would self-recurse), mirroring
# run_registry()'s own selector-then-run order, and catches any exception: a plugin that raises IS
# EXACTLY the "asserts a Central-only expectation as a crash" disease this plugin exists to catch,
# ongoing -- the same live-execution-not-prose-reading discipline every other keystone-to-gate
# plugin in this file already applies to ITS OWN keystone. Degrade-never: an unreadable/absent
# tenant marker resolves to "not tenant", never a crash of this or any sibling plugin's findings.
# --------------------------------------------------------------------------------------------- #
_TENANT_MARKER_REL = Path(".cex") / "distill" / "distillation_manifest.yaml"


def _is_distilled_tenant(root: Path) -> bool:
    """True iff `root` looks like a `_tools/cex_distill.py` OUTPUT tree (a distilled tenant repo),
    never Central. See the Plugin 15 module comment above for the marker's provenance + the
    live-verified absence in Central's own `.cex/`. A bare `.cex/distill/` dir with at least one
    entry also counts (e.g. `copy_ledger.json`/`skeleton_manifest.json` present without the final
    manifest write completing) -- degrade-toward-tenant-detected only on REAL on-disk evidence,
    never a guess."""
    if (root / _TENANT_MARKER_REL).is_file():
        return True
    distill_dir = root / ".cex" / "distill"
    try:
        return distill_dir.is_dir() and any(distill_dir.iterdir())
    except OSError:
        return False


def _run_tenant_honesty(root: Path) -> List[CheckFinding]:
    if not _is_distilled_tenant(root):
        return [CheckFinding(
            plugin_id="tenant_honesty", ok=True,
            message=(
                "not running inside a distilled tenant repo (no %s marker) -- Central or an "
                "undetectable environment; nothing tenant-specific to assert"
                % _TENANT_MARKER_REL.as_posix()
            ),
            detail={"state": "central_or_unknown", "tenant_marker": _TENANT_MARKER_REL.as_posix()},
        )]

    crashed: List[dict] = []
    checked = 0
    for plugin in CHECK_REGISTRY:
        if plugin.id == "tenant_honesty":
            continue  # never self-invoke -- avoids recursing into run_registry()
        if not plugin.selector(root):
            continue
        checked += 1
        try:
            plugin.run(root)
        except Exception as e:
            crashed.append({
                "plugin_id": plugin.id, "error_type": type(e).__name__, "error": str(e)[:200],
            })

    ok = not crashed
    message = (
        "distilled tenant context detected (marker: %s); %d sibling plugin(s) executed directly "
        "-- %d raised instead of degrading (the Central-only-expectation crash class this plugin "
        "guards against)" % (_TENANT_MARKER_REL.as_posix(), checked, len(crashed))
    )
    return [CheckFinding(
        plugin_id="tenant_honesty",
        ok=ok,
        message=message,
        detail={"state": "tenant", "checked": checked, "crashed": crashed},
    )]


# --------------------------------------------------------------------------------------------- #
# Plugin 16: compiled_name_doctor -- mechanization of R-311 ("kind_manifest compiled-twin
# collision"), generalized to a corpus-wide uniqueness gate so the DISEASE CLASS cannot recur,
# not just the one kind that surfaced it.
#
# THE BUG (R-307 measure Sec 4 side-find, docs/IMPROVEMENT_REGISTER.md R-311): all ~294
# kind_manifest source files (`kind_{kind}/kind_manifest_n00.md`, one per registered kind, an
# INVARIANT filename that varies only by parent directory -- see
# archetypes/builders/kind-manifest-builder/bld_config_kind_manifest.md) collapsed onto the SAME
# compiled output path per pillar (`N00_genesis/P0X_*/compiled/kind_manifest_n00.yaml`), because
# _tools/cex_compile.py's naming seam (`compile_file()`) only ever looked at `md_path.stem` --
# identical for every instance -- never the parent directory that actually disambiguates them.
# Only the last-compiled survived; N-1 vanished silently, per pillar (12 collision points).
#
# THE FIX (companion, same R-311 mission): cex_compile.derive_out_name() now folds the parent
# directory's kind-suffix into the stem for kind_manifest ONLY (`kind_manifest_n00` ->
# `kind_manifest_{kind}_n00`) -- every other kind's stem was already unique within its LP, so
# derive_out_name() is a no-op for them (before/after name-map diff over >=5 non-kind_manifest
# kinds proves byte-identical output names, see _tools/tests/test_compile_r311.py).
#
# THIS PLUGIN'S JOB: a GENERAL compiled-name uniqueness probe, not a kind_manifest-specific
# regex. It predicts, for EVERY typed source _iter_typed_md_files() already scopes (reuse, same
# "one parser of truth" precedent as reference_doctor/identity_doctor above -- Plugin 9's own
# canonical N0X_.../P0Y_.../ corpus scan), the (lp_dir, out_name) pair cex_compile.compile_file()
# would derive for it -- via the SAME imported derive_out_name() (never re-implemented) -- and
# flags any (lp_dir, out_name) pair claimed by 2+ DISTINCT source files as a live collision. This
# catches the kind_manifest class ongoing (a future edit that reverts/bypasses the fix) AND any
# analogous future disease (a different kind adopting the same "fixed filename, varying directory"
# convention without a matching naming-seam fix).
#
# NOTE ON GRANULARITY: `lp_dir = md_path.parent.parent` (compile_file()'s own derivation) resolves
# to the LP dir 2 levels above the source (e.g. `N00_genesis/P01_knowledge` for both an
# `examples/*.md` file and a `kind_{kind}/kind_manifest_n00.md` file -- they share ONE compiled/
# dir), but for a nucleus artifact living directly at `N0X_domain/P0Y_pillar/artifact.md` (only
# ONE level below the nucleus root), `lp_dir` resolves to the NUCLEUS ROOT `N0X_domain` -- i.e.
# ALL 12 pillars of a nucleus share one `compiled/` dir too (live-verified: cex_flywheel_audit.py's
# L2 check reads `{nucleus}/compiled/`, not a per-pillar one). This plugin does not special-case
# that -- it derives `lp_dir` the IDENTICAL way compile_file() does, so a collision across two
# different pillars of the same nucleus (two files with the same stem) is correctly caught too.
#
# DEGRADE-NEVER: cex_compile is in _tools/cex_distill.py's FROZEN_TOOLS_CORE (live-verified
# 2026-07-12), unlike cex_stats/cex_kind_register/cex_preflight_mcp -- every distilled tenant
# carries it, so this import is not wrapped in the Central-only-tool try/except idiom Plugins
# 1/2/9 use (there is nothing to degrade from). A per-file read/parse error is skipped
# individually (never crashes the whole scan), matching every sibling plugin's file-loop posture.
# --------------------------------------------------------------------------------------------- #
def _run_compiled_name_doctor(root: Path) -> List[CheckFinding]:
    import cex_compile as cc  # local import, same reasoning as counter_gate (FROZEN_TOOLS_CORE)
    import cex_shared as csh  # local import, same reasoning as counter_gate

    groups: dict = {}
    scanned = 0
    schema_cache: dict = {}
    for rel in _iter_typed_md_files(root):
        md_path = root / rel
        try:
            text = md_path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        if not text.lstrip().startswith("---"):
            continue
        fm = csh.parse_frontmatter(text)
        if not fm:
            continue
        scanned += 1

        lp_dir = md_path.parent.parent
        try:
            lp_key = str(lp_dir.relative_to(root)).replace("\\", "/")
        except ValueError:
            lp_key = str(lp_dir)  # degrade-never: not under root, use the absolute path as key
        if lp_key not in schema_cache:
            try:
                schema_cache[lp_key] = cc.load_schema(lp_dir)
            except Exception:
                schema_cache[lp_key] = {}
        schema_formats = schema_cache[lp_key]
        kind = fm.get("kind")
        ext = "json" if schema_formats.get(kind, "yaml") == "json" else "yaml"
        try:
            out_name = cc.derive_out_name(md_path, kind, ext)
        except Exception:
            continue

        groups.setdefault((lp_key, out_name), []).append(rel)

    collisions = [
        {"lp_dir": lp_key, "out_name": out_name, "count": len(files), "files": sorted(files)}
        for (lp_key, out_name), files in sorted(groups.items())
        if len(files) > 1
    ]

    ok = not collisions
    message = (
        "%d typed source(s) scanned; %d predicted compiled-output name collision(s) (2+ distinct "
        "sources that would overwrite the same compiled/{name} on disk -- R-311 class)"
        % (scanned, len(collisions))
    )
    return [CheckFinding(
        plugin_id="compiled_name_doctor",
        ok=ok,
        message=message,
        detail={"scanned": scanned, "collisions": collisions[:50]},
    )]


CHECK_REGISTRY: Tuple[CheckPlugin, ...] = (
    CheckPlugin(
        id="counter_gate",
        severity="MEDIUM",
        description=(
            "R-018 class: badge/managed-region counts (kinds/builders/tools/sub_agents) in "
            "CLAUDE.md/README.md drift from the live compute() -- kills 'CLAUDE.md says 333, "
            "the repo has 334' inconsistency."
        ),
        run=_run_counter_gate,
        fix_hint="python _tools/cex_stats.py --apply",
    ),
    CheckPlugin(
        id="registry_drift",
        severity="HIGH",
        description=(
            "R-158 class: .cex/kinds_meta.json vs archetypes/TYPE_TO_TEMPLATE.yaml vs "
            "_tools/cex_8f_motor.py fall out of sync (a kind exists in the taxonomy but has no "
            "template mapping and/or no Motor routing entry)."
        ),
        run=_run_registry_drift,
        fix_hint="python _tools/cex_kind_register.py --validate  (then register the missing kind(s))",
    ),
    CheckPlugin(
        id="schema_doctor",
        severity="HIGH",
        description=(
            "R-157/R-171 class: a N00_genesis/P{01..12}_*/_schema.yaml fails to parse (flattened "
            "indentation) OR parses but maps 0 kinds to a machine_format (compile silently drops "
            "every kind in that pillar)."
        ),
        run=_run_schema_doctor,
        fix_hint="check _schema.yaml indentation under 'kinds:' -- each kind needs a machine_format key",
    ),
    CheckPlugin(
        id="provenance_doctor",
        severity="MEDIUM",
        description=(
            "S5 falsified-pointer class: a .cex/kinds_meta.json field (builder / sdk_module / "
            "schema_ref / any path-shaped value) names a path that does not resolve to an "
            "existing file."
        ),
        run=_run_provenance_doctor,
        fix_hint="fix or remove the dangling pointer field in .cex/kinds_meta.json",
    ),
    CheckPlugin(
        id="frontmatter_doctor",
        severity="HIGH",
        description=(
            "R-155/R-196 class: an artifact's frontmatter fails to parse, OR its close-delimiter "
            "would be mis-detected by the old naive substring scan vs the line-anchored helper "
            "in cex_shared.py (sampled across N00_genesis/ + archetypes/builders/)."
        ),
        run=_run_frontmatter_doctor,
        fix_hint="fix the frontmatter YAML (see detail.parse_failures / detail.close_mismatches)",
    ),
    CheckPlugin(
        id="index_freshness",
        severity="MEDIUM",
        description=(
            "R-248/R-334 class: .cex/total_index/ (L0/L1/L2 + index_meta.json) drifts once the "
            "tracked corpus is edited after the last build -- WARNs (never FAILs, never folds "
            "into --plugins-strict) once that drift exceeds 24h; absent-before-first-build is "
            "the ordinary state, not a warning. Reports the STALEST of index_meta.json's own "
            "built_at AND each heavy file's (l1_documents.json/l2_subdocuments.json) own "
            "on-disk mtime -- built_at alone can be refreshed without the heavy files "
            "themselves being rebuilt (R-334: caught live, built_at read 0.9h fresh while "
            "l1/l2 were 8 days stale)."
        ),
        run=_run_index_freshness,
        fix_hint="python _tools/cex_total_index.py --rebuild-if-stale  (or --build if never built)",
    ),
    CheckPlugin(
        id="hydration_doctor",
        severity="MEDIUM",
        description=(
            "R-249/R-250 class: generalizes R-167's per-nucleus-per-pillar thinness audit "
            "(disk-audit -> rank -> promote-from->=2x-usage, never mass-synthesize) from 1 "
            "pillar/1 nucleus to all 12 pillars x 7 operational nuclei -- 4 composed signals "
            "(density-measurement coverage, file-count unevenness, stub markers, 8f:/related: "
            "coordinate coverage) into one ranked gap table. Measurement only, never a gate."
        ),
        run=_run_hydration_doctor,
        fix_hint="python _tools/cex_hydration_doctor.py --audit  (ranks + writes docs/HYDRATION_MAP.md)",
    ),
    CheckPlugin(
        id="handoff_context_doctor",
        severity="MEDIUM",
        description=(
            "R-097/R-128 class: a N06 handoff (.cex/runtime/handoffs/*_n06.md or n06_task.md) "
            "declares a `kind:` that requires_external_context=true in kinds_meta.json, but the "
            "handoff text is missing the Phase-0 '## External Context (pre-compiled by N07 via "
            "MCP)' section -- N07 dispatched without pre-compiling the context the kind needs."
        ),
        run=_run_handoff_context_doctor,
        fix_hint=(
            "python _tools/cex_preflight_mcp.py --nucleus n06 --kind <kind> --task \"...\" "
            "--gather  (then bake the result into the handoff before dispatch)"
        ),
    ),
    CheckPlugin(
        id="identity_doctor",
        severity="MEDIUM",
        description=(
            "R-040/R-109..R-111/R-116/R-263/R-288/R-289 class: over the typed-artifact corpus, "
            "(a) an id that fails its OWN kind's LABELED bld_schema '## ID Pattern' Regex (opt-in "
            "per kind, never invented), and (b) the SAME `id:` frontmatter value duplicated across "
            "2+ files (the nucleus_def/agent_card P02-vs-P08 twin disease class). A documented, "
            "cited EXEMPT_ID_CONVENTIONS subset (R-314, load-bearing filename populations) is "
            "removed from (a)'s counted total but never silently -- see the "
            "exempted_by_convention field."
        ),
        run=_run_identity_doctor,
        fix_hint=(
            "(a) rename the id to match archetypes/builders/<kind>-builder/bld_schema_<kind>.md's "
            "'## ID Pattern' Regex; (b) pick ONE canonical file per duplicate id and delete/merge "
            "the other(s) (see R-288's P02_model-canonical-wins precedent)"
        ),
    ),
    CheckPlugin(
        id="license_doctor",
        severity="MEDIUM",
        description=(
            "Stream-G SPDX gate class: every N01_intelligence/P01_knowledge/kc_oss_*.md must "
            "declare an allowlisted permissive license (MIT/Apache-2.0/BSD-2/BSD-3/CC-BY-4.0/ISC/"
            "Unlicense), any AGPL/SSPL/GPL/BUSL/PolyForm mention must carry an explicit reference-"
            "only/negation marker nearby, and _tools/*.py top-of-file headers must not claim a "
            "non-repo license."
        ),
        run=_run_license_doctor,
        fix_hint=(
            "add/fix a license_status (or license + license_gate) line in the kc_oss_* file's "
            "Quick Reference block, or a RED/reference-only marker next to any copyleft mention; "
            "for a flagged _tools/*.py header, verify + document the vendored file's provenance"
        ),
    ),
    CheckPlugin(
        id="reference_doctor",
        severity="MEDIUM",
        description=(
            "R-160 class: a [[wikilink]] in a typed artifact's body (canonical N0X_.../P0Y_.../ "
            "tree) that does not resolve to any repo-wide frontmatter 'id:' declaration -- reuses "
            "cex_wikilink_gate.py's own id-decl scan (the Benchmark-2 grounding gate), scoped to "
            "the same corpus identity_doctor already established, as an ongoing repo-wide health "
            "measurement (complementary to cex_doctor.py's --wikilinks flag, which only gates "
            "STAGED/produced artifacts at commit time)."
        ),
        run=_run_reference_doctor,
        fix_hint=(
            "python _tools/cex_wikilink_gate.py <file> --on-fail drop  (drops fabricated links) "
            "or fix the [[target]] to the correct declared id"
        ),
    ),
    CheckPlugin(
        id="runtime_cap_doctor",
        severity="MEDIUM",
        description=(
            "R-003/audit#3 class ('content capability enabled with no generator'): every "
            "capability card in _docs/compiled/cexai_capability_catalog.yaml checked for (a) a "
            "kind actually registered in .cex/kinds_meta.json, and (b) a registered "
            "capability_generators structured generator (by slug or kind) -- a card failing (b) "
            "falls through to the generic cex_sdk build path, the exact precondition R-003's "
            "ModuleNotFoundError incident exposed in a tenant missing cex_sdk/."
        ),
        run=_run_runtime_cap_doctor,
        fix_hint=(
            "register a _tools/capability_generators/<slug>.py generator for the kind, or fix the "
            "catalog's kind: field to a real .cex/kinds_meta.json entry"
        ),
    ),
    CheckPlugin(
        id="memory_doctor",
        severity="MEDIUM",
        description=(
            "R-162 P10 class: wraps cex_memory_promote.py's promote(apply=False) (R-153 PM-3 v2, "
            "read-only) to surface the backlog of learning_record lesson groups (>=min_count) with "
            "no up-to-date pm_promoted_{key}.md draft yet (decision=ADD/UPDATE) -- N07's periodic "
            "'is anything waiting to be promoted' keystone check, mechanized."
        ),
        run=_run_memory_doctor,
        fix_hint=(
            "python _tools/cex_memory_promote.py --apply  (writes/updates the DRAFT "
            "pm_promoted_{key}.md addenda -- review before committing)"
        ),
    ),
    CheckPlugin(
        id="trace_auditor",
        severity="MEDIUM",
        description=(
            "R-009 class: an Ollama-grid wave_report.json's top-level 'usable' COUNT never "
            "cross-checked the real .trace.json-sidecar tool-call evidence -- re-derives the "
            "verdict via cex_ollama_grid.is_usable() (imported, never re-implemented) over every "
            "_reports/**/wave_report.json's own recorded per-nucleus fields, flagging any "
            "mismatch between the claimed count and the recomputed one."
        ),
        run=_run_trace_auditor,
        fix_hint=(
            "re-run the grid wave (python _tools/cex_ollama_grid.py ...) and diff the fresh "
            "wave_report.json against the flagged one; a stale/legacy report predating commit "
            "b4eb1e8695 (no require_reads key) is expected and never counted as a mismatch"
        ),
    ),
    CheckPlugin(
        id="tenant_honesty",
        severity="MEDIUM",
        description=(
            "R-162 'tenant-mode honesty (S7)' class: when this toolchain runs inside a DISTILLED "
            "TENANT repo (detected via the .cex/distill/distillation_manifest.yaml marker "
            "cex_distill.py writes), no sibling plugin may assert a Central-only expectation as a "
            "crash -- calls every other registered plugin's run() directly and reports any that "
            "raises instead of degrading (the exact disease that made counter_gate/registry_drift/"
            "handoff_context_doctor's formerly-unguarded cex_stats/cex_kind_register/"
            "cex_preflight_mcp imports risk silently blanking the WHOLE advisory tail). Outside a "
            "tenant (Central), there is nothing to assert -- ok=True, informational."
        ),
        run=_run_tenant_honesty,
        fix_hint=(
            "wrap the crashing plugin's Central-only-tool import in the same "
            "try/except-degrade-never idiom used throughout this file (see counter_gate/"
            "registry_drift/handoff_context_doctor for the pattern)"
        ),
    ),
    CheckPlugin(
        id="compiled_name_doctor",
        severity="MEDIUM",
        description=(
            "R-311 class: 2+ distinct typed .md sources under the same LP dir that "
            "cex_compile.derive_out_name() would resolve to the SAME compiled/{name} -- a silent "
            "last-compiled-wins collision (the kind_manifest disease: ~294 sources, invariant "
            "filename varying only by parent directory, collapsed onto 12 shared compiled "
            "outputs before the R-311 fix)."
        ),
        run=_run_compiled_name_doctor,
        fix_hint=(
            "disambiguate the colliding sources' compiled name in cex_compile.derive_out_name() "
            "(see the kind_manifest branch for the precedent -- fold a structural signal, e.g. "
            "the parent directory, into the stem for the colliding kind only)"
        ),
    ),
)

_BY_ID = {p.id: p for p in CHECK_REGISTRY}


def run_registry(root: Path, plugin_ids: Optional[List[str]] = None) -> List[CheckFinding]:
    """Run every selected+gated plugin in CHECK_REGISTRY order; return the flat finding list.

    R-335 per-plugin exception isolation (docs/IMPROVEMENT_REGISTER.md R-335, judge
    crash-simulation 2026-07-12): each plugin's run() is now wrapped in its OWN try/except.
    Before this fix, a plugin that RAISES (instead of the established ok=False convention
    every registered plugin uses today) propagated straight out of this loop -- and because
    this function had no per-plugin isolation, cex_doctor.py's check_registry_advisory()
    caught the exception at THIS outer call and silently degraded the WHOLE advisory tail to
    an empty list, defeating BOTH exit-code folds (the default-on PROMOTED_PLUGINS fold and
    the opt-in --plugins-strict fold) with zero visible warning -- proven live: a raise
    injected into a promoted plugin produced exit 0 in every combo. Latent in production
    (all 16 plugins use the ok=False pattern today), but one future raise would have blinded
    the doctor with no signal.

    The fix: catch any exception PER PLUGIN and emit a synthetic CheckFinding in its place --
    ok=False, plugin_id preserved as the CRASHED plugin's own id (never rewritten to a generic
    id), detail["state"]="plugin_crashed". Preserving plugin_id is what makes the synthetic
    finding "flow through both folds exactly like a genuine failure": severity_for() and
    PROMOTED_PLUGINS membership both key off plugin_id, so a crash in a promoted plugin folds
    the default exit code exactly as a genuine ok=False from that same plugin would, and a
    crash in a HIGH/BLOCKING-severity plugin folds --plugins-strict the same way. Every OTHER
    (non-crashing) plugin's findings are unaffected and still appear -- zero behavior change
    versus the pre-fix loop when nothing raises (see test_check_registry_r334_r335.py).
    """
    findings: List[CheckFinding] = []
    for plugin in CHECK_REGISTRY:
        if plugin_ids and plugin.id not in plugin_ids:
            continue
        if not plugin.selector(root):
            continue
        try:
            findings.extend(plugin.run(root))
        except Exception as e:
            findings.append(CheckFinding(
                plugin_id=plugin.id,
                ok=False,
                message="plugin %r crashed: %s: %s" % (plugin.id, type(e).__name__, e),
                detail={
                    "state": "plugin_crashed",
                    "error_type": type(e).__name__,
                    "error": str(e),
                },
            ))
    return findings


def summarize(findings: List[CheckFinding]) -> dict:
    """Suite-level aggregate -- the ExpectationSuiteValidationResult analog (successful /
    unsuccessful / evaluated / success_percent, computed by summing each finding's `ok`)."""
    evaluated = len(findings)
    successful = sum(1 for f in findings if f.ok)
    unsuccessful = evaluated - successful
    return {
        "evaluated_checks": evaluated,
        "successful_checks": successful,
        "unsuccessful_checks": unsuccessful,
        "success_percent": (100.0 * successful / evaluated) if evaluated else 100.0,
    }


def severity_for(finding: CheckFinding) -> str:
    plugin = _BY_ID.get(finding.plugin_id)
    return plugin.severity if plugin else "OBSERVATION"


def _print_human(findings: List[CheckFinding]) -> None:
    print("=" * 72)
    print("CEX Check Registry -- typed pluggable keystone checks (R-162)")
    print("Root: %s" % ROOT)
    print("=" * 72)
    for f in findings:
        sev = severity_for(f)
        tag = "OK" if f.ok else "FAIL[%s]" % sev
        print("[%s] %s: %s" % (tag, f.plugin_id, f.message))
    print("-" * 72)
    summary = summarize(findings)
    print(
        "%(successful_checks)d/%(evaluated_checks)d checks passed "
        "(%(success_percent).1f%%)" % summary
    )
    print("=" * 72)


def main(argv: Optional[List[str]] = None) -> int:
    ap = argparse.ArgumentParser(description="CEX typed pluggable check registry (R-162)")
    ap.add_argument("--json", action="store_true", help="emit machine-readable JSON findings")
    ap.add_argument("--ci", action="store_true", help="exit 1 if any BLOCKING/HIGH finding fails")
    ap.add_argument("--list", action="store_true", help="list registered plugins and exit")
    ap.add_argument("--plugin", action="append", default=None, help="run only this plugin id (repeatable)")
    args = ap.parse_args(argv)

    if args.list:
        for p in CHECK_REGISTRY:
            print("%-16s %-10s fix: %s" % (p.id, p.severity, p.fix_hint or "(none)"))
            print("  %s" % p.description)
        return 0

    findings = run_registry(ROOT, plugin_ids=args.plugin)

    if args.json:
        payload = {
            "root": str(ROOT),
            "findings": [f.to_dict() for f in findings],
            "summary": summarize(findings),
        }
        print(json.dumps(payload, indent=2, ensure_ascii=False))
    else:
        _print_human(findings)

    if args.ci:
        blocking = [f for f in findings if not f.ok and severity_for(f) in ("BLOCKING", "HIGH")]
        return 1 if blocking else 0
    return 0


if __name__ == "__main__":
    sys.exit(main())
