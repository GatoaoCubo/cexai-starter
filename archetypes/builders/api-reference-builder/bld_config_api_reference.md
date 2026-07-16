---
kind: config
id: bld_config_api_reference
pillar: P09
llm_function: CONSTRAIN
purpose: Naming, paths, limits for api_reference production
quality: null
title: "Config Api Reference"
version: "1.0.0"
author: wave1_builder_gen_v2
tags: [api_reference, builder, config]
tldr: "Production constraints for api reference: naming (p06_ar_{{name}}.md), output paths (P06/), size limit 8192B. API docs."
domain: "api_reference construction"
created: "2026-04-14"
updated: "2026-04-14"
8f: "F1_constrain"
keywords: [limits for api_reference production, api_reference construction, config api reference, output paths, size limit, api docs, api_reference, builder, config, p06_ar_<name>.md]
density_score: 0.85
related:
  - bld_config_ab_test_config
  - bld_config_collaboration_pattern
  - bld_config_repo_map
  - bld_config_agents_md
  - bld_config_model_registry
---

## Naming Convention
Pattern: `p06_ar_<name>.md` (e.g., `p06_ar_userapi.md`, `p06_ar_payment.md`)

## Paths
`/artifacts/api_refs/p06/<name>.md`

## Limits
max_bytes: 8192 | max_turns: 20 | effort level: 3

## Hooks
pre_build: null | post_build: null | on_error: null | on_quality_fail: null

## Domain-Specific Constraints

| Constraint | Value |
|-----------|-------|
| Boundary | API docs |
| Dependencies | api_client, input_schema |
| Primary 8F function | F5_call |
| Max artifact size | 8192 bytes |

## Edge Cases

| Scenario | Handling |
|----------|---------|
| Missing required frontmatter field | Fail H01 gate; return to F6 |
| ID collision with existing artifact | Append version suffix (_v2) |
| Body exceeds 8192 bytes | Trim prose sections; preserve tables |
| Dependency api_client not found | Warn; proceed with defaults |

## Properties

| Property | Value |
|----------|-------|
| Kind | `config` |
| Pillar | P09 |
| Domain | api reference construction |
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
| [[bld_config_collaboration_pattern]] | sibling | 0.52 |
| [[bld_config_repo_map]] | sibling | 0.51 |
| [[bld_config_agents_md]] | sibling | 0.51 |
| [[bld_config_model_registry]] | sibling | 0.51 |
