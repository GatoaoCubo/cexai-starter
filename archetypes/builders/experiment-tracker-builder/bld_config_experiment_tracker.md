---
kind: config
id: bld_config_experiment_tracker
pillar: P09
llm_function: CONSTRAIN
purpose: Naming, paths, limits for experiment_tracker production
quality: null
title: "Config Experiment Tracker"
version: "1.0.0"
author: wave1_builder_gen
tags: [experiment_tracker, builder, config]
tldr: "Production constraints for experiment tracker: naming (p07_et_{{name}}.md), output paths (P07/), size limit 4096B. Experiment tracking."
domain: "experiment_tracker construction"
created: "2026-04-13"
updated: "2026-04-13"
8f: "F1_constrain"
keywords: [limits for experiment_tracker production, experiment_tracker construction, config experiment tracker, output paths, size limit, experiment tracking, experiment_tracker, builder, config, naming convention
pattern]
density_score: 0.85
related:
  - bld_config_api_reference
  - bld_config_ab_test_config
  - bld_config_collaboration_pattern
  - bld_config_repo_map
  - bld_config_model_registry
---

## Naming Convention
Pattern: p07_et_{{name}}.md
Examples: p07_et_baseline.md, p07_et_v1_test.md

## Paths
Artifacts: ./outputs/p07/experiments/

## Limits
max_bytes: 4096
max_turns: 15
effort_level: medium

## Hooks
pre_build: null
post_build: null
on_error: null
on_quality_fail: null

## Domain-Specific Constraints

| Constraint | Value |
|-----------|-------|
| Boundary | Experiment tracking |
| Dependencies | experiment_config, eval_metric |
| Primary 8F function | F7_govern |
| Max artifact size | 4096 bytes |

## Edge Cases

| Scenario | Handling |
|----------|---------|
| Missing required frontmatter field | Fail H01 gate; return to F6 |
| ID collision with existing artifact | Append version suffix (_v2) |
| Body exceeds 4096 bytes | Trim prose sections; preserve tables |
| Dependency experiment_config not found | Warn; proceed with defaults |

## Properties

| Property | Value |
|----------|-------|
| Kind | `config` |
| Pillar | P09 |
| Domain | experiment tracker construction |
| Pipeline | 8F (F1-F8) |
| Scorer | cex_score.py |
| Compiler | cex_compile.py |
| Retriever | cex_retriever.py |
| Quality target | 9.0+ |
| Density target | 0.85+ |

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[bld_config_api_reference]] | sibling | 0.56 |
| [[bld_config_ab_test_config]] | sibling | 0.53 |
| [[bld_config_collaboration_pattern]] | sibling | 0.52 |
| [[bld_config_repo_map]] | sibling | 0.52 |
| [[bld_config_model_registry]] | sibling | 0.52 |
