---
kind: config
id: bld_config_referral_program
pillar: P09
llm_function: CONSTRAIN
purpose: Naming, paths, limits for referral_program production
quality: null
title: "Config Referral Program"
version: "1.0.0"
author: wave1_builder_gen_v2
tags: [referral_program, builder, config]
tldr: "Production constraints for referral program: naming (p11_rp_{{name}}.yaml), output paths (P11/), size limit 4096B. Referral spec."
domain: "referral_program construction"
created: "2026-04-14"
updated: "2026-04-14"
8f: "F1_constrain"
keywords: [limits for referral_program production, referral_program construction, config referral program, output paths, size limit, referral spec, referral_program, builder, config, "p11_rp_{{name}}.yaml"]
density_score: 0.85
related:
  - bld_config_ab_test_config
  - bld_config_api_reference
  - bld_config_collaboration_pattern
  - bld_config_discovery_questions
  - bld_config_repo_map
---

## Naming Convention
Pattern: `p11_rp_{{name}}.yaml`
Examples: `p11_rp_referral_program.yaml`, `p11_rp_loyalty.yaml`

## Paths
`/artifacts/referral_programs/p11_rp_{{name}}.yaml`
`/src/pillars/P11/configs/referral_programs/`

## Limits
max_bytes: 4096
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
| Boundary | Referral spec |
| Dependencies | customer_segment, knowledge_card |
| Primary 8F function | F6_produce |
| Max artifact size | 4096 bytes |

## Edge Cases

| Scenario | Handling |
|----------|---------|
| Missing required frontmatter field | Fail H01 gate; return to F6 |
| ID collision with existing artifact | Append version suffix (_v2) |
| Body exceeds 4096 bytes | Trim prose sections; preserve tables |
| Dependency customer_segment not found | Warn; proceed with defaults |

## Properties

| Property | Value |
|----------|-------|
| Kind | `config` |
| Pillar | P09 |
| Domain | referral program construction |
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
| [[bld_config_api_reference]] | sibling | 0.53 |
| [[bld_config_collaboration_pattern]] | sibling | 0.51 |
| [[bld_config_discovery_questions]] | sibling | 0.50 |
| [[bld_config_repo_map]] | sibling | 0.49 |
