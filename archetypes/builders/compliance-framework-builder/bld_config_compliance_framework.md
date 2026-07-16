---
kind: config
id: bld_config_compliance_framework
pillar: P09
llm_function: CONSTRAIN
purpose: Naming, paths, limits for compliance_framework production
quality: null
title: "Config Compliance Framework"
version: "1.0.0"
author: wave1_builder_gen
tags: [compliance_framework, builder, config]
tldr: "Production constraints for compliance framework: naming (p11_cfw_{{name}}.md), output paths (P11/), size limit 5120B. Regulatory compliance mapping."
domain: "compliance_framework construction"
created: "2026-04-13"
updated: "2026-04-13"
8f: "F1_constrain"
keywords: [limits for compliance_framework production, compliance_framework construction, config compliance framework, output paths, size limit, regulatory compliance mapping, compliance_framework, builder, config, p11_cfw_<name>_<version>.md]
density_score: 0.85
related:
  - bld_config_safety_policy
  - bld_config_ab_test_config
  - bld_config_api_reference
  - bld_config_content_filter
  - bld_config_agents_md
---

## Naming Convention
Pattern: `p11_cfw_<name>_<version>.md` (e.g., `p11_cfw_compliance_policy_v1.md`, `p11_cfw_data_protection_v2.md`)

## Paths
Artifacts stored in: `/artifacts/p11/cfw/{{name}}/`
Root reference: `/compliance_frameworks/p11/`

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
| Boundary | Regulatory compliance mapping |
| Dependencies | compliance_checklist, constitutional_rule |
| Primary 8F function | F1_constrain |
| Max artifact size | 5120 bytes |

## Edge Cases

| Scenario | Handling |
|----------|---------|
| Missing required frontmatter field | Fail H01 gate; return to F6 |
| ID collision with existing artifact | Append version suffix (_v2) |
| Body exceeds 5120 bytes | Trim prose sections; preserve tables |
| Dependency compliance_checklist not found | Warn; proceed with defaults |

## Properties

| Property | Value |
|----------|-------|
| Kind | `config` |
| Pillar | P09 |
| Domain | compliance framework construction |
| Pipeline | 8F (F1-F8) |
| Scorer | cex_score.py |
| Compiler | cex_compile.py |
| Retriever | cex_retriever.py |
| Quality target | 9.0+ |
| Density target | 0.85+ |

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[bld_config_safety_policy]] | sibling | 0.55 |
| [[bld_config_ab_test_config]] | sibling | 0.53 |
| [[bld_config_api_reference]] | sibling | 0.53 |
| [[bld_config_content_filter]] | sibling | 0.53 |
| [[bld_config_agents_md]] | sibling | 0.52 |
