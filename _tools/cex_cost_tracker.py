#!/usr/bin/env python3
# -*- coding: ascii -*-
"""CEX Cost Tracker -- aggregate token + USD costs across providers.

Reads .cex/runtime/cost_log.jsonl (emitted by cex_router_v2 on every call).
Each line is a JSON object with at least:
  {ts, session, mission, nucleus, provider, model,
   input_tokens, output_tokens, usd, preflight_used}

The README promises ~70% cost reduction via preflight; this tool measures it.
If the log file is missing, the tool no-ops gracefully (returns empty rollup).

Usage:
  python _tools/cex_cost_tracker.py --session abc123
  python _tools/cex_cost_tracker.py --mission AUTOWIRE
  python _tools/cex_cost_tracker.py --since 2026-04-27 --json
  python _tools/cex_cost_tracker.py --aggregate-30d
  python _tools/cex_cost_tracker.py --record --provider claude --model opus \\
                                    --input 100 --output 50 --usd 0.012
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Iterable

ROOT = Path(__file__).resolve().parent.parent
# A2.x tenant-path migration: route the RUNTIME surface through the ONE canonical resolver
# (cex_tenant_paths). CEX_TENANT_ID unset -> tenant_runtime_dir() returns the legacy global
# .cex/runtime (byte-identical single-tenant); a tenant bound -> .cex/tenants/<tid>/runtime.
# Degrade-never: fall back to the legacy join if the resolver is not importable here.
if str(ROOT / "_tools") not in sys.path:
    sys.path.insert(0, str(ROOT / "_tools"))
try:
    from cex_tenant_paths import tenant_runtime_dir as _tenant_runtime_dir
    COST_LOG = _tenant_runtime_dir() / "cost_log.jsonl"
except Exception:
    COST_LOG = ROOT / ".cex" / "runtime" / "cost_log.jsonl"


# Conservative public USD-per-1M-token estimates as fallback when the
# emitter does not record `usd` directly. Update if pricing changes.
DEFAULT_PRICING = {
    # --- Anthropic (claude) ---  premium > mid > cheap = opus > sonnet > haiku
    "claude-opus-4-8": {"input": 15.0, "output": 75.0},
    "claude-opus-4-7": {"input": 15.0, "output": 75.0},
    "claude-opus-4-6": {"input": 15.0, "output": 75.0},
    "claude-sonnet-4-6": {"input": 3.0, "output": 15.0},
    "claude-haiku-4-5-20251001": {"input": 0.25, "output": 1.25},
    # --- OpenAI (codex) ---  premium > cheap = gpt > gpt_mini
    "gpt-5.2": {"input": 5.0, "output": 20.0},
    "gpt-5": {"input": 5.0, "output": 20.0},
    "gpt-5-mini": {"input": 0.25, "output": 2.0},
    # --- Google (gemini) ---  premium > mid > cheap = pro > flash > flash-lite
    "gemini-2.5-pro": {"input": 1.25, "output": 10.0},
    "gemini-2.5-flash": {"input": 0.30, "output": 1.20},
    "gemini-2.5-flash-lite": {"input": 0.075, "output": 0.30},
    # --- Local (ollama) cost zero ---
    "ollama/qwen3:8b": {"input": 0.0, "output": 0.0},
    "ollama/qwen3:14b": {"input": 0.0, "output": 0.0},
    "ollama/gemma4:26b": {"input": 0.0, "output": 0.0},
    "ollama/cex-student": {"input": 0.0, "output": 0.0},
}

BASELINE_PER_BUILD_USD = 0.30  # Pre-preflight reference cost per build (audit)


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _read_log() -> list[dict]:
    if not COST_LOG.exists():
        return []
    rows: list[dict] = []
    try:
        for line in COST_LOG.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    except Exception:
        return []
    return rows


def estimate_usd(model: str, input_tokens: int, output_tokens: int) -> float:
    """Fallback USD estimate from public pricing."""
    pricing = DEFAULT_PRICING.get(model)
    if not pricing:
        return 0.0
    return (input_tokens / 1_000_000.0) * pricing["input"] \
         + (output_tokens / 1_000_000.0) * pricing["output"]


def record(provider: str, model: str, input_tokens: int, output_tokens: int,
           usd: float | None = None, session: str | None = None,
           mission: str = "", nucleus: str = "", preflight_used: bool = False,
           subagent_id: str = "") -> dict:
    """Append an event to cost_log.jsonl. Used by cex_router_v2 + manual probes.

    subagent_id (W5, optional): tags the sub-producer / escalation tier that
    incurred the cost, e.g. "producer_0#sonnet". The cex_mentor_swarm escalation
    path uses it to attribute per-tier cost (haiku/sonnet/opus) to one producer.

    Backward-compat: when subagent_id is omitted (""), the emitted entry is
    BYTE-IDENTICAL to the pre-W5 schema -- the key is only added when non-empty,
    so existing callers and every rollup reader (_rollup uses .get) are untouched.
    """
    if usd is None:
        usd = estimate_usd(model, input_tokens, output_tokens)
    entry = {
        "ts": _now_iso(),
        "session": session or os.environ.get("CEX_SESSION_ID") or "unknown",
        "mission": mission,
        "nucleus": nucleus or os.environ.get("CEX_NUCLEUS", "unknown"),
        "provider": provider,
        "model": model,
        "input_tokens": int(input_tokens),
        "output_tokens": int(output_tokens),
        "usd": round(usd, 6),
        "preflight_used": bool(preflight_used),
    }
    if subagent_id:
        entry["subagent_id"] = subagent_id
    COST_LOG.parent.mkdir(parents=True, exist_ok=True)
    with COST_LOG.open("a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")
    return entry


def _filter(rows: list[dict], session: str | None = None,
            mission: str | None = None, since: datetime | None = None) -> list[dict]:
    out = []
    for r in rows:
        if session and r.get("session") != session:
            continue
        if mission and r.get("mission") != mission:
            continue
        if since:
            ts = r.get("ts", "")
            try:
                if datetime.fromisoformat(ts.replace("Z", "+00:00")) < since:
                    continue
            except Exception:
                continue
        out.append(r)
    return out


def _rollup(rows: Iterable[dict], dim: str) -> dict:
    groups: dict[str, dict] = defaultdict(
        lambda: {"calls": 0, "input_tokens": 0, "output_tokens": 0, "usd": 0.0,
                 "preflight_calls": 0}
    )
    for r in rows:
        key = r.get(dim, "unknown") or "unknown"
        g = groups[key]
        g["calls"] += 1
        g["input_tokens"] += int(r.get("input_tokens", 0))
        g["output_tokens"] += int(r.get("output_tokens", 0))
        g["usd"] += float(r.get("usd", 0.0))
        if r.get("preflight_used"):
            g["preflight_calls"] += 1
    for g in groups.values():
        g["usd"] = round(g["usd"], 4)
    return dict(groups)


def session_summary(session_id: str) -> dict:
    rows = _filter(_read_log(), session=session_id)
    return {
        "session": session_id,
        "calls": len(rows),
        "by_provider": _rollup(rows, "provider"),
        "by_model": _rollup(rows, "model"),
        "total_input_tokens": sum(int(r.get("input_tokens", 0)) for r in rows),
        "total_output_tokens": sum(int(r.get("output_tokens", 0)) for r in rows),
        "total_usd": round(sum(float(r.get("usd", 0.0)) for r in rows), 4),
    }


def mission_rollup(mission: str) -> dict:
    rows = _filter(_read_log(), mission=mission)
    by_session = _rollup(rows, "session")
    total_usd = sum(float(r.get("usd", 0.0)) for r in rows)
    preflight_calls = sum(1 for r in rows if r.get("preflight_used"))
    delta = roi_delta(rows)
    return {
        "mission": mission,
        "calls": len(rows),
        "sessions": len(by_session),
        "by_session": by_session,
        "by_nucleus": _rollup(rows, "nucleus"),
        "total_usd": round(total_usd, 4),
        "preflight_calls": preflight_calls,
        "preflight_rate": round((preflight_calls / len(rows)) if rows else 0.0, 3),
        "roi_delta": delta,
    }


def roi_delta(rows: list[dict]) -> dict:
    """Compare actual cost to a pre-preflight baseline.

    Baseline assumes BASELINE_PER_BUILD_USD per call without preflight.
    Reduction = 1 - actual / baseline (negative means we got more expensive).
    """
    if not rows:
        # Empty path must return identical schema to non-empty path
        # so _print_aggregate / _print_mission don't KeyError.
        return {
            "baseline_usd": 0.0,
            "actual_usd": 0.0,
            "reduction": 0.0,
            "reduction_pct": 0.0,
        }
    baseline = len(rows) * BASELINE_PER_BUILD_USD
    actual = sum(float(r.get("usd", 0.0)) for r in rows)
    reduction = (1 - actual / baseline) if baseline else 0.0
    return {
        "baseline_usd": round(baseline, 4),
        "actual_usd": round(actual, 4),
        "reduction": round(reduction, 4),
        "reduction_pct": round(reduction * 100, 2),
    }


def aggregate(days: int = 30, since_iso: str | None = None) -> dict:
    if since_iso:
        try:
            since = datetime.fromisoformat(since_iso)
            if since.tzinfo is None:
                since = since.replace(tzinfo=timezone.utc)
        except ValueError:
            since = datetime.now(timezone.utc) - timedelta(days=days)
    else:
        since = datetime.now(timezone.utc) - timedelta(days=days)
    rows = _filter(_read_log(), since=since)
    return {
        "period_start": since.isoformat(),
        "period_days": days if not since_iso else None,
        "calls": len(rows),
        "total_usd": round(sum(float(r.get("usd", 0.0)) for r in rows), 4),
        "by_provider": _rollup(rows, "provider"),
        "by_model": _rollup(rows, "model"),
        "by_nucleus": _rollup(rows, "nucleus"),
        "by_mission": _rollup(rows, "mission"),
        "roi_delta": roi_delta(rows),
    }


def _print_table(title: str, groups: dict, sort_key: str = "usd") -> None:
    print(f"\n{title}")
    print(f"  {'name':<28} {'calls':>6} {'in_tok':>10} {'out_tok':>10} {'usd':>10}")
    items = sorted(groups.items(), key=lambda kv: kv[1].get(sort_key, 0), reverse=True)
    for name, g in items:
        print(f"  {str(name)[:28]:<28} {g['calls']:>6} "
              f"{g['input_tokens']:>10} {g['output_tokens']:>10} "
              f"{g['usd']:>10.4f}")


def _print_session(report: dict) -> None:
    print(f"=== Session {report['session']} ===")
    print(f"Calls: {report['calls']} | "
          f"Input: {report['total_input_tokens']} | "
          f"Output: {report['total_output_tokens']} | "
          f"USD: {report['total_usd']}")
    if report["by_provider"]:
        _print_table("By provider:", report["by_provider"])
    if report["by_model"]:
        _print_table("By model:", report["by_model"])


def _print_mission(report: dict) -> None:
    print(f"=== Mission {report['mission']} ===")
    print(f"Calls: {report['calls']} | Sessions: {report['sessions']} | "
          f"USD: {report['total_usd']}")
    print(f"Preflight rate: {report['preflight_rate']*100:.1f}% "
          f"({report['preflight_calls']}/{report['calls']})")
    delta = report["roi_delta"]
    print(f"ROI vs baseline: {delta['reduction_pct']}% reduction "
          f"(baseline ${delta['baseline_usd']} -> actual ${delta['actual_usd']})")
    if report["by_nucleus"]:
        _print_table("By nucleus:", report["by_nucleus"])


def _print_aggregate(report: dict) -> None:
    print(f"=== Aggregate (since {report['period_start']}) ===")
    print(f"Calls: {report['calls']} | Total USD: {report['total_usd']}")
    delta = report["roi_delta"]
    print(f"ROI vs baseline: {delta['reduction_pct']}% reduction")
    if report["by_provider"]:
        _print_table("By provider:", report["by_provider"])
    if report["by_mission"]:
        _print_table("By mission:", report["by_mission"])


def main() -> int:
    VERB_HELP = {
        "aggregate": "30-day rollup (or --days N). Prints calls, total USD, "
                     "ROI vs baseline, by-provider table.",
        "record":    "Append a manual cost event. Requires --provider --model "
                     "and at least --usd or --input/--output token counts.",
        "report":    "Same as `aggregate` (alias).",
        "session":   "Show cost summary for a single session. Use --session SID.",
        "mission":   "Roll up costs across all sessions tagged with a mission. "
                     "Use --mission NAME.",
    }
    try:
        from cex_agent_io import maybe_print_verb_help
        if maybe_print_verb_help(sys.argv[1:], VERB_HELP):
            return 0
    except ImportError:
        pass

    parser = argparse.ArgumentParser(
        description="Aggregate token + USD costs from cex_router_v2 cost_log.jsonl",
    )
    # Positional verb (v1.2.0+ canonical form). Flag form preserved below.
    parser.add_argument("verb", nargs="?", default=None,
                        choices=("aggregate", "record", "report", "session", "mission"),
                        help="Subcommand. Try `tool <verb> --help`.")
    parser.add_argument("--session", default=None, help="Filter by session id")
    parser.add_argument("--mission", default=None, help="Filter by mission name")
    parser.add_argument("--since", default=None,
                        help="ISO date (e.g. 2026-04-27); overrides --aggregate-30d window")
    parser.add_argument("--aggregate-30d", action="store_true",
                        help="30-day rollup")
    parser.add_argument("--days", type=int, default=30,
                        help="Custom window in days (default 30)")
    parser.add_argument("--record", action="store_true",
                        help="Append a manual cost event (use --provider/--model/...)")
    parser.add_argument("--provider", default=None)
    parser.add_argument("--model", default=None)
    parser.add_argument("--nucleus", default="",
                        help="Tag the target nucleus (e.g. n03). Falls back to "
                             "CEX_NUCLEUS env when omitted.")
    parser.add_argument("--input", type=int, default=0)
    parser.add_argument("--output", type=int, default=0)
    parser.add_argument("--usd", type=float, default=None)
    parser.add_argument("--subagent-id", default="",
                        help="Tag the sub-producer/escalation tier (e.g. producer_0#sonnet)")
    parser.add_argument("--preflight-used", action="store_true")
    parser.add_argument("--json", action="store_true",
                        help="JSON output")
    args = parser.parse_args()

    # Positional verb -> flag dispatch (back-compat: flags still work directly).
    if args.verb == "aggregate" or args.verb == "report":
        args.aggregate_30d = True
    elif args.verb == "record":
        args.record = True
    # `session` and `mission` are activated by --session / --mission flag presence.

    if args.record:
        if not args.provider or not args.model:
            print("ERROR: --record requires --provider and --model", file=sys.stderr)
            return 2
        entry = record(args.provider, args.model, args.input, args.output,
                       usd=args.usd, session=args.session,
                       mission=args.mission or "", nucleus=args.nucleus,
                       preflight_used=args.preflight_used,
                       subagent_id=args.subagent_id)
        if args.json:
            print(json.dumps(entry))
        else:
            print(f"recorded: {entry}")
        return 0

    if args.session:
        report = session_summary(args.session)
        if args.json:
            print(json.dumps(report))
        else:
            _print_session(report)
        return 0

    if args.mission:
        report = mission_rollup(args.mission)
        if args.json:
            print(json.dumps(report))
        else:
            _print_mission(report)
        return 0

    # Default: aggregate
    report = aggregate(days=args.days, since_iso=args.since)
    if args.json:
        print(json.dumps(report))
    else:
        _print_aggregate(report)
    return 0


if __name__ == "__main__":
    try:
        from cex_agent_io import wrap_main

        def _main_wrapper(argv):
            sys.argv = [sys.argv[0]] + argv
            return main()

        sys.exit(wrap_main(_main_wrapper, sys.argv[1:], label="cex_cost_tracker"))
    except ImportError:
        sys.exit(main())
