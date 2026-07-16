---
kind: config
id: bld_config_sales_playbook
pillar: P09
llm_function: CONSTRAIN
purpose: Naming, paths, limits for sales_playbook production
quality: null
title: "Config Sales Playbook"
version: "1.0.0"
author: wave1_builder_gen_v2
tags: [sales_playbook, builder, config]
tldr: "Production constraints for sales playbook: naming (p03_sp_{{name}}.md), output paths (P03/), size limit 8192B. Sales playbook."
domain: "sales_playbook construction"
created: "2026-04-14"
updated: "2026-04-14"
8f: "F1_constrain"
keywords: [limits for sales_playbook production, sales_playbook construction, config sales playbook, output paths, size limit, sales playbook, sales_playbook, builder, config, "p03_sp_{{name}}.md"]
density_score: 0.85
related:
  - bld_config_agents_md
  - bld_config_search_strategy
  - bld_config_collaboration_pattern
  - bld_config_reasoning_strategy
  - bld_config_api_reference
---

## Naming Convention
Pattern: `p03_sp_{{name}}.md`
Examples: `p03_sp_onboarding.md`, `p03_sp_retention.md`

## Paths
Artifacts stored in: `/artifacts/sales_playbooks/p03/{{name}}.md`

## Limits
max_bytes: 8192
max_turns: 5
effort_level: medium

## Hooks
pre_build: null
post_build: null
on_error: null
on_quality_fail: null

## Domain-Specific Constraints

| Constraint | Value |
|-----------|-------|
| Boundary | Sales playbook |
| Dependencies | customer_segment, prompt_template |
| Primary 8F function | F6_produce |
| Max artifact size | 8192 bytes |

## Edge Cases

| Scenario | Handling |
|----------|---------|
| Missing required frontmatter field | Fail H01 gate; return to F6 |
| ID collision with existing artifact | Append version suffix (_v2) |
| Body exceeds 8192 bytes | Trim prose sections; preserve tables |
| Dependency customer_segment not found | Warn; proceed with defaults |

## Properties

| Property | Value |
|----------|-------|
| Kind | `config` |
| Pillar | P09 |
| Domain | sales playbook construction |
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
| [[bld_config_search_strategy]] | sibling | 0.52 |
| [[bld_config_collaboration_pattern]] | sibling | 0.52 |
| [[bld_config_reasoning_strategy]] | sibling | 0.52 |
| [[bld_config_api_reference]] | sibling | 0.52 |
