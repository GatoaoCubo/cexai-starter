---
kind: config
id: bld_config_safety_policy
pillar: P09
llm_function: CONSTRAIN
purpose: Naming, paths, limits for safety_policy production
quality: null
title: "Config Safety Policy"
version: "1.0.0"
author: wave1_builder_gen
tags: [safety_policy, builder, config]
tldr: "Production constraints for safety policy: naming (p11_sp_{{name}}.md), output paths (P11/), size limit 5120B. Safety governance rules."
domain: "safety_policy construction"
created: "2026-04-13"
updated: "2026-04-13"
8f: "F1_constrain"
keywords: [limits for safety_policy production, safety_policy construction, config safety policy, output paths, size limit, safety governance rules, safety_policy, builder, config, "p11_sp_{{name}}.md"]
density_score: 0.85
related:
  - bld_config_content_filter
  - bld_config_compliance_framework
  - bld_config_ab_test_config
  - bld_config_agents_md
  - bld_config_api_reference
---

## Naming Convention
Pattern: `p11_sp_{{name}}.md`
Examples: `p11_sp_data.md`, `p11_sp_network.md`

## Paths
Artifacts stored in: `/artifacts/p11/sp/{{name}}/`
Config file path: `/artifacts/p11/sp/{{name}}/safety_policy.md`

## Limits
max_bytes: 5120
max_turns: 10
effort_level: medium

## Hooks
pre_build: null
post_build: null
on_error: null
on_quality_fail: null

## Domain-Specific Constraints

| Constraint | Value |
|-----------|-------|
| Boundary | Safety governance rules |
| Dependencies | guardrail, constitutional_rule |
| Primary 8F function | F1_constrain |
| Max artifact size | 5120 bytes |

## Edge Cases

| Scenario | Handling |
|----------|---------|
| Missing required frontmatter field | Fail H01 gate; return to F6 |
| ID collision with existing artifact | Append version suffix (_v2) |
| Body exceeds 5120 bytes | Trim prose sections; preserve tables |
| Dependency guardrail not found | Warn; proceed with defaults |

## Properties

| Property | Value |
|----------|-------|
| Kind | `config` |
| Pillar | P09 |
| Domain | safety policy construction |
| Pipeline | 8F (F1-F8) |
| Scorer | cex_score.py |
| Compiler | cex_compile.py |
| Retriever | cex_retriever.py |
| Quality target | 9.0+ |
| Density target | 0.85+ |

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[bld_config_content_filter]] | sibling | 0.55 |
| [[bld_config_compliance_framework]] | sibling | 0.54 |
| [[bld_config_ab_test_config]] | sibling | 0.53 |
| [[bld_config_agents_md]] | sibling | 0.52 |
| [[bld_config_api_reference]] | sibling | 0.52 |
