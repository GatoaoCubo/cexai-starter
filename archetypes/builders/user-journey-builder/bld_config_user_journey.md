---
kind: config
id: bld_config_user_journey
pillar: P09
llm_function: CONSTRAIN
purpose: Naming, paths, limits for user_journey production
quality: null
title: "Config User Journey"
version: "1.0.0"
author: wave1_builder_gen_v2
tags: [user_journey, builder, config]
tldr: "Production constraints for user journey: naming (p05_uj_{{name}}.md), output paths (P05/), size limit 5120B. Journey map."
domain: "user_journey construction"
created: "2026-04-14"
updated: "2026-04-14"
8f: "F1_constrain"
keywords: [limits for user_journey production, user_journey construction, config user journey, output paths, size limit, journey map, user_journey, builder, config, "p05_uj_{{name}}.md"]
density_score: 0.85
related:
  - bld_config_api_reference
  - bld_config_repo_map
  - bld_config_discovery_questions
  - bld_config_pricing_page
  - bld_config_ab_test_config
---

## Naming Convention
Pattern: `p05_uj_{{name}}.md`
Examples: `p05_uj_onboarding.md`, `p05_uj_checkout.md`

## Paths
Artifacts: `/cex/artifacts/p05/user_journeys/{{name}}.md`
Templates: `/cex/templates/p05/user_journey-builder/`

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
| Boundary | Journey map |
| Dependencies | customer_segment, knowledge_card |
| Primary 8F function | F4_reason |
| Max artifact size | 5120 bytes |

## Edge Cases

| Scenario | Handling |
|----------|---------|
| Missing required frontmatter field | Fail H01 gate; return to F6 |
| ID collision with existing artifact | Append version suffix (_v2) |
| Body exceeds 5120 bytes | Trim prose sections; preserve tables |
| Dependency customer_segment not found | Warn; proceed with defaults |

## Properties

| Property | Value |
|----------|-------|
| Kind | `config` |
| Pillar | P09 |
| Domain | user journey construction |
| Pipeline | 8F (F1-F8) |
| Scorer | cex_score.py |
| Compiler | cex_compile.py |
| Retriever | cex_retriever.py |
| Quality target | 9.0+ |
| Density target | 0.85+ |

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[bld_config_api_reference]] | sibling | 0.53 |
| [[bld_config_repo_map]] | sibling | 0.53 |
| [[bld_config_discovery_questions]] | sibling | 0.53 |
| [[bld_config_pricing_page]] | sibling | 0.52 |
| [[bld_config_ab_test_config]] | sibling | 0.51 |
