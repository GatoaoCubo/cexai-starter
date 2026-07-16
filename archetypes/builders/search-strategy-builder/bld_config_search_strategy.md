---
kind: config
id: bld_config_search_strategy
pillar: P09
llm_function: CONSTRAIN
purpose: Naming, paths, limits for search_strategy production
quality: null
title: "Config Search Strategy"
version: "1.0.0"
author: wave1_builder_gen
tags: [search_strategy, builder, config]
tldr: "Production constraints for search strategy: naming (p04_ss_{{name}}.md), output paths (P04/), size limit 4096B. Search/inference strategy."
domain: "search_strategy construction"
created: "2026-04-13"
updated: "2026-04-13"
8f: "F1_constrain"
keywords: [limits for search_strategy production, search_strategy construction, config search strategy, output paths, size limit, inference strategy, search_strategy, builder, config, "p04_ss_{{name}}.md"]
density_score: 0.85
related:
  - bld_config_agents_md
  - bld_config_api_reference
  - bld_config_reasoning_strategy
  - bld_config_collaboration_pattern
  - bld_config_agent_profile
---

## Naming Convention
Pattern: `p04_ss_{{name}}.md`
Examples: `p04_ss_basic.md`, `p04_ss_advanced.md`

## Paths
Artifacts stored in: `/artifacts/p04/search_strategies/{{name}}`

## Limits
max_bytes: 4096
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
| Boundary | Search/inference strategy |
| Dependencies | retriever_config |
| Primary 8F function | F5_call |
| Max artifact size | 4096 bytes |

## Edge Cases

| Scenario | Handling |
|----------|---------|
| Missing required frontmatter field | Fail H01 gate; return to F6 |
| ID collision with existing artifact | Append version suffix (_v2) |
| Body exceeds 4096 bytes | Trim prose sections; preserve tables |
| Dependency retriever_config not found | Warn; proceed with defaults |

## Properties

| Property | Value |
|----------|-------|
| Kind | `config` |
| Pillar | P09 |
| Domain | search strategy construction |
| Pipeline | 8F (F1-F8) |
| Scorer | cex_score.py |
| Compiler | cex_compile.py |
| Retriever | cex_retriever.py |
| Quality target | 9.0+ |
| Density target | 0.85+ |

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[bld_config_agents_md]] | sibling | 0.54 |
| [[bld_config_api_reference]] | sibling | 0.53 |
| [[bld_config_reasoning_strategy]] | sibling | 0.52 |
| [[bld_config_collaboration_pattern]] | sibling | 0.51 |
| [[bld_config_agent_profile]] | sibling | 0.51 |
