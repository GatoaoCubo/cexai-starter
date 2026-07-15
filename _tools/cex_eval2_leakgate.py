# -*- coding: utf-8 -*-
"""CEX eval2 Leak Gate -- DP6 enforcement for BETTER_EVAL.

DECISION DP6 (LOCKED): eval2 NEVER enters any training corpus -- gate by
construction + a validator check. This tool IS that check.

WHAT IT ASSERTS
  ZERO intent overlap between the eval2 gold set (_data/ft/eval2/*.jsonl) and
  ALL training corpora the FT carteiro learns from. Overlap is detected two
  ways, both fatal:
    exact       -- byte-identical intent string.
    normalized  -- casefold + whitespace-collapsed identical (catches a
                   re-cased / re-spaced restatement of the SAME intent).
  The normalizer is byte-identical to the W0 harvester's dedup `norm()`
  (re.sub(r"\\s+", " ", s.strip().casefold())) so the gate and the harvest
  agree on what "the same intent" means -- a leak the harvest deduped against
  can never reappear as a false miss here.

WHY THESE CORPORA (and NOT the glue telemetry)
  The FT trains on the CURATED _gold/ files (distill_gold, combined_train,
  outcome_gold*, round/wave splits, snapshots). The raw glue telemetry
  (glue_carteiro_*.jsonl) is the eval2 SOURCE -- eval2 intents are sampled
  FROM it by design, so it is deliberately EXCLUDED from the leak set (including
  it would flag every legitimately-harvested row). Leak = eval2 vs TRAIN, never
  eval2 vs its own source.

CONTRACT
  - Pure read-only. Never mutates a corpus. ASCII-only source.
  - Importable: check_leak(eval2_paths, corpus_paths) -> report dict.
  - Exit 1 on ANY hit (exact or normalized), listing offenders. Exit 0 clean.

CLI:
  python _tools/cex_eval2_leakgate.py                 # defaults: eval2 vs all train
  python _tools/cex_eval2_leakgate.py --json
  python _tools/cex_eval2_leakgate.py --eval2 PATH --corpus PATH [--corpus PATH...]
  python _tools/cex_eval2_leakgate.py --show 50       # cap printed offenders
"""
from __future__ import annotations

import argparse
import glob
import json
import re
import sys
from pathlib import Path
from typing import Any, Iterable

REPO_ROOT = Path(__file__).resolve().parent.parent

# eval2 gold (the set under protection). *.jsonl so candidate + gold both count.
DEFAULT_EVAL2_GLOBS = [
    "_data/ft/eval2/*.jsonl",
]

# ALL training corpora the FT carteiro learns from. Comprehensive by design:
# over-inclusion only makes the gate STRICTER (eval2 must be disjoint from every
# one of these by DP6), never wrong. The raw glue telemetry is intentionally
# absent (it is the eval2 source -- see module docstring).
DEFAULT_CORPUS_GLOBS = [
    "_data/ft/glue/_gold/distill_gold.jsonl",
    "_data/ft/glue/_gold/combined_train*.jsonl",
    "_data/ft/glue/_gold/outcome_gold.jsonl",
    "_data/ft/glue/_gold/outcome_gold_train.jsonl",
    "_data/ft/glue/_gold/_rounds/*.jsonl",
    "_data/ft/glue/_gold/_snap_*.jsonl",
]


# ---------------------------------------------------------------------------
# Intent extraction + normalization
# ---------------------------------------------------------------------------

def norm_intent(s: str) -> str:
    """Casefold + whitespace-collapse. BYTE-IDENTICAL to the W0 harvest dedup
    `norm()` so the gate and the harvester share one definition of sameness."""
    return re.sub(r"\s+", " ", s.strip().casefold())


def extract_intent(rec: Any) -> str | None:
    """Best-effort intent string from a row of EITHER shape:
      eval2            -> top-level "intent"
      training corpora -> "input": {"intent"|"query"|"text"|"prompt"|"q": ...}
    Returns None if no usable intent string is present.
    """
    if not isinstance(rec, dict):
        return None
    top = rec.get("intent")
    if isinstance(top, str) and top.strip():
        return top
    inp = rec.get("input")
    if isinstance(inp, dict):
        for k in ("intent", "query", "text", "prompt", "q"):
            v = inp.get(k)
            if isinstance(v, str) and v.strip():
                return v
    if isinstance(inp, str) and inp.strip():
        return inp
    return None


def _iter_rows(path: Path) -> Iterable[tuple[int, dict]]:
    """Yield (lineno, record) for each well-formed JSON object line."""
    try:
        with open(path, "r", encoding="utf-8", errors="replace") as fh:
            for i, raw in enumerate(fh, 1):
                raw = raw.strip()
                if not raw:
                    continue
                try:
                    rec = json.loads(raw)
                except Exception:
                    continue
                if isinstance(rec, dict):
                    yield i, rec
    except Exception:
        return


def expand_paths(patterns: Iterable[str]) -> list[Path]:
    """Resolve glob patterns (relative to REPO_ROOT or absolute) to existing
    files, de-duplicated and sorted."""
    seen: dict[str, Path] = {}
    for pat in patterns:
        target = pat if Path(pat).is_absolute() else str(REPO_ROOT / pat)
        for m in glob.glob(target):
            mp = Path(m).resolve()
            if mp.is_file():
                seen[str(mp)] = mp
    return sorted(seen.values(), key=str)


# ---------------------------------------------------------------------------
# Core check
# ---------------------------------------------------------------------------

def build_corpus_index(paths: list[Path]) -> dict[str, dict]:
    """Index training-corpus intents for O(1) lookup.

    Returns {"exact": {raw_intent: where}, "norm": {norm_intent: where}} where
    `where` = "filename:lineno" of the FIRST occurrence. First-occurrence is
    enough: the gate only needs to PROVE a hit and point at one witness.
    """
    exact: dict[str, str] = {}
    norm: dict[str, str] = {}
    for path in paths:
        for lineno, rec in _iter_rows(path):
            intent = extract_intent(rec)
            if not intent:
                continue
            where = "%s:%d" % (path.name, lineno)
            exact.setdefault(intent, where)
            norm.setdefault(norm_intent(intent), where)
    return {"exact": exact, "norm": norm}


def check_leak(eval2_paths: list[Path], corpus_paths: list[Path]) -> dict:
    """Assert zero eval2<->training overlap. Returns a report dict:

      {clean: bool, n_eval2_rows, n_eval2_intents, n_corpus_files,
       n_corpus_intents, exact_hits, normalized_hits, offenders: [...]}

    An offender = an eval2 intent found in the corpus. `match_type` is "exact"
    when byte-identical, else "normalized". exact is checked first so a row is
    reported once at its strongest match.
    """
    # Defensive: never let an eval2 file double as a corpus file (self-compare).
    eval2_set = {str(p) for p in eval2_paths}
    corpus_paths = [p for p in corpus_paths if str(p) not in eval2_set]

    idx = build_corpus_index(corpus_paths)
    exact_idx, norm_idx = idx["exact"], idx["norm"]

    offenders: list[dict] = []
    n_rows = 0
    eval2_intents: set[str] = set()
    for path in eval2_paths:
        for lineno, rec in _iter_rows(path):
            intent = extract_intent(rec)
            if not intent:
                continue
            n_rows += 1
            eval2_intents.add(intent)
            ni = norm_intent(intent)
            if intent in exact_idx:
                offenders.append({
                    "eval2_file": path.name,
                    "eval2_line": lineno,
                    "eval2_id": rec.get("id"),
                    "match_type": "exact",
                    "corpus_where": exact_idx[intent],
                    "intent": intent[:120],
                })
            elif ni in norm_idx:
                offenders.append({
                    "eval2_file": path.name,
                    "eval2_line": lineno,
                    "eval2_id": rec.get("id"),
                    "match_type": "normalized",
                    "corpus_where": norm_idx[ni],
                    "intent": intent[:120],
                })

    exact_hits = sum(1 for o in offenders if o["match_type"] == "exact")
    norm_hits = sum(1 for o in offenders if o["match_type"] == "normalized")
    return {
        "clean": not offenders,
        "n_eval2_rows": n_rows,
        "n_eval2_intents": len(eval2_intents),
        "n_corpus_files": len(corpus_paths),
        "n_corpus_intents": len(exact_idx),
        "exact_hits": exact_hits,
        "normalized_hits": norm_hits,
        "offenders": offenders,
        "eval2_files": [p.name for p in eval2_paths],
        "corpus_files": [p.name for p in corpus_paths],
    }


def run_default_gate(eval2_globs: list[str] | None = None,
                     corpus_globs: list[str] | None = None) -> dict:
    """Resolve default (or supplied) globs and run check_leak."""
    e2 = expand_paths(eval2_globs or DEFAULT_EVAL2_GLOBS)
    corp = expand_paths(corpus_globs or DEFAULT_CORPUS_GLOBS)
    rep = check_leak(e2, corp)
    rep["eval2_globs"] = eval2_globs or DEFAULT_EVAL2_GLOBS
    rep["corpus_globs"] = corpus_globs or DEFAULT_CORPUS_GLOBS
    return rep


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def _print_report(rep: dict, show: int) -> None:
    print("=== eval2 Leak Gate (DP6) ===")
    print("eval2 files   : %d (%s)" % (
        len(rep.get("eval2_files", [])), ", ".join(rep.get("eval2_files", [])) or "none"))
    print("corpus files  : %d   corpus intents: %d" % (
        rep["n_corpus_files"], rep["n_corpus_intents"]))
    print("eval2 intents : %d (rows=%d)" % (rep["n_eval2_intents"], rep["n_eval2_rows"]))
    print("hits          : exact=%d  normalized=%d" % (
        rep["exact_hits"], rep["normalized_hits"]))
    if rep["clean"]:
        print("\n[OK] CLEAN -- zero eval2 intent overlap with training corpora.")
        return
    n = len(rep["offenders"])
    print("\n[FAIL] %d LEAK(S) -- eval2 intents present in a training corpus:" % n)
    for o in rep["offenders"][:show]:
        print("  [%s] %s:%s (id=%s) <-> %s" % (
            o["match_type"], o["eval2_file"], o["eval2_line"],
            o.get("eval2_id"), o["corpus_where"]))
        print("      intent: %s" % o["intent"])
    if n > show:
        print("  ... and %d more (use --show %d or --json)" % (n - show, n))


def main() -> int:
    ap = argparse.ArgumentParser(
        description="eval2 Leak Gate (DP6): assert zero eval2<->training overlap")
    ap.add_argument("--eval2", action="append", metavar="GLOB",
                    help="eval2 JSONL path/glob (repeatable; default: %s)"
                         % DEFAULT_EVAL2_GLOBS)
    ap.add_argument("--corpus", action="append", metavar="GLOB",
                    help="training corpus path/glob (repeatable; default: all FT "
                         "_gold/ train files)")
    ap.add_argument("--json", action="store_true", help="emit the report as JSON")
    ap.add_argument("--show", type=int, default=25, metavar="N",
                    help="cap printed offenders (default 25; JSON holds all)")
    args = ap.parse_args()

    rep = run_default_gate(args.eval2, args.corpus)
    if args.json:
        print(json.dumps(rep, indent=2, ensure_ascii=True))
    else:
        _print_report(rep, args.show)
    return 0 if rep["clean"] else 1


if __name__ == "__main__":
    try:
        from cex_agent_io import wrap_main

        def _main_wrapper(argv):
            sys.argv = [sys.argv[0]] + argv
            return main()

        sys.exit(wrap_main(_main_wrapper, sys.argv[1:], label="cex_eval2_leakgate"))
    except ImportError:
        sys.exit(main())
