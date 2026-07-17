#!/usr/bin/env python3
# -*- coding: ascii -*-
"""CEXAI wave_state engine -- cex_wave_state (spec 06, P3 PHASES & WAVES).

THE testable engine behind the in-session wave-runner. It makes a vertical build run as ONE
governed multi-wave mission instead of N07 hand-driving each wave boundary (dispatch grid ->
monitor -> manual consolidate -> manually compose the next wave, re-deriving the gate from
memory each time). P3 closes that gap with a thin, testable BETWEEN-WAVES GATE that REUSES the
mature pieces; the LIVE multi-wave loop (write handoffs -> dispatch grid -> Monitor -> gate ->
advance) is driven by N07 via the companion skill `.claude/skills/wave_run.md` -- this module
holds NO spawning (mirrors P2's injected-dispatch: the runner never spawns inside the module).

WHY THIS EXISTS (spec 06 P3 -- the mission loop):
  Today the between-waves gate is RE-DERIVED from memory each boundary (error-prone, ad hoc).
  A mature headless wave-runner exists (cex_mission_runner.py) but it is DORMANT and uses the
  BLOCKING signal_watch the rules brand an anti-pattern; nothing runs an in-session multi-wave
  mission with a MECHANICAL between-waves gate. This module IS that mechanical gate -- one
  function (`gate`) that sequences the four checks a wave boundary must pass, fail-closed and
  never-fabricating, and a side ledger that records the verdict so the loop is auditable.

THE GATE (the keystone -- `gate(...) -> GateResult`):
  Sequence at a wave boundary, AGGREGATING (a)-(c) (NO early-exit -- the feedback must name
  EVERY failing check), then (d) merge ONLY if a/b/c are all green:
    (a) consolidate `verify`   -- ONLY if worktree (-w grid); a non-worktree grid honestly SKIPS.
    (b) `doctor` FAIL-count    -- ALWAYS (rc 0 PASS / 1 FAIL).
    (c) `quality_gate` floor   -- ALWAYS, per-nucleus (build the watch_result shape
                                  {"nuclei": {n0X: {"quality": q}}} from MissionState quality).
    (d) `merge-all --cleanup`  -- ONLY if worktree AND a/b/c all green (the doctor 0-FAIL
                                  auto-revert is built into merge-all itself).
  FAIL-CLOSED + NEVER-FABRICATE: a subprocess error / unparseable output -> that check is
  FAILED, never skipped-as-pass. The ONLY honest skips are the worktree-only checks (a, d) on a
  non-worktree grid. On any fail -> `build_feedback` naming EVERY failing check (mirrors
  cex_mission_runner.redispatch_with_feedback's feedback shape) so N07 can append it to the
  failing nuclei's handoffs and re-dispatch ONLY those.

THE SUBPROCESS SEAM (pluggable + testable):
  Every gate CLI (verify / doctor / merge-all) is invoked through an INJECTED ``run`` callable
  -- `gate` NEVER calls subprocess directly. The signature is:
      run(cmd: List[str], *, timeout: int) -> RunResult   (rc + stdout + stderr)
  The DEFAULT is a real subprocess wrapper (SubprocessRun); tests inject a FakeRun to prove the
  sequence / fail-closed / never-fabricate offline. This mirrors P2's injected dispatch exactly.

STATE (two surfaces, one source of truth):
  * MissionState (cex_mission_state, REUSED + UNTOUCHED) -- waves / nuclei / per-nucleus quality.
    It is the wave-state source of truth (crash-recoverable JSON; 12+ callers; zero-regression).
  * a side `.cex/runtime/wave_state.json` GATE LEDGER (the spec-named path) -- records each
    gate verdict (wave, pass/fail, per-check results, feedback) so the loop is auditable.
    Tenant-aware: routed through cex_tenant_paths (degrade-never to the legacy global path).

HARD RULES (task contract + .claude/rules/ascii-code-rule.md):
  * REUSE (lazy imports): cex_mission_runner.parse_waves_from_plan + quality_gate;
    cex_mission_state.MissionState. Gate CLIs via subprocess: cex_worktree_consolidate.py
    verify + merge-all --cleanup; cex_doctor.py. Do NOT edit those files -- import/call them.
  * ASCII-only; fully type-hinted; FAIL-CLOSED; degrade-never (a missing tool -> the check
    FAILS honestly, the engine still returns a GateResult -- it never crashes the loop);
    NEVER-FABRICATE (the gate never reports a pass it did not earn).

Spec: docs/specs/06_orchestration_engine/spec.md (P3 PHASES & WAVES). Sibling of:
_tools/cex_workflow_run.py (P2 -- the same testable-engine + injected-seam + fail-closed
discipline mirrored). Companion skill: .claude/skills/wave_run.md (the N07-facing live loop).
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Dict, List, Mapping, Optional

# --------------------------------------------------------------------------- #
# Make _tools importable so the REUSE modules can be lazily imported (NOT at module import --
# keep this module import-light; the live loop is driven by N07, not by importing this).
# --------------------------------------------------------------------------- #
_TOOLS_DIR = str(Path(__file__).resolve().parent)
if _TOOLS_DIR not in sys.path:
    sys.path.insert(0, _TOOLS_DIR)

_REPO_ROOT = Path(_TOOLS_DIR).resolve().parent

# Check status vocabulary (a check is one of: passed | failed | skipped). A skip is ONLY ever the
# honest worktree-only skip on a non-worktree grid -- never a subprocess error masked as a skip.
CHECK_PASS = "passed"
CHECK_FAIL = "failed"
CHECK_SKIP = "skipped"

# The four gate checks, in sequence order. (a) + (d) are worktree-only.
CHECK_VERIFY = "verify"       # (a) consolidate verify  -- worktree-only
CHECK_DOCTOR = "doctor"       # (b) doctor FAIL-count    -- always
CHECK_QUALITY = "quality"     # (c) quality_gate floor   -- always
CHECK_MERGE = "merge"         # (d) merge-all --cleanup  -- worktree-only, after a/b/c green

# The default per-CLI timeouts (seconds). A doctor pass over the whole repo can be slow; merge-all
# runs doctor per branch. Generous but finite (NO infinite wait -- fail-closed on TimeoutExpired).
_TIMEOUT_VERIFY = 120
_TIMEOUT_DOCTOR = 600
_TIMEOUT_MERGE = 1800


# --------------------------------------------------------------------------- #
# RunResult -- the typed outcome of one injected subprocess call. PURE data (no secret).
# --------------------------------------------------------------------------- #
@dataclass
class RunResult:
    """One subprocess call's REAL outcome. ``rc`` None means the call could not run at all (a
    spawn error / timeout) -- treated as a FAILED check (fail-closed), never a fabricated pass."""

    rc: Optional[int] = None
    stdout: str = ""
    stderr: str = ""
    error: Optional[str] = None   # set when the call could not run (spawn error / timeout)

    @property
    def ran(self) -> bool:
        """True iff the subprocess actually executed and returned an exit code (rc is not None)."""
        return self.rc is not None


# --------------------------------------------------------------------------- #
# CheckResult -- one gate check's outcome (verify | doctor | quality | merge). NEVER fabricated.
# --------------------------------------------------------------------------- #
@dataclass
class CheckResult:
    name: str
    status: str = CHECK_FAIL            # passed | failed | skipped
    detail: str = ""                    # a short human reason (rc, fail-count, sub-floor names)
    rc: Optional[int] = None            # the subprocess rc when this check shelled out
    meta: Dict[str, Any] = field(default_factory=dict)

    @property
    def passed(self) -> bool:
        return self.status == CHECK_PASS

    @property
    def failed(self) -> bool:
        return self.status == CHECK_FAIL

    @property
    def skipped(self) -> bool:
        return self.status == CHECK_SKIP


# --------------------------------------------------------------------------- #
# GateResult -- the verdict of one between-waves gate. AGGREGATES (a)-(c) + (d).
# --------------------------------------------------------------------------- #
@dataclass
class GateResult:
    mission_id: str
    wave: int
    worktree: bool = False
    quality_floor: float = 8.0
    passed: bool = False
    checks: List[CheckResult] = field(default_factory=list)
    feedback: str = ""                  # names EVERY failing check (empty when passed)
    nuclei: List[str] = field(default_factory=list)

    def check(self, name: str) -> Optional[CheckResult]:
        for c in self.checks:
            if c.name == name:
                return c
        return None

    @property
    def failing(self) -> List[CheckResult]:
        return [c for c in self.checks if c.failed]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "mission_id": self.mission_id,
            "wave": self.wave,
            "worktree": self.worktree,
            "quality_floor": self.quality_floor,
            "passed": self.passed,
            "nuclei": list(self.nuclei),
            "checks": [
                {"name": c.name, "status": c.status, "detail": c.detail, "rc": c.rc}
                for c in self.checks
            ],
            "feedback": self.feedback,
        }


# --------------------------------------------------------------------------- #
# The default real subprocess wrapper (injected as ``run``; tests inject a FakeRun instead).
# --------------------------------------------------------------------------- #
class SubprocessRun:
    """The DEFAULT injected ``run`` backend. Shells a command, returns a RunResult. degrade-never
    + fail-closed: a spawn error / timeout -> RunResult(rc=None, error=...) (the gate treats a
    non-ran result as a FAILED check -- never a fabricated pass)."""

    def __init__(self, *, repo_root: Optional[Path] = None) -> None:
        self.repo_root = repo_root or _REPO_ROOT
        self.calls: List[Dict[str, Any]] = []   # provenance: every command attempted

    def __call__(self, cmd: List[str], *, timeout: int = 600) -> RunResult:
        self.calls.append({"cmd": list(cmd), "timeout": timeout})
        try:
            proc = subprocess.run(
                cmd, cwd=str(self.repo_root), capture_output=True, text=True, timeout=timeout,
            )
        except subprocess.TimeoutExpired as exc:
            return RunResult(rc=None, error="timeout after %ss: %s" % (timeout, exc))
        except Exception as exc:
            return RunResult(rc=None, error="spawn_error: %s: %s" % (type(exc).__name__, exc))
        return RunResult(rc=proc.returncode, stdout=proc.stdout or "", stderr=proc.stderr or "")


# A run-wrapper is any callable(cmd, *, timeout) -> RunResult.
RunFn = Callable[..., RunResult]


# --------------------------------------------------------------------------- #
# THE GATE -- the keystone.
# --------------------------------------------------------------------------- #
def gate(
    mission_id: str,
    wave_num: int,
    *,
    worktree: bool = False,
    quality_floor: float = 8.0,
    nuclei: Optional[List[str]] = None,
    run: Optional[RunFn] = None,
    state_dir: Optional[Path] = None,
    ledger_path: Optional[Path] = None,
    record: bool = True,
    python_exe: Optional[str] = None,
) -> GateResult:
    """The between-waves gate (spec 06 P3). Sequence, fail-closed, AGGREGATE (a)-(c) then (d):

      (a) consolidate `verify`  -- ONLY if worktree;  a non-worktree grid honestly SKIPS.
      (b) `doctor` FAIL-count   -- ALWAYS (rc 0 PASS / 1 FAIL).
      (c) `quality_gate` floor  -- ALWAYS, per-nucleus, from MissionState quality.
      (d) `merge-all --cleanup` -- ONLY if worktree AND a/b/c all green.

    AGGREGATE (a)-(c): all three run (NO early-exit) so the feedback names EVERY failing check.
    (d) runs ONLY when a/b/c are all green (merging a red tree is forbidden -- never advance past
    a red gate). NEVER-FABRICATE + FAIL-CLOSED: a subprocess that could not run (spawn error /
    timeout) OR an unparseable output -> that check is FAILED, never skipped-as-pass. The ONLY
    honest skips are the worktree-only checks (a, d) on a non-worktree grid.

    Args:
      mission_id: the MissionState id (the wave-state source of truth).
      wave_num: the wave whose boundary is being gated.
      worktree: True iff the grid was dispatched with -w (per-cell worktrees). Gates (a) + (d).
      quality_floor: the per-nucleus quality floor (default 8.0). quality:null passes (peer
        review later) -- mirrors cex_mission_runner.quality_gate.
      nuclei: the wave's nuclei (n0X). Defaults to the wave's nuclei recorded in MissionState.
      run: the INJECTED subprocess wrapper (defaults to SubprocessRun -- a real wrapper). Tests
        inject a FakeRun. ``gate`` NEVER calls subprocess directly.
      state_dir / ledger_path: override the MissionState dir / the gate-ledger path (tests).
      record: write the verdict to the side ledger (default True; tests may disable).
      python_exe: the interpreter for the python-tool CLIs (defaults to sys.executable).

    Returns a GateResult (passed iff every NON-skipped check passed). NEVER raises on a check
    failure -- a failure is data on the GateResult, not an exception (the loop stays in control).
    """
    runner: RunFn = run if run is not None else SubprocessRun()
    py = python_exe or sys.executable

    # Resolve the wave's nuclei from MissionState when not explicitly supplied (never fabricated:
    # an absent MissionState / wave -> []; quality(c) then has nothing to gate, which is itself a
    # fail-closed FAIL rather than a vacuous pass -- see _check_quality).
    ms = _load_mission_state(mission_id, state_dir)
    wave_quality = _wave_quality_map(ms, wave_num)
    if nuclei is None:
        nuclei = sorted(wave_quality.keys())

    result = GateResult(
        mission_id=mission_id, wave=wave_num, worktree=bool(worktree),
        quality_floor=float(quality_floor), nuclei=list(nuclei),
    )

    # (a) verify -- worktree-only. A non-worktree grid honestly SKIPS (the ONLY honest skip).
    if worktree:
        result.checks.append(_check_verify(runner, py))
    else:
        result.checks.append(CheckResult(
            name=CHECK_VERIFY, status=CHECK_SKIP,
            detail="non-worktree grid: verify is worktree-only (honest skip, not a pass)",
        ))

    # (b) doctor -- ALWAYS.
    result.checks.append(_check_doctor(runner, py))

    # (c) quality_gate per-nucleus floor -- ALWAYS.
    result.checks.append(_check_quality(nuclei, wave_quality, float(quality_floor)))

    # AGGREGATE (a)-(c): pass iff every NON-skipped check among a/b/c passed.
    abc = [c for c in result.checks if c.name in (CHECK_VERIFY, CHECK_DOCTOR, CHECK_QUALITY)]
    abc_green = all(c.passed for c in abc if not c.skipped)

    # (d) merge-all --cleanup -- worktree-only AND only when a/b/c are all green. Otherwise an
    # honest skip on a non-worktree grid, or a FAIL-GATED skip when a/b/c are red (we NEVER merge
    # a red tree -- recorded as skipped with the gating reason, and the gate stays failed via abc).
    if worktree:
        if abc_green:
            result.checks.append(_check_merge(runner, py))
        else:
            result.checks.append(CheckResult(
                name=CHECK_MERGE, status=CHECK_SKIP,
                detail="merge withheld: aggregate (a)-(c) not all green -- never merge a red tree",
            ))
    else:
        result.checks.append(CheckResult(
            name=CHECK_MERGE, status=CHECK_SKIP,
            detail="non-worktree grid: merge-all is worktree-only (honest skip, not a pass)",
        ))

    # The gate PASSES iff every NON-skipped check passed. (A worktree gate also requires the merge
    # check to have passed; a non-worktree gate has merge skipped -> a/b/c decide.)
    result.passed = all(c.passed for c in result.checks if not c.skipped)
    if not result.passed:
        result.feedback = build_feedback(result)

    if record:
        _record_ledger(result, ledger_path)
    return result


# --------------------------------------------------------------------------- #
# The four checks (each returns a CheckResult; each is fail-closed + never-fabricate).
# --------------------------------------------------------------------------- #
def _check_verify(run: RunFn, py: str) -> CheckResult:
    """(a) consolidate `verify` (exit 0 OK / 2 issues). A non-zero/non-(0,2) rc, or a call that
    could not run, is a FAIL (fail-closed) -- never skipped-as-pass."""
    cmd = [py, str(_REPO_ROOT / "_tools" / "cex_worktree_consolidate.py"), "verify"]
    res = run(cmd, timeout=_TIMEOUT_VERIFY)
    if not res.ran:
        return CheckResult(name=CHECK_VERIFY, status=CHECK_FAIL,
                           detail="verify could not run: %s" % (res.error or "unknown"))
    if res.rc == 0:
        return CheckResult(name=CHECK_VERIFY, status=CHECK_PASS, rc=0,
                           detail="worktrees verified clean")
    if res.rc == 2:
        return CheckResult(name=CHECK_VERIFY, status=CHECK_FAIL, rc=2,
                           detail="verify found issues: %s" % _tail(res.stdout or res.stderr))
    # Any OTHER rc is an unexpected verify outcome -> FAIL (never coerce-to-pass).
    return CheckResult(name=CHECK_VERIFY, status=CHECK_FAIL, rc=res.rc,
                       detail="verify unexpected rc=%s: %s" % (res.rc, _tail(res.stderr or res.stdout)))


def _check_doctor(run: RunFn, py: str) -> CheckResult:
    """(b) `doctor` (exit 0 PASS / 1 FAIL). A non-(0,1) rc, or a call that could not run, is a
    FAIL (fail-closed). NEVER reports a pass it did not earn."""
    cmd = [py, str(_REPO_ROOT / "_tools" / "cex_doctor.py")]
    res = run(cmd, timeout=_TIMEOUT_DOCTOR)
    if not res.ran:
        return CheckResult(name=CHECK_DOCTOR, status=CHECK_FAIL,
                           detail="doctor could not run: %s" % (res.error or "unknown"))
    fail_count = _parse_doctor_fail_count(res.stdout)
    if res.rc == 0:
        return CheckResult(name=CHECK_DOCTOR, status=CHECK_PASS, rc=0,
                           detail="doctor 0 FAIL", meta={"fail_count": fail_count or 0})
    if res.rc == 1:
        fc = fail_count if fail_count is not None else "?"
        return CheckResult(name=CHECK_DOCTOR, status=CHECK_FAIL, rc=1,
                           detail="doctor FAIL count=%s" % fc, meta={"fail_count": fail_count})
    return CheckResult(name=CHECK_DOCTOR, status=CHECK_FAIL, rc=res.rc,
                       detail="doctor unexpected rc=%s: %s" % (res.rc, _tail(res.stderr or res.stdout)))


def _check_quality(nuclei: List[str], wave_quality: Mapping[str, Any], floor: float) -> CheckResult:
    """(c) per-nucleus quality floor via the REUSED cex_mission_runner.quality_gate. Builds the
    watch_result shape {"nuclei": {n0X: {"quality": q}}} from MissionState quality. A nucleus
    scoring below floor FAILS the check (naming the sub-floor nuclei). quality:null / quality 0
    PASSES (peer review later) -- mirrors quality_gate's own rule. FAIL-CLOSED on a missing
    quality_gate import OR an empty nuclei set (nothing to gate is NOT a vacuous pass)."""
    if not nuclei:
        return CheckResult(name=CHECK_QUALITY, status=CHECK_FAIL,
                           detail="no nuclei to gate (no wave nuclei resolved from MissionState)")
    qg = _import_quality_gate()
    if qg is None:
        return CheckResult(name=CHECK_QUALITY, status=CHECK_FAIL,
                           detail="quality_gate unavailable (cex_mission_runner import failed)")
    nuclei_arg = [{"nucleus": n, "expected_output": ""} for n in nuclei]
    watch_result = {"nuclei": {n: {"quality": wave_quality.get(n, 0)} for n in nuclei}}
    try:
        verdict = qg(nuclei_arg, watch_result, floor)
    except Exception as exc:
        return CheckResult(name=CHECK_QUALITY, status=CHECK_FAIL,
                           detail="quality_gate raised: %s: %s" % (type(exc).__name__, exc))
    failed = sorted(n for n, v in verdict.items() if not v.get("passed", False))
    if failed:
        scores = ", ".join("%s=%s" % (n, verdict[n].get("quality")) for n in failed)
        return CheckResult(name=CHECK_QUALITY, status=CHECK_FAIL,
                           detail="below floor %.1f: %s" % (floor, scores),
                           meta={"failed": failed, "verdict": verdict})
    return CheckResult(name=CHECK_QUALITY, status=CHECK_PASS,
                       detail="all %d nucleus(es) >= floor %.1f (quality:null passes)" % (len(nuclei), floor),
                       meta={"verdict": verdict})


def _check_merge(run: RunFn, py: str) -> CheckResult:
    """(d) `merge-all --cleanup` (exit 0 done / 2 conflict-or-abort; the doctor 0-FAIL auto-revert
    is built into merge-all). A non-zero rc (conflict / abort) is a FAIL; a call that could not
    run is a FAIL (fail-closed). NEVER fabricates a merged-pass."""
    cmd = [py, str(_REPO_ROOT / "_tools" / "cex_worktree_consolidate.py"), "merge-all", "--cleanup"]
    res = run(cmd, timeout=_TIMEOUT_MERGE)
    if not res.ran:
        return CheckResult(name=CHECK_MERGE, status=CHECK_FAIL,
                           detail="merge-all could not run: %s" % (res.error or "unknown"))
    if res.rc == 0:
        return CheckResult(name=CHECK_MERGE, status=CHECK_PASS, rc=0,
                           detail="merge-all done (doctor 0 FAIL gate held)")
    return CheckResult(name=CHECK_MERGE, status=CHECK_FAIL, rc=res.rc,
                       detail="merge-all failed rc=%s: %s" % (res.rc, _tail(res.stderr or res.stdout)))


# --------------------------------------------------------------------------- #
# Feedback (mirrors cex_mission_runner.redispatch_with_feedback's shape) -- names EVERY fail.
# --------------------------------------------------------------------------- #
def build_feedback(result: GateResult) -> str:
    """Build the retry feedback that names EVERY failing check (NO early-exit aggregation means
    the feedback is complete). N07 appends this to the failing nuclei's handoffs and re-dispatches
    ONLY those (see the wave_run skill). Mirrors redispatch_with_feedback's plain-text shape."""
    failing = result.failing
    if not failing:
        return ""
    lines = [
        "## GATE FEEDBACK (wave %d)" % result.wave,
        "The between-waves gate FAILED. Fix EVERY item below, then this wave re-gates "
        "(it does NOT advance past a red gate). Target quality floor: %.1f." % result.quality_floor,
        "",
    ]
    for c in failing:
        lines.append("- [%s] %s" % (c.name.upper(), c.detail))
    # If quality named sub-floor nuclei, surface them explicitly (the re-dispatch target set).
    q = result.check(CHECK_QUALITY)
    if q is not None and q.failed and q.meta.get("failed"):
        lines.append("")
        lines.append("Sub-floor nuclei to re-dispatch: %s" % ", ".join(q.meta["failed"]))
    return "\n".join(lines)


# --------------------------------------------------------------------------- #
# State: MissionState (REUSED) + the side gate ledger (.cex/runtime/wave_state.json).
# --------------------------------------------------------------------------- #
def _load_mission_state(mission_id: str, state_dir: Optional[Path]) -> Any:
    """Load MissionState (REUSED, UNTOUCHED). degrade-never: an import failure -> None (the gate
    still runs; quality(c) then fails-closed on an empty wave-quality map rather than crashing)."""
    try:
        from cex_mission_state import MissionState  # type: ignore[import]
    except Exception:
        return None
    try:
        if state_dir is not None:
            return MissionState(mission_id, state_dir=Path(state_dir))
        return MissionState(mission_id)
    except Exception:
        return None


def _wave_quality_map(ms: Any, wave_num: int) -> Dict[str, Any]:
    """Extract {nucleus: quality} for a wave from MissionState. An absent MissionState / wave ->
    {} (never fabricated). quality may be None (quality:null) -- passed through verbatim (the
    quality_gate treats null/0 as a pass: peer review later)."""
    if ms is None:
        return {}
    try:
        wave = ms.get_wave(wave_num)
    except Exception:
        return {}
    out: Dict[str, Any] = {}
    for nuc, task in (wave.get("nuclei", {}) or {}).items():
        out[str(nuc)] = task.get("quality") if isinstance(task, Mapping) else None
    return out


def _ledger_path(override: Optional[Path]) -> Path:
    """The side gate-ledger path (.cex/runtime/wave_state.json -- the spec-named path). Tenant-
    aware via cex_tenant_paths (degrade-never to the legacy global path)."""
    if override is not None:
        return Path(override)
    try:
        from cex_tenant_paths import tenant_runtime_dir  # type: ignore[import]
        return tenant_runtime_dir() / "wave_state.json"
    except Exception:
        return _REPO_ROOT / ".cex" / "runtime" / "wave_state.json"


def _record_ledger(result: GateResult, override: Optional[Path]) -> None:
    """Append a gate verdict to the side ledger (atomic write-to-temp + rename). degrade-never:
    any IO error is swallowed (the ledger is an audit aid, never the gate's authority -- the
    GateResult the caller holds is the verdict)."""
    path = _ledger_path(override)
    entry = dict(result.to_dict())
    entry["recorded_at"] = datetime.now(timezone.utc).isoformat()
    try:
        ledger: Dict[str, Any] = {}
        if path.exists():
            try:
                ledger = json.loads(path.read_text(encoding="utf-8"))
            except (json.JSONDecodeError, OSError):
                ledger = {}
        if not isinstance(ledger, dict):
            ledger = {}
        missions = ledger.setdefault("missions", {})
        if not isinstance(missions, dict):
            missions = {}
            ledger["missions"] = missions
        gates = missions.setdefault(result.mission_id, [])
        if not isinstance(gates, list):
            gates = []
            missions[result.mission_id] = gates
        gates.append(entry)
        ledger["updated_at"] = entry["recorded_at"]
        path.parent.mkdir(parents=True, exist_ok=True)
        tmp = path.with_suffix(".tmp")
        tmp.write_text(json.dumps(ledger, indent=2, default=str), encoding="utf-8")
        if sys.platform == "win32" and path.exists():
            path.unlink()
        tmp.rename(path)
    except Exception:
        pass  # an audit-ledger IO error never breaks the gate (degrade-never).


def read_ledger(mission_id: Optional[str] = None, *, ledger_path: Optional[Path] = None) -> Any:
    """Read the gate ledger (all missions, or one mission's gate list). Missing -> {} / []."""
    path = _ledger_path(ledger_path)
    if not path.exists():
        return [] if mission_id else {}
    try:
        ledger = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return [] if mission_id else {}
    if mission_id:
        return ledger.get("missions", {}).get(mission_id, [])
    return ledger


# --------------------------------------------------------------------------- #
# Plan -> wave table (the Step-0 entry; REUSES parse_waves_from_plan).
# --------------------------------------------------------------------------- #
def plan_waves(plan_path: str) -> List[Dict[str, Any]]:
    """Resolve the wave table from a mission plan .md (REUSES cex_mission_runner.parse_waves_from_
    plan). Empty waves are DROPPED by the parser (never fabricated). Returns the list of
    {wave, nuclei:[{nucleus, expected_output}], description}. FAIL-CLOSED: a missing parser raises
    (we never fabricate a wave table)."""
    from cex_mission_runner import parse_waves_from_plan  # type: ignore[import]
    return parse_waves_from_plan(plan_path)


def _wave_table_rows(waves: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Compact, de-duplicated wave rows for the printed table (a wave's nuclei may repeat in the
    raw parse -- the unique set is what gets dispatched)."""
    rows: List[Dict[str, Any]] = []
    for w in waves:
        seen: List[str] = []
        for n in w.get("nuclei", []):
            nuc = n.get("nucleus", "")
            if nuc and nuc not in seen:
                seen.append(nuc)
        rows.append({
            "wave": w.get("wave"),
            "nuclei": seen,
            "count": len(seen),
            "description": (w.get("description", "") or "").strip(),
        })
    return rows


# --------------------------------------------------------------------------- #
# Helpers (PURE).
# --------------------------------------------------------------------------- #
def _import_quality_gate() -> Optional[Callable[..., Dict[str, Any]]]:
    """Lazily import the REUSED quality_gate (degrade-never -> None)."""
    try:
        from cex_mission_runner import quality_gate  # type: ignore[import]
        return quality_gate
    except Exception:
        return None


def _parse_doctor_fail_count(stdout: str) -> Optional[int]:
    """Best-effort parse of the doctor FAIL count from its Result line (e.g. '... | 3 FAIL').
    Display aid only -- the rc (0 PASS / 1 FAIL) is the authority. None when unparseable (NEVER
    coerced to 0: a None alongside rc=1 is reported as 'count=?', honestly)."""
    import re
    if not stdout:
        return None
    m = re.findall(r"(\d+)\s+FAIL\b", stdout)
    if not m:
        return None
    try:
        return max(int(x) for x in m)
    except ValueError:
        return None


def _tail(text: str, n: int = 240) -> str:
    s = " ".join((text or "").split())
    return s if len(s) <= n else s[: n - 3] + "..."


# --------------------------------------------------------------------------- #
# CLI (mirror cex_workflow_run): plan / gate / status.
# --------------------------------------------------------------------------- #
def _cmd_plan(args: argparse.Namespace) -> int:
    """`plan --plan <p> [--json]` -- print the wave table (the Step-0 entry)."""
    try:
        waves = plan_waves(args.plan)
    except FileNotFoundError as exc:
        print("[FAIL] %s" % exc)
        return 1
    except Exception as exc:
        print("[FAIL] could not parse plan: %s: %s" % (type(exc).__name__, exc))
        return 1
    rows = _wave_table_rows(waves)
    if args.json:
        print(json.dumps({"plan": args.plan, "waves": rows}, indent=2, ensure_ascii=True))
        return 0
    print("plan:  %s" % args.plan)
    print("waves: %d (empty waves dropped by the parser -- never fabricated)" % len(rows))
    print("")
    print("  wave | count | nuclei")
    print("  -----+-------+--------------------------------------------------")
    for r in rows:
        print("  %-4s | %-5d | %s" % (str(r["wave"]), r["count"], ", ".join(r["nuclei"]) or "(none)"))
    print("")
    print("  Between each wave: the mandatory gate (consolidate verify [-w] + doctor + quality")
    print("  floor) must be GREEN before the next wave dispatches. Run:")
    print("    python _tools/cex_wave_state.py gate --mission <id> --wave <n> [--worktree]")
    return 0


def _gate_commands(worktree: bool, py: str) -> List[str]:
    """The EXACT subprocess commands `gate` WOULD run, in order (the --dry-run preview). PURE."""
    cw = str(_REPO_ROOT / "_tools" / "cex_worktree_consolidate.py")
    doc = str(_REPO_ROOT / "_tools" / "cex_doctor.py")
    cmds: List[str] = []
    if worktree:
        cmds.append("%s %s verify" % (py, cw))
    cmds.append("%s %s" % (py, doc))
    cmds.append("(in-process) quality_gate per-nucleus floor from MissionState quality")
    if worktree:
        cmds.append("%s %s merge-all --cleanup   [ONLY if verify+doctor+quality all green]" % (py, cw))
    return cmds


def _cmd_gate(args: argparse.Namespace) -> int:
    """`gate --mission <id> --wave <n> [--worktree] [--quality-floor] [--dry-run] [--json]`.
    rc 0 pass / 2 fail. --dry-run prints the EXACT subprocess commands WITHOUT running them."""
    py = sys.executable
    if args.dry_run:
        cmds = _gate_commands(args.worktree, py)
        if args.json:
            print(json.dumps({
                "mission_id": args.mission, "wave": args.wave, "worktree": bool(args.worktree),
                "quality_floor": args.quality_floor, "dry_run": True, "commands": cmds,
            }, indent=2, ensure_ascii=True))
            return 0
        print("gate (DRY-RUN -- no subprocess executed):")
        print("  mission:       %s" % args.mission)
        print("  wave:          %s" % args.wave)
        print("  worktree:      %s" % bool(args.worktree))
        print("  quality_floor: %s" % args.quality_floor)
        print("")
        print("  EXACT commands a real gate WOULD run (AGGREGATE a-c, then d only if a-c green):")
        for c in cmds:
            print("    %s" % c)
        return 0

    result = gate(
        args.mission, args.wave,
        worktree=args.worktree, quality_floor=args.quality_floor,
    )
    if args.json:
        print(json.dumps(result.to_dict(), indent=2, ensure_ascii=True))
        return 0 if result.passed else 2
    print("gate verdict: %s" % ("PASS" if result.passed else "FAIL"))
    print("  mission:       %s" % result.mission_id)
    print("  wave:          %s" % result.wave)
    print("  worktree:      %s" % result.worktree)
    print("  quality_floor: %s" % result.quality_floor)
    print("  nuclei:        %s" % (", ".join(result.nuclei) or "(none)"))
    print("")
    print("  check    | status   | detail")
    print("  ---------+----------+------------------------------------------------------")
    for c in result.checks:
        print("  %-8s | %-8s | %s" % (c.name, c.status, _tail(c.detail, 120)))
    if not result.passed:
        print("")
        print(result.feedback)
    return 0 if result.passed else 2


def _cmd_status(args: argparse.Namespace) -> int:
    """`status --mission <id>` -- MissionState.summary + the gate-ledger verdicts for the mission."""
    ms = _load_mission_state(args.mission, None)
    summary: Dict[str, Any] = {}
    if ms is not None:
        try:
            summary = ms.summary()
        except Exception:
            summary = {}
    gates = read_ledger(args.mission)
    if args.json:
        print(json.dumps({"mission": args.mission, "summary": summary, "gates": gates},
                         indent=2, ensure_ascii=True))
        return 0
    print("mission: %s" % args.mission)
    if summary:
        print("  status:   %s" % summary.get("status"))
        print("  waves:    %s (current: %s)" % (summary.get("waves"), summary.get("current_wave")))
        q = summary.get("quality", {})
        if q:
            print("  quality:  mean=%s min=%s max=%s below_8=%s"
                  % (q.get("mean", "?"), q.get("min", "?"), q.get("max", "?"), q.get("below_8", 0)))
    else:
        print("  (no MissionState found for this mission id)")
    print("  gates recorded: %d" % (len(gates) if isinstance(gates, list) else 0))
    for g in (gates if isinstance(gates, list) else []):
        print("    wave %s: %s (%s)" % (
            g.get("wave"), "PASS" if g.get("passed") else "FAIL", g.get("recorded_at", "")[:19]))
    return 0


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        prog="cex_wave_state",
        description="The in-session wave-runner engine (spec 06 P3). Sub-commands: plan (the "
                    "wave table), gate (the mandatory between-waves gate -- rc 0 pass / 2 fail), "
                    "status (MissionState summary + the gate ledger).",
    )
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_plan = sub.add_parser("plan", help="Print the wave table parsed from a mission plan .md.")
    p_plan.add_argument("--plan", required=True, help="Path to the mission plan .md.")
    p_plan.add_argument("--json", action="store_true", help="Emit the wave table as JSON.")
    p_plan.set_defaults(func=_cmd_plan)

    p_gate = sub.add_parser("gate", help="Run the between-waves gate (rc 0 pass / 2 fail).")
    p_gate.add_argument("--mission", required=True, help="The MissionState id.")
    p_gate.add_argument("--wave", required=True, type=int, help="The wave number to gate.")
    p_gate.add_argument("--worktree", action="store_true",
                        help="The grid was dispatched with -w (gates verify + merge-all).")
    p_gate.add_argument("--quality-floor", type=float, default=8.0,
                        help="Per-nucleus quality floor (default 8.0; quality:null passes).")
    p_gate.add_argument("--dry-run", action="store_true",
                        help="Print the EXACT subprocess commands the gate WOULD run (no run).")
    p_gate.add_argument("--json", action="store_true", help="Emit the GateResult as JSON.")
    p_gate.set_defaults(func=_cmd_gate)

    p_status = sub.add_parser("status", help="Show MissionState summary + the gate ledger.")
    p_status.add_argument("--mission", required=True, help="The MissionState id.")
    p_status.add_argument("--json", action="store_true", help="Emit status as JSON.")
    p_status.set_defaults(func=_cmd_status)

    args = parser.parse_args(argv)
    return int(args.func(args))


__all__ = [
    "gate",
    "GateResult",
    "CheckResult",
    "RunResult",
    "SubprocessRun",
    "build_feedback",
    "plan_waves",
    "read_ledger",
    "CHECK_PASS",
    "CHECK_FAIL",
    "CHECK_SKIP",
    "CHECK_VERIFY",
    "CHECK_DOCTOR",
    "CHECK_QUALITY",
    "CHECK_MERGE",
]


if __name__ == "__main__":
    sys.exit(main())
