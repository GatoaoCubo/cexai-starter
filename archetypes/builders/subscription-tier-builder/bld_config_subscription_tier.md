---
kind: config
id: bld_config_subscription_tier
pillar: P09
llm_function: CONSTRAIN
purpose: Naming, paths, limits for subscription_tier production
quality: null
title: "Config Subscription Tier"
version: "1.0.0"
author: wave1_builder_gen_v2
tags: [subscription_tier, builder, config]
tldr: "Production constraints for subscription tier: naming (p11_st_{{name}}.yaml), output paths (P11/), size limit 3072B. Pricing tier."
domain: "subscription_tier construction"
created: "2026-04-14"
updated: "2026-04-14"
8f: "F1_constrain"
keywords: [limits for subscription_tier production, subscription_tier construction, config subscription tier, output paths, size limit, pricing tier, subscription_tier, builder, config, "p11_st_{{name}}.yaml"]
density_score: 0.85
related:
  - bld_config_ab_test_config
  - bld_config_api_reference
  - bld_config_customer_segment
  - bld_config_collaboration_pattern
  - bld_config_pricing_page
---

## Naming Convention
Pattern: `p11_st_{{name}}.yaml`
Examples: `p11_st_bronze.yaml`, `p11_st_premium.yaml`

## Paths
Artifacts: `/artifacts/subscription_tiers/p11_st_{{name}}.yaml`
Logs: `/logs/build/p11_st_{{name}}`

## Limits
max_bytes: 3072
max_turns: 150
effort_level: high

## Hooks
pre_build: null
post_build: null
on_error: null
on_quality_fail: null

## Domain-Specific Constraints

| Constraint | Value |
|-----------|-------|
| Boundary | Pricing tier |
| Dependencies | customer_segment |
| Primary 8F function | F1_constrain |
| Max artifact size | 3072 bytes |

## Edge Cases

| Scenario | Handling |
|----------|---------|
| Missing required frontmatter field | Fail H01 gate; return to F6 |
| ID collision with existing artifact | Append version suffix (_v2) |
| Body exceeds 3072 bytes | Trim prose sections; preserve tables |
| Dependency customer_segment not found | Warn; proceed with defaults |

## Properties

| Property | Value |
|----------|-------|
| Kind | `config` |
| Pillar | P09 |
| Domain | subscription tier construction |
| Pipeline | 8F (F1-F8) |
| Scorer | cex_score.py |
| Compiler | cex_compile.py |
| Retriever | cex_retriever.py |
| Quality target | 9.0+ |
| Density target | 0.85+ |

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| bld_config_ab_test_config | sibling | 0.52 |
| bld_config_api_reference | sibling | 0.49 |
| [[bld_config_customer_segment]] | sibling | 0.48 |
| bld_config_collaboration_pattern | sibling | 0.48 |
| bld_config_pricing_page | sibling | 0.47 |
