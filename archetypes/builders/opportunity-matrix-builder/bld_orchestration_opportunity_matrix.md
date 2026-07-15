---
kind: collaboration
id: bld_collaboration_opportunity_matrix
pillar: P12
llm_function: COLLABORATE
purpose: How opportunity-matrix-builder works in crews with other builders
quality: null
title: "Collaboration Opportunity Matrix"
version: "1.0.0"
author: n03_builder
tags: [opportunity_matrix, builder, collaboration]
tldr: "How opportunity-matrix-builder works in crews with other builders"
domain: "opportunity_matrix construction"
created: "2026-07-02"
updated: "2026-07-02"
8f: "F8_collaborate"
keywords: [opportunity_matrix construction, collaboration opportunity matrix, opportunity_matrix, builder, collaboration, crew role, receives from, produces for, boundary, canonical_product]
density_score: 0.85
related:
  - opportunity-matrix-builder
  - bld_config_opportunity_matrix
  - p08_adr_opportunity_matrix_kind
  - bld_instruction_opportunity_matrix
  - roi-calculator-builder
---
## Crew Role
Authors the ranked cost x demand opportunity artifact from parsed supplier-catalog cost rows and market demand signals. Translates raw catalog + demand data into an actionable, gated buy/no-buy ranking.

## Receives From
| Builder | What | Format |
|---------|------|--------|
| research-pipeline-builder | Market demand/price signal per product_type (S1-S5 rigor) | structured data_sources map |
| roi-calculator-builder | Per-item margin primitive (cost -> ROI math reference) | roi_calculator artifact |
| scoring-rubric-builder | Rank/weighting criteria for opp_score | scoring_rubric artifact |

## Produces For
| Builder | What | Format |
|---------|------|--------|
| marketplace_listing (TUDAO) mold | GO items on a passing sourcing_confiavel gate | canonical_product-keyed list |
| pipeline_template (p11_om_sourcing_opportunity recipe) | The final typed section of the composed sourcing pipeline | opportunity_matrix artifact |
| N06 dashboard (sourcing_opportunity capability card) | The 8-section structured_output rendered in the dashboard | StructuredOutput JSON |

## Boundary
Does NOT run the sourcing pipeline itself (parse + research + join/score is the composing `pipeline_template`'s job, per ADR driver a -- "compose, don't invent"). Does NOT perform visual product matching or record-linkage (that is `product_match`, P04/N03 -- Section 6 only surfaces its result, sharing the join-key contract via `match_join_keys`/`match_exclude_keys`).

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[opportunity-matrix-builder]] | upstream | 0.35 |
| [[bld_config_opportunity_matrix]] | upstream | 0.30 |
| p08_adr_opportunity_matrix_kind | upstream | 0.28 |
| [[bld_instruction_opportunity_matrix]] | upstream | 0.26 |
| [[roi-calculator-builder]] | related | 0.24 |
