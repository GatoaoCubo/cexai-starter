---
kind: config
id: bld_config_action_paradigm
pillar: P09
llm_function: CONSTRAIN
purpose: Naming, paths, limits for action_paradigm production
quality: null
title: "Config Action Paradigm"
version: "1.0.0"
author: wave1_builder_gen
tags: [action_paradigm, builder, config]
tldr: "Production constraints for action paradigm: naming (p04_act_{{name}}.md), output paths (P04/), size limit 4096B. Action execution paradigm."
domain: "action_paradigm construction"
created: "2026-04-13"
updated: "2026-04-13"
8f: "F1_constrain"
keywords: [limits for action_paradigm production, action_paradigm construction, config action paradigm, output paths, size limit, action execution paradigm, action_paradigm, builder, config, naming convention
pattern]
density_score: 0.85
related:
  - bld_config_collaboration_pattern
  - bld_config_api_reference
  - bld_config_ab_test_config
  - bld_config_agents_md
  - bld_config_diff_strategy
---

## Naming Convention
Pattern: p04_act_<name> (lowercase alphanumeric, underscores allowed)
Examples: p04_act_data_flow, p04_act_error_handler

## Paths
Base: /artifacts/p04/actions/
Per-action: /artifacts/p04/actions/<name>/

## Limits
max_bytes: 4096
max_turns: 10
effort_level: 3

## Hooks
pre_build: null
post_build: null
on_error: null
on_quality_fail: null

## Properties

| Property | Value |
|----------|-------|
| Kind | `config` |
| Pillar | P09 |
| Domain | action_paradigm construction |
| Pipeline | 8F (F1-F8) |
| Scorer | cex_score.py |
| Compiler | cex_compile.py |
| Retriever | cex_retriever.py |
| Quality target | 9.0+ |
| Density target | 0.85+ |

## Domain-Specific Constraints

| Constraint | Value |
|-----------|-------|
| Boundary | Action execution paradigm |
| Dependencies | function_def, skill |
| Primary 8F function | F6_produce |
| Max artifact size | 4096 bytes |

## Edge Cases

| Scenario | Handling |
|----------|---------|
| Missing required frontmatter field | Fail H01 gate; return to F6 |
| ID collision with existing artifact | Append version suffix (_v2) |
| Body exceeds 4096 bytes | Trim prose sections; preserve tables |
| Dependency function_def not found | Warn; proceed with defaults |

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[bld_config_collaboration_pattern]] | sibling | 0.52 |
| [[bld_config_api_reference]] | sibling | 0.52 |
| [[bld_config_ab_test_config]] | sibling | 0.49 |
| [[bld_config_agents_md]] | sibling | 0.49 |
| [[bld_config_diff_strategy]] | sibling | 0.48 |
