---
id: hydration_map
kind: context_doc
pillar: P08
nucleus: n07
version: 1.0.0
quality: null
tags: [hydration, gap-map, generated, R-249, R-250]
generated_by: _tools/cex_hydration_doctor.py --audit
generated_at: "2026-07-15T18:21:16.068802+00:00"
index_built_at: "2026-07-15T18:21:14.822292+00:00"
---

# CEXAI Hydration Map -- Per-Nucleus x Per-Pillar Gap Measurement

> Generated successor to the one-time `docs/DIAGNOSTICO_COBERTURA_CEXAI_2026_07_03.md` table.
> This file is REGENERATED, not hand-maintained -- run `python _tools/cex_hydration_doctor.py
> --audit` to refresh it. Source: `_tools/cex_check_registry.py`'s `hydration_doctor` plugin
> (R-249/R-250), reading `.cex/total_index/l1_documents.json` (built_at: 2026-07-15T18:21:14.822292+00:00) plus one targeted
> read pass over the paths that index already places inside a canonical N00-N07 nucleus/pillar
> directory (never a rescan of the full tracked corpus).

## 1. Scope + Method

Generalizes R-167's proven method (disk-audit -> rank uneven cells -> promote from a REAL
>=2x-usage exemplar, never mass-synthesize) from 1 pillar (P03) / 1 nucleus (N07) to the full
12-pillar x 7-operational-nucleus grid. Per GDP Q3 (closed 2026-07-03,
`.cex/runtime/decisions/decision_manifest_total_hydration_2026_07_03.yaml`
"prompt_loadouts_scope"): **measure ALL 8 nuclei, but only N07 is fill-eligible this cycle** --
every other nucleus's cells (including N00, the archetype baseline) are measure-only in this doc.

Composite severity per cell = the equal-weighted mean of 4 signals (each contributes 25%,
deliberately simple/auditable, not tuned toward any nucleus's rank):

- **s1 density-measurement coverage gap** (`s1_density_gap`): share of this cell's TYPED artifacts with no density_score at all (numeric, non-null). Unmeasured != thin -- an empty cell scores 0.0 here (that gap is s2's job).
- **s2 file-count unevenness** (`s2_uneven`): how far this cell's raw file count sits BELOW the cross-nucleus median for that pillar (computed over the 7 OPERATIONAL nuclei only -- N00 the archetype baseline is excluded from the median, generalizing R-167's own N01-N07 comparison).
- **s3 stub markers** (`s3_stub`): share of this cell's files (typed + governance) carrying an unintentional [preencher] and/or bare-word TODO marker.
- **s4 coordinate coverage gap** (`s4_coord_gap`): share of this cell's TYPED artifacts missing EITHER an 8f: or a related: frontmatter field (both required to count as coordinate-complete).

`severity = 0.25 * (s1 + s2 + s3 + s4)`, each si in [0, 1], 1 = maximal gap for that signal.

## 2. N05 Cybersec Exemption (explicit, never silent)

`N05_operations/cybersec/` and `N05_operations/cybersec_distilled/` are an externally-derived
research corpus (**0 files exempted** this run) living as a sibling top-level directory to
N05_operations' 12 pillar dirs -- not organized into the pillar fractal at all, and therefore
never counted in any nucleus x pillar cell above. This is a documented decision
(`N05_CYBERSEC_EXEMPT_PREFIXES` in `_tools/cex_check_registry.py`), not a silent byproduct of
the path-matching regex -- see spec Sec 3.2 signal 4.

## 3. Sanity Check (R-167 reproduction)

| Check | Result |
|---|---|
| Thinnest operational nucleus (by total raw file count) | **N07** |
| N07 is the thinnest operational nucleus | **True** |
| N07 cells among the top-10 ranked by the s2 (file-count unevenness) signal alone | **2 / 10** |

Operational nucleus totals (raw file count, all 12 pillars): {'N01': 73, 'N02': 34, 'N03': 21, 'N04': 80, 'N05': 22, 'N06': 36, 'N07': 15}

## 4. Raw File-Count Grid (nucleus x pillar, DIAGNOSTICO-style)

| Nucleus | P01 | P02 | P03 | P04 | P05 | P06 | P07 | P08 | P09 | P10 | P11 | P12 | Total |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| N00 (archetype baseline) | 117 | 1 | 1 | 0 | 0 | 0 | 0 | 1 | 0 | 1 | 0 | 0 | 121 |
| N01 | 70 | 1 | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 1 | 0 | 0 | 73 |
| N02 | 32 | 1 | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 34 |
| N03 | 18 | 1 | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 1 | 0 | 0 | 21 |
| N04 | 77 | 1 | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 1 | 0 | 0 | 80 |
| N05 | 19 | 1 | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 1 | 0 | 0 | 22 |
| N06 | 33 | 1 | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 1 | 0 | 0 | 36 |
| N07 | 9 | 1 | 4 | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 15 |

## 5. Ranked Gap Table (worst cell first, composite severity)

| Rank | Nucleus | Pillar | Severity | Files | Peer Median | s1 (density) | s2 (uneven) | s3 (stub) | s4 (coord) | Fill-eligible |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | N04 | P02 | 0.5000 | 1 | 1.0 | 100.0% | 0.0% | 0.0% | 100.0% | measure-only |
| 2 | N00 | P10 | 0.2500 | 1 | 1.0 | 100.0% | 0.0% | 0.0% | 0.0% | archetype -- measure-only |
| 3 | N01 | P02 | 0.2500 | 1 | 1.0 | 0.0% | 0.0% | 0.0% | 100.0% | measure-only |
| 4 | N01 | P10 | 0.2500 | 1 | 1.0 | 100.0% | 0.0% | 0.0% | 0.0% | measure-only |
| 5 | N02 | P10 | 0.2500 | 0 | 1.0 | 0.0% | 100.0% | 0.0% | 0.0% | measure-only |
| 6 | N03 | P02 | 0.2500 | 1 | 1.0 | 0.0% | 0.0% | 0.0% | 100.0% | measure-only |
| 7 | N03 | P10 | 0.2500 | 1 | 1.0 | 100.0% | 0.0% | 0.0% | 0.0% | measure-only |
| 8 | N04 | P08 | 0.2500 | 1 | 1.0 | 100.0% | 0.0% | 0.0% | 0.0% | measure-only |
| 9 | N04 | P10 | 0.2500 | 1 | 1.0 | 100.0% | 0.0% | 0.0% | 0.0% | measure-only |
| 10 | N05 | P02 | 0.2500 | 1 | 1.0 | 0.0% | 0.0% | 0.0% | 100.0% | measure-only |
| 11 | N05 | P10 | 0.2500 | 1 | 1.0 | 100.0% | 0.0% | 0.0% | 0.0% | measure-only |
| 12 | N06 | P02 | 0.2500 | 1 | 1.0 | 0.0% | 0.0% | 0.0% | 100.0% | measure-only |
| 13 | N07 | P10 | 0.2500 | 0 | 1.0 | 0.0% | 100.0% | 0.0% | 0.0% | N07 (this cycle) |
| 14 | N07 | P01 | 0.2352 | 9 | 32.0 | 22.2% | 71.9% | 0.0% | 0.0% | N07 (this cycle) |
| 15 | N05 | P01 | 0.2331 | 19 | 32.0 | 52.6% | 40.6% | 0.0% | 0.0% | measure-only |
| 16 | N04 | P01 | 0.2175 | 77 | 32.0 | 49.4% | 0.0% | 0.0% | 37.7% | measure-only |
| 17 | N03 | P01 | 0.1788 | 18 | 32.0 | 16.7% | 43.8% | 0.0% | 11.1% | measure-only |
| 18 | N01 | P01 | 0.1544 | 70 | 32.0 | 50.0% | 0.0% | 0.0% | 11.8% | measure-only |
| 19 | N00 | P01 | 0.1175 | 117 | 32.0 | 46.2% | 0.0% | 0.0% | 0.9% | archetype -- measure-only |
| 20 | N06 | P01 | 0.0682 | 33 | 32.0 | 21.2% | 0.0% | 0.0% | 6.1% | measure-only |
| 21 | N02 | P01 | 0.0625 | 32 | 32.0 | 15.6% | 0.0% | 0.0% | 9.4% | measure-only |
| 22 | N00 | P02 | 0.0000 | 1 | 1.0 | 0.0% | 0.0% | 0.0% | 0.0% | archetype -- measure-only |
| 23 | N00 | P03 | 0.0000 | 1 | 0.0 | 0.0% | 0.0% | 0.0% | 0.0% | archetype -- measure-only |
| 24 | N00 | P04 | 0.0000 | 0 | 0.0 | 0.0% | 0.0% | 0.0% | 0.0% | archetype -- measure-only |
| 25 | N00 | P05 | 0.0000 | 0 | 0.0 | 0.0% | 0.0% | 0.0% | 0.0% | archetype -- measure-only |
| 26 | N00 | P06 | 0.0000 | 0 | 0.0 | 0.0% | 0.0% | 0.0% | 0.0% | archetype -- measure-only |
| 27 | N00 | P07 | 0.0000 | 0 | 0.0 | 0.0% | 0.0% | 0.0% | 0.0% | archetype -- measure-only |
| 28 | N00 | P08 | 0.0000 | 1 | 1.0 | 0.0% | 0.0% | 0.0% | 0.0% | archetype -- measure-only |
| 29 | N00 | P09 | 0.0000 | 0 | 0.0 | 0.0% | 0.0% | 0.0% | 0.0% | archetype -- measure-only |
| 30 | N00 | P11 | 0.0000 | 0 | 0.0 | 0.0% | 0.0% | 0.0% | 0.0% | archetype -- measure-only |
| 31 | N00 | P12 | 0.0000 | 0 | 0.0 | 0.0% | 0.0% | 0.0% | 0.0% | archetype -- measure-only |
| 32 | N01 | P03 | 0.0000 | 0 | 0.0 | 0.0% | 0.0% | 0.0% | 0.0% | measure-only |
| 33 | N01 | P04 | 0.0000 | 0 | 0.0 | 0.0% | 0.0% | 0.0% | 0.0% | measure-only |
| 34 | N01 | P05 | 0.0000 | 0 | 0.0 | 0.0% | 0.0% | 0.0% | 0.0% | measure-only |
| 35 | N01 | P06 | 0.0000 | 0 | 0.0 | 0.0% | 0.0% | 0.0% | 0.0% | measure-only |
| 36 | N01 | P07 | 0.0000 | 0 | 0.0 | 0.0% | 0.0% | 0.0% | 0.0% | measure-only |
| 37 | N01 | P08 | 0.0000 | 1 | 1.0 | 0.0% | 0.0% | 0.0% | 0.0% | measure-only |
| 38 | N01 | P09 | 0.0000 | 0 | 0.0 | 0.0% | 0.0% | 0.0% | 0.0% | measure-only |
| 39 | N01 | P11 | 0.0000 | 0 | 0.0 | 0.0% | 0.0% | 0.0% | 0.0% | measure-only |
| 40 | N01 | P12 | 0.0000 | 0 | 0.0 | 0.0% | 0.0% | 0.0% | 0.0% | measure-only |
| 41 | N02 | P02 | 0.0000 | 1 | 1.0 | 0.0% | 0.0% | 0.0% | 0.0% | measure-only |
| 42 | N02 | P03 | 0.0000 | 0 | 0.0 | 0.0% | 0.0% | 0.0% | 0.0% | measure-only |
| 43 | N02 | P04 | 0.0000 | 0 | 0.0 | 0.0% | 0.0% | 0.0% | 0.0% | measure-only |
| 44 | N02 | P05 | 0.0000 | 0 | 0.0 | 0.0% | 0.0% | 0.0% | 0.0% | measure-only |
| 45 | N02 | P06 | 0.0000 | 0 | 0.0 | 0.0% | 0.0% | 0.0% | 0.0% | measure-only |
| 46 | N02 | P07 | 0.0000 | 0 | 0.0 | 0.0% | 0.0% | 0.0% | 0.0% | measure-only |
| 47 | N02 | P08 | 0.0000 | 1 | 1.0 | 0.0% | 0.0% | 0.0% | 0.0% | measure-only |
| 48 | N02 | P09 | 0.0000 | 0 | 0.0 | 0.0% | 0.0% | 0.0% | 0.0% | measure-only |
| 49 | N02 | P11 | 0.0000 | 0 | 0.0 | 0.0% | 0.0% | 0.0% | 0.0% | measure-only |
| 50 | N02 | P12 | 0.0000 | 0 | 0.0 | 0.0% | 0.0% | 0.0% | 0.0% | measure-only |
| 51 | N03 | P03 | 0.0000 | 0 | 0.0 | 0.0% | 0.0% | 0.0% | 0.0% | measure-only |
| 52 | N03 | P04 | 0.0000 | 0 | 0.0 | 0.0% | 0.0% | 0.0% | 0.0% | measure-only |
| 53 | N03 | P05 | 0.0000 | 0 | 0.0 | 0.0% | 0.0% | 0.0% | 0.0% | measure-only |
| 54 | N03 | P06 | 0.0000 | 0 | 0.0 | 0.0% | 0.0% | 0.0% | 0.0% | measure-only |
| 55 | N03 | P07 | 0.0000 | 0 | 0.0 | 0.0% | 0.0% | 0.0% | 0.0% | measure-only |
| 56 | N03 | P08 | 0.0000 | 1 | 1.0 | 0.0% | 0.0% | 0.0% | 0.0% | measure-only |
| 57 | N03 | P09 | 0.0000 | 0 | 0.0 | 0.0% | 0.0% | 0.0% | 0.0% | measure-only |
| 58 | N03 | P11 | 0.0000 | 0 | 0.0 | 0.0% | 0.0% | 0.0% | 0.0% | measure-only |
| 59 | N03 | P12 | 0.0000 | 0 | 0.0 | 0.0% | 0.0% | 0.0% | 0.0% | measure-only |
| 60 | N04 | P03 | 0.0000 | 0 | 0.0 | 0.0% | 0.0% | 0.0% | 0.0% | measure-only |
| 61 | N04 | P04 | 0.0000 | 0 | 0.0 | 0.0% | 0.0% | 0.0% | 0.0% | measure-only |
| 62 | N04 | P05 | 0.0000 | 0 | 0.0 | 0.0% | 0.0% | 0.0% | 0.0% | measure-only |
| 63 | N04 | P06 | 0.0000 | 0 | 0.0 | 0.0% | 0.0% | 0.0% | 0.0% | measure-only |
| 64 | N04 | P07 | 0.0000 | 0 | 0.0 | 0.0% | 0.0% | 0.0% | 0.0% | measure-only |
| 65 | N04 | P09 | 0.0000 | 0 | 0.0 | 0.0% | 0.0% | 0.0% | 0.0% | measure-only |
| 66 | N04 | P11 | 0.0000 | 0 | 0.0 | 0.0% | 0.0% | 0.0% | 0.0% | measure-only |
| 67 | N04 | P12 | 0.0000 | 0 | 0.0 | 0.0% | 0.0% | 0.0% | 0.0% | measure-only |
| 68 | N05 | P03 | 0.0000 | 0 | 0.0 | 0.0% | 0.0% | 0.0% | 0.0% | measure-only |
| 69 | N05 | P04 | 0.0000 | 0 | 0.0 | 0.0% | 0.0% | 0.0% | 0.0% | measure-only |
| 70 | N05 | P05 | 0.0000 | 0 | 0.0 | 0.0% | 0.0% | 0.0% | 0.0% | measure-only |
| 71 | N05 | P06 | 0.0000 | 0 | 0.0 | 0.0% | 0.0% | 0.0% | 0.0% | measure-only |
| 72 | N05 | P07 | 0.0000 | 0 | 0.0 | 0.0% | 0.0% | 0.0% | 0.0% | measure-only |
| 73 | N05 | P08 | 0.0000 | 1 | 1.0 | 0.0% | 0.0% | 0.0% | 0.0% | measure-only |
| 74 | N05 | P09 | 0.0000 | 0 | 0.0 | 0.0% | 0.0% | 0.0% | 0.0% | measure-only |
| 75 | N05 | P11 | 0.0000 | 0 | 0.0 | 0.0% | 0.0% | 0.0% | 0.0% | measure-only |
| 76 | N05 | P12 | 0.0000 | 0 | 0.0 | 0.0% | 0.0% | 0.0% | 0.0% | measure-only |
| 77 | N06 | P03 | 0.0000 | 0 | 0.0 | 0.0% | 0.0% | 0.0% | 0.0% | measure-only |
| 78 | N06 | P04 | 0.0000 | 0 | 0.0 | 0.0% | 0.0% | 0.0% | 0.0% | measure-only |
| 79 | N06 | P05 | 0.0000 | 0 | 0.0 | 0.0% | 0.0% | 0.0% | 0.0% | measure-only |
| 80 | N06 | P06 | 0.0000 | 0 | 0.0 | 0.0% | 0.0% | 0.0% | 0.0% | measure-only |
| 81 | N06 | P07 | 0.0000 | 0 | 0.0 | 0.0% | 0.0% | 0.0% | 0.0% | measure-only |
| 82 | N06 | P08 | 0.0000 | 1 | 1.0 | 0.0% | 0.0% | 0.0% | 0.0% | measure-only |
| 83 | N06 | P09 | 0.0000 | 0 | 0.0 | 0.0% | 0.0% | 0.0% | 0.0% | measure-only |
| 84 | N06 | P10 | 0.0000 | 1 | 1.0 | 0.0% | 0.0% | 0.0% | 0.0% | measure-only |
| 85 | N06 | P11 | 0.0000 | 0 | 0.0 | 0.0% | 0.0% | 0.0% | 0.0% | measure-only |
| 86 | N06 | P12 | 0.0000 | 0 | 0.0 | 0.0% | 0.0% | 0.0% | 0.0% | measure-only |
| 87 | N07 | P02 | 0.0000 | 1 | 1.0 | 0.0% | 0.0% | 0.0% | 0.0% | N07 (this cycle) |
| 88 | N07 | P03 | 0.0000 | 4 | 0.0 | 0.0% | 0.0% | 0.0% | 0.0% | N07 (this cycle) |
| 89 | N07 | P04 | 0.0000 | 0 | 0.0 | 0.0% | 0.0% | 0.0% | 0.0% | N07 (this cycle) |
| 90 | N07 | P05 | 0.0000 | 0 | 0.0 | 0.0% | 0.0% | 0.0% | 0.0% | N07 (this cycle) |
| 91 | N07 | P06 | 0.0000 | 0 | 0.0 | 0.0% | 0.0% | 0.0% | 0.0% | N07 (this cycle) |
| 92 | N07 | P07 | 0.0000 | 0 | 0.0 | 0.0% | 0.0% | 0.0% | 0.0% | N07 (this cycle) |
| 93 | N07 | P08 | 0.0000 | 1 | 1.0 | 0.0% | 0.0% | 0.0% | 0.0% | N07 (this cycle) |
| 94 | N07 | P09 | 0.0000 | 0 | 0.0 | 0.0% | 0.0% | 0.0% | 0.0% | N07 (this cycle) |
| 95 | N07 | P11 | 0.0000 | 0 | 0.0 | 0.0% | 0.0% | 0.0% | 0.0% | N07 (this cycle) |
| 96 | N07 | P12 | 0.0000 | 0 | 0.0 | 0.0% | 0.0% | 0.0% | 0.0% | N07 (this cycle) |

## 6. Wave-Fill Shortlist (N07-only this cycle, READ-ONLY recommendations)

Per GDP Q3, only N07 is fill-eligible this cycle -- the cells below are the TOP-RANKED N07
cells with a peer-pillar `kind` pattern pulled from the SAME total index (which kinds populate
this pillar across the other 6 operational nuclei). These are candidate POINTERS for a future
fill wave, **not** verified >=2x-real-usage exemplars in the R-167 sense -- that verification
(scanning N07's own dispatch/handoff corpus for something already reused twice) is Wave 3 fill
work, out of scope for this measure-only pass.

- **N07/P10** -- severity 0.2500, 0 file(s) vs peer median 1.0. Peer-pillar kind pattern (index-only, NOT yet a verified >=2x-usage exemplar): procedural_memory (x5 among peers)
- **N07/P01** -- severity 0.2352, 9 file(s) vs peer median 32.0. Peer-pillar kind pattern (index-only, NOT yet a verified >=2x-usage exemplar): knowledge_card (x158 among peers), few_shot_example (x15 among peers), vector_store (x7 among peers)
- **N07/P02** -- severity 0.0000, 1 file(s) vs peer median 1.0. Peer-pillar kind pattern (index-only, NOT yet a verified >=2x-usage exemplar): nucleus_def (x6 among peers)
- **N07/P03** -- severity 0.0000, 4 file(s) vs peer median 0.0. Peer-pillar kind pattern (index-only, NOT yet a verified >=2x-usage exemplar): (no peer-kind pattern found)
- **N07/P04** -- severity 0.0000, 0 file(s) vs peer median 0.0. Peer-pillar kind pattern (index-only, NOT yet a verified >=2x-usage exemplar): (no peer-kind pattern found)

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
