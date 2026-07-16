---
kind: config
id: bld_config_data_residency
pillar: P09
llm_function: CONSTRAIN
purpose: Naming, paths, limits for data_residency production
quality: null
title: "Config Data Residency"
version: "1.0.0"
author: wave1_builder_gen_v2
tags: [data_residency, builder, config]
tldr: "Production constraints for data residency: naming (p09_dr_{{name}}.yaml), output paths (P09/), size limit 3072B. Residency spec."
domain: "data_residency construction"
created: "2026-04-14"
updated: "2026-04-14"
8f: "F1_constrain"
keywords: [limits for data_residency production, data_residency construction, config data residency, output paths, size limit, residency spec, data_residency, builder, config, p09_dr_<project_name>.yaml]
density_score: 0.85
related:
  - bld_config_transport_config
  - bld_config_ab_test_config
  - bld_config_api_reference
  - bld_config_agents_md
  - bld_config_sandbox_config
---

## Naming Convention
Pattern: `p09_dr_<project_name>.yaml`
Examples: `p09_dr_customer_data.yaml`, `p09_dr_inventory.yaml`

## Paths
Artifacts stored in:
`/artifacts/pillar/P09/{{name}}/build`
`/artifacts/pillar/P09/{{name}}/output`

## Limits
max_bytes: 3072
max_turns: 50
effort_level: medium

## Hooks
pre_build: null
post_build: null
on_error: null
on_quality_fail: null

## Domain-Specific Constraints

| Constraint | Value |
|-----------|-------|
| Boundary | Residency spec |
| Dependencies | env_config, secret_config |
| Primary 8F function | F1_constrain |
| Max artifact size | 3072 bytes |

## Edge Cases

| Scenario | Handling |
|----------|---------|
| Missing required frontmatter field | Fail H01 gate; return to F6 |
| ID collision with existing artifact | Append version suffix (_v2) |
| Body exceeds 3072 bytes | Trim prose sections; preserve tables |
| Dependency env_config not found | Warn; proceed with defaults |

## Properties

| Property | Value |
|----------|-------|
| Kind | `config` |
| Pillar | P09 |
| Domain | data residency construction |
| Pipeline | 8F (F1-F8) |
| Scorer | cex_score.py |
| Compiler | cex_compile.py |
| Retriever | cex_retriever.py |
| Quality target | 9.0+ |
| Density target | 0.85+ |

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[bld_config_transport_config]] | sibling | 0.55 |
| [[bld_config_ab_test_config]] | sibling | 0.53 |
| [[bld_config_api_reference]] | sibling | 0.52 |
| [[bld_config_agents_md]] | sibling | 0.51 |
| [[bld_config_sandbox_config]] | sibling | 0.50 |
