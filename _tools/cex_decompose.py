#!/usr/bin/env python3
# -*- coding: ascii -*-
"""cex_decompose.py -- 8F Decompose Dispatch Orchestrator (3-stage pipeline).

Drives `bash _spawn/dispatch.sh decompose <nucleus> <task>` end-to-end.

Pipeline (corrected 2026-07-13, R-343 -- see docs/IMPROVEMENT_REGISTER.md):
  Stage 1 (reasoning):     F1-F4 -> writes prompt_package to .cex/runtime/packages/
  Stage 2 (F6 generation): reads prompt_package -> raw artifact on disk. The
                           git commit ALSO happens HERE, inside cex_8f_runner.py's
                           f8_collaborate(), gated on verdict.passed -- NOT in
                           Stage 3 as earlier drafts of this docstring claimed.
  Stage 3 (deterministic, zero LLM): wikilink gate -> cex_doctor + cex_compile ->
                           honest signal. There is NO cex_score call anywhere in
                           this file (grep confirms 0 hits) -- an earlier draft of
                           this docstring promised one that was never implemented.
                           The completion signal reflects the REAL Stage-2 F7
                           verdict (read from the freshest .cex/learning_records/
                           lr_*.json) AND doctor/compile exit codes -- never an
                           unconditional hardcoded score. See stage_3()/_stage2_
                           verdict()/_emit_signal() below.

Reads `tiers.decompose` from .cex/config/nucleus_models.yaml:
  stage_1: <model alias>    # resolved via model_aliases. SONNET5_DEFAULT_POLICY
                            # (.claude/rules/model-economy.md) resolves this to
                            # claude-sonnet-4-6 TODAY -- NOT Opus, despite the
                            # "Opus reasoning" language in older comments/tests.
  stage_2: <model alias>    # resolved via model_aliases. Same policy resolves
                            # this to claude-sonnet-4-6 TODAY -- NOT Haiku.
  stage_2_fallback: [gemini-2.5-flash-lite, qwen3:8b]  # BOTH are members of
                            # cex_intent.LEGACY_PASSTHROUGH_MODELS (R-336's
                            # audited frozenset): neither id actually reaches
                            # Gemini/Ollama today -- execute_prompt()'s Claude-
                            # CLI default branch serves both. stage_2() prints a
                            # loud [WARN] disclosure when a fallback attempt
                            # hits this set (see _legacy_passthrough_models()).
                            # Redesigning the chain itself is a GDP decision,
                            # out of this fix's scope -- disclosure only.

Environment variables:
  CEX_DECOMPOSE_STAGE        -- "1" or "2" (consumed by boot_pipeline)
  CEX_DECOMPOSE_STAGE1_MODEL -- override Stage 1 model
  CEX_DECOMPOSE_STAGE2_MODEL -- override Stage 2 model
  CEX_DECOMPOSE_GUARD        -- DGUARD policy when a factual-synthesis kind hits
                                the cheap-F6 path: warn|upgrade|refuse. Defaults
                                to warn as of R-343 (2026-07-13); explicit
                                off/0/false/no restores the pre-R-343 OFF
                                behavior byte-for-byte. See the DGUARD block
                                below.
  CEX_NUCLEUS                -- target nucleus id (n01..n07)
  CEX_SESSION_ID             -- inherited from dispatch.sh
  CEX_TRACK_COST             -- "1" (default) emits cost_log.jsonl events
  CEX_COST_CONTEXT           -- set per stage (decompose_stage_1 / _stage_2)
                                so cex_cost_tracker.py rolls up Stage 1 vs 2

Exit codes:
  0 -- success
  1 -- input error (bad args, missing config)
  2 -- Stage 1 failure
  3 -- Stage 2 failure
  4 -- Stage 3 failure

Usage examples:
  python _tools/cex_decompose.py --nucleus n03 --task "create kc_react_patterns"
  python _tools/cex_decompose.py --nucleus n04 --task "..." --dry-run
  python _tools/cex_decompose.py --nucleus n05 --task "..." \
      --stage-1-model opus --stage-2-model haiku
  python _tools/cex_decompose.py --nucleus n03 --task "..." --no-track-cost
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parent.parent
CONFIG = ROOT / ".cex" / "config" / "nucleus_models.yaml"
PACKAGES_DIR = ROOT / ".cex" / "runtime" / "packages"
RUNNER = ROOT / "_tools" / "cex_8f_runner.py"
# R-343: cex_8f_runner.py's f8_collaborate() writes ONE learning record here,
# UNCONDITIONALLY, before gating anything on verdict.passed (cex_shared.
# write_learning_record). This is the "runner already persists state" seam
# stage_3() reads to recover the REAL Stage-2 F7 verdict -- see _stage2_verdict.
LEARNING_RECORDS_DIR = ROOT / ".cex" / "learning_records"

VALID_NUCLEI = {"n01", "n02", "n03", "n04", "n05", "n06", "n07"}

EXIT_OK = 0
EXIT_INPUT = 1
EXIT_STAGE1 = 2
EXIT_STAGE2 = 3
EXIT_STAGE3 = 4


def _load_decompose_tier() -> dict[str, Any]:
    """Read tiers.decompose from nucleus_models.yaml. Empty dict on error."""
    if not CONFIG.exists():
        return {}
    try:
        data = yaml.safe_load(CONFIG.read_text(encoding="utf-8")) or {}
    except Exception as exc:  # pylint: disable=broad-except
        print("[decompose] WARN: failed to parse %s: %s" % (CONFIG, exc),
              file=sys.stderr)
        return {}
    tiers = data.get("tiers", {}) or {}
    return tiers.get("decompose", {}) or {}


def _resolve_models(args: argparse.Namespace) -> tuple[str, str, list[str]]:
    """Resolve Stage 1 / Stage 2 models with precedence:
       CLI flag > env var > YAML tier > sensible default.
    """
    tier = _load_decompose_tier()
    # Deepest defaults resolve through the alias map (no hardcoded slug -- keeps the
    # cex_doctor --models gate green); bare shorthands if the resolver is unavailable.
    try:
        from cex_model_resolver import resolve_shorthand as _rs
        _s1_default, _s2_default = _rs("opus"), _rs("haiku")
    except Exception:
        _s1_default, _s2_default = "opus", "haiku"
    s1 = (
        args.stage_1_model
        or os.environ.get("CEX_DECOMPOSE_STAGE1_MODEL", "")
        or tier.get("stage_1", "")
        or _s1_default
    )
    s2 = (
        args.stage_2_model
        or os.environ.get("CEX_DECOMPOSE_STAGE2_MODEL", "")
        or tier.get("stage_2", "")
        or _s2_default
    )
    fallback = list(tier.get("stage_2_fallback", []) or [])
    return s1, s2, fallback


def _print_call(label: str, cmd: list[str], env_extra: dict[str, str]) -> None:
    """Pretty-print a planned subprocess call (used in --dry-run)."""
    print("\n[%s] subprocess call:" % label)
    print("  cmd: %s" % " ".join(cmd))
    if env_extra:
        env_keys = ", ".join("%s=%s" % (k, v) for k, v in env_extra.items())
        print("  env: %s" % env_keys)


def _spawn(cmd: list[str], env_extra: dict[str, str], dry_run: bool,
           label: str) -> int:
    """Run a subprocess (or print it under --dry-run). Return exit code."""
    if dry_run:
        _print_call(label, cmd, env_extra)
        return 0
    env = os.environ.copy()
    env.update(env_extra)
    print("\n[%s] running: %s" % (label, " ".join(cmd)))
    proc = subprocess.run(cmd, env=env, cwd=str(ROOT), check=False)
    return int(proc.returncode)


def _find_latest_package(nucleus: str) -> Path | None:
    """Return newest pp_*.md under PACKAGES_DIR (Stage 1 output handle)."""
    if not PACKAGES_DIR.exists():
        return None
    candidates = sorted(
        PACKAGES_DIR.glob("pp_*.md"),
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )
    return candidates[0] if candidates else None


def stage_1(nucleus: str, task: str, model: str, dry_run: bool,
            track_cost: bool = True) -> tuple[int, Path | None]:
    """Run Stage 1: reasoning -> prompt_package (tiers.decompose.stage_1;
    claude-sonnet-4-6 today under SONNET5_DEFAULT_POLICY, not Opus).

    When track_cost=True (default), sets CEX_COST_CONTEXT=decompose_stage_1
    so cex_intent.execute_prompt() tags emitted cost_log entries with the
    stage. Pass --no-track-cost to disable for CI/sandbox runs.
    """
    cmd = [
        sys.executable, str(RUNNER),
        "--stage", "1",
        "--mode", "B",
        "--nucleus", nucleus.upper(),
        "--model", model,
        task,
    ]
    env_extra = {
        "CEX_DECOMPOSE_STAGE": "1",
        "CEX_NUCLEUS": nucleus.upper(),
        "CEX_MODEL_OVERRIDE": model,
        "CEX_TRACK_COST": "1" if track_cost else "0",
    }
    if track_cost:
        env_extra["CEX_COST_CONTEXT"] = "decompose_stage_1"
    code = _spawn(cmd, env_extra, dry_run, "STAGE-1")
    if code != 0:
        return code, None
    pkg = _find_latest_package(nucleus) if not dry_run else None
    if not dry_run and pkg is None:
        print("[decompose] FAIL: Stage 1 produced no prompt_package", file=sys.stderr)
        return EXIT_STAGE1, None
    return EXIT_OK, pkg


# --- R-343 fix 4: fallback-fiction disclosure -----------------------------
# tiers.decompose.stage_2_fallback = [gemini-2.5-flash-lite, qwen3:8b] -- BOTH
# ids are members of cex_intent.LEGACY_PASSTHROUGH_MODELS (the R-336 audited
# frozenset of model_override values that execute_prompt() silently serves via
# its Claude-CLI default branch, never reaching the named provider). This does
# NOT redesign the fallback chain (that is a GDP decision, out of scope) -- it
# only makes the fact LOUD at the moment a fallback attempt actually fires.
def _legacy_passthrough_models() -> frozenset:
    """Read-only view of cex_intent.LEGACY_PASSTHROUGH_MODELS.

    cex_intent.py is a SIBLING lane's fence in this wave (HARDEN_0713 router
    lane) -- this helper only ever READS the set via a lazy, function-scoped
    import (mirrors _resolve/_ladder_for/_score_fast_value's existing lazy-
    import style in this same file) and never edits cex_intent.py. Degrade-
    never: any import failure returns an empty frozenset, so the disclosure
    below simply does not fire -- exactly the pre-fix silence, never a crash.
    """
    try:
        from cex_intent import LEGACY_PASSTHROUGH_MODELS
        return LEGACY_PASSTHROUGH_MODELS
    except Exception:
        return frozenset()


def stage_2(nucleus: str, model: str, fallback: list[str], pkg: Path | None,
            dry_run: bool, track_cost: bool = True) -> int:
    """Run Stage 2: cheap model F6 from prompt_package.

    When track_cost=True (default), sets CEX_COST_CONTEXT=decompose_stage_2
    so emitted cost events can be rolled up per stage in cex_cost_tracker.
    """
    pkg_arg = str(pkg) if pkg else "<package_from_stage_1>"
    cmd = [
        sys.executable, str(RUNNER),
        "--stage", "2",
        "--mode", "B",
        "--nucleus", nucleus.upper(),
        "--model", model,
        "--prompt-package", pkg_arg,
        "--execute",
    ]
    env_extra = {
        "CEX_DECOMPOSE_STAGE": "2",
        "CEX_NUCLEUS": nucleus.upper(),
        "CEX_MODEL_OVERRIDE": model,
        "CEX_TRACK_COST": "1" if track_cost else "0",
    }
    if track_cost:
        env_extra["CEX_COST_CONTEXT"] = "decompose_stage_2"
    code = _spawn(cmd, env_extra, dry_run, "STAGE-2")
    if code == 0 or dry_run:
        return code
    # Fallback chain: try each cheaper model in turn
    for alt in fallback:
        print("[decompose] Stage 2 retry with fallback model: %s" % alt)
        if alt in _legacy_passthrough_models():
            print("[WARN] fallback '%s' is LEGACY_PASSTHROUGH -> served by "
                  "Claude CLI, not %s" % (alt, alt))
        cmd[cmd.index(model)] = alt
        env_extra["CEX_MODEL_OVERRIDE"] = alt
        code = _spawn(cmd, env_extra, dry_run, "STAGE-2-FALLBACK")
        if code == 0:
            return code
        model = alt
    return EXIT_STAGE2 if code != 0 else EXIT_OK


# --- W2 wikilink gate (Benchmark-2 mandated hard gate on the cheap path) ------
# bench2 proved the producer-rail does NOT stop wikilink hallucination: 3/3
# rail-governed cheap producers fabricated links (7/7 = 0 id-decls on disk). The
# gate runs at the TOP of Stage 3, before doctor/compile/signal, so a
# fabricated-link artifact never reaches F8 (no completion signal is written).

_GATE_SKIP_DIRS = {".git", ".obsidian", "__pycache__", "node_modules", ".cex",
                   ".pytest_cache", ".mypy_cache"}


def _find_recent_artifact(since_ts: float) -> Path | None:
    """Newest .md under ROOT modified at/after since_ts (the Stage-2 output).

    Best-effort: decompose builds ONE artifact per run, so the freshly-written
    .md (outside infra dirs -- Stage-1 packages live under .cex and are skipped)
    is that artifact. Returns None if nothing matches, in which case Stage 3
    logs and skips the in-pipeline gate. The W3 swarm does not rely on this
    discovery -- it calls cex_wikilink_gate.gate(path) with an explicit path.
    """
    newest: Path | None = None
    newest_mtime = since_ts - 2.0  # small slack for fs timestamp granularity
    for dirpath, dirnames, filenames in os.walk(ROOT):
        dirnames[:] = [d for d in dirnames if d not in _GATE_SKIP_DIRS]
        for fn in filenames:
            if not fn.endswith(".md"):
                continue
            fp = Path(dirpath) / fn
            try:
                mt = fp.stat().st_mtime
            except OSError:
                continue
            if mt >= newest_mtime:
                newest_mtime = mt
                newest = fp
    return newest


def _run_wikilink_gate(artifact_path: Path, on_fail: str) -> int:
    """Gate one artifact's wikilinks. EXIT_OK to proceed, EXIT_STAGE3 to abort.

    Policy:
      drop     -- strip fabricated [[X]] to plain text, then proceed (EXIT_OK).
      escalate -- abort Stage 3 (artifact kept for mentor review).
      reject   -- abort Stage 3 (default; artifact blocked from F8).
    """
    try:
        from cex_wikilink_gate import gate, repair_file
    except Exception as exc:  # pragma: no cover - defensive (module ships beside this)
        print("[decompose] WARN: wikilink gate unavailable (%s); skipping" % exc,
              file=sys.stderr)
        return EXIT_OK
    ok, fabricated = gate(str(artifact_path))
    if ok:
        print("[decompose] wikilink gate PASS: %s" % artifact_path)
        return EXIT_OK
    if on_fail == "drop":
        dropped = repair_file(str(artifact_path), fabricated)
        print("[decompose] wikilink gate DROP: removed %d fabricated link(s) %s "
              "from %s; artifact proceeds" % (len(dropped), dropped, artifact_path))
        return EXIT_OK
    label = "ESCALATE" if on_fail == "escalate" else "REJECT"
    print("[decompose] wikilink gate %s: %d fabricated link(s) in %s -> %s"
          % (label, len(fabricated), artifact_path, fabricated), file=sys.stderr)
    print("[decompose] artifact BLOCKED from F8 (no signal written). "
          "Fix the links or re-run with --gate-on-fail drop.", file=sys.stderr)
    return EXIT_STAGE3


# --- R-352 safety net: kind-fidelity gate (Stage 3, sibling to wikilink gate) -
# docs/IMPROVEMENT_REGISTER.md R-352 (estreia lote42, 2026-07-13): glm-cpw
# drifted the declared `kind:` in 3/12 Stage-2 artifacts. cex_8f_runner.py's
# own F7 GOVERN (H03, hardened by this same wave) already enforces
# frontmatter.kind against the Stage-1-constrained kind INSIDE the Stage-2
# subprocess, with the R-342 retry/ladder machinery attached. This is a
# SEPARATE, INDEPENDENT check at the decompose-orchestrator level: f8_
# collaborate() writes the artifact to disk UNCONDITIONALLY -- even on a
# failed F7 verdict, only the git COMMIT itself is gated on verdict.passed
# (cex_8f_runner.py f8_collaborate, "Auto-commit if gates passed" block) -- so
# a kind-drifted draft can still land, uncommitted, in the working tree, where
# a later blanket `git add` (outside this fix's fence) could sweep it up. This
# gate re-verifies the ON-DISK artifact against the Stage-1 package's own
# target_kind independently of whatever the Stage-2 subprocess's F7 decided --
# defense in depth, mirroring the wikilink gate's exact role. Provably new:
# cex_decompose.py had ZERO kind-verification before this fix (grep for any
# kind-comparison in this file pre-fix returns nothing beyond DGUARD's
# ROUTING heuristic, which never reads a produced artifact's own frontmatter).


def _extract_target_kind(pkg_text: str) -> str:
    """target_kind: value from a Stage-1 prompt_package's frontmatter. Empty
    string when absent/unparseable -- degrade-never (caller treats empty as
    "nothing to check against", never a false rejection)."""
    m = re.search(r"^target_kind:\s*(\S+)", pkg_text, re.MULTILINE)
    return m.group(1).strip() if m else ""


def _run_kind_gate(artifact_path: "Path | str", pkg_path: "Path | None") -> int:
    """Verify the freshly-produced artifact's frontmatter kind matches the
    Stage-1 package's target_kind. EXIT_OK to proceed (including every
    degrade-never skip below), EXIT_STAGE3 to reject.

    Degrade-never: no pkg_path, an unreadable package, a missing target_kind,
    an unreadable artifact, unparseable frontmatter, or a missing kind field
    are ALL silent skips (EXIT_OK) -- this gate only ever REJECTS on a
    positive, confident mismatch; it never invents a failure from missing
    signal (same contract as _run_wikilink_gate's own "module unavailable ->
    skip" branch).
    """
    if pkg_path is None:
        return EXIT_OK
    try:
        pkg_text = Path(pkg_path).read_text(encoding="utf-8")
    except OSError:
        return EXIT_OK
    target_kind = _extract_target_kind(pkg_text)
    if not target_kind:
        return EXIT_OK
    try:
        artifact_text = Path(artifact_path).read_text(encoding="utf-8")
    except OSError:
        return EXIT_OK
    try:
        from cex_shared import extract_frontmatter_dict
        fm = extract_frontmatter_dict(artifact_text)
    except Exception:
        return EXIT_OK
    if not fm:
        return EXIT_OK
    actual_kind = str(fm.get("kind", ""))
    if not actual_kind or actual_kind == target_kind:
        return EXIT_OK
    print(
        "[decompose] KIND-GATE REJECT: artifact declares kind '%s', Stage 1 "
        "constrained '%s' (R-352, fail-closed -- never accept the model's "
        "own auto-declared kind over the constrained one). Re-dispatch, "
        "optionally at a stronger Stage-2 tier (-2 sonnet / -2 opus)."
        % (actual_kind, target_kind),
        file=sys.stderr,
    )
    print("[decompose] artifact BLOCKED from F8 (no signal written).",
          file=sys.stderr)
    return EXIT_STAGE3


# --- R-351 content-fidelity gate (Stage 3, sibling to wikilink+kind gates) ----
# docs/IMPROVEMENT_REGISTER.md R-351 (estreia lote42, 2026-07-13): the F7
# GOVERN hard gates (H01-H06 + kind) are PURELY STRUCTURAL -- frontmatter
# parses, id matches its pattern, required fields present, body <= max_bytes,
# kind matches. NONE of them check that the CONTENT actually answers the
# request: a pricing input_schema came back as generic field1/field2/field3
# placeholders (author "Example Author") while the prompt_package carried the
# 8 real requested fields, and gate-PASSED 6/6. This is the "sugar code" trap
# the founder explicitly warned against, proved live. Fix, per the register's
# own star-recommendation (simplest that closes the hole, no over-engineering):
#   (a) SEMPRE-ON, zero-token, deterministic assert -- extract the field/
#       section tokens the ORIGINAL --task string declares as expected (e.g.
#       "... fields product str required, segment str required, ...") and
#       check the produced body actually mentions them (not placeholder
#       filler); a placeholder-token blacklist (field1, Example Author,
#       unresolved {{...}}, lorem) is an independent, always-checked signal.
#   (b) OPT-IN llm_judge hook, gated on CEX_DECOMPOSE_CONTENT_JUDGE=1 (default
#       OFF -- behavior is (a) alone unless the env is set). The default judge
#       implementation is mockable via the judge_fn seam so the test suite
#       never touches the network.
# Provably new: cex_decompose.py had ZERO content-fidelity checking before
# this fix (grep confirms -- the only "content" awareness pre-fix is DGUARD's
# kind-based ROUTING heuristic, which runs BEFORE Stage 1 and never reads a
# produced artifact's body).

_PLACEHOLDER_TOKENS = (
    "field1", "field2", "field3", "example author", "example_operation",
    "lorem ipsum", "todo:", "placeholder text",
)

_FIELD_CLAUSE_RE = re.compile(
    r"\b(?:fields|campos|sections|secoes)\s*[:\s]\s*(.+)$",
    re.IGNORECASE,
)


def _detect_placeholder_tokens(body_lower: str) -> list:
    """Blacklist scan for generic-template filler (R-351's own examples:
    field1/field2/field3, 'Example Author', unresolved {{...}}, lorem)."""
    found = [tok for tok in _PLACEHOLDER_TOKENS if tok in body_lower]
    if re.search(r"\{\{\s*[a-zA-Z_][a-zA-Z0-9_]*\s*\}\}", body_lower):
        found.append("{{unresolved}}")
    return found


def _extract_expected_tokens(task_text: str) -> list:
    """Best-effort expected content tokens from the ORIGINAL --task string
    (e.g. "... fields product str required, segment str required, ..."):
    returns the lowercased identifier-looking first token of each comma-
    separated clause after a fields/sections keyword. Empty when no such
    clause is found -- the caller then relies on the placeholder blacklist
    alone (degrade-never: absent signal never manufactures a rejection)."""
    if not task_text:
        return []
    m = _FIELD_CLAUSE_RE.search(task_text)
    if not m:
        return []
    tokens = []
    for chunk in m.group(1).split(","):
        chunk = chunk.strip()
        if not chunk:
            continue
        first = re.split(r"\s+", chunk)[0].strip(".:;")
        if first and re.match(r"^[a-zA-Z_][a-zA-Z0-9_]*$", first):
            tokens.append(first.lower())
    return tokens


def _check_content_fidelity(artifact_text: str, task_text: str) -> "tuple[bool, str]":
    """(a) SEMPRE-ON deterministic, zero-token content-fidelity check.
    Returns (ok, reason) -- reason is "" when ok."""
    try:
        from cex_shared import strip_frontmatter
        body = strip_frontmatter(artifact_text)
    except Exception:
        body = artifact_text
    body_lower = body.lower()

    placeholders = _detect_placeholder_tokens(body_lower)
    if placeholders:
        return False, "placeholder tokens found: %s" % ", ".join(placeholders)

    expected = _extract_expected_tokens(task_text)
    if expected:
        missing = [t for t in expected if t not in body_lower]
        # Majority-present: allow the model paraphrase slack, but a MAJORITY
        # missing means the artifact ignored the real requested fields.
        if len(missing) > len(expected) // 2:
            return False, (
                "expected fields mostly absent (%d/%d missing: %s)"
                % (len(missing), len(expected), ", ".join(missing))
            )
    return True, ""


def _content_judge_stub(artifact_path: "Path | str", task_text: str) -> "tuple[bool, str]":
    """(b) OPT-IN llm_judge hook -- default implementation, CEX_DECOMPOSE_
    CONTENT_JUDGE=1 only. Reuses the same zero-LLM structural scorer A3
    escalation already uses (cex_score_python.score_fast) rather than a live
    LLM call -- cheap, deterministic, and never touches the network; a true
    LLM judge can be wired later behind the same judge_fn seam without
    changing this function's callers. Never invoked by the test suite's
    default path (tests inject judge_fn), so this code is not exercised over
    the network in CI regardless."""
    try:
        from cex_score_python import score_fast
        result = score_fast(str(artifact_path))
        score = result.get("score")
        if score is None:
            return True, "judge: no score available, not blocking"
        return (score >= 6.0), "judge score=%.1f" % score
    except Exception as e:
        return True, "judge unavailable (%s), not blocking" % e


def _run_content_fidelity_gate(artifact_path: "Path | str", task_text: str = "",
                               judge_fn=None) -> int:
    """R-351: (a) always-on placeholder/field-coverage check, fail-closed --
    plus (b) an opt-in llm_judge hook (env CEX_DECOMPOSE_CONTENT_JUDGE=1).
    EXIT_OK to proceed (incl. every degrade-never skip), EXIT_STAGE3 reject.
    """
    try:
        artifact_text = Path(artifact_path).read_text(encoding="utf-8")
    except OSError:
        return EXIT_OK
    ok, reason = _check_content_fidelity(artifact_text, task_text)
    if not ok:
        print(
            "[decompose] CONTENT-FIDELITY REJECT: %s (R-351, fail-closed -- "
            "the sugar-code trap: structural gates alone do not check the "
            "content matches the request). Re-dispatch, optionally at a "
            "stronger Stage-2 tier (-2 sonnet / -2 opus)." % reason,
            file=sys.stderr,
        )
        print("[decompose] artifact BLOCKED from F8 (no signal written).",
              file=sys.stderr)
        return EXIT_STAGE3
    if os.environ.get("CEX_DECOMPOSE_CONTENT_JUDGE", "").strip() == "1":
        judge_fn = judge_fn or _content_judge_stub
        j_ok, j_reason = judge_fn(artifact_path, task_text)
        print("[decompose] content judge (opt-in, CEX_DECOMPOSE_CONTENT_JUDGE=1): %s"
              % j_reason)
        if not j_ok:
            print("[decompose] CONTENT-FIDELITY REJECT (judge): %s" % j_reason,
                  file=sys.stderr)
            print("[decompose] artifact BLOCKED from F8 (no signal written).",
                  file=sys.stderr)
            return EXIT_STAGE3
    return EXIT_OK


# --- R-343 fix 1+2: honest signal (real Stage-2 verdict, never a hardcoded
# score, never 'complete' when doctor/compile fail) ---------------------------
# Pre-fix, this module wrote write_signal(nucleus, 'complete', 9.0) UNCONDIT-
# IONALLY: cex_8f_runner.py's own main() returns exit 0 even when F7 exhausts
# retries with verdict.passed=False (confirmed by direct reading -- there is no
# `sys.exit` tied to verdict.get("passed") anywhere in that file), so Stage 2's
# subprocess exit code alone cannot tell decompose.py whether F7 actually
# passed. The runner DOES persist the real verdict, just not where the R-343
# register row first assumed (the 8f_state/ enforcer json only tracks WHICH
# F1-F8 markers fired, not pass/fail): cex_shared.write_learning_record() is
# called UNCONDITIONALLY at the top of f8_collaborate(), before anything is
# gated on verdict.passed, and its record includes "passed"/"gates_passed"/
# "gates_total"/"issues" straight from the real F7 verdict dict. That is the
# seam below reads.


def _find_recent_learning_record(since_ts: float) -> Path | None:
    """Newest .cex/learning_records/lr_*.json written at/after since_ts.

    Mirrors _find_recent_artifact's discovery pattern exactly (same slack,
    same incremental-max-mtime scan), applied to LEARNING_RECORDS_DIR instead
    of the whole repo. Returns None if the dir is absent or nothing matches --
    the caller (_stage2_verdict) treats that as UNVERIFIED, never as a pass.
    """
    if not LEARNING_RECORDS_DIR.exists():
        return None
    newest: Path | None = None
    newest_mtime = since_ts - 2.0  # small slack for fs timestamp granularity
    for fp in LEARNING_RECORDS_DIR.glob("lr_*.json"):
        try:
            mt = fp.stat().st_mtime
        except OSError:
            continue
        if mt >= newest_mtime:
            newest_mtime = mt
            newest = fp
    return newest


def _stage2_verdict(since_ts: "float | None",
                    find_fn=None) -> "dict | None":
    """Read the REAL Stage-2 F7 verdict persisted by the runner itself.

    Returns None when since_ts is None or no matching learning record exists
    (degrade-never -- the caller must treat None as UNVERIFIED, never as an
    implicit pass). On a real record, returns {"passed": bool, "gates_passed":
    int|None, "gates_total": int|None, "issues": list} -- read-only fields
    straight from cex_shared.write_learning_record()'s own output, no new
    coupling to cex_8f_runner.py internals.

    `find_fn` is an injectable seam (default _find_recent_learning_record) so
    unit tests can simulate a PASS/FAIL verdict with no real learning record
    on disk -- same shape as _escalate_below_floor's find_fn/score_fn seams.
    """
    if since_ts is None:
        return None
    find_fn = find_fn or _find_recent_learning_record
    lr_path = find_fn(since_ts)
    if lr_path is None:
        return None
    try:
        data = json.loads(Path(lr_path).read_text(encoding="utf-8"))
    except Exception:
        return None
    return {
        "passed": bool(data.get("passed", False)),
        "gates_passed": data.get("gates_passed"),
        "gates_total": data.get("gates_total"),
        "issues": data.get("issues", []),
    }


def _emit_signal(nucleus: str, status: str, score: float, **extra) -> None:
    """Emit one signal via signal_writer.write_signal, never raising.

    Signal delivery failing must not crash Stage 3 (matches the pre-fix
    try/except-and-WARN contract) -- but unlike pre-fix, `status` and `score`
    are supplied by the caller (never a hardcoded literal in this function).
    """
    try:
        sys.path.insert(0, str(ROOT / "_tools"))
        from signal_writer import write_signal  # noqa: E402

        write_signal(nucleus.upper(), status, float(score), **extra)
    except Exception as exc:  # pylint: disable=broad-except
        print("[decompose] WARN: signal_writer failed: %s" % exc,
              file=sys.stderr)


def stage_3(nucleus: str, dry_run: bool, artifact_path: Path | None = None,
            on_fail: str = "reject", since_ts: "float | None" = None,
            verdict_fn=None, score_fn=None,
            pkg_path: "Path | None" = None, task_text: str = "",
            kind_gate_fn=None, content_gate_fn=None) -> int:
    """Run Stage 3: wikilink gate -> kind gate -> content-fidelity gate ->
    deterministic validation -> honest signal.

    W2 HARD GATE (Benchmark-2 mandated): before any doctor/compile/signal, the
    freshly-produced artifact must pass the wikilink grounding gate. A fabricated
    [[link]] (target id not declared on disk) means the cheap producer
    hallucinated; the artifact must NOT reach F8. See _run_wikilink_gate for the
    drop/escalate/reject policy. The authoritative per-artifact entry point for
    the W3 swarm is cex_wikilink_gate.gate(path); this hook is the in-pipeline
    safety net for the `decompose` dispatch mode. A wikilink-gate rejection
    returns here immediately -- no signal is written either way (unchanged).

    R-352 kind gate + R-351 content-fidelity gate (2026-07-13, this fix): run
    immediately after the wikilink gate, same reject-and-return-early shape.
    Both are defense-in-depth, independent of whatever the Stage-2 subprocess's
    own F7 GOVERN decided -- see _run_kind_gate / _run_content_fidelity_gate's
    own docstrings for the full rationale. `pkg_path` (the Stage-1 package,
    for target_kind) and `task_text` (the original --task string, for expected
    content tokens) are OPTIONAL -- omitting either degrade-never-skips the
    corresponding gate (EXIT_OK), so every pre-existing caller of stage_3()
    that does not pass them is completely unaffected. `kind_gate_fn` /
    `content_gate_fn` are injectable seams (default _run_kind_gate /
    _run_content_fidelity_gate) mirroring verdict_fn/score_fn's own pattern.

    R-343 honest signal (this function's other half): the completion signal
    is gated on TWO real conditions, never assumed --
      1. the REAL Stage-2 F7 verdict, read from the freshest learning record
         via _stage2_verdict(since_ts) -- NOT the Stage-2 subprocess exit code
         (which is 0 even when F7 exhausted retries with passed=False);
      2. doctor + compile both exiting 0 in THIS Stage 3 run.
    Only when BOTH hold does the signal say 'complete', carrying a REAL score
    (_score_fast_value on the artifact -- zero-LLM structural score, the same
    mechanism A3 escalation already uses -- 0.0 + score_real=False if that is
    unavailable). Any other outcome writes 'failed' + a `reason` and returns
    EXIT_STAGE3 -- never a silent, unconditional 'complete'.

    `since_ts` should be the Stage-2 start timestamp (main() passes produce_t0)
    so _stage2_verdict can find the right learning record; None degrades to an
    UNVERIFIED verdict (treated as failed -- never an implicit pass). `verdict_fn`
    / `score_fn` are injectable seams (default _stage2_verdict / _score_fast_
    value) for hermetic unit tests, mirroring _escalate_below_floor's pattern.
    """
    if artifact_path is not None and not dry_run:
        code = _run_wikilink_gate(artifact_path, on_fail)
        if code != EXIT_OK:
            return code
        kind_gate_fn = kind_gate_fn or _run_kind_gate
        code = kind_gate_fn(artifact_path, pkg_path)
        if code != EXIT_OK:
            return code
        content_gate_fn = content_gate_fn or _run_content_fidelity_gate
        code = content_gate_fn(artifact_path, task_text)
        if code != EXIT_OK:
            return code
    elif artifact_path is not None and dry_run:
        print("\n[STAGE-3:wikilink-gate] would gate %s (on-fail=%s)"
              % (artifact_path, on_fail))
        print("[STAGE-3:kind-gate] would verify artifact kind vs Stage-1 "
              "target_kind (R-352 safety net)")
        print("[STAGE-3:content-fidelity-gate] would verify content vs "
              "intent -- placeholder-blacklist + expected-field coverage "
              "(R-351)")
    steps: list[tuple[str, list[str]]] = [
        ("doctor", [sys.executable, str(ROOT / "_tools" / "cex_doctor.py")]),
        ("compile", [sys.executable, str(ROOT / "_tools" / "cex_compile.py"),
                     "--all"]),
    ]
    tools_ok = True
    for label, cmd in steps:
        code = _spawn(cmd, {}, dry_run, "STAGE-3:" + label)
        if code != 0 and not dry_run:
            print("[decompose] WARN: %s exited %d (continuing)" % (label, code),
                  file=sys.stderr)
            tools_ok = False

    if dry_run:
        print("\n[STAGE-3:signal] (dry-run) would resolve the REAL Stage-2 "
              "verdict via the freshest .cex/learning_records/lr_*.json + "
              "doctor/compile exit codes, then write_signal('%s', "
              "'complete'|'failed', <real score or 0.0>) -- never a "
              "hardcoded 9.0, never unconditional 'complete'." % nucleus.upper())
        return EXIT_OK

    verdict_fn = verdict_fn or _stage2_verdict
    score_fn = score_fn or _score_fast_value
    verdict = verdict_fn(since_ts)
    stage2_passed = bool(verdict and verdict.get("passed"))

    if stage2_passed and tools_ok:
        score = score_fn(artifact_path) if artifact_path else None
        real_score = score is not None
        _emit_signal(nucleus, "complete", score if real_score else 0.0,
                    score_real=real_score)
        return EXIT_OK

    reason = "stage_2_verdict_failed" if not stage2_passed else "stage_3_tools_nonzero"
    _emit_signal(nucleus, "failed", 0.0, reason=reason,
                gates_passed=(verdict or {}).get("gates_passed"),
                gates_total=(verdict or {}).get("gates_total"))
    print("[decompose] FAIL: %s -- no 'complete' signal written" % reason,
          file=sys.stderr)
    return EXIT_STAGE3


# --- A3 quality-floor escalation (LEVERAGE_A3, flag-gated, OFF by default) ------
# bench2 + W5 proved the cheap tier sometimes lands a GATE-CLEAN artifact that is
# still BELOW the quality floor. The mentor-student swarm already auto-escalates
# such an artifact (cheap -> mid -> premium); the `decompose` dispatch path did
# NOT. This closes that gap WITHOUT changing today's behavior: the whole block is
# unreachable unless CEX_DECOMPOSE_ESCALATE=1 (or --escalate-on-floor) is set, so
# an unset run is BYTE-IDENTICAL to pre-A3. When ON, after Stage 2 the freshly
# produced artifact is scored (zero-LLM score_fast) and, while it is below the
# decompose floor (tiers.decompose.min_score = 8.0), Stage 2 is RE-RUN at the next
# tier of the SAME provider escalation ladder the swarm uses
# (tiers.escalation_ladders -- single source of truth, provider-agnostic). The
# existing Stage-3 wikilink gate still runs after, so escalation never weakens the
# grounding invariant. Degrade-never: any escalation error keeps the Stage-2
# artifact and proceeds (no worse than OFF).

ESCALATE_FLOOR = 8.0  # tiers.decompose.min_score fallback (see _decompose_floor)


def _decompose_floor() -> float:
    """The decompose quality floor (tiers.decompose.min_score), default 8.0."""
    tier = _load_decompose_tier()
    try:
        return float(tier.get("min_score", ESCALATE_FLOOR))
    except (TypeError, ValueError):
        return ESCALATE_FLOOR


def _escalation_enabled(args: argparse.Namespace) -> bool:
    """True iff the A3 escalation pass is opted in (CLI flag OR env flag).
    OFF by default -> the escalation block is never reached (byte-identical)."""
    if getattr(args, "escalate_on_floor", False):
        return True
    return os.environ.get("CEX_DECOMPOSE_ESCALATE", "0") == "1"


def _score_fast_value(path: "Path | str") -> "float | None":
    """Zero-LLM structural score for one artifact (cex_score_python.score_fast).
    None on any failure -> the caller treats it as 'no signal' (no climb)."""
    try:
        from cex_score_python import score_fast
        return score_fast(str(path)).get("score")
    except Exception:
        return None


def _resolve(model: str) -> str:
    """Resolve a shorthand/alias to a concrete model id (identity on failure)."""
    try:
        from cex_model_resolver import resolve_shorthand as _rs
        return (_rs(model) or model).lower()
    except Exception:
        return (model or "").lower()


def _ladder_for(model: str):
    """The provider escalation ladder for `model` (cex_mentor_swarm, W6) -- a tuple
    of (tier_name, alias, floor) steps. None if unavailable (no climb)."""
    try:
        from cex_mentor_swarm import load_escalation_ladder
        return load_escalation_ladder(model)
    except Exception:
        return None


def _next_tier_model(cur_model: str, ladder) -> "str | None":
    """Model id of the tier ABOVE cur_model on `ladder`, or None at/after terminal.
    Matches cur_model against each step's resolved alias; a cur_model not on the
    ladder is assumed to sit at the cheapest tier (index 0)."""
    if not ladder:
        return None
    resolved = _resolve(cur_model)
    idx = 0
    for i, step in enumerate(ladder):
        if _resolve(step[1]) == resolved or step[0] in resolved:
            idx = i
            break
    nxt = idx + 1
    if nxt >= len(ladder):
        return None  # already at the terminal (premium) tier
    return _resolve(ladder[nxt][1])


def _escalate_below_floor(nucleus: str, s2_model: str, fallback: "list[str]",
                          pkg: "Path | None", since_ts: float, *,
                          floor: "float | None" = None, track_cost: bool = True,
                          ladder=None, score_fn=None, produce_fn=None,
                          find_fn=None) -> str:
    """Climb the escalation ladder while the fresh artifact scores below `floor`.

    Re-runs Stage 2 at each stronger tier (cheap -> mid -> premium). Returns the
    FINAL model id used. Seams (score_fn / produce_fn / find_fn / ladder) default
    to the real implementations; the unit test injects deterministic fixtures so
    the climb is exercised with no subprocess and no model call. Bounded by the
    ladder length (no infinite climb). Degrade-never: a missing ladder or score
    signal stops the climb and keeps the current artifact.
    """
    if floor is None:
        floor = _decompose_floor()
    if find_fn is None:
        find_fn = _find_recent_artifact
    if score_fn is None:
        score_fn = _score_fast_value
    if ladder is None:
        ladder = _ladder_for(s2_model)
    if produce_fn is None:
        def produce_fn(model: str) -> "Path | None":
            stage_2(nucleus, model, fallback, pkg, dry_run=False,
                    track_cost=track_cost)
            return find_fn(since_ts)
    cur_model = s2_model
    art = find_fn(since_ts)
    for _ in range(len(ladder) if ladder else 0):
        if art is None:
            break
        score = score_fn(art)
        if score is None or score >= floor:
            break
        nxt = _next_tier_model(cur_model, ladder)
        if not nxt or _resolve(nxt) == _resolve(cur_model):
            break  # terminal tier -- accept whatever it produced
        print("[decompose] ESCALATE: score %.1f < floor %.1f -> re-produce at %s"
              % (score, floor, nxt))
        art = produce_fn(nxt)
        cur_model = nxt
    return cur_model


# --- DGUARD: factual-synthesis decompose guard (MISSION_DGUARD, flag-gated) -----
# MISSION_BENCH (2026-06-15, p07_bm_mission_bench) proved topology C -- the
# `decompose` path (Opus F1-F4 -> cheap Haiku F6 -> tools) -- CONSISTENTLY FAILS
# T1 factual synthesis (knowledge_card q=1.2 BOTH rounds; 8.4x worse than the
# frontier path D/E). Root cause (benchmark line 138 / H4): the cheap Stage-2
# producer cannot SYNTHESIZE factual prose from a prompt_package -- it can fill a
# schema/template (decompose's real value) but not compose grounded factual
# content. The routing playbook (kc_mission_token_routing) documents the
# anti-pattern ("NEVER use C for T1") but NOTHING enforced it: cex_router_v2's
# STRUCTURED_ALLOW force-routes knowledge_card to decompose AND dispatch.sh
# autoroute is DEFAULT-ON (2026-06-14), so `solo n0X "create kc_x"` silently
# becomes a known-failing cheap-F6 run. This guard is the missing safety net at
# the single chokepoint every decompose run (manual OR autoroute child) flows
# through. R-343 (2026-07-13): default flipped to 'warn' -- the 2026-07-13 live
# demo ran this exact proven-bad case (decompose n04, knowledge_card) with ZERO
# warning because the guard was OFF unless explicitly opted in. Explicit
# CEX_DECOMPOSE_GUARD=off (or 0/false/no) restores the pre-R-343 OFF behavior
# byte-for-byte; 'upgrade'/'refuse' remain opt-in only. See _guard_policy.

# The factual-SYNTHESIS subset of cex_router_v2.STRUCTURED_ALLOW. Pure schema /
# template kinds (enum_def, type_def, env_config, naming_rule, response_format,
# input_schema, validation_schema, event_schema) are DELIBERATELY EXCLUDED -- the
# cheap F6 fills those well; guarding them would defeat decompose's purpose. Only
# kinds that synthesize factual PROSE are guarded. knowledge_card is the
# benchmark-PROVEN member (T1); the rest share its "synthesize grounded factual
# content" shape (conservative, P01-knowledge prose kinds).
FACTUAL_SYNTHESIS_KINDS = frozenset({
    "knowledge_card", "faq_entry", "glossary_entry", "mental_model",
    "domain_vocabulary",
})

# Route-away recommendation (benchmark per-task: D native Sonnet frontier 17.75
# and E decompose+thin 19.60 both WIN T1; decompose C = 2.35, fails).
_DGUARD_REC = ("solo (Mode-A) or native Sonnet (solo n0X -m sonnet) -- "
               "MISSION_BENCH T1: D=17.75 / E=19.60 frontier vs decompose C=2.35")


def _guard_policy(args: argparse.Namespace) -> "str | None":
    """Resolve the DGUARD policy. None => OFF (opt-out only, see below).

    R-343 (2026-07-13): the default changed from OFF to 'warn'. MISSION_BENCH
    measured q=1.2/10 for FACTUAL_SYNTHESIS_KINDS on the cheap-F6 decompose
    path, and the pre-fix OFF-by-default let the 2026-07-13 live demo run that
    exact proven-bad case with zero warning. Only an EXPLICIT opt-out
    (CEX_DECOMPOSE_GUARD=off/0/false/no) still resolves to None, restoring the
    pre-R-343 behavior byte-for-byte for anyone who sets it; leaving both the
    CLI flag and the env var unset now means 'warn', not OFF.

    Precedence: CLI --guard-on-factual > env CEX_DECOMPOSE_GUARD > default
    'warn'. Any unrecognised truthy env value (e.g. "1"/"on"/"yes") also
    resolves to the safest active policy ('warn'); 'upgrade'/'refuse' remain
    opt-in only (CLI flag or explicit env word)."""
    cli = (getattr(args, "guard_on_factual", "") or "").strip().lower()
    if cli in ("warn", "upgrade", "refuse"):
        return cli
    env = os.environ.get("CEX_DECOMPOSE_GUARD", "").strip().lower()
    if env in ("0", "false", "no", "off"):
        return None
    if env in ("warn", "upgrade", "refuse"):
        return env
    return "warn"  # unset (new default) OR truthy-but-unrecognised -> advisory


def _infer_guard_kind(nucleus: str, task: str) -> str:
    """Best-effort kind for the guard (lowercased). Empty when undetermined ->
    the guard does NOT fire (degrade-never: never block a run on a guess).

    Precedence (safety-first -- a guard must not MISS a factual run, but must
    honour an operator who is explicit):
      1. Explicit `kind=`/`kind:` token in the task -- authoritative for THIS
         run (returned even if non-factual, so an explicit schema-kind run is
         NOT guarded; a stale handoff cannot override it).
      2. Otherwise fire on ANY factual signal: handoff frontmatter (authoritative
         for the autoroute path, written fresh before dispatch) OR a task
         heuristic (a named factual kind / the `kc_` convention). This covers a
         manual `decompose n0X "create kc_x"` whose handoff is STALE -- the
         observed failure mode (a context_doc handoff masking a kc_ task)."""
    low = (task or "").lower()
    m = re.search(r"kind\s*[=:]\s*([a-z_]+)", low)
    if m:
        return m.group(1)
    try:
        from cex_router_v2 import infer_kind_from_handoff
        handoff = (ROOT / ".cex" / "runtime" / "handoffs"
                   / ("%s_task.md" % nucleus.lower()))
        k = (infer_kind_from_handoff(handoff) or "").strip().lower()
        if k in FACTUAL_SYNTHESIS_KINDS:
            return k
    except Exception:
        pass
    for k in FACTUAL_SYNTHESIS_KINDS:
        if k in low:
            return k
    if re.search(r"\bkc_\w+", low):
        return "knowledge_card"
    return ""


def _apply_factual_guard(policy: str, kind: str, s2_model: str, dry_run: bool,
                         ladder=None) -> "tuple[int, str]":
    """Act on a factual-synthesis `kind` hitting the cheap-F6 decompose path.

    Returns (exit_code, stage_2_model). Policies:
      warn    -- print the finding + route-away recommendation, PROCEED (advisory).
      upgrade -- bump Stage 2 one escalation-ladder tier (Haiku->Sonnet, the SAME
                 ladder A3 uses); PROCEED with the stronger F6. Best for the
                 default-ON autoroute path -- it self-heals in place.
      refuse  -- abort (EXIT_INPUT) with the recommendation (Gating Wrath: hard
                 stop). Under --dry-run it prints 'would refuse' and PROCEEDS so
                 the routing-proof plan still prints.
    The `ladder` seam defaults to the real provider ladder (tests inject one)."""
    finding = ("[decompose] DGUARD: kind '%s' is a factual-synthesis kind; the "
               "cheap-F6 decompose path FAILS factual synthesis "
               "(MISSION_BENCH T1 q=1.2 both rounds)." % kind)
    if policy == "refuse":
        print(finding, file=sys.stderr)
        if dry_run:
            print("[decompose] DGUARD refuse (dry-run): would abort; route to %s"
                  % _DGUARD_REC, file=sys.stderr)
            return EXIT_OK, s2_model
        print("[decompose] DGUARD refuse: route to %s" % _DGUARD_REC,
              file=sys.stderr)
        print("[decompose] override: unset CEX_DECOMPOSE_GUARD, or "
              "--guard-on-factual {warn|upgrade}.", file=sys.stderr)
        return EXIT_INPUT, s2_model
    if policy == "upgrade":
        if ladder is None:
            ladder = _ladder_for(s2_model)
        nxt = _next_tier_model(s2_model, ladder) if ladder else None
        if nxt and _resolve(nxt) != _resolve(s2_model):
            print(finding)
            print("[decompose] DGUARD upgrade: Stage-2 %s -> %s (stronger F6 for "
                  "factual synthesis)" % (s2_model, nxt))
            return EXIT_OK, nxt
        print(finding)
        print("[decompose] DGUARD upgrade: no stronger tier above %s; keeping it "
              "-- recommend %s" % (s2_model, _DGUARD_REC))
        return EXIT_OK, s2_model
    # warn (the default active policy)
    print(finding)
    print("[decompose] DGUARD warn: recommend %s. Proceeding with Stage-2 %s "
          "(advisory)." % (_DGUARD_REC, s2_model))
    return EXIT_OK, s2_model


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="cex_decompose -- 3-stage 8F dispatch (reasoning -> F6 generation -> tools)",
    )
    parser.add_argument("--nucleus", required=True,
                        help="Target nucleus (n01..n07)")
    parser.add_argument("--task", required=True,
                        help="Natural-language intent (passed to Stage 1)")
    parser.add_argument("--stage-1-model", default="",
                        help="Stage 1 model id (overrides YAML/env)")
    parser.add_argument("--stage-2-model", default="",
                        help="Stage 2 model id (overrides YAML/env)")
    parser.add_argument("--dry-run", action="store_true",
                        help="Print intended subprocess calls; do not spawn")
    parser.add_argument("--skip-stage-3", action="store_true",
                        help="Stop after Stage 2 (debug use)")
    parser.add_argument("--track-cost", dest="track_cost",
                        action="store_true", default=True,
                        help="Emit cost_log.jsonl events per stage (default: on)")
    parser.add_argument("--no-track-cost", dest="track_cost",
                        action="store_false",
                        help="Disable cost tracking (CI/sandbox runs)")
    parser.add_argument("--gate-on-fail", choices=["drop", "escalate", "reject"],
                        default="reject",
                        help="Stage-3 wikilink-gate policy on fabrication "
                             "(default: reject -- block fabricated artifact from F8)")
    parser.add_argument("--escalate-on-floor", action="store_true",
                        help="A3: after Stage 2, re-produce at the next escalation-"
                             "ladder tier while the artifact scores below the "
                             "decompose floor (also via CEX_DECOMPOSE_ESCALATE=1; "
                             "OFF by default -> byte-identical to pre-A3)")
    parser.add_argument("--guard-on-factual",
                        choices=["warn", "upgrade", "refuse"], default="",
                        help="DGUARD: when a factual-synthesis kind (knowledge_card "
                             "+ similar P01 prose kinds) is routed onto the cheap-F6 "
                             "decompose path, warn / upgrade Stage-2 a tier / refuse "
                             "(MISSION_BENCH: decompose FAILS T1 factual, q=1.2). "
                             "Also via CEX_DECOMPOSE_GUARD=warn|upgrade|refuse; "
                             "defaults to warn as of R-343 (2026-07-13) -- set "
                             "CEX_DECOMPOSE_GUARD=off to restore pre-R-343 OFF")
    args = parser.parse_args(argv)

    nucleus = args.nucleus.lower()
    if nucleus not in VALID_NUCLEI:
        print("[decompose] FAIL: unknown nucleus %s (need n01..n07)" % nucleus,
              file=sys.stderr)
        return EXIT_INPUT
    if not args.task.strip():
        print("[decompose] FAIL: empty --task", file=sys.stderr)
        return EXIT_INPUT

    s1_model, s2_model, fallback = _resolve_models(args)

    # DGUARD (defaults to 'warn' as of R-343, 2026-07-13; explicit
    # CEX_DECOMPOSE_GUARD=off restores pre-R-343 OFF): when a factual-
    # synthesis kind is routed onto the cheap-F6 decompose path (manually or via
    # default-ON autoroute), act BEFORE spending Stage-1 reasoning. Runs after
    # model resolution so an `upgrade` is reflected in the banner below. See
    # _apply_factual_guard (and the DGUARD block) for the policy semantics.
    guard_policy = _guard_policy(args)
    if guard_policy:
        guard_kind = _infer_guard_kind(nucleus, args.task)
        if guard_kind in FACTUAL_SYNTHESIS_KINDS:
            g_code, s2_model = _apply_factual_guard(
                guard_policy, guard_kind, s2_model, args.dry_run)
            if g_code != EXIT_OK:
                return g_code

    print("=" * 60)
    print("CEX 8F DECOMPOSE  -- nucleus=%s" % nucleus.upper())
    print("  Stage 1 model: %s" % s1_model)
    print("  Stage 2 model: %s (fallback: %s)" %
          (s2_model, ", ".join(fallback) if fallback else "none"))
    print("  Task: %s" % args.task[:100])
    print("  Dry-run: %s" % args.dry_run)
    print("=" * 60)

    t0 = time.perf_counter()

    code, pkg = stage_1(nucleus, args.task, s1_model, args.dry_run,
                        track_cost=args.track_cost)
    if code != EXIT_OK:
        return EXIT_STAGE1
    print("[decompose] Stage 1 OK%s" %
          (": " + str(pkg) if pkg else " (dry-run)"))

    produce_t0 = time.time()
    code = stage_2(nucleus, s2_model, fallback, pkg, args.dry_run,
                   track_cost=args.track_cost)
    if code != EXIT_OK:
        return EXIT_STAGE2
    print("[decompose] Stage 2 OK")

    # A3 quality-floor escalation (flag-gated; OFF -> this branch is skipped and
    # the pipeline is byte-identical to pre-A3). See _escalate_below_floor.
    if _escalation_enabled(args) and not args.dry_run:
        final_model = _escalate_below_floor(
            nucleus, s2_model, fallback, pkg, produce_t0,
            track_cost=args.track_cost)
        if _resolve(final_model) != _resolve(s2_model):
            print("[decompose] A3 escalation settled on model: %s" % final_model)
    elif _escalation_enabled(args) and args.dry_run:
        print("[decompose] (dry-run) A3 escalation ON: would score the Stage-2 "
              "artifact and climb the ladder while below floor %.1f"
              % _decompose_floor())

    if args.skip_stage_3:
        print("[decompose] Stage 3 skipped (--skip-stage-3)")
        return EXIT_OK

    artifact_path = None
    if not args.dry_run:
        artifact_path = _find_recent_artifact(produce_t0)
        if artifact_path is not None:
            print("[decompose] gating freshly-produced artifact: %s"
                  % artifact_path)
        else:
            print("[decompose] WARN: no fresh artifact found to wikilink-gate "
                  "(skipping in-pipeline gate)", file=sys.stderr)

    code = stage_3(nucleus, args.dry_run, artifact_path=artifact_path,
                   on_fail=args.gate_on_fail, since_ts=produce_t0,
                   pkg_path=pkg, task_text=args.task)
    if code != EXIT_OK:
        return EXIT_STAGE3
    print("[decompose] Stage 3 OK")

    elapsed_ms = (time.perf_counter() - t0) * 1000
    print("[decompose] DONE in %.0f ms" % elapsed_ms)
    return EXIT_OK


if __name__ == "__main__":
    sys.exit(main())
