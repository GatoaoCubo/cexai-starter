---
kind: config
id: bld_config_expansion_play
pillar: P09
llm_function: CONSTRAIN
purpose: Naming, paths, limits for expansion_play production
quality: null
title: "Config Expansion Play"
version: "1.0.0"
author: wave1_builder_gen_v2
tags: [expansion_play, builder, config]
tldr: "Production constraints for expansion play: naming (p03_ep_{{name}}.md), output paths (P03/), size limit 5120B. Expansion play."
domain: "expansion_play construction"
created: "2026-04-14"
updated: "2026-04-14"
8f: "F1_constrain"
keywords: [limits for expansion_play production, expansion_play construction, config expansion play, output paths, size limit, expansion play, expansion_play, builder, config, "p03_ep_{{name}}.md"]
density_score: 0.85
related:
  - bld_config_api_reference
  - bld_config_planning_strategy
  - bld_config_collaboration_pattern
  - bld_config_ab_test_config
  - bld_config_agents_md
---

p03_ep_{{name}}.md
Pillar: P03

## Naming Convention
Pattern: `p03_ep_{{name}}.md`
Examples:
- p03_ep_initial.md
- p03_ep_v1.md

## Paths
Artifacts: `/artifacts/p03/ep/{{name}}`
Examples:
- `/artifacts/p03/ep/initial`
- `/artifacts/p03/ep/v1`

## Limits
max_bytes: 5120
max_turns: 10
effort_level: 3

## Hooks
pre_build: null
post_build: null
on_error: null
on_quality_fail: null

## Domain
expansion_play configuration -- governs naming, paths, and runtime limits for expansion play artifacts.
Expansion plays are triggered by usage thresholds and cross-sell signals, targeting NRR >120%.

## Domain-Specific Constraints

| Constraint | Value |
|-----------|-------|
| Boundary | Expansion play |
| Dependencies | customer_segment, sales_playbook |
| Primary 8F function | F8_collaborate |
| Max artifact size | 5120 bytes |

## Edge Cases

| Scenario | Handling |
|----------|---------|
| Missing required frontmatter field | Fail H01 gate; return to F6 |
| ID collision with existing artifact | Append version suffix (_v2) |
| Body exceeds 5120 bytes | Trim prose sections; preserve tables |
| Dependency customer_segment not found | Warn; proceed with defaults |

## Properties

| Property | Value |
|----------|-------|
| Kind | `config` |
| Pillar | P09 |
| Domain | expansion play construction |
| Pipeline | 8F (F1-F8) |
| Scorer | cex_score.py |
| Compiler | cex_compile.py |
| Retriever | cex_retriever.py |
| Quality target | 9.0+ |
| Density target | 0.85+ |

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[bld_config_api_reference]] | sibling | 0.49 |
| [[bld_config_planning_strategy]] | sibling | 0.49 |
| [[bld_config_collaboration_pattern]] | sibling | 0.48 |
| [[bld_config_ab_test_config]] | sibling | 0.48 |
| [[bld_config_agents_md]] | sibling | 0.47 |
