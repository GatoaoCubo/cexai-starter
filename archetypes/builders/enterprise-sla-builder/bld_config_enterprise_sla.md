---
kind: config
id: bld_config_enterprise_sla
pillar: P09
llm_function: CONSTRAIN
purpose: Naming, paths, limits for enterprise_sla production
quality: null
title: "Config Enterprise Sla"
version: "1.0.0"
author: wave1_builder_gen_v2
tags: [enterprise_sla, builder, config]
tldr: "Production constraints for enterprise sla: naming (p11_sla_{{name}}.md), output paths (P11/), size limit 6144B. SLA contract."
domain: "enterprise_sla construction"
created: "2026-04-14"
updated: "2026-04-14"
8f: "F1_constrain"
keywords: [limits for enterprise_sla production, enterprise_sla construction, config enterprise sla, output paths, size limit, sla contract, enterprise_sla, builder, config, "p11_sla_{{name}}.md"]
density_score: 0.85
related:
  - bld_config_api_reference
  - bld_config_collaboration_pattern
  - bld_config_ab_test_config
  - bld_config_agents_md
  - bld_config_repo_map
---

## Naming Convention
Pattern: `p11_sla_{{name}}.md`
Examples: `p11_sla_annual_review.md`, `p11_sla_q4_2023.md`

## Paths
/artifacts/enterprise/sla/P11/{{name}}

## Limits
max_bytes: 6144
max_turns: 5
effort level: medium

## Hooks
pre_build: null
post_build: null
on_error: null
on_quality_fail: null

## Domain-Specific Constraints

| Constraint | Value |
|-----------|-------|
| Boundary | SLA contract |
| Dependencies | quality_gate, env_config |
| Primary 8F function | F8_collaborate |
| Max artifact size | 6144 bytes |

## Edge Cases

| Scenario | Handling |
|----------|---------|
| Missing required frontmatter field | Fail H01 gate; return to F6 |
| ID collision with existing artifact | Append version suffix (_v2) |
| Body exceeds 6144 bytes | Trim prose sections; preserve tables |
| Dependency quality_gate not found | Warn; proceed with defaults |

## Properties

| Property | Value |
|----------|-------|
| Kind | `config` |
| Pillar | P09 |
| Domain | enterprise sla construction |
| Pipeline | 8F (F1-F8) |
| Scorer | cex_score.py |
| Compiler | cex_compile.py |
| Retriever | cex_retriever.py |
| Quality target | 9.0+ |
| Density target | 0.85+ |

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[bld_config_api_reference]] | sibling | 0.55 |
| [[bld_config_collaboration_pattern]] | sibling | 0.51 |
| [[bld_config_ab_test_config]] | sibling | 0.51 |
| [[bld_config_agents_md]] | sibling | 0.49 |
| [[bld_config_repo_map]] | sibling | 0.49 |
