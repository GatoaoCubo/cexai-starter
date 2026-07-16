---
kind: config
id: bld_config_eval_framework
pillar: P09
llm_function: CONSTRAIN
purpose: Naming, paths, limits for eval_framework production
quality: null
title: "Config Eval Framework"
version: "1.0.0"
author: wave1_builder_gen_v2
tags: [eval_framework, builder, config]
tldr: "Production constraints for eval framework: naming (p07_efw_{{name}}.md), output paths (P07/), size limit 5120B. Eval framework."
domain: "eval_framework construction"
created: "2026-04-14"
updated: "2026-04-14"
8f: "F1_constrain"
keywords: [limits for eval_framework production, eval_framework construction, config eval framework, output paths, size limit, eval framework, eval_framework, builder, config, "p07_efw_{{name}}.md"]
density_score: 0.85
related:
  - bld_config_ab_test_config
  - bld_config_memory_benchmark
  - bld_config_api_reference
  - bld_config_agents_md
  - bld_config_customer_segment
---

## Naming Convention
Pattern: `p07_efw_{{name}}.md`
Examples: `p07_efw_chatbot.md`, `p07_efw_summarizer.md`

## Paths
Artifacts: `/mnt/artifacts/p07/efw/{{name}}`
Logs: `/var/log/eval_framework/p07/{{name}}`

## Limits
max_bytes: 5120
max_turns: 20
effort_level: 3

## Hooks
pre_build: null
post_build: null
on_error: null
on_quality_fail: null

## Domain-Specific Constraints

| Constraint | Value |
|-----------|-------|
| Boundary | Eval framework |
| Dependencies | eval_metric, scoring_rubric |
| Primary 8F function | F7_govern |
| Max artifact size | 5120 bytes |

## Edge Cases

| Scenario | Handling |
|----------|---------|
| Missing required frontmatter field | Fail H01 gate; return to F6 |
| ID collision with existing artifact | Append version suffix (_v2) |
| Body exceeds 5120 bytes | Trim prose sections; preserve tables |
| Dependency eval_metric not found | Warn; proceed with defaults |

## Properties

| Property | Value |
|----------|-------|
| Kind | `config` |
| Pillar | P09 |
| Domain | eval framework construction |
| Pipeline | 8F (F1-F8) |
| Scorer | cex_score.py |
| Compiler | cex_compile.py |
| Retriever | cex_retriever.py |
| Quality target | 9.0+ |
| Density target | 0.85+ |

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[bld_config_ab_test_config]] | sibling | 0.54 |
| [[bld_config_memory_benchmark]] | sibling | 0.52 |
| [[bld_config_api_reference]] | sibling | 0.51 |
| [[bld_config_agents_md]] | sibling | 0.50 |
| [[bld_config_customer_segment]] | sibling | 0.50 |
