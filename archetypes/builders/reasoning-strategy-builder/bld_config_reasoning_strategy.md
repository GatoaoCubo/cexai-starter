---
kind: config
id: bld_config_reasoning_strategy
pillar: P09
llm_function: CONSTRAIN
purpose: Naming, paths, limits for reasoning_strategy production
quality: null
title: "Config Reasoning Strategy"
version: "1.0.0"
author: wave1_builder_gen
tags: [reasoning_strategy, builder, config]
tldr: "Production constraints for reasoning strategy: naming (p03_rs_{{name}}.md), output paths (P03/), size limit 5120B. Reasoning technique."
domain: "reasoning_strategy construction"
created: "2026-04-13"
updated: "2026-04-13"
8f: "F1_constrain"
keywords: [limits for reasoning_strategy production, reasoning_strategy construction, config reasoning strategy, output paths, size limit, reasoning technique, reasoning_strategy, builder, config, "p03_rs_{{name}}.md"]
density_score: 0.85
related:
  - bld_config_search_strategy
  - bld_config_prompt_technique
  - bld_config_agents_md
  - bld_config_planning_strategy
  - bld_config_api_reference
---

## Naming Convention  

This ISO selects a reasoning strategy (e.g. chain-of-thought) and the conditions under which it applies.
Pattern: `p03_rs_{{name}}.md`  
Examples: `p03_rs_basic.md`, `p03_rs_advanced.md`  

## Paths  
Artifacts stored in: `/artifacts/p03/rs/{{name}}/`  

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
| Boundary | Reasoning technique |
| Dependencies | prompt_template, mental_model |
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
| Domain | reasoning strategy construction |
| Pipeline | 8F (F1-F8) |
| Scorer | cex_score.py |
| Compiler | cex_compile.py |
| Retriever | cex_retriever.py |
| Quality target | 9.0+ |
| Density target | 0.85+ |

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| bld_config_search_strategy | sibling | 0.55 |
| bld_config_prompt_technique | sibling | 0.54 |
| bld_config_agents_md | sibling | 0.53 |
| bld_config_planning_strategy | sibling | 0.53 |
| bld_config_api_reference | sibling | 0.51 |
