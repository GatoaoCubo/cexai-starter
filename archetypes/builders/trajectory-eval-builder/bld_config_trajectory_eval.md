---
kind: config
id: bld_config_trajectory_eval
pillar: P09
llm_function: CONSTRAIN
purpose: Naming, paths, limits for trajectory_eval production
quality: null
title: "Config Trajectory Eval"
version: "1.0.0"
author: wave1_builder_gen_v2
tags: [trajectory_eval, builder, config]
tldr: "Production constraints for trajectory eval: naming (p07_te_{{name}}.md), output paths (P07/), size limit 5120B. Trajectory evaluation."
domain: "trajectory_eval construction"
created: "2026-04-14"
updated: "2026-04-14"
8f: "F1_constrain"
keywords: [limits for trajectory_eval production, trajectory_eval construction, config trajectory eval, output paths, size limit, trajectory evaluation, trajectory_eval, builder, config, p07_te_<agent>_<task_slug>]
density_score: 0.85
related:
  - bld_config_ab_test_config
  - bld_config_agents_md
  - bld_config_agent_profile
  - bld_config_api_reference
  - bld_config_collaboration_pattern
---

## Naming Convention
Pattern: `p07_te_<agent>_<task_slug>`
Examples: `p07_te_gpt4o_webArena_045`, `p07_te_claude_swebench_12`
Scope: trajectory_eval artifacts for LLM agent step-level path analysis

## Paths
Artifacts: `P07_evaluation/trajectory_eval/`
Logs: `.cex/runtime/logs/trajectory_eval/`

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
| Boundary | Trajectory evaluation |
| Dependencies | eval_dataset, scoring_rubric |
| Primary 8F function | F7_govern |
| Max artifact size | 5120 bytes |

## Edge Cases

| Scenario | Handling |
|----------|---------|
| Missing required frontmatter field | Fail H01 gate; return to F6 |
| ID collision with existing artifact | Append version suffix (_v2) |
| Body exceeds 5120 bytes | Trim prose sections; preserve tables |
| Dependency eval_dataset not found | Warn; proceed with defaults |

## Properties

| Property | Value |
|----------|-------|
| Kind | `config` |
| Pillar | P09 |
| Domain | trajectory eval construction |
| Pipeline | 8F (F1-F8) |
| Scorer | cex_score.py |
| Compiler | cex_compile.py |
| Retriever | cex_retriever.py |
| Quality target | 9.0+ |
| Density target | 0.85+ |

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[bld_config_ab_test_config]] | sibling | 0.51 |
| [[bld_config_agents_md]] | sibling | 0.50 |
| [[bld_config_agent_profile]] | sibling | 0.50 |
| [[bld_config_api_reference]] | sibling | 0.50 |
| [[bld_config_collaboration_pattern]] | sibling | 0.49 |
