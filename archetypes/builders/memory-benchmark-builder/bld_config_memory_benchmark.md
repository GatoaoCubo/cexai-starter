---
kind: config
id: bld_config_memory_benchmark
pillar: P09
llm_function: CONSTRAIN
purpose: Naming, paths, limits for memory_benchmark production
quality: null
title: "Config Memory Benchmark"
version: "1.0.0"
author: wave1_builder_gen_v2
tags: [memory_benchmark, builder, config]
tldr: "Production constraints for memory benchmark: naming (p07_mb_{{name}}.md), output paths (P07/), size limit 5120B. Memory eval suite."
domain: "memory_benchmark construction"
created: "2026-04-14"
updated: "2026-04-14"
8f: "F1_constrain"
keywords: [limits for memory_benchmark production, memory_benchmark construction, config memory benchmark, output paths, size limit, memory eval suite, memory_benchmark, builder, config, "p07_mb_{{name}}.md"]
density_score: 0.85
related:
  - bld_config_eval_framework
  - bld_config_benchmark_suite
  - bld_config_ab_test_config
  - bld_config_api_reference
  - bld_config_workflow_node
---

p07_mb_{{name}}.md
## Naming Convention
Pattern: `p07_mb_{{name}}.md`
Examples: `p07_mb_memory_test.md`, `p07_mb_cache_check.md`

## Paths
Artifacts: `/mnt/artifacts/p07/memory_benchmarks/`
Logs: `/var/log/p07/memory_benchmark-builder/`

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
| Boundary | Memory eval suite |
| Dependencies | benchmark, entity_memory |
| Primary 8F function | F3_inject |
| Max artifact size | 5120 bytes |

## Edge Cases

| Scenario | Handling |
|----------|---------|
| Missing required frontmatter field | Fail H01 gate; return to F6 |
| ID collision with existing artifact | Append version suffix (_v2) |
| Body exceeds 5120 bytes | Trim prose sections; preserve tables |
| Dependency benchmark not found | Warn; proceed with defaults |

## Properties

| Property | Value |
|----------|-------|
| Kind | `config` |
| Pillar | P09 |
| Domain | memory benchmark construction |
| Pipeline | 8F (F1-F8) |
| Scorer | cex_score.py |
| Compiler | cex_compile.py |
| Retriever | cex_retriever.py |
| Quality target | 9.0+ |
| Density target | 0.85+ |

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[bld_config_eval_framework]] | sibling | 0.54 |
| [[bld_config_benchmark_suite]] | sibling | 0.52 |
| [[bld_config_ab_test_config]] | sibling | 0.52 |
| [[bld_config_api_reference]] | sibling | 0.50 |
| [[bld_config_workflow_node]] | sibling | 0.49 |
