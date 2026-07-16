---
kind: config
id: bld_config_planning_strategy
pillar: P09
llm_function: CONSTRAIN
purpose: Naming, paths, limits for planning_strategy production
quality: null
title: "Config Planning Strategy"
version: "1.0.0"
author: wave1_builder_gen
tags: [planning_strategy, builder, config]
tldr: "Production constraints for planning strategy: naming (p03_ps_{{name}}.md), output paths (P03/), size limit 5120B. Planning approach."
domain: "planning_strategy construction"
created: "2026-04-13"
updated: "2026-04-13"
8f: "F1_constrain"
keywords: [limits for planning_strategy production, planning_strategy construction, config planning strategy, output paths, size limit, planning approach, planning_strategy, builder, config, "p03_ps_{{name}}.md"]
density_score: 0.85
related:
  - bld_config_reasoning_strategy
  - bld_config_api_reference
  - bld_config_agents_md
  - bld_config_search_strategy
  - bld_config_collaboration_pattern
---

## Naming Convention
Pattern: `p03_ps_{{name}}.md`
Examples: `p03_ps_strategy.md`, `p03_ps_example_plan.md`

## Paths
Artifacts stored in: `/artifacts/p03/ps/{{name}}/`
Root: `/artifacts/p03/ps/`

## Limits
max_bytes: 5120
max_turns: 10
effort_level: 3

## Hooks
pre_build: null
post_build: null
on_error: null
on_quality_fail: null

## Domain-Specific Constraints

| Constraint | Value |
|-----------|-------|
| Boundary | Planning approach |
| Dependencies | prompt_template, reasoning_strategy |
| Primary 8F function | F4_reason |
| Max artifact size | 5120 bytes |

## Edge Cases

| Scenario | Handling |
|----------|---------|
| Missing required frontmatter field | Fail H01 gate; return to F6 |
| ID collision with existing artifact | Append version suffix (_v2) |
| Body exceeds 5120 bytes | Trim prose sections; preserve tables |
| Dependency prompt_template not found | Warn; proceed with defaults |

## Properties

| Property | Value |
|----------|-------|
| Kind | `config` |
| Pillar | P09 |
| Domain | planning strategy construction |
| Pipeline | 8F (F1-F8) |
| Scorer | cex_score.py |
| Compiler | cex_compile.py |
| Retriever | cex_retriever.py |
| Quality target | 9.0+ |
| Density target | 0.85+ |

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[bld_config_reasoning_strategy]] | sibling | 0.54 |
| [[bld_config_api_reference]] | sibling | 0.53 |
| [[bld_config_agents_md]] | sibling | 0.52 |
| [[bld_config_search_strategy]] | sibling | 0.52 |
| [[bld_config_collaboration_pattern]] | sibling | 0.51 |
