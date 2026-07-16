---
kind: architecture
id: bld_architecture_safety_hazard_taxonomy
pillar: P08
llm_function: CONSTRAIN
purpose: Component map of safety_hazard_taxonomy -- inventory, dependencies
quality: null
title: "Architecture Safety Hazard Taxonomy"
version: "1.0.0"
author: n01_wave7
tags: [safety_hazard_taxonomy, builder, architecture, MLCommons, AILuminate, Llama-Guard]
tldr: "Component map of safety_hazard_taxonomy -- inventory, dependencies"
domain: "safety_hazard_taxonomy construction"
created: "2026-04-14"
updated: "2026-04-14"
8f: "F1_constrain"
keywords: [safety_hazard_taxonomy construction, architecture safety hazard taxonomy, safety_hazard_taxonomy, builder, architecture, mlcommons, ailuminate, llama-guard, component inventory, architectural position]
density_score: 0.85
related:
  - bld_architecture_app_directory_entry
  - bld_architecture_legal_vertical
  - bld_architecture_roi_calculator
  - bld_architecture_code_of_conduct
  - bld_architecture_api_reference
---

## Component Inventory
| ISO Name | Role | Pillar | Status |
|----------|------|--------|--------|
| bld_manifest | Builder identity and routing | P11 | Active |
| bld_instruction | Taxonomy production process | P03 | Active |
| bld_system_prompt | LLM persona for safety classification | P03 | Active |
| bld_schema | Taxonomy schema and required fields | P06 | Active |
| bld_quality_gate | Taxonomy completeness gates | P11 | Active |
| bld_output_template | Per-category hazard template | P05 | Active |
| bld_examples | Golden taxonomy + anti-examples | P07 | Active |
| bld_knowledge_card | MLCommons AILuminate domain knowledge | P01 | Active |
| bld_architecture | Component map and dependencies | P08 | Active |
| bld_collaboration | Cross-builder workflow | P12 | Active |
| bld_config | Naming, paths, limits | P09 | Active |
| bld_memory | Session persistence and patterns | P10 | Active |
| bld_tools | Production and validation tools | P04 | Active |

## Dependencies
| From | To | Type |
|------|----|------|
| bld_manifest | bld_config | configuration |
| bld_instruction | bld_schema | dependency |
| bld_output_template | bld_schema | dependency |
| bld_quality_gate | bld_examples | validation reference |
| bld_tools | bld_quality_gate | validation |

## Architectural Position
safety_hazard_taxonomy provides the classification FOUNDATION layer within CEX P11 safety infrastructure. Position in safety stack: taxonomy (this kind) -> content_filter (pipeline config) -> guardrail (enforcement rules) -> eval_dataset (test cases) -> benchmark (scores). Upstream: MLCommons AILuminate specification, Llama Guard 4 model card. Downstream: content_filter, guardrail, red_team_eval artifacts all reference this taxonomy.

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[bld_architecture_app_directory_entry]] | sibling | 0.64 |
| [[bld_architecture_legal_vertical]] | sibling | 0.64 |
| [[bld_architecture_roi_calculator]] | sibling | 0.63 |
| [[bld_architecture_code_of_conduct]] | sibling | 0.62 |
| [[bld_architecture_api_reference]] | sibling | 0.62 |
