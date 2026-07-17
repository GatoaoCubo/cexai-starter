#!/usr/bin/env python3
# -*- coding: ascii -*-
"""CEX Hydration Doctor -- thin CLI wrapper around cex_check_registry's hydration_doctor plugin
(R-249/R-250, spec docs/SPEC_CEXAI_TOTAL_HYDRATION_INDEX_2026_07_03.md Sec 3.2 "STREAM B" +
Sec 4.1 WAVE 3).

ONE implementation, two entrypoints (mission mandate): every signal-computation function
(_bucket_l1_docs, _severity_s1..s4, _composite_severity, _scan_cell_body_signals,
compute_hydration_report) lives in cex_check_registry.py, where the hydration_doctor CheckPlugin
also calls it -- this file owns NOTHING but (1) Markdown rendering of an already-computed report
dict and (2) the --audit CLI verb that computes the report, writes docs/HYDRATION_MAP.md, and
prints the top-10 to stdout. It never re-derives a signal cex_check_registry.py already computes.

Usage:
    python _tools/cex_hydration_doctor.py --audit
    python _tools/cex_hydration_doctor.py --audit --top 20     # print more than 10 rows
    python _tools/cex_hydration_doctor.py --audit --out PATH   # write elsewhere (mainly for tests)

Measurement, not gating (see cex_check_registry.py's Plugin 7 comment for the full rationale):
this CLI has no notion of pass/fail -- it always writes the map and exits 0, UNLESS the total
index has never been built at all (--build has never run), in which case it prints [FAIL] and
exits 1 so a CI/automation caller can distinguish "nothing to measure yet" from a real run.

ASCII-only (enforced repo-wide for .py, see .claude/rules/ascii-code-rule.md).
"""
from __future__ import annotations

import argparse
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT / "_tools") not in sys.path:
    sys.path.insert(0, str(ROOT / "_tools"))

import cex_check_registry as ccr  # noqa: E402

MAP_PATH = ROOT / "docs" / "HYDRATION_MAP.md"

_SIGNAL_DOC = (
    ("s1_density_gap", "s1 density-measurement coverage gap",
     "share of this cell's TYPED artifacts with no density_score at all (numeric, non-null). "
     "Unmeasured != thin -- an empty cell scores 0.0 here (that gap is s2's job)."),
    ("s2_uneven", "s2 file-count unevenness",
     "how far this cell's raw file count sits BELOW the cross-nucleus median for that pillar "
     "(computed over the 7 OPERATIONAL nuclei only -- N00 the archetype baseline is excluded "
     "from the median, generalizing R-167's own N01-N07 comparison)."),
    ("s3_stub", "s3 stub markers",
     "share of this cell's files (typed + governance) carrying an unintentional [preencher] "
     "and/or bare-word TODO marker."),
    ("s4_coord_gap", "s4 coordinate coverage gap",
     "share of this cell's TYPED artifacts missing EITHER an 8f: or a related: frontmatter "
     "field (both required to count as coordinate-complete)."),
)


def _fmt_pct(x: float) -> str:
    return "%.1f%%" % (100.0 * x)


def _render_grid_table(cells: list) -> str:
    """Classic nucleus x pillar RAW FILE COUNT grid -- the DIAGNOSTICO-style at-a-glance view,
    now generated instead of hand-typed."""
    by_cell = {(c["nucleus"], c["pillar"]): c for c in cells}
    lines = []
    header = "| Nucleus | " + " | ".join(ccr.PILLAR_CODES) + " | Total |"
    sep = "|---|" + "---|" * (len(ccr.PILLAR_CODES) + 1)
    lines.append(header)
    lines.append(sep)
    for nucleus_code in ccr.NUCLEUS_DIRS:
        row_counts = [by_cell.get((nucleus_code, p), {}).get("file_count", 0) for p in ccr.PILLAR_CODES]
        marker = " (archetype baseline)" if nucleus_code == "N00" else ""
        lines.append(
            "| %s%s | " % (nucleus_code, marker) + " | ".join(str(v) for v in row_counts)
            + " | %d |" % sum(row_counts)
        )
    return "\n".join(lines)


def _render_ranked_table(cells: list) -> str:
    """The NEW deliverable: every cell, worst-first by composite severity, with the 4 signal
    columns broken out (spec: 'per-signal columns')."""
    lines = [
        "| Rank | Nucleus | Pillar | Severity | Files | Peer Median | s1 (density) "
        "| s2 (uneven) | s3 (stub) | s4 (coord) | Fill-eligible |",
        "|---|---|---|---|---|---|---|---|---|---|---|",
    ]
    for i, c in enumerate(cells, start=1):
        role = "N07 (this cycle)" if c["fill_eligible"] else (
            "archetype -- measure-only" if c["is_archetype_baseline"] else "measure-only"
        )
        lines.append(
            "| %d | %s | %s | %.4f | %d | %.1f | %s | %s | %s | %s | %s |"
            % (
                i, c["nucleus"], c["pillar"], c["severity"], c["file_count"], c["pillar_median"],
                _fmt_pct(c["s1_density_gap"]), _fmt_pct(c["s2_uneven"]),
                _fmt_pct(c["s3_stub"]), _fmt_pct(c["s4_coord_gap"]), role,
            )
        )
    return "\n".join(lines)


def _render_shortlist(shortlist: list) -> str:
    if not shortlist:
        return "(no fill-eligible cells found -- N07 may already be fully measured/at parity)\n"
    lines = []
    for row in shortlist:
        kinds = ", ".join("%s (x%d among peers)" % (k, n) for k, n in row["candidate_kinds"]) or "(no peer-kind pattern found)"
        lines.append(
            "- **%s/%s** -- severity %.4f, %d file(s) vs peer median %.1f. "
            "Peer-pillar kind pattern (index-only, NOT yet a verified >=2x-usage exemplar): %s"
            % (row["nucleus"], row["pillar"], row["severity"], row["file_count"],
               row["pillar_median"], kinds)
        )
    return "\n".join(lines)


def render_hydration_map(report: dict, generated_at: Optional[str] = None) -> str:
    """Pure function: report dict (from cex_check_registry.compute_hydration_report) -> the full
    docs/HYDRATION_MAP.md Markdown text. No I/O -- write_hydration_map() does the actual write, so
    this half stays independently unit-testable (deterministic given a fixed report + timestamp)."""
    generated_at = generated_at or datetime.now(timezone.utc).isoformat()
    cells = report["cells"]
    sanity = report["sanity"]
    cyber = report["cybersec_exempt"]

    signal_doc_lines = "\n".join(
        "- **%s** (`%s`): %s" % (label, key, desc) for key, label, desc in _SIGNAL_DOC
    )

    frontmatter = (
        "---\n"
        "id: hydration_map\n"
        "kind: context_doc\n"
        "pillar: P08\n"
        "nucleus: n07\n"
        "version: 1.0.0\n"
        "quality: null\n"
        "tags: [hydration, gap-map, generated, R-249, R-250]\n"
        "generated_by: _tools/cex_hydration_doctor.py --audit\n"
        "generated_at: \"%s\"\n"
        "index_built_at: \"%s\"\n"
        "---\n"
    ) % (generated_at, report.get("index_built_at") or "unknown")

    body = """
# CEXAI Hydration Map -- Per-Nucleus x Per-Pillar Gap Measurement

> Generated successor to the one-time `docs/DIAGNOSTICO_COBERTURA_CEXAI_2026_07_03.md` table.
> This file is REGENERATED, not hand-maintained -- run `python _tools/cex_hydration_doctor.py
> --audit` to refresh it. Source: `_tools/cex_check_registry.py`'s `hydration_doctor` plugin
> (R-249/R-250), reading `.cex/total_index/l1_documents.json` (built_at: %s) plus one targeted
> read pass over the paths that index already places inside a canonical N00-N07 nucleus/pillar
> directory (never a rescan of the full tracked corpus).

## 1. Scope + Method

Generalizes R-167's proven method (disk-audit -> rank uneven cells -> promote from a REAL
>=2x-usage exemplar, never mass-synthesize) from 1 pillar (P03) / 1 nucleus (N07) to the full
12-pillar x 7-operational-nucleus grid. Per GDP Q3 (closed 2026-07-03,
`.cex/runtime/decisions/decision_manifest_total_hydration_2026_07_03.yaml`
"prompt_loadouts_scope"): **measure ALL 8 nuclei, but only N07 is fill-eligible this cycle** --
every other nucleus's cells (including N00, the archetype baseline) are measure-only in this doc.

Composite severity per cell = the equal-weighted mean of 4 signals (each contributes 25%%,
deliberately simple/auditable, not tuned toward any nucleus's rank):

%s

`severity = 0.25 * (s1 + s2 + s3 + s4)`, each si in [0, 1], 1 = maximal gap for that signal.

## 2. N05 Cybersec Exemption (explicit, never silent)

`N05_operations/cybersec/` and `N05_operations/cybersec_distilled/` are an externally-derived
research corpus (**%d files exempted** this run) living as a sibling top-level directory to
N05_operations' 12 pillar dirs -- not organized into the pillar fractal at all, and therefore
never counted in any nucleus x pillar cell above. This is a documented decision
(`N05_CYBERSEC_EXEMPT_PREFIXES` in `_tools/cex_check_registry.py`), not a silent byproduct of
the path-matching regex -- see spec Sec 3.2 signal 4.

## 3. Sanity Check (R-167 reproduction)

| Check | Result |
|---|---|
| Thinnest operational nucleus (by total raw file count) | **%s** |
| N07 is the thinnest operational nucleus | **%s** |
| N07 cells among the top-10 ranked by the s2 (file-count unevenness) signal alone | **%d / 10** |

Operational nucleus totals (raw file count, all 12 pillars): %s

## 4. Raw File-Count Grid (nucleus x pillar, DIAGNOSTICO-style)

%s

## 5. Ranked Gap Table (worst cell first, composite severity)

%s

## 6. Wave-Fill Shortlist (N07-only this cycle, READ-ONLY recommendations)

Per GDP Q3, only N07 is fill-eligible this cycle -- the cells below are the TOP-RANKED N07
cells with a peer-pillar `kind` pattern pulled from the SAME total index (which kinds populate
this pillar across the other 6 operational nuclei). These are candidate POINTERS for a future
fill wave, **not** verified >=2x-real-usage exemplars in the R-167 sense -- that verification
(scanning N07's own dispatch/handoff corpus for something already reused twice) is Wave 3 fill
work, out of scope for this measure-only pass.

%s

## 7. How to Refresh

```
python _tools/cex_total_index.py --rebuild-if-stale   # keep the index fresh first
python _tools/cex_hydration_doctor.py --audit          # regenerate this file
```

## Related Artifacts

| Artifact | Relationship |
|----------|---------------|
| `docs/SPEC_CEXAI_TOTAL_HYDRATION_INDEX_2026_07_03.md` | spec (Sec 3.2 STREAM B + Sec 4.1 WAVE 3) |
| `docs/DIAGNOSTICO_COBERTURA_CEXAI_2026_07_03.md` | predecessor (hand-made, one-time) |
| `docs/PROJECT_BACKLOG.md` | R-167 (origin method), R-249/R-250 (this generator) |
| `_tools/cex_check_registry.py` | hydration_doctor plugin (the one implementation) |
| `_tools/cex_total_index.py` | L1 document index this reads (never rescans the corpus) |
""" % (
        report.get("index_built_at") or "unknown",
        signal_doc_lines,
        cyber["files_skipped"],
        sanity["thinnest_operational_nucleus"], sanity["n07_is_thinnest"],
        sanity["n07_cells_in_top10_s2"],
        report["operational_totals"],
        _render_grid_table(cells),
        _render_ranked_table(cells),
        _render_shortlist(report["wave_fill_shortlist"]),
    )

    return frontmatter + body


def write_hydration_map(report: dict, out_path: Optional[Path] = None) -> str:
    out_path = out_path or MAP_PATH
    text = render_hydration_map(report)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(text, encoding="utf-8")
    return text


def cmd_audit(out_path: Optional[Path] = None, top: int = 10) -> int:
    report = ccr.compute_hydration_report(ROOT)
    if not report.get("available"):
        print("[FAIL] %s" % report.get("reason"))
        return 1

    write_hydration_map(report, out_path)
    dest = out_path or MAP_PATH
    print("[OK] wrote %s" % dest)
    print("Top %d worst cells (nucleus/pillar/severity):" % top)
    for c in report["cells"][:top]:
        print(
            "  %s/%s severity=%.4f (files=%d vs pillar-median=%.1f) "
            "s1=%.3f s2=%.3f s3=%.3f s4=%.3f"
            % (
                c["nucleus"], c["pillar"], c["severity"], c["file_count"], c["pillar_median"],
                c["s1_density_gap"], c["s2_uneven"], c["s3_stub"], c["s4_coord_gap"],
            )
        )
    sanity = report["sanity"]
    print(
        "Sanity: thinnest operational nucleus=%s (N07=%s), N07 cells in top10 s2=%d/10"
        % (sanity["thinnest_operational_nucleus"], sanity["n07_is_thinnest"],
           sanity["n07_cells_in_top10_s2"])
    )
    return 0


def main(argv: Optional[list] = None) -> int:
    ap = argparse.ArgumentParser(description="CEX Hydration Doctor -- R-249/R-250 (measurement only)")
    ap.add_argument("--audit", action="store_true",
                     help="Compute the hydration report, write docs/HYDRATION_MAP.md, print top-N")
    ap.add_argument("--top", type=int, default=10, help="How many worst cells to print (default: 10)")
    ap.add_argument("--out", default=None, help="Override output path (mainly for tests)")
    args = ap.parse_args(argv)

    if args.audit:
        out_path = Path(args.out) if args.out else None
        return cmd_audit(out_path=out_path, top=args.top)

    ap.print_help()
    return 2


if __name__ == "__main__":
    sys.exit(main())
