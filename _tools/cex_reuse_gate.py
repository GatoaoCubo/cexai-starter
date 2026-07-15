#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""CEX Reuse Gate (LEVERAGE_A4) -- semantic artifact-reuse gate.

The cheapest build is the one you do NOT redo. Before building, this gate
queries cex_retriever (TF-IDF) for the top-K most-similar EXISTING artifacts
of the same kind. If the closest match scores >= threshold, it emits a REUSE
proposal (path + score + "adapt vs regenerate" advice) so an operator/agent
can reuse or adapt instead of regenerating. This automates Commandment VI
("scout before create") as a pre-build gate.

CONTRACT (non-negotiable):
  - ADVISORY ONLY: it PROPOSES reuse. It NEVER blocks, never auto-skips a
    build. The build path treats the proposal as a hint.
  - FAIL-OPEN: any retriever error / missing index -> decision="build"
    (proceed). check_reuse() NEVER raises into the build path.
  - FLAG-GATED at the call site: the build-path wiring only consults this gate
    when CEX_REUSE_GATE is truthy. OFF (default) = no-op = byte-identical to
    today. The CLI runs the check regardless (a human asked explicitly).
  - INDEX-REUSE: accepts a pre-loaded retriever index so it never rebuilds the
    TF-IDF corpus; it reuses whatever F3 INJECT already loaded.
  - ASCII-only source (per .claude/rules/ascii-code-rule.md).

Threshold:
  default 0.85 (conservative -- only genuine near-duplicates trip it).
  Override with env CEX_REUSE_GATE_THRESHOLD (float in [0, 1]) or --threshold.

CLI:
  python _tools/cex_reuse_gate.py --kind agent --intent "support triage agent"
  python _tools/cex_reuse_gate.py --kind quality_gate --intent "..." --json
  python _tools/cex_reuse_gate.py --kind X --intent "..." --path P05/x.md --json
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

# Optional dependency -- degrade gracefully (fail-open). If the retriever is
# unavailable the gate can never propose reuse, so every build proceeds.
try:
    from cex_retriever import find_similar as _find_similar
    from cex_retriever import load_index as _load_index
    _RETRIEVER_AVAILABLE = True
except Exception:  # ImportError or any transitive import failure -> fail-open
    _RETRIEVER_AVAILABLE = False

    def _find_similar(*_a, **_k):  # type: ignore
        return []

    def _load_index(*_a, **_k):  # type: ignore
        return None


DEFAULT_THRESHOLD = 0.85
FLAG_ENV = "CEX_REUSE_GATE"
THRESHOLD_ENV = "CEX_REUSE_GATE_THRESHOLD"
_TRUTHY = frozenset({"1", "true", "yes", "on", "enabled"})


# ---------------------------------------------------------------------------
# Flag + threshold resolution
# ---------------------------------------------------------------------------


def is_enabled() -> bool:
    """True iff the build-path reuse gate is flag-enabled (CEX_REUSE_GATE).

    Default OFF -> the build path is byte-identical to today.
    """
    return os.environ.get(FLAG_ENV, "").strip().lower() in _TRUTHY


def resolve_threshold(explicit: float | None = None) -> float:
    """Resolve the reuse threshold: explicit arg > env > default, clamped [0, 1].

    Any malformed env value falls back to DEFAULT_THRESHOLD (fail-safe).
    """
    if explicit is not None:
        try:
            return _clamp01(float(explicit))
        except (TypeError, ValueError):
            return DEFAULT_THRESHOLD
    raw = os.environ.get(THRESHOLD_ENV, "").strip()
    if raw:
        try:
            return _clamp01(float(raw))
        except ValueError:
            return DEFAULT_THRESHOLD
    return DEFAULT_THRESHOLD


def _clamp01(x: float) -> float:
    if x < 0.0:
        return 0.0
    if x > 1.0:
        return 1.0
    return x


def _norm_path(p: str | None) -> str:
    """Normalize a path for self-exclusion comparison (posix, lowercase)."""
    if not p:
        return ""
    return str(p).replace("\\", "/").strip().lower()


# ---------------------------------------------------------------------------
# Core gate
# ---------------------------------------------------------------------------


def check_reuse(
    kind: str,
    intent: str = "",
    path: str | None = None,
    threshold: float | None = None,
    top_k: int = 5,
    index: dict | None = None,
) -> dict:
    """Decide whether an EXISTING artifact should be reused instead of rebuilt.

    Pure + fail-open: this function NEVER raises and NEVER consults the flag
    (the call site gates on is_enabled()); the CLI and tests call it directly.

    Args:
        kind: resolved target kind (e.g. "agent"). Empty/"generic" -> build
              (no kind to scope a near-duplicate search to).
        intent: the build request text (enriches the similarity query).
        path: proposed output path. If given, any match at that exact path is
              excluded -- you cannot "reuse" the very file you are about to
              (over)write.
        threshold: similarity cutoff; resolved via resolve_threshold() if None.
        top_k: how many candidate matches to return for context.
        index: pre-loaded retriever index (reused as-is; never rebuilt). Loaded
               from disk only if None.

    Returns:
        dict with keys:
          decision   -- "reuse" | "build"
          kind, intent, threshold
          max_score  -- best same-kind cosine similarity (0.0 if none)
          matches    -- list of {path, id, kind, pillar, title, tldr, score}
          advice     -- human-readable next-step guidance
          reuse_target -- best match dict when decision == "reuse", else None
          error      -- present only on fail-open (retriever error / no index)
    """
    thr = resolve_threshold(threshold)
    result: dict = {
        "decision": "build",
        "kind": kind,
        "intent": intent,
        "threshold": round(thr, 4),
        "max_score": 0.0,
        "matches": [],
        "advice": "",
        "reuse_target": None,
    }

    # Nothing to scope the search to -> proceed to build (conservative).
    kind_norm = (kind or "").strip()
    if not kind_norm or kind_norm == "generic":
        result["advice"] = "No resolved kind; reuse check skipped -> build."
        return result

    try:
        idx = index if index is not None else _load_index()
        if not idx:
            result["error"] = "no_index"
            result["advice"] = "Retriever index unavailable -> build (fail-open)."
            return result

        # Query mirrors F3 INJECT's example search (kind + intent), filtered to
        # the SAME kind: a genuine near-duplicate is almost always same-kind,
        # and the filter keeps the gate conservative (fewer false positives).
        query = ("%s %s" % (kind_norm, intent or "")).strip()
        raw = _find_similar(
            query,
            index=idx,
            kind=kind_norm,
            top_k=max(top_k, 1) + 1,  # +1 headroom for self-exclusion
            min_score=0.0,
        )

        excl = _norm_path(path)
        matches = [m for m in raw if _norm_path(m.get("path")) != excl][:top_k]
        result["matches"] = matches

        if matches:
            top = matches[0]
            result["max_score"] = top.get("score", 0.0)
            if result["max_score"] >= thr:
                result["decision"] = "reuse"
                result["reuse_target"] = top
                result["advice"] = (
                    "Near-duplicate exists: '%s' (%s, score %.3f >= %.2f). "
                    "ADAPT it instead of regenerating from scratch."
                    % (top.get("title", top.get("id", "?")),
                       top.get("path", "?"), result["max_score"], thr)
                )
            else:
                result["advice"] = (
                    "Closest existing artifact scores %.3f < %.2f -> no "
                    "near-duplicate; proceed to build."
                    % (result["max_score"], thr)
                )
        else:
            result["advice"] = "No same-kind candidates found -> build."
        return result

    except Exception as e:  # fail-open: never break the build path
        result["error"] = "%s: %s" % (type(e).__name__, e)
        result["advice"] = "Reuse check errored -> build (fail-open)."
        return result


def format_proposal(result: dict) -> str:
    """Render a check_reuse() result as a human-readable advisory block."""
    lines = []
    decision = result.get("decision", "build").upper()
    lines.append("=== CEX Reuse Gate: %s ===" % decision)
    lines.append("  kind:      %s" % result.get("kind", "?"))
    lines.append("  threshold: %.2f" % result.get("threshold", DEFAULT_THRESHOLD))
    lines.append("  max_score: %.3f" % result.get("max_score", 0.0))
    if result.get("error"):
        lines.append("  note:      fail-open (%s)" % result["error"])
    lines.append("  advice:    %s" % result.get("advice", ""))
    matches = result.get("matches", [])
    if matches:
        lines.append("  candidates:")
        for m in matches:
            lines.append(
                "    - %.3f  %s  (%s)"
                % (m.get("score", 0.0), m.get("path", "?"), m.get("id", "?"))
            )
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="CEX Reuse Gate -- propose reuse of near-duplicate artifacts (advisory)."
    )
    parser.add_argument("--kind", "-k", required=True, help="Target artifact kind")
    parser.add_argument("--intent", "-i", default="", help="Build intent text")
    parser.add_argument("--path", "-p", default=None, help="Proposed output path (self-excluded)")
    parser.add_argument("--threshold", "-t", type=float, default=None,
                        help="Similarity cutoff (default 0.85 / env CEX_REUSE_GATE_THRESHOLD)")
    parser.add_argument("--top-k", "-n", type=int, default=5, help="Max candidate matches")
    parser.add_argument("--json", action="store_true", help="Emit JSON")
    args = parser.parse_args(argv)

    result = check_reuse(
        kind=args.kind,
        intent=args.intent,
        path=args.path,
        threshold=args.threshold,
        top_k=args.top_k,
    )
    result["gate_enabled"] = is_enabled()  # transparency: would the build path act?

    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(format_proposal(result))
        if not result["gate_enabled"]:
            print("  (CEX_REUSE_GATE is OFF -- the build path ignores this proposal)")

    return 0  # advisory: always exit 0 (never break a pipeline)


if __name__ == "__main__":
    try:
        from cex_agent_io import wrap_main

        def _main_wrapper(argv):
            return main(argv)

        sys.exit(wrap_main(_main_wrapper, sys.argv[1:], label="cex_reuse_gate"))
    except ImportError:
        sys.exit(main())
