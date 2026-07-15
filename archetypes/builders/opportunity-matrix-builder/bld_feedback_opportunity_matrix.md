---
quality: null
id: p11_fb_opportunity_matrix
kind: builder_default
pillar: P11
title: "Feedback: Opportunity Matrix"
domain: opportunity_matrix
version: 1.1.0
tags: [feedback, anti-patterns, P11, opportunity_matrix]
8f: "F7_govern"
keywords: [opportunity matrix, never rules, failure modes, correction protocol, feedback, anti-patterns, opportunity_matrix, common failure modes, sourcing_confiavel, honest-null]
tldr: "Anti-patterns and correction protocol for opportunity matrix builders. 6 NEVER rules + 4 failure modes + 4-step correction."
author: builder
llm_function: GOVERN
density_score: 0.88
created: "2026-07-02"
updated: "2026-07-02"
related:
  - p11_qg_opportunity_matrix
  - bld_instruction_opportunity_matrix
  - opportunity-matrix-builder
  - p11_fb_roi_calculator
  - p08_adr_opportunity_matrix_kind
---
# Feedback: Opportunity Matrix

## Anti-Patterns (NEVER do)
| Rule | Violation | Gate |
|------|-----------|------|
| No self-score | Never assign quality score to own output | H01 |
| No hallucination | Cite sources; no invented facts, metrics, refs | H03 |
| ASCII-only code | No emoji, no accented chars in .py/.ps1/.sh | H04 |
| No partial output | Complete artifact; no truncation, no "..." | H05 |
| No fabricated market data | Never show a sell price/demand level as real when offline/blocked -- honest-null only | H07 |
| No EAN/GTIN join key | Never use ean/gtin/barcode as the cross-marketplace join key | H08 |

## Common Failure Modes
| Failure Mode | Signal | Fix |
|-------------|--------|-----|
| Section drift | Section count != 8, or titles/order differ from MOLD_SOURCING_OPPORTUNITY | Re-read bld_output ISO; restore frozen shape |
| Table cell mismatch | A table row has more/fewer cells than its columns array | Re-count against the frozen column list per section |
| Silent drop of uncovered rows | Cauda-longa / manual-bucket counts missing from Cobertura | Surface every parsed row somewhere (priced, manual, or long-tail) |
| Gate stated without conditions | "sourcing_confiavel: true" with no boolean conditions shown | Add the 4-condition string + an evaluation line (S4) |

## Correction Protocol
| Step | Action | Gate |
|------|--------|------|
| 1 | Identify which H01-H08 gate failed | F7 |
| 2 | Return to F6 PRODUCE with explicit fix instruction | F6 |
| 3 | Re-run F7 GOVERN | F7 |
| 4 | Max 2 retries before escalating to N07 | F8 |

## Key Behaviors
- Builder MUST load all 12 ISOs (1:1 with pillars) before producing any artifact
- Builder MUST run F7 GOVERN quality gate before saving output
- Builder MUST compile output via cex_compile.py after saving (F8 COLLABORATE)
- Builder MUST signal completion with quality score to N07 orchestrator
- Builder MUST NOT self-score: quality field is always null in own output
## Quality Thresholds

| Dimension | Weight | Target | Gate |
|-----------|--------|--------|------|
| Structural completeness | 30% | >= 8.0 | L1 |
| Rubric compliance | 30% | >= 8.0 | L2 |
| Semantic coherence | 40% | >= 8.5 | L3 |
| Density score | -- | >= 0.85 | S09 |
| Tables present | -- | >= 1 | S05 |

## Gate Check

```bash
python _tools/cex_score.py {FILE} --layer structural
python _tools/cex_score.py {FILE} --layer rubric
```

```yaml
# Expected output structure
structural: 8.5+
rubric: 7.5+
average: 8.0+
gates_passed: 8/8
density: 0.85+
```

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[p11_qg_opportunity_matrix]] | sibling | 0.82 |
| [[bld_instruction_opportunity_matrix]] | sibling | 0.75 |
| [[opportunity-matrix-builder]] | sibling | 0.70 |
| [[p11_fb_roi_calculator]] | related | 0.55 |
| p08_adr_opportunity_matrix_kind | upstream | 0.40 |
