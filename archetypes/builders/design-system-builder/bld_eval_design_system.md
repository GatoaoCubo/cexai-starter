---
id: bld_eval_design_system
kind: quality_gate
pillar: P06
llm_function: GOVERN
8f: F7_govern
version: 1.0.0
created: "2026-06-15"
updated: "2026-06-15"
author: n03_builder
title: "Gate: design_system"
domain: design_system
quality: null
tags: [design_system, builder, eval, quality_gate, P06]
tldr: "HARD + SOFT gates for design_system: token completeness, single-signal, contrast floor, reduce-motion, and a present leverage block."
density_score: 0.9
related:
  - bld_schema_design_system
  - p06_vs_design_system
  - bld_output_design_system
  - p06_ds_ferro
  - p01_kc_design_system
---

# Gate: design_system
## HARD gates (any FAIL -> REJECT, no score)
| ID | Check | Rule |
|----|-------|------|
| H01 | Frontmatter parses | valid YAML, complete |
| H02 | id pattern | `^p06_ds_[a-z][a-z0-9_]+$`, equals filename stem |
| H03 | kind literal | `kind` is exactly `design_system` |
| H04 | quality null | `quality` is null |
| H05 | five token groups | color, type, space, motion, form all present |
| H06 | leverage present | `leverage.feeds_kinds` non-empty (active asset) |
## SOFT scoring (0 or 10 x weight)
| Dimension | Weight | Pass condition |
|-----------|--------|----------------|
| Single signal | 1.0 | exactly one accent role |
| Contrast floor | 1.0 | ink-on-canvas and signal_ink-on-signal >= 4.5:1 |
| Reduce-motion | 1.0 | every move collapses to dur.instant |
| Four recipes | 1.0 | surface/control/field/marker from slots only |
| Distinct coordinate | 0.5 | not a sibling of an existing system |
| Clean-room | 1.0 | original name + values; no copied system |
| Density mode set | 0.5 | comfortable or compact declared |
Sum weights 6.0; `soft = sum(weight*score)/6.0*10`.
## Actions
| Score | Action |
|-------|--------|
| >= 9.5 | GOLDEN -- canonical library entry |
| >= 8.0 | PUBLISH |
| >= 7.0 | REVISE -- coordinate or contrast needs work |
| < 7.0 | REJECT |
## Golden vs Anti
- GOLDEN: p06_ds_ferro -- five groups, one teal signal, ~15:1 ink contrast, snap motion, leverage declared.
- ANTI: two competing accents; spring under reduce-motion; copied palette; missing leverage.
## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[bld_schema_design_system]] | upstream | 0.55 |
| p06_vs_design_system | upstream | 0.5 |
| [[bld_output_design_system]] | sibling | 0.42 |
| p06_ds_ferro | example | 0.42 |
| [[kc_design_system]] | related | 0.4 |
