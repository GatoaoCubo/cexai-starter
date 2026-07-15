#!/usr/bin/env python3
# -*- coding: ascii -*-
"""CEX 8F Enforcer -- mechanical compliance tracking for the 8F pipeline.

Shifts 8F from "rule the LLM should follow" to "rule the system measures
and reports on". Non-blocking by design -- never gates publication.

How it works:
  1. Each LLM session creates state file: .cex/runtime/8f_state/{session_id}.json
  2. Stages emit markers in stdout: === F1 CONSTRAIN ===, === F2 BECOME ===, etc.
  3. The enforcer parses transcripts (or markers logged via update_marker)
     and records which of F1-F8 fired per session.
  4. On F8 COLLABORATE, it validates F1-F7 markers were all seen.
  5. Per-session compliance JSONL appended to .cex/runtime/8f_compliance.log
  6. Aggregate report shows compliance % over a window (target >= 80%).

Usage:
  python _tools/cex_8f_enforcer.py --session abc123 --check
  python _tools/cex_8f_enforcer.py --session abc123 --mark F3 --kind agent
  python _tools/cex_8f_enforcer.py --report
  python _tools/cex_8f_enforcer.py --report --days 7 --json
  python _tools/cex_8f_enforcer.py --parse path/to/transcript.txt --session abc123
  python _tools/cex_8f_enforcer.py --watch     # daemon mode
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
STATE_DIR = ROOT / ".cex" / "runtime" / "8f_state"
COMPLIANCE_LOG = ROOT / ".cex" / "runtime" / "8f_compliance.log"

STAGES = ["F1", "F2", "F3", "F4", "F5", "F6", "F7", "F8"]
STAGE_NAMES = {
    "F1": "CONSTRAIN", "F2": "BECOME", "F3": "INJECT",
    "F4": "REASON", "F5": "CALL", "F6": "PRODUCE",
    "F7": "GOVERN", "F8": "COLLABORATE",
}
# Marker pattern: === F1 CONSTRAIN === or F1: kind=...
MARKER_RE = re.compile(r"^\s*(?:===\s*)?(F[1-8])\b", re.MULTILINE)
COMPLIANCE_TARGET = 0.80  # 80% of sessions should hit all 8 markers


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _state_path(session_id: str) -> Path:
    safe = re.sub(r"[^a-zA-Z0-9_-]", "_", session_id)[:64]
    return STATE_DIR / f"{safe}.json"


def _load_state(session_id: str) -> dict:
    path = _state_path(session_id)
    if not path.exists():
        return {
            "session_id": session_id,
            "started": _now_iso(),
            "stages": {},  # {F1: timestamp, ...}
            "nucleus": os.environ.get("CEX_NUCLEUS", "unknown"),
            "kind": None,
        }
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {"session_id": session_id, "started": _now_iso(),
                "stages": {}, "nucleus": "unknown", "kind": None}


def _save_state(state: dict) -> None:
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    _state_path(state["session_id"]).write_text(
        json.dumps(state, indent=2), encoding="utf-8"
    )


def mark_stage(session_id: str, stage: str, kind: str | None = None) -> dict:
    """Record that a stage fired. Used as `--mark F3 --kind agent`."""
    stage = stage.upper()
    if stage not in STAGES:
        raise ValueError(f"Invalid stage '{stage}'. Must be one of: {STAGES}")
    state = _load_state(session_id)
    state["stages"][stage] = _now_iso()
    if kind:
        state["kind"] = kind
    _save_state(state)
    return state


def check_session(session_id: str) -> dict:
    """Validate F1-F8 compliance for a session. Returns report."""
    state = _load_state(session_id)
    fired = set(state.get("stages", {}).keys())
    missing = [s for s in STAGES if s not in fired]
    pct = (len(fired) / len(STAGES)) * 100
    report = {
        "session_id": session_id,
        "nucleus": state.get("nucleus", "unknown"),
        "kind": state.get("kind"),
        "stages_fired": sorted(fired),
        "stages_missing": missing,
        "compliance_pct": round(pct, 2),
        "complete": len(missing) == 0,
        "checked_at": _now_iso(),
    }
    _append_compliance(report)
    return report


def parse_transcript(transcript_path: str, session_id: str) -> dict:
    """Parse a transcript file for F-stage markers. Updates state + checks."""
    path = Path(transcript_path)
    if not path.exists():
        return {"error": f"transcript not found: {transcript_path}"}
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except Exception as exc:
        return {"error": f"read failed: {exc}"}
    seen = set()
    for match in MARKER_RE.finditer(text):
        seen.add(match.group(1))
    state = _load_state(session_id)
    now = _now_iso()
    for stage in seen:
        state["stages"].setdefault(stage, now)
    _save_state(state)
    return check_session(session_id)


def _append_compliance(report: dict) -> None:
    """Append a compliance entry to the JSONL log."""
    try:
        COMPLIANCE_LOG.parent.mkdir(parents=True, exist_ok=True)
        with COMPLIANCE_LOG.open("a", encoding="utf-8") as f:
            f.write(json.dumps(report) + "\n")
    except Exception:
        pass


def aggregate_report(days: int = 7) -> dict:
    """Compute compliance over the last N days. Aggregate per-nucleus + per-kind."""
    if not COMPLIANCE_LOG.exists():
        return {"period_days": days, "total_sessions": 0,
                "compliance_pct": 0.0, "target_pct": COMPLIANCE_TARGET * 100,
                "meets_target": False, "by_nucleus": {}, "by_kind": {}}
    cutoff = datetime.now(timezone.utc) - timedelta(days=days)
    entries = []
    try:
        for line in COMPLIANCE_LOG.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            try:
                entry = json.loads(line)
                ts = entry.get("checked_at", "")
                if ts:
                    try:
                        entry_dt = datetime.fromisoformat(ts.replace("Z", "+00:00"))
                        if entry_dt < cutoff:
                            continue
                    except ValueError:
                        continue
                entries.append(entry)
            except json.JSONDecodeError:
                continue
    except Exception:
        pass

    total = len(entries)
    complete = sum(1 for e in entries if e.get("complete"))
    pct = (complete / total * 100) if total else 0.0

    by_nucleus: dict[str, dict] = {}
    by_kind: dict[str, dict] = {}
    for e in entries:
        nuc = e.get("nucleus", "unknown")
        by_nucleus.setdefault(nuc, {"total": 0, "complete": 0})
        by_nucleus[nuc]["total"] += 1
        if e.get("complete"):
            by_nucleus[nuc]["complete"] += 1
        kind = e.get("kind") or "unspecified"
        by_kind.setdefault(kind, {"total": 0, "complete": 0})
        by_kind[kind]["total"] += 1
        if e.get("complete"):
            by_kind[kind]["complete"] += 1

    for stats in list(by_nucleus.values()) + list(by_kind.values()):
        stats["compliance_pct"] = round(
            (stats["complete"] / stats["total"] * 100) if stats["total"] else 0.0, 2
        )

    return {
        "period_days": days,
        "total_sessions": total,
        "complete_sessions": complete,
        "compliance_pct": round(pct, 2),
        "target_pct": COMPLIANCE_TARGET * 100,
        "meets_target": pct >= COMPLIANCE_TARGET * 100,
        "by_nucleus": by_nucleus,
        "by_kind": by_kind,
    }


def watch_loop(interval: int = 30) -> None:
    """Daemon mode: periodically scan state files + emit aggregate to stdout."""
    print(f"[8f-enforcer] watch started, interval={interval}s, log={COMPLIANCE_LOG}")
    while True:
        try:
            report = aggregate_report(days=1)
            print(f"[8f-enforcer] {_now_iso()} sessions={report['total_sessions']} "
                  f"compliance={report['compliance_pct']}% "
                  f"target={report['target_pct']}%")
            time.sleep(interval)
        except KeyboardInterrupt:
            print("[8f-enforcer] watch stopped")
            return
        except Exception as exc:  # pylint: disable=broad-except
            print(f"[8f-enforcer] error: {exc}")
            time.sleep(interval)


def _print_report(report: dict) -> None:
    """Human-readable session check output."""
    print(f"Session:      {report['session_id']}")
    print(f"Nucleus:      {report['nucleus']}")
    print(f"Kind:         {report.get('kind') or '(unset)'}")
    print(f"Compliance:   {report['compliance_pct']}% "
          f"({len(report['stages_fired'])}/8 stages)")
    print(f"Stages fired: {', '.join(report['stages_fired']) or '(none)'}")
    if report["stages_missing"]:
        print(f"Stages MISSING: {', '.join(report['stages_missing'])}")
    print(f"Complete:     {report['complete']}")


def _print_aggregate(report: dict) -> None:
    """Human-readable aggregate report."""
    print(f"=== 8F Compliance Report (last {report['period_days']} days) ===")
    print(f"Total sessions:     {report['total_sessions']}")
    print(f"Complete (F1-F8):   {report.get('complete_sessions', 0)}")
    print(f"Compliance:         {report['compliance_pct']}% "
          f"(target {report['target_pct']}%)")
    print(f"Meets target:       {report['meets_target']}")
    if report.get("by_nucleus"):
        print("\nBy nucleus:")
        for nuc, stats in sorted(report["by_nucleus"].items()):
            print(f"  {nuc}: {stats['compliance_pct']}% "
                  f"({stats['complete']}/{stats['total']})")
    if report.get("by_kind"):
        print("\nBy kind:")
        for kind, stats in sorted(report["by_kind"].items()):
            print(f"  {kind}: {stats['compliance_pct']}% "
                  f"({stats['complete']}/{stats['total']})")


def main() -> int:
    # Article Sec 2.1: per-verb help (light resolver, no subparsers refactor).
    VERB_HELP = {
        "mark":   "Record that a stage fired. Requires --mark Fx (F1..F8) and "
                  "usually --session SID. Optional --kind to tag the artifact "
                  "kind. Idempotent per (session, stage).",
        "check":  "Validate session compliance. Reports which Fx stages have/"
                  "haven't fired. Use --session SID; rc=0 if 8F complete, 1 otherwise.",
        "report": "Aggregate compliance over a window (default 7 days). Counts "
                  "complete F1-F8 sessions vs total. --json for machine output.",
        "watch":  "Daemon mode: print rolling report every --interval seconds.",
        "parse":  "Parse a transcript file for F-stage markers (=== F1 CONSTRAIN === "
                  "etc). Use --parse path/to/transcript.txt.",
    }
    try:
        from cex_agent_io import maybe_print_verb_help
        if maybe_print_verb_help(sys.argv[1:], VERB_HELP):
            return 0
    except ImportError:
        pass

    parser = argparse.ArgumentParser(
        description="CEX 8F Enforcer -- track F1-F8 compliance per session.",
    )
    # Positional verb (v1.2.0+ canonical form). Flag form preserved below.
    parser.add_argument("verb", nargs="?", default=None,
                        choices=("mark", "check", "report", "watch", "parse"),
                        help="Subcommand. Try `tool <verb> --help` for verb-specific help.")
    parser.add_argument("--session", default=None, help="Session id to check/mark")
    parser.add_argument("--check", action="store_true",
                        help="Validate session compliance")
    parser.add_argument("--mark", default=None,
                        help="Record that a stage fired (F1..F8)")
    parser.add_argument("--kind", default=None,
                        help="Kind being built (with --mark)")
    parser.add_argument("--parse", default=None,
                        help="Parse transcript file for F-stage markers")
    parser.add_argument("--report", action="store_true",
                        help="Aggregate compliance over a window")
    parser.add_argument("--days", type=int, default=7,
                        help="Window for --report (default: 7)")
    parser.add_argument("--watch", action="store_true",
                        help="Daemon mode: periodic aggregate")
    parser.add_argument("--interval", type=int, default=30,
                        help="Watch interval seconds (default: 30)")
    parser.add_argument("--json", action="store_true",
                        help="JSON output (default: human-readable)")
    parser.add_argument("--nucleus", default=None,
                        help="Nucleus id (e.g. n03). Overrides CEX_NUCLEUS env var.")
    args = parser.parse_args()

    # --nucleus flag wins over env var for this invocation.
    # Allows ad-hoc CLI use without exporting CEX_NUCLEUS.
    if args.nucleus:
        os.environ["CEX_NUCLEUS"] = args.nucleus.upper()

    # Positional verb -> activate corresponding mode.
    # `mark F1` requires --session OR --mark Fx; we can't infer Fx from positional alone.
    if args.verb == "report":
        args.report = True
    elif args.verb == "watch":
        args.watch = True
    elif args.verb == "check":
        args.check = True

    if args.watch:
        watch_loop(args.interval)
        return 0

    if args.report:
        report = aggregate_report(days=args.days)
        if args.json:
            print(json.dumps(report))
        else:
            _print_aggregate(report)
        return 0

    if args.parse:
        if not args.session:
            print("ERROR: --parse requires --session", file=sys.stderr)
            return 2
        report = parse_transcript(args.parse, args.session)
        if "error" in report:
            print(f"ERROR: {report['error']}", file=sys.stderr)
            return 2
        if args.json:
            print(json.dumps(report))
        else:
            _print_report(report)
        return 0

    if args.mark:
        if not args.session:
            print("ERROR: --mark requires --session", file=sys.stderr)
            return 2
        try:
            mark_stage(args.session, args.mark, args.kind)
            print(f"[OK] marked {args.mark} for session {args.session}")
        except ValueError as exc:
            print(f"ERROR: {exc}", file=sys.stderr)
            return 2
        return 0

    if args.check:
        if not args.session:
            print("ERROR: --check requires --session", file=sys.stderr)
            return 2
        report = check_session(args.session)
        if args.json:
            print(json.dumps(report))
        else:
            _print_report(report)
        return 0

    parser.print_help()
    return 0


if __name__ == "__main__":
    try:
        from cex_agent_io import wrap_main

        def _main_wrapper(argv):
            sys.argv = [sys.argv[0]] + argv
            return main()

        sys.exit(wrap_main(_main_wrapper, sys.argv[1:], label="cex_8f_enforcer"))
    except ImportError:
        sys.exit(main())
