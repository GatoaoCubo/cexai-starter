---
kind: config
id: bld_config_interactive_demo
pillar: P09
llm_function: CONSTRAIN
purpose: Naming, paths, limits for interactive_demo production
quality: null
title: "Config Interactive Demo"
version: "1.0.0"
author: wave1_builder_gen_v2
tags: [interactive_demo, builder, config]
tldr: "Production constraints for interactive demo: naming (p05_id_{{name}}.md), output paths (P05/), size limit 6144B. Demo script."
domain: "interactive_demo construction"
created: "2026-04-14"
updated: "2026-04-14"
8f: "F1_constrain"
keywords: [limits for interactive_demo production, interactive_demo construction, config interactive demo, output paths, size limit, demo script, interactive_demo, builder, config, "p05_id_{{name}}.md"]
density_score: 0.85
related:
  - bld_config_integration_guide
  - bld_config_api_reference
  - bld_config_ab_test_config
  - bld_config_agents_md
  - bld_config_customer_segment
---

## Naming Convention
Pattern: `p05_id_{{name}}.md`
Examples: `p05_id_demo1.md`, `p05_id_userflow.md`

## Paths
Artifacts: `/artifacts/p05/demos/{{name}}`
Logs: `/logs/p05/{{name}}_build.log`

## Limits
max_bytes: 6144
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
| Boundary | Demo script |
| Dependencies | landing_page |
| Primary 8F function | F6_produce |
| Max artifact size | 6144 bytes |

## Edge Cases

| Scenario | Handling |
|----------|---------|
| Missing required frontmatter field | Fail H01 gate; return to F6 |
| ID collision with existing artifact | Append version suffix (_v2) |
| Body exceeds 6144 bytes | Trim prose sections; preserve tables |
| Dependency landing_page not found | Warn; proceed with defaults |

## Properties

| Property | Value |
|----------|-------|
| Kind | `config` |
| Pillar | P09 |
| Domain | interactive demo construction |
| Pipeline | 8F (F1-F8) |
| Scorer | cex_score.py |
| Compiler | cex_compile.py |
| Retriever | cex_retriever.py |
| Quality target | 9.0+ |
| Density target | 0.85+ |

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[bld_config_integration_guide]] | sibling | 0.53 |
| [[bld_config_api_reference]] | sibling | 0.52 |
| [[bld_config_ab_test_config]] | sibling | 0.51 |
| [[bld_config_agents_md]] | sibling | 0.51 |
| [[bld_config_customer_segment]] | sibling | 0.51 |
