#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
cex_mission.py -- Mission Executor: high-level goal -> decomposed tasks -> artifacts.

The capstone of CEX autonomy. Takes a mission description, decomposes it into
concrete artifact-building tasks, and executes them via 8F Runner.

Modes:
  decompose  -- Break mission into artifact intents (read-only)
  execute    -- Decompose + build all artifacts
  status     -- Check progress of running mission

Usage:
  python _tools/cex_mission.py decompose "build analytics dashboard system"
  python _tools/cex_mission.py execute "build content marketing pipeline" --nucleus N02
  python _tools/cex_mission.py execute --from-file mission.md
  python _tools/cex_mission.py status
"""

import datetime
import json
import os
import re
import subprocess
import sys
import time
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

CEX_ROOT = Path(__file__).resolve().parent.parent
os.chdir(str(CEX_ROOT))

# Optional secretariat integration for smarter nucleus routing
sys.path.insert(0, str(Path(__file__).resolve().parent))
try:
    from cex_secretariat import classify_intent as _secretariat_classify
    _SECRETARIAT_AVAILABLE = True
except ImportError:
    _SECRETARIAT_AVAILABLE = False

# Core artifact kinds that make up a complete system
SYSTEM_TEMPLATE = [
    {"kind": "agent", "desc": "core identity and capabilities"},
    {"kind": "system_prompt", "desc": "LLM behavior rules"},
    {"kind": "knowledge_card", "desc": "domain knowledge distilled"},
    {"kind": "agent_card", "desc": "deployment specification"},
    {"kind": "dispatch_rule", "desc": "routing rules for this domain"},
    {"kind": "workflow", "desc": "execution pipeline with steps"},
    {"kind": "quality_gate", "desc": "validation gates for output"},
]

EXTENDED_KINDS = [
    {"kind": "scoring_rubric", "desc": "quality scoring dimensions"},
    {"kind": "prompt_template", "desc": "reusable prompt patterns"},
    {"kind": "action_prompt", "desc": "quick execution prompts"},
    {"kind": "pattern", "desc": "architectural patterns"},
    {"kind": "dag", "desc": "dependency graph"},
]

# Mission complexity -> how many kinds to generate
COMPLEXITY = {
    "minimal": SYSTEM_TEMPLATE[:4],          # agent, system_prompt, KC, agent_card
    "standard": SYSTEM_TEMPLATE,             # 7 core kinds
    "full": SYSTEM_TEMPLATE + EXTENDED_KINDS, # 12 kinds
}

# ---------------------------------------------------------------------------
# Compound-mission detection (spec_decomposer_fix v1.0.0)
# ---------------------------------------------------------------------------
# A "compound" mission operates on existing artifacts and/or fans out across
# runtimes/cells. The SYSTEM_TEMPLATE assumes a greenfield single-artifact
# build; for compound missions it emits the wrong plan. We branch via a small
# set of conservative regex patterns; if NONE match -> simple path is used
# (backward compatible).
#
# If a new compound shape appears in the wild, add the pattern below AND a
# corresponding entry under `_SMOKE_CASES` so the regression is locked.

_COMPOUND_PATTERN_SOURCES = {
    # (a) action verbs that operate on existing artifacts (not greenfield)
    "compound_verb": (
        r"\b("
        r"refactor|refactoring|"
        r"migrate|migration|migrating|"
        r"port|porting|"
        r"transform|transformation|transforming|"
        r"bulk|"
        r"evolve|evolving"
        r")\b"
    ),
    # (b) count quantifiers signalling fan-out
    "count_quantifier": (
        r"\b("
        r"all\s+\d+|"
        r"all\s+[Nn]\b|"
        r"\d+\s+bundles?|"
        r"\d+\s+parallel|"
        r"[Nn]\s+parallel|"
        r"each\s+of"
        r")\b"
    ),
    # (c) multi-runtime tokens
    "multi_runtime": (
        r"("
        r"multi-runtime|multi[-_]platform|cross[-_]runtime|"
        r"Custom\s+GPT|ChatGPT\s+Projects|"
        r"Claude\s+Projects|Gemini\s+Gems|"
        r"\bOllama\b"
        r")"
    ),
    # (d) source-artifact path references (operating on EXISTING content)
    "source_path": (
        r"("
        r"\.cex/runtime/scratch/|"
        r"_bundles/|"
        r"_courses/|"
        r"examples/"
        r")"
    ),
    # (e) existing-mission/spec references
    "mission_ref": (
        r"("
        r"decision_manifest\.yaml#|"
        r"\bmission:\s|"
        r"\bspec_[a-z0-9_]+|"
        r"\bMISSION_[A-Z0-9_]+|"
        r"\bWAVE_[A-Z0-9_]+"
        r")"
    ),
}

_COMPOUND_PATTERNS = {
    name: re.compile(src, re.IGNORECASE if name != "mission_ref" else 0)
    for name, src in _COMPOUND_PATTERN_SOURCES.items()
}


def _is_compound(intent: str) -> tuple[bool, list[str]]:
    """Return (is_compound, list_of_matched_pattern_names).

    Conservative: ANY pattern hit -> compound. The matched-pattern list is
    surfaced by --explain so the decision is auditable.
    """
    matched = []
    for name, pat in _COMPOUND_PATTERNS.items():
        if pat.search(intent):
            matched.append(name)
    return (len(matched) > 0, matched)


# COMPOUND_TEMPLATE -- emitted on compound detection. Wave-shaped plan; the
# caller (or N07) fills in cell-specific handoffs.
COMPOUND_TEMPLATE = [
    {
        "step": 1,
        "phase": "AUDIT",
        "kind": "audit_report",
        "intent_suffix": "audit existing artifacts: gap matrix vs CEXAI capability, proposed builder kinds per concern, fidelity targets",
        "nucleus": "N01",
        "priority": "high",
        "guidance": "N07 should write one handoff per audit cell; dispatch as grid",
    },
    {
        "step": 2,
        "phase": "BUILD",
        "kind": "<derived from audit_report output>",
        "intent_suffix": "build/refactor artifacts identified in audit",
        "nucleus": "N03",
        "priority": "high",
        "guidance": "N03 in worktrees (-w) when multi-commit per cell and >5min cell wall-clock",
    },
    {
        "step": 3,
        "phase": "VALIDATE",
        "kind": "quality_gate",
        "intent_suffix": "validate built artifacts against checklist + smoke test",
        "nucleus": "N05",
        "priority": "high",
        "guidance": "doctor 0 FAIL + per-artifact quality >= 9.0",
    },
    {
        "step": 4,
        "phase": "CONSOLIDATE",
        "kind": "consolidation_report",
        "intent_suffix": "consolidate, archive handoffs, signal completion",
        "nucleus": "N07",
        "priority": "high",
        "guidance": "stop dispatched workers; archive handoffs under .cex/runtime/archive/",
    },
]

_COMPOUND_RECOMMENDATION = {
    "template": "compound",
    "recommendation": (
        "Author a constraint_spec under _docs/specs/spec_<mission>.md before "
        "dispatch. This compound template gives the wave skeleton; N07 must "
        "fill in cell-specific handoffs."
    ),
    "spec_template_path": "_docs/specs/_template_compound_mission.md",
}


def _decompose_simple(mission: str, nucleus: str, complexity: str) -> list[dict]:
    """Original (greenfield single-artifact) decomposition path."""
    kinds = COMPLEXITY.get(complexity, COMPLEXITY["standard"])
    tasks = []

    for i, k in enumerate(kinds, 1):
        intent = f"create {k['kind']} for {mission} -- {k['desc']}"
        task = {
            "step": i,
            "kind": k["kind"],
            "intent": intent,
            "nucleus": nucleus,
            "priority": "high" if i <= 4 else "medium",
            "secretariat_provider": "local/simple",
        }
        # Secretariat: refine nucleus assignment for this sub-task
        if _SECRETARIAT_AVAILABLE and not nucleus:
            try:
                sec = _secretariat_classify(intent)
                if sec.get("nucleus") and sec.get("confidence", 0) >= 0.6:
                    task["nucleus"] = sec["nucleus"]
                    task["secretariat_provider"] = sec.get("provider", "local/simple")
            except Exception:
                pass
        tasks.append(task)

    return tasks


def _decompose_compound(mission: str, nucleus: str,
                        matched_patterns: list[str]) -> list[dict]:
    """Wave-shaped decomposition for compound missions."""
    tasks = []
    for entry in COMPOUND_TEMPLATE:
        task = {
            "step": entry["step"],
            "phase": entry["phase"],
            "kind": entry["kind"],
            "intent": f"{entry['intent_suffix']} for mission: {mission}",
            "nucleus": nucleus or entry["nucleus"],
            "priority": entry["priority"],
            "secretariat_provider": "local/compound",
            "guidance": entry["guidance"],
        }
        # Secretariat may still refine BUILD-step nucleus when caller omitted it
        if _SECRETARIAT_AVAILABLE and not nucleus and entry["phase"] == "BUILD":
            try:
                sec = _secretariat_classify(task["intent"])
                if sec.get("nucleus") and sec.get("confidence", 0) >= 0.6:
                    task["nucleus"] = sec["nucleus"]
                    task["secretariat_provider"] = sec.get(
                        "provider", "local/compound"
                    )
            except Exception:
                pass
        tasks.append(task)

    # Prepend top-level recommendation as a meta-task (step 0)
    meta = dict(_COMPOUND_RECOMMENDATION)
    meta["step"] = 0
    meta["matched_patterns"] = matched_patterns
    return [meta] + tasks


def decompose_mission(mission: str, nucleus: str = None,
                      complexity: str = "standard",
                      mode: str = "auto") -> list[dict]:
    """Decompose a mission into concrete artifact-building intents.

    mode:
      auto     -- detect compound via _is_compound, branch accordingly (default)
      simple   -- force SYSTEM_TEMPLATE path (backward compat)
      compound -- force COMPOUND_TEMPLATE path
    """
    if mode == "simple":
        return _decompose_simple(mission, nucleus, complexity)
    if mode == "compound":
        _, matched = _is_compound(mission)
        return _decompose_compound(mission, nucleus, matched)

    # auto
    is_cmp, matched = _is_compound(mission)
    if is_cmp:
        return _decompose_compound(mission, nucleus, matched)
    return _decompose_simple(mission, nucleus, complexity)


def execute_task(task: dict, dry_run: bool = False) -> dict:
    """Execute a single decomposed task via 8F Runner."""
    cmd = [
        sys.executable, str(CEX_ROOT / "_tools" / "cex_8f_runner.py"),
        task["intent"], "--kind", task["kind"],
    ]
    if task.get("nucleus"):
        cmd.extend(["--nucleus", task["nucleus"]])
    if dry_run:
        cmd.append("--dry-run")
    else:
        cmd.append("--execute")

    t0 = time.time()
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=180)
        elapsed = time.time() - t0
        full = r.stdout + r.stderr
        passed = "PASS" in full and "Verdict" in full

        # Extract output path
        path = None
        for line in full.split("\n"):
            if "Output:" in line:
                path = line.split("Output:")[-1].strip()
                break

        return {
            "step": task["step"],
            "kind": task["kind"],
            "passed": passed or dry_run,
            "path": path,
            "elapsed_s": round(elapsed, 1),
        }
    except subprocess.TimeoutExpired:
        return {"step": task["step"], "kind": task["kind"], "passed": False,
                "elapsed_s": 180, "error": "TIMEOUT"}
    except Exception as e:
        return {"step": task["step"], "kind": task["kind"], "passed": False,
                "elapsed_s": 0, "error": str(e)}


def run_mission(mission: str, nucleus: str = None, complexity: str = "standard",
                dry_run: bool = False, mode: str = "auto") -> dict:
    """Full mission execution: decompose -> execute -> validate -> commit."""
    print(f"\n{'='*60}")
    print(f"  CEX MISSION EXECUTOR -- {'DRY-RUN' if dry_run else 'EXECUTE'}")
    print(f"{'='*60}")
    print(f"  Mission: {mission}")
    print(f"  Nucleus: {nucleus or 'auto'}")
    print(f"  Complexity: {complexity}")
    print(f"  Mode: {mode}")

    # DECOMPOSE
    print("\n[>>] Decomposing mission...")
    tasks = decompose_mission(mission, nucleus, complexity, mode=mode)
    # COMPOUND_TEMPLATE prepends a step-0 meta block; skip it during execution
    exec_tasks = [t for t in tasks if t.get("step", 0) >= 1 and "kind" in t]
    print(f"   Generated {len(exec_tasks)} tasks:")
    for t in exec_tasks:
        intent_str = str(t.get("intent", ""))[:50]
        print(f"   [{t['step']}] {t['kind']:20s} -- {intent_str}...")
    # Replace tasks with exec_tasks downstream; meta block is informational
    tasks = exec_tasks

    # EXECUTE
    print("\n[>>] Executing tasks...")
    results = []
    passed = 0
    failed = 0

    for task in tasks:
        print(f"\n   [{task['step']}/{len(tasks)}] Building {task['kind']}...")
        result = execute_task(task, dry_run)
        results.append(result)

        if result["passed"]:
            passed += 1
            path = result.get("path", "N/A")
            print(f"   [OK] PASS ({result['elapsed_s']}s) -> {path}")
        else:
            failed += 1
            err = result.get("error", "gates failed")
            print(f"   [FAIL] FAIL ({result['elapsed_s']}s) -- {err}")

    # VALIDATE
    if not dry_run and passed > 0:
        print("\n[?] Post-mission validation...")
        r = subprocess.run(
            [sys.executable, "_tools/cex_hooks.py", "validate-all"],
            capture_output=True, text=True, timeout=30
        )
        full = r.stdout + r.stderr
        m = re.search(r"Errors:\s+(\d+)", full)
        hook_errors = int(m.group(1)) if m else -1
        print(f"   Hooks: {hook_errors} errors")

        # Git commit
        subprocess.run(["git", "add", "-A"], capture_output=True)
        subprocess.run(
            ["git", "commit", "-m",
             f"[MISSION] {mission[:50]} -- {passed}/{len(tasks)} artifacts built"],
            capture_output=True
        )
        print("   [>>] Mission committed to git")

    # SUMMARY
    total_time = sum(r["elapsed_s"] for r in results)
    print(f"\n{'='*60}")
    print("  MISSION COMPLETE")
    print(f"  Results: {passed} PASS | {failed} FAIL | {len(tasks)} total")
    print(f"  Time: {total_time:.0f}s ({total_time/60:.1f}min)")
    print(f"{'='*60}")

    # Save mission report
    report = {
        "mission": mission,
        "nucleus": nucleus,
        "complexity": complexity,
        "timestamp": datetime.datetime.now().isoformat(),
        "passed": passed,
        "failed": failed,
        "total": len(tasks),
        "elapsed_s": round(total_time, 1),
        "results": results,
    }

    reports_dir = CEX_ROOT / ".cex" / "mission_reports"
    reports_dir.mkdir(parents=True, exist_ok=True)
    ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    report_path = reports_dir / f"mission_{ts}.json"
    report_path.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\n  Report saved to {report_path.relative_to(CEX_ROOT)}")

    return report


def show_status():
    """Show status of recent missions."""
    reports_dir = CEX_ROOT / ".cex" / "mission_reports"
    if not reports_dir.exists():
        print("No missions executed yet.")
        return

    reports = sorted(reports_dir.glob("mission_*.json"), reverse=True)
    if not reports:
        print("No mission reports found.")
        return

    print(f"\n{'='*60}")
    print(f"  RECENT MISSIONS ({len(reports)} total)")
    print(f"{'='*60}\n")

    for rp in reports[:5]:
        data = json.loads(rp.read_text(encoding="utf-8"))
        status = "[OK]" if data["failed"] == 0 else "[WARN]"
        print(f"  {status} {data['timestamp'][:16]}")
        print(f"     Mission: {data['mission'][:50]}")
        print(f"     Results: {data['passed']}/{data['total']} PASS | {data['elapsed_s']}s")
        print()


def main():
    import argparse
    parser = argparse.ArgumentParser(
        description=(
            "CEX Mission Executor -- decompose missions into artifact intents. "
            "Auto-detects COMPOUND missions (refactor / multi-runtime / "
            "operate-on-existing-artifacts) and emits a wave-shaped plan; "
            "otherwise emits the simple SYSTEM_TEMPLATE."
        )
    )
    parser.add_argument("mode", choices=["decompose", "execute", "status", "selftest"],
                        help="Operation mode (selftest runs inline smoke tests)")
    parser.add_argument("mission", nargs="?", help="Mission description")
    parser.add_argument("--nucleus", help="Target nucleus (N01-N07)")
    parser.add_argument("--complexity", choices=["minimal", "standard", "full"],
                        default="standard", help="How many artifact kinds to generate")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--from-file", help="Read mission from file")
    parser.add_argument(
        "--decompose-mode",
        choices=["auto", "simple", "compound"],
        default="auto",
        help=(
            "Template selector: auto (detect via patterns), simple "
            "(force SYSTEM_TEMPLATE), compound (force wave-shaped plan). "
            "Default: auto."
        ),
    )
    parser.add_argument(
        "--explain",
        action="store_true",
        help="Print which compound patterns matched + chosen template path.",
    )
    args = parser.parse_args()

    if args.mode == "status":
        show_status()
        return

    if args.mode == "selftest":
        _run_smoke_tests()
        return

    mission = args.mission
    if args.from_file:
        mission = Path(args.from_file).read_text(encoding="utf-8").strip()
    if not mission:
        print("ERROR: mission description required", file=sys.stderr)
        sys.exit(1)

    if args.explain:
        is_cmp, matched = _is_compound(mission)
        chosen = args.decompose_mode
        if chosen == "auto":
            chosen = "compound" if is_cmp else "simple"
        print("=== --explain ===", file=sys.stderr)
        print(f"  mode_requested: {args.decompose_mode}", file=sys.stderr)
        print(f"  is_compound:    {is_cmp}", file=sys.stderr)
        print(f"  matched:        {matched if matched else '[]'}", file=sys.stderr)
        print(f"  chosen_path:    {chosen}", file=sys.stderr)
        print("================", file=sys.stderr)

    if args.mode == "decompose":
        tasks = decompose_mission(
            mission, args.nucleus, args.complexity, mode=args.decompose_mode
        )
        print(json.dumps(tasks, indent=2, ensure_ascii=False))

    elif args.mode == "execute":
        run_mission(
            mission, args.nucleus, args.complexity, args.dry_run,
            mode=args.decompose_mode,
        )


# ---------------------------------------------------------------------------
# Inline smoke tests (run with `python _tools/cex_mission.py selftest`)
# Covers acceptance criteria #1-#5 from spec_decomposer_fix.md section 6.
# ---------------------------------------------------------------------------

_SMOKE_CASES = [
    {
        "name": "simple_greenfield_build",
        "mission": "create a knowledge card about React patterns",
        "mode": "auto",
        "expect_template": "simple",
        "expect_matched": [],
    },
    {
        "name": "compound_refactor_multi_runtime",
        "mission": "refactor the 3 bundles into multi-runtime variants",
        "mode": "auto",
        "expect_template": "compound",
        "expect_matched_any": ["compound_verb", "count_quantifier", "multi_runtime"],
    },
    {
        "name": "compound_migrate_existing",
        "mission": "migrate legacy artifacts to new schema",
        "mode": "auto",
        "expect_template": "compound",
        "expect_matched_any": ["compound_verb"],
    },
    {
        "name": "compound_existing_spec_reference",
        "mission": "execute mission: spec_codexa_v2 -- decision_manifest.yaml#codexa_v2",
        "mode": "auto",
        "expect_template": "compound",
        "expect_matched_any": ["mission_ref"],
    },
    {
        "name": "force_simple_overrides_compound_signal",
        "mission": "refactor the 3 bundles into multi-runtime variants",
        "mode": "simple",
        "expect_template": "simple",
        "expect_matched_any": [],
    },
]


def _classify_emitted(tasks: list[dict]) -> str:
    """Return 'compound' if a step-0 meta block with template=compound was
    emitted; else 'simple'.
    """
    if tasks and isinstance(tasks[0], dict) and tasks[0].get("template") == "compound":
        return "compound"
    return "simple"


def _run_smoke_tests() -> None:
    failures = 0
    total = 0
    print("=== cex_mission selftest (spec_decomposer_fix v1.0.0) ===")
    for case in _SMOKE_CASES:
        total += 1
        tasks = decompose_mission(
            case["mission"], nucleus=None, complexity="standard",
            mode=case["mode"],
        )
        emitted = _classify_emitted(tasks)
        ok = emitted == case["expect_template"]

        # When auto/compound -- assert SOMETHING from expect_matched_any hit
        matched_ok = True
        if case["expect_template"] == "compound" and case.get("expect_matched_any"):
            _, actual_matched = _is_compound(case["mission"])
            matched_ok = any(p in actual_matched for p in case["expect_matched_any"])

        if ok and matched_ok:
            print(f"  [PASS] {case['name']:42s} -> {emitted}")
        else:
            failures += 1
            print(
                f"  [FAIL] {case['name']:42s} -> got {emitted}, "
                f"expected {case['expect_template']}; matched_ok={matched_ok}"
            )

    print(f"=== {total - failures}/{total} PASS ===")
    sys.exit(0 if failures == 0 else 1)


if __name__ == "__main__":
    try:
        from cex_agent_io import wrap_main

        def _main_wrapper(argv):
            sys.argv = [sys.argv[0]] + argv
            main()
            return 0

        sys.exit(wrap_main(_main_wrapper, sys.argv[1:], label="cex_mission"))
    except ImportError:
        main()
