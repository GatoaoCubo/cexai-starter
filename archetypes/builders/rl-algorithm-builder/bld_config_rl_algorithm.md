---
kind: config
id: bld_config_rl_algorithm
pillar: P09
llm_function: CONSTRAIN
purpose: Naming, paths, limits for rl_algorithm production
quality: null
title: "Config Rl Algorithm"
version: "1.0.0"
author: wave1_builder_gen
tags: [rl_algorithm, builder, config]
tldr: "Production constraints for rl algorithm: naming (p02_rla_{{name}}.md), output paths (P02/), size limit 5120B. RL algorithm def."
domain: "rl_algorithm construction"
created: "2026-04-13"
updated: "2026-04-13"
8f: "F1_constrain"
keywords: [limits for rl_algorithm production, rl_algorithm construction, config rl algorithm, output paths, size limit, rl algorithm def, rl_algorithm, builder, config, "p02_rla_{{name}}.md"]
density_score: 0.85
related:
  - bld_config_ab_test_config
  - bld_config_agents_md
  - bld_config_eval_framework
  - bld_config_customer_segment
  - bld_config_api_reference
---

## Naming Convention
Pattern: `p02_rla_{{name}}.md`
Examples: `p02_rla_dqn.md`, `p02_rla_ppo.md`

## Paths
Artifacts: `/mnt/artifacts/p02/rla/{{name}}`
Logs: `/var/log/rla/{{name}}`
Checkpoints: `/mnt/models/p02/rla/{{name}}`

## Limits
max_bytes: 5120
max_turns: 100
effort_level: 3

## Hooks
pre_build: null
post_build: null
on_error: null
on_quality_fail: null

## Domain-Specific Constraints

| Constraint | Value |
|-----------|-------|
| Boundary | RL algorithm def |
| Dependencies | reward_model, training_method |
| Primary 8F function | F7_govern |
| Max artifact size | 5120 bytes |

## Edge Cases

| Scenario | Handling |
|----------|---------|
| Missing required frontmatter field | Fail H01 gate; return to F6 |
| ID collision with existing artifact | Append version suffix (_v2) |
| Body exceeds 5120 bytes | Trim prose sections; preserve tables |
| Dependency reward_model not found | Warn; proceed with defaults |

## Properties

| Property | Value |
|----------|-------|
| Kind | `config` |
| Pillar | P09 |
| Domain | rl algorithm construction |
| Pipeline | 8F (F1-F8) |
| Scorer | cex_score.py |
| Compiler | cex_compile.py |
| Retriever | cex_retriever.py |
| Quality target | 9.0+ |
| Density target | 0.85+ |

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[bld_config_ab_test_config]] | sibling | 0.52 |
| [[bld_config_agents_md]] | sibling | 0.51 |
| [[bld_config_eval_framework]] | sibling | 0.50 |
| [[bld_config_customer_segment]] | sibling | 0.50 |
| [[bld_config_api_reference]] | sibling | 0.50 |
