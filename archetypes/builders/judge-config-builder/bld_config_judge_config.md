---
kind: config
id: bld_config_judge_config
pillar: P09
llm_function: CONSTRAIN
purpose: Naming, paths, limits for judge_config production
quality: null
title: "Config Judge Config"
version: "1.0.0"
author: wave1_builder_gen_v2
tags: [judge_config, builder, config]
tldr: "Production constraints for judge config: naming (p07_jc_{{name}}.md), output paths (P07/), size limit 4096B. Judge config."
domain: "judge_config construction"
created: "2026-04-14"
updated: "2026-04-14"
8f: "F1_constrain"
keywords: [limits for judge_config production, judge_config construction, config judge config, output paths, size limit, judge config, judge_config, builder, config, "p07_jc_{{name}}.md"]
density_score: 0.85
related:
  - bld_config_ab_test_config
  - bld_config_api_reference
  - bld_config_collaboration_pattern
  - bld_config_eval_framework
  - bld_config_graph_rag_config
---

## Naming Convention
Pattern: `p07_jc_{{name}}.md`
Examples: `p07_jc_initial.md`, `p07_jc_final.md`

## Paths
Artifacts: `/mnt/artifacts/p07/{{name}}/`
Judge config: `/mnt/configs/judge/p07_jc_{{name}}.md`

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
| Boundary | Judge config |
| Dependencies | content_filter, audit_log |
| Primary 8F function | F7_govern |
| Max artifact size | 4096 bytes |

## Edge Cases

| Scenario | Handling |
|----------|---------|
| Missing required frontmatter field | Fail H01 gate; return to F6 |
| ID collision with existing artifact | Append version suffix (_v2) |
| Body exceeds 4096 bytes | Trim prose sections; preserve tables |
| Dependency content_filter not found | Warn; proceed with defaults |

## Properties

| Property | Value |
|----------|-------|
| Kind | `config` |
| Pillar | P09 |
| Domain | judge config construction |
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
| [[bld_config_api_reference]] | sibling | 0.51 |
| [[bld_config_collaboration_pattern]] | sibling | 0.49 |
| [[bld_config_eval_framework]] | sibling | 0.49 |
| [[bld_config_graph_rag_config]] | sibling | 0.49 |
