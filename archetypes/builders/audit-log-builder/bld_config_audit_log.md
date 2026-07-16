---
kind: config
id: bld_config_audit_log
pillar: P09
llm_function: CONSTRAIN
purpose: Naming, paths, limits for audit_log production
quality: null
title: "Config Audit Log"
version: "1.0.0"
author: wave1_builder_gen_v2
tags: [audit_log, builder, config]
tldr: "Production constraints for audit log: naming (p11_al_{{name}}.yaml), output paths (P11/), size limit 3072B. Audit log spec."
domain: "audit_log construction"
created: "2026-04-14"
updated: "2026-04-14"
8f: "F1_constrain"
keywords: [limits for audit_log production, audit_log construction, config audit log, output paths, size limit, audit log spec, audit_log, builder, config, "p11_al_{{name}}.yaml"]
density_score: 0.85
related:
  - bld_config_ab_test_config
  - bld_config_api_reference
  - bld_config_collaboration_pattern
  - bld_config_agents_md
  - bld_config_repo_map
---

## Naming Convention
Pattern: `p11_al_{{name}}.yaml`
Examples: `p11_al_user123.yaml`, `p11_al_system456.yaml`

## Paths
Artifacts: `/opt/cex/audit_logs/{{name}}/`
Backup: `/backup/cex/audit_logs/{{name}}/`

## Limits
max_bytes: 3072
max_turns: 100
effort_level: 3

## Hooks
pre_build: null
post_build: null
on_error: null
on_quality_fail: null

## Domain-Specific Constraints

| Constraint | Value |
|-----------|-------|
| Boundary | Audit log spec |
| Dependencies | env_config, knowledge_card |
| Primary 8F function | F8_collaborate |
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
| Domain | audit log construction |
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
| [[bld_config_api_reference]] | sibling | 0.50 |
| [[bld_config_collaboration_pattern]] | sibling | 0.49 |
| [[bld_config_agents_md]] | sibling | 0.49 |
| [[bld_config_repo_map]] | sibling | 0.48 |
