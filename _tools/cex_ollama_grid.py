#!/usr/bin/env python3
"""cex_ollama_grid.py: HEADLESS Ollama grid launcher.

Runs the DECLARED agentic runner (_tools/cex_agentic_nucleus.py) for each
nucleus, headless and concurrent (capped worker pool), with the correct
per-nucleus handoff and output path. This is the headless sibling of the
interactive windowed grid (_spawn/spawn_grid_ollama.ps1) -- it is the path the
automated grid (cex_grid_test.py -> cex_mission_dispatch.py) should use, because
it lands real output where the poller looks instead of leaving REPL windows open.

Why this exists (BUG A): the windowed path launched boot/n0X_ollama.ps1 which
(a) ran the STALE single-shot _tools/ollama_nucleus.py, not the declared agentic
runner, (b) had no param() block so it ignored -Handoff/-Output/-MaxIters, and
(c) used -NoExit so windows never closed. Output never landed in
_reports/{mission}_{tag}/ -> the poller timed out 0/6. This launcher fixes all
three: declared runner, correct handoff/output, no -NoExit, blocks to completion.

Per-nucleus contract (matches the proven invocation):
    python _tools/cex_agentic_nucleus.py --nucleus n02 \
        --handoff .cex/runtime/handoffs/LEVERAGE_MAP_V2_n02.md \
        --output _reports/leverage_map_v2_<tag>/LEVERAGE_MAP_V2_n02.md \
        --model qwen2.5-coder:7b --max-iters 12 --require-reads 2 \
        --min-report-bytes 1100 --quiet

Output dir convention (identical to spawn_grid_ollama.ps1 / cex_grid_test.py):
    _reports/{mission.lower()}            (no tag)
    _reports/{mission.lower()}_{tag}      (with --output-tag)

Usage:
    python _tools/cex_ollama_grid.py --mission LEVERAGE_MAP_V2 \
        --nuclei n02,n03 --concurrency 2 --max-iters 12 --require-reads 2 \
        --output-tag n05verify
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RUNNER = ROOT / "_tools" / "cex_agentic_nucleus.py"

# A2.x tenant-path migration: route the RUNTIME surface through the ONE canonical resolver
# (cex_tenant_paths). CEX_TENANT_ID unset -> tenant_runtime_dir() returns the legacy global
# .cex/runtime (byte-identical single-tenant); a tenant bound -> .cex/tenants/<tid>/runtime.
# Degrade-never: fall back to the legacy join if the resolver is not importable here.
if str(ROOT / "_tools") not in sys.path:
    sys.path.insert(0, str(ROOT / "_tools"))
try:
    from cex_tenant_paths import tenant_runtime_dir as _tenant_runtime_dir
    PID_DIR = _tenant_runtime_dir() / "pids"
except Exception:
    PID_DIR = ROOT / ".cex" / "runtime" / "pids"


def output_dir_for(mission: str, tag: str) -> Path:
    """Resolve the report dir exactly like spawn_grid_ollama.ps1 does."""
    subdir = mission.lower()
    if tag:
        subdir = f"{subdir}_{tag}"
    return ROOT / "_reports" / subdir


def read_trace(output_path: Path) -> dict:
    """Read the runner's .trace.json sidecar for reason/iters/wall/reads."""
    trace_path = output_path.with_suffix(".trace.json")
    info = {"reason": None, "iters": None, "wall": None, "reads": None}
    if not trace_path.exists():
        return info
    try:
        t = json.loads(trace_path.read_text(encoding="utf-8", errors="replace"))
    except (json.JSONDecodeError, OSError):
        return info
    if isinstance(t, dict):
        info["reason"] = t.get("reason")
        info["iters"] = t.get("iters")
        info["wall"] = t.get("wall")
        # reads are per-trace-entry; take the max seen
        reads = 0
        for entry in t.get("trace", []) or []:
            if isinstance(entry, dict):
                reads = max(reads, entry.get("reads_so_far", 0) or 0,
                            entry.get("reads", 0) or 0)
        info["reads"] = reads
    return info


def run_one(nucleus: str, handoff: Path, output: Path, model: str,
            max_iters: int, require_reads: int, min_report_bytes: int,
            timeout_s: int, quiet_child: bool) -> dict:
    """Run a single nucleus headless via the declared runner. Returns a record."""
    import subprocess  # local import keeps module import cheap for --help

    output.parent.mkdir(parents=True, exist_ok=True)
    cmd = [
        sys.executable, str(RUNNER),
        "--nucleus", nucleus,
        "--handoff", str(handoff),
        "--output", str(output),
        "--model", model,
        "--max-iters", str(max_iters),
        "--require-reads", str(require_reads),
        "--min-report-bytes", str(min_report_bytes),
        "--mission", "OLLAMA_GRID",
    ]
    if quiet_child:
        cmd.append("--quiet")
    print(f"  [start] {nucleus} -> {output.name}", flush=True)
    t0 = time.time()
    rc = None
    err = ""
    try:
        proc = subprocess.run(
            cmd, cwd=ROOT, capture_output=True, text=True, timeout=timeout_s,
        )
        rc = proc.returncode
        if rc != 0 and proc.stderr:
            err = proc.stderr.strip().splitlines()[-1][:200] if proc.stderr.strip() else ""
    except subprocess.TimeoutExpired:
        rc = -1
        err = f"timeout after {timeout_s}s"
    elapsed = round(time.time() - t0, 1)

    nbytes = output.stat().st_size if output.exists() else 0
    trace = read_trace(output)
    rec = {
        "nucleus": nucleus,
        "rc": rc,
        "elapsed_s": elapsed,
        "bytes": nbytes,
        "reason": trace["reason"],
        "iters": trace["iters"],
        "reads": trace["reads"],
        "output": str(output.relative_to(ROOT)) if output.is_relative_to(ROOT) else str(output),
        "error": err,
    }
    print(f"  [done]  {nucleus} rc={rc} {elapsed}s {nbytes}B reason={trace['reason']}"
          + (f" ERR={err}" if err else ""), flush=True)
    return rec


def is_usable(rec: dict, min_bytes: int, require_reads: int = 1) -> bool:
    """Usable = evidence-based success, judged ONLY from harness ground truth.

    1. bytes: the report on DISK is >= min_bytes (real st_size, never a claim);
    2. reason: the runner did not end in the max_iters stub (nor no trace at all);
    3. reads (R-009): the harness-counted read_file/grep total from the
       .trace.json sidecar is >= require_reads. The trace is appended by the
       RUNNER per tool call it actually executed -- the model cannot inflate
       it. This closes the fail-open paths where a >=min_bytes report with
       ZERO real reads was marked usable (3rd done() accepted after the
       anti-fab rejection cap, text-only no_tool_call answers, and
       forced_synthesis after an all-list_dir loop): a fabricated self-report
       cannot pass the verdict without read evidence in the trace.

    Fail-closed: a missing/unreadable trace yields reads=None -> counted as 0.
    require_reads=0 is the EXPLICIT escape hatch that restores the legacy
    bytes+reason-only verdict (never the silent default).
    """
    if rec["bytes"] < min_bytes or rec["reason"] in (None, "max_iters"):
        return False
    return (rec.get("reads") or 0) >= require_reads


def clear_pid_file(mission: str) -> None:
    """Clear any stale windowed PID file so cex_grid_test close_wave is a no-op.

    The headless launcher blocks to completion and its child processes exit, so
    there are never live PIDs to reap. Clearing avoids close_wave taskkill'ing a
    recycled PID left over from a prior windowed run.
    """
    PID_DIR.mkdir(parents=True, exist_ok=True)
    pid_file = PID_DIR / f"grid_ollama_{mission}.txt"
    pid_file.write_text(
        f"# Headless grid (no live PIDs) - {mission}\n", encoding="ascii")


def main() -> int:
    p = argparse.ArgumentParser(description="Headless Ollama agentic grid launcher")
    p.add_argument("--mission", required=True, help="mission tag, e.g. LEVERAGE_MAP_V2")
    p.add_argument("--nuclei", default="n01,n02,n03,n04,n05,n06",
                   help="comma-separated nucleus ids")
    p.add_argument("--model", default="qwen2.5-coder:7b",
                   help="agentic local-grid model (default qwen2.5-coder:7b; "
                        "llama3.1:8b available as fallback)")
    p.add_argument("--model-map", default="",
                   help='optional JSON per-nucleus model override, e.g. {"n03":"qwen2.5-coder:7b"}')
    p.add_argument("--max-iters", type=int, default=15)
    p.add_argument("--require-reads", type=int, default=2,
                   help="min read_file/grep calls: passed to the runner "
                        "(anti-fabrication done() gate) AND enforced on the "
                        "trace-counted reads in the usable verdict (R-009 "
                        "evidence gate; 0 restores the legacy bytes+reason "
                        "verdict)")
    p.add_argument("--min-report-bytes", type=int, default=1100,
                   help="anti-shallow done() floor passed to the runner "
                        "(reject thin reports, bounded retries; 0 disables)")
    p.add_argument("--output-tag", default="",
                   help="suffix for _reports/{mission.lower()}_{tag}/")
    p.add_argument("--concurrency", type=int, default=2,
                   help="max concurrent nuclei (worker pool cap, default 2)")
    p.add_argument("--per-nucleus-timeout", type=int, default=900,
                   help="seconds before a single nucleus subprocess is killed")
    p.add_argument("--handoff-dir", default=".cex/runtime/handoffs")
    p.add_argument("--min-bytes", type=int, default=1000,
                   help="usable-report byte floor (default 1000)")
    p.add_argument("--verbose-children", action="store_true",
                   help="let child runners print iter logs (default quiet)")
    args = p.parse_args()

    if not RUNNER.exists():
        print(f"ERROR: runner not found: {RUNNER}", file=sys.stderr)
        return 1

    nuclei = [n.strip() for n in args.nuclei.split(",") if n.strip()]
    if not nuclei:
        print("ERROR: no nuclei specified", file=sys.stderr)
        return 1

    model_map = {}
    if args.model_map:
        try:
            model_map = json.loads(args.model_map)
        except json.JSONDecodeError as e:
            print(f"ERROR: --model-map is not valid JSON: {e}", file=sys.stderr)
            return 1

    handoff_dir = (ROOT / args.handoff_dir) if not Path(args.handoff_dir).is_absolute() \
        else Path(args.handoff_dir)
    out_dir = output_dir_for(args.mission, args.output_tag)
    out_dir.mkdir(parents=True, exist_ok=True)

    # Build the per-nucleus job list, skipping any missing handoff.
    jobs = []
    skipped = []
    for n in nuclei:
        handoff = handoff_dir / f"{args.mission}_{n}.md"
        if not handoff.exists():
            skipped.append(n)
            print(f"  [skip]  {n}: handoff missing ({handoff.relative_to(ROOT) if handoff.is_relative_to(ROOT) else handoff})",
                  flush=True)
            continue
        output = out_dir / f"{args.mission}_{n}.md"
        # Clean stale output/trace so a prior run cannot masquerade as success.
        for stale in (output, output.with_suffix(".trace.json")):
            try:
                stale.unlink()
            except OSError:
                pass
        jobs.append((n, handoff, output, model_map.get(n, args.model)))

    if not jobs:
        print("ERROR: no runnable nuclei (all handoffs missing)", file=sys.stderr)
        return 1

    clear_pid_file(args.mission)

    print("=" * 60, flush=True)
    print(f"  HEADLESS OLLAMA GRID -- {args.mission}", flush=True)
    print(f"  nuclei={[j[0] for j in jobs]} concurrency={args.concurrency}", flush=True)
    print(f"  max_iters={args.max_iters} require_reads={args.require_reads} "
          f"min_report_bytes={args.min_report_bytes}", flush=True)
    print(f"  output={out_dir.relative_to(ROOT)}", flush=True)
    if skipped:
        print(f"  SKIPPED (no handoff): {skipped}", flush=True)
    print("=" * 60, flush=True)

    t0 = time.time()
    results: list[dict] = []
    with ThreadPoolExecutor(max_workers=max(1, args.concurrency)) as pool:
        futs = {
            pool.submit(
                run_one, n, handoff, output, model,
                args.max_iters, args.require_reads, args.min_report_bytes,
                args.per_nucleus_timeout, not args.verbose_children,
            ): n
            for (n, handoff, output, model) in jobs
        }
        for fut in as_completed(futs):
            try:
                results.append(fut.result())
            except Exception as e:  # defensive: a worker should not raise
                n = futs[fut]
                print(f"  [error] {n}: {type(e).__name__}: {e}", flush=True)
                results.append({"nucleus": n, "rc": -2, "elapsed_s": 0,
                                "bytes": 0, "reason": "worker_error",
                                "iters": None, "reads": None, "output": "",
                                "error": str(e)[:200]})

    elapsed = int(time.time() - t0)
    results.sort(key=lambda r: r["nucleus"])
    usable = sum(1 for r in results
                 if is_usable(r, args.min_bytes, args.require_reads))
    landed = sum(1 for r in results if r["bytes"] > 0)

    wave = {
        "mission": args.mission,
        "model": args.model,
        "concurrency": args.concurrency,
        "output_dir": str(out_dir.relative_to(ROOT)),
        "expected": len(jobs),
        "landed": landed,
        "usable": usable,
        "elapsed_s": elapsed,
        "min_bytes": args.min_bytes,
        "require_reads": args.require_reads,
        "skipped": skipped,
        "results": {r["nucleus"]: r for r in results},
    }
    (out_dir / "wave_report.json").write_text(
        json.dumps(wave, indent=2, ensure_ascii=False), encoding="utf-8")

    # Matrix to stdout.
    print("", flush=True)
    print("=" * 60, flush=True)
    print(f"  MATRIX -- {args.mission}  ({usable}/{len(jobs)} usable, {elapsed}s)", flush=True)
    print("  nucleus | rc | elapsed | bytes | reads | reason | usable", flush=True)
    print("  " + "-" * 60, flush=True)
    for r in results:
        print(f"  {r['nucleus']:7} | {str(r['rc']):2} | {str(r['elapsed_s']):7} | "
              f"{str(r['bytes']):5} | {str(r['reads']):5} | {str(r['reason']):16} | "
              f"{'YES' if is_usable(r, args.min_bytes, args.require_reads) else 'no'}",
              flush=True)
    print("=" * 60, flush=True)
    print(f"  wave_report: {(out_dir / 'wave_report.json').relative_to(ROOT)}", flush=True)

    # Exit 0 only when every runnable nucleus produced a usable report.
    return 0 if usable == len(jobs) else 2


if __name__ == "__main__":
    try:
        from cex_agent_io import wrap_main

        def _main_wrapper(argv):
            sys.argv = [sys.argv[0]] + argv
            return main()

        sys.exit(wrap_main(_main_wrapper, sys.argv[1:], label="cex_ollama_grid"))
    except ImportError:
        sys.exit(main())
