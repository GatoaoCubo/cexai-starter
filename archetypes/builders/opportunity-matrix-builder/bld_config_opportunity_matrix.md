---
kind: config
id: bld_config_opportunity_matrix
pillar: P09
llm_function: CONSTRAIN
purpose: Naming, paths, limits for opportunity_matrix production
quality: null
title: "Config Opportunity Matrix"
version: "1.0.0"
author: n03_builder
tags: [opportunity_matrix, builder, config]
tldr: "Production constraints for opportunity matrix: naming (p11_om_{{name}}.md), output path P11/, size limit 5120B. Scored supplier-cost x market-demand buy-side sourcing decision."
domain: "opportunity_matrix construction"
created: "2026-07-02"
updated: "2026-07-02"
8f: "F1_constrain"
keywords: [limits for opportunity_matrix production, opportunity_matrix construction, config opportunity matrix, output paths, size limit, opportunity_matrix, builder, config, p11_om_name.md]
density_score: 0.85
related:
  - bld_config_roi_calculator
  - bld_config_scoring_rubric
  - bld_config_research_pipeline
  - p08_adr_opportunity_matrix_kind
  - opportunity-matrix-builder
---
## Naming Convention
Pattern: `p11_om_{{name}}.md`
Examples: `p11_om_ferramentas_q3.md`, `p11_om_hardware_catalog_2026.md`

## Paths
Artifacts: `N06_commercial/P11_feedback/p11_om_{{name}}.md` (pillar+nucleus convention; no instance yet on disk -- this kind is newly registered)
Logs: `.cex/runtime/logs/opportunity_matrix/{{name}}/`

## Limits
max_bytes: 5120
max_turns: 10
effort_level: medium

## Hooks
pre_build: null
post_build: null
on_error: null
on_quality_fail: null

## Domain-Specific Constraints
| Constraint | Value |
|-----------|-------|
| Boundary | Scored supplier-cost x market-demand join for buy/sourcing decisions (inbound twin of marketplace_listing). NOT competitive_matrix nor roi_calculator. |
| Dependencies | roi_calculator, research_pipeline, scoring_rubric |
| Primary 8F function | F4_reason |
| Max artifact size | 5120 bytes |
| requires_external_context | true (web demand research) |
| requires_live_tools | false |
| f7_enforce | true |

## Edge Cases
| Scenario | Handling |
|----------|----------|
| Missing required frontmatter field | Fail H01 gate; return to F6 |
| catalog_sources empty/invalid | Generator emits empty matrix + note "catalog_sources vazio ou invalido"; score -0.3 |
| No credential / no demand_sources | Offline path: every market/demand cell honest-null; score -0.25 |
| data_window_days > 365 | Freshness band RED; note "dado muito antigo"; score -0.15 |
| ID collision with existing artifact | Append version suffix (_v2) |
| Body exceeds 5120 bytes | Trim prose sections; preserve tables |

## Properties
| Property | Value |
|----------|-------|
| Kind | `config` |
| Pillar | P09 |
| Domain | opportunity matrix construction |
| Pipeline | 8F (F1-F8) |
| Scorer | cex_score.py |
| Compiler | cex_compile.py |
| Retriever | cex_retriever.py |
| Quality target | 9.0+ |
| Density target | 0.85+ |

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[bld_config_roi_calculator]] | sibling | 0.51 |
| [[bld_config_scoring_rubric]] | sibling | 0.44 |
| [[bld_config_research_pipeline]] | sibling | 0.42 |
| p08_adr_opportunity_matrix_kind | upstream | 0.40 |
| [[opportunity-matrix-builder]] | related | 0.38 |
