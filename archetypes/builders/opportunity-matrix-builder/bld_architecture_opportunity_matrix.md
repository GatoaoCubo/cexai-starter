---
kind: architecture
id: bld_architecture_opportunity_matrix
pillar: P08
llm_function: CONSTRAIN
purpose: Component map of opportunity_matrix -- inventory, dependencies
quality: null
title: "Architecture Opportunity Matrix"
version: "1.0.0"
author: n03_builder
tags: [opportunity_matrix, builder, architecture]
tldr: "Component map of opportunity_matrix -- inventory, dependencies"
domain: "opportunity_matrix construction"
created: "2026-07-02"
updated: "2026-07-02"
8f: "F1_constrain"
keywords: [opportunity_matrix construction, architecture opportunity matrix, opportunity_matrix, builder, architecture, component inventory, architectural position, sourcing_opportunity generator, canonical_product seam]
density_score: 0.85
related:
  - bld_architecture_roi_calculator
  - roi-calculator-builder
  - research-pipeline-builder
  - scoring-rubric-builder
---
## Component Inventory
| ISO Name | Role | Pillar | Status |
|----------|------|--------|--------|
| bld_manifest (bld_model) | Builder configuration + identity | P11 | Active |
| bld_instruction (bld_prompt) | Task execution guidelines | P03 | Active |
| bld_schema | Data structure definition | P06 | Active |
| bld_quality_gate (bld_eval) | Validation rules | P11 | Active |
| bld_output_template (bld_output) | Result formatting | P05 | Active |
| bld_knowledge_card (bld_knowledge) | Domain-specific knowledge | P01 | Active |
| bld_architecture | Builder system design | P08 | Active |
| bld_collaboration (bld_orchestration) | Multi-builder coordination | P12 | Active |
| bld_config | Runtime parameter management | P09 | Active |
| bld_memory | State retention mechanism | P10 | Active |
| bld_tools | Utility functions | P04 | Active |
| bld_feedback | Anti-patterns + correction protocol | P11 | Active |

## Dependencies
| From | To | Type |
|------|-----|------|
| opportunity_matrix (this kind) | roi_calculator | Composition (per-item margin primitive) |
| opportunity_matrix (this kind) | research_pipeline | Composition (demand research, S1-S5) |
| opportunity_matrix (this kind) | scoring_rubric | Composition (rank criteria) |
| opportunity_matrix (this kind) | product_match | Sibling (shares Section 6 match/audit engine, soft-imported) |
| bld_instruction | bld_schema | Execution (fields feed the schema) |
| bld_quality_gate | bld_output_template | Validation (section shape checked against template) |

## Architectural Position
`opportunity_matrix` operates within CEX Pillar P11 (feedback / decision economics) as the buy-side sourcing decision artifact -- the inbound twin of `marketplace_listing` (P05, outbound/TUDAO). Per `p08_adr_opportunity_matrix_kind` (ACCEPTED 2026-06-25), it is a leaf kind that exists because the capability-generator framework is 1-generator-per-KIND: `competitive_matrix` was already occupied, forcing a dedicated registrable slot. The kind does NOT own the sourcing pipeline (a `pipeline_template` instance composes `research_pipeline` + `roi_calculator` + `scoring_rubric` around it); it is only the typed OUTPUT the composing pipeline and the real generator (`_tools/capability_generators/sourcing_opportunity.py`, capability slug `sourcing_opportunity`, wired N06/P11/analyze in `_tools/cex_run_capability.py`) both target. The two sourcing kinds (`opportunity_matrix` + `product_match`) meet the outbound `marketplace_listing` mold at exactly one seam: the `canonical_product` record.

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| p08_adr_opportunity_matrix_kind | upstream | 0.60 |
| [[bld_architecture_roi_calculator]] | sibling | 0.55 |
| [[roi-calculator-builder]] | related | 0.45 |
| [[research-pipeline-builder]] | related | 0.40 |
| [[scoring-rubric-builder]] | related | 0.38 |
