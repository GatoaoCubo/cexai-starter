---
kind: architecture
id: bld_architecture_analyst_briefing
pillar: P08
llm_function: CONSTRAIN
purpose: Component map of analyst_briefing -- inventory, dependencies
quality: null
title: "Architecture Analyst Briefing"
version: "1.0.0"
author: n01_wave6
tags: [analyst_briefing, builder, architecture]
tldr: "Component map of analyst_briefing -- inventory, dependencies"
domain: "analyst_briefing construction"
created: "2026-04-14"
updated: "2026-04-14"
8f: "F1_constrain"
keywords: [analyst_briefing construction, architecture analyst briefing, analyst_briefing, builder, architecture, component inventory, architectural position, magic quadrant, forrester wave, related artifacts]
density_score: 0.85
related:
  - bld_architecture_app_directory_entry
  - bld_architecture_benchmark_suite
  - bld_architecture_legal_vertical
  - bld_architecture_fintech_vertical
  - bld_architecture_healthcare_vertical
---

## Component Inventory
| ISO Name            | Role                          | Pillar | Status |
|---------------------|-------------------------------|--------|--------|
| bld_manifest        | Builder identity and routing  | P05    | Active |
| bld_instruction     | Production process (3 phases) | P03    | Active |
| bld_system_prompt   | LLM persona and rules         | P03    | Active |
| bld_schema          | Frontmatter + body contract   | P06    | Active |
| bld_quality_gate    | HARD gates + SOFT scoring     | P11    | Active |
| bld_output_template | Variable-substitution template| P05    | Active |
| bld_examples        | Golden + anti-examples        | P07    | Active |
| bld_knowledge_card  | Gartner/Forrester/IDC domain  | P01    | Active |
| bld_architecture    | Component inventory + deps    | P08    | Active |
| bld_collaboration   | Crew role and handoff map     | P12    | Active |
| bld_config          | Naming, paths, limits         | P09    | Active |
| bld_memory          | Learned patterns and pitfalls | P10    | Active |
| bld_tools           | Production + validation tools | P04    | Active |

## Dependencies
| From                | To                    | Type          |
|---------------------|-----------------------|---------------|
| bld_manifest        | bld_config            | configuration |
| bld_instruction     | bld_system_prompt     | dependency    |
| bld_output_template | bld_schema            | dependency    |
| bld_quality_gate    | bld_examples          | validation    |
| bld_collaboration   | bld_memory            | coordination  |
| bld_tools           | external data sources | integration   |
| bld_knowledge_card  | bld_instruction       | injection     |

## Architectural Position
analyst_briefing lives in CEX P05 (PRODUCE pillar), serving as the vendor-to-analyst communication layer. It consumes proof points from internal data sources (CRM, telemetry, customer success), applies Gartner/Forrester/IDC evaluation frameworks from the knowledge card, and produces structured briefing artifacts consumed by AR teams. Its output feeds both one-on-one analyst briefing sessions and formal research submission processes (Magic Quadrant RFIs, Forrester Wave vendor submissions).

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[bld_architecture_app_directory_entry]] | sibling | 0.67 |
| [[bld_architecture_benchmark_suite]] | sibling | 0.67 |
| [[bld_architecture_legal_vertical]] | sibling | 0.66 |
| [[bld_architecture_fintech_vertical]] | sibling | 0.65 |
| [[bld_architecture_healthcare_vertical]] | sibling | 0.65 |
