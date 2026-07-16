---
kind: config
id: bld_config_product_tour
pillar: P09
llm_function: CONSTRAIN
purpose: Naming, paths, limits for product_tour production
quality: null
title: "Config Product Tour"
version: "1.0.0"
author: wave1_builder_gen_v2
tags: [product_tour, builder, config]
tldr: "Production constraints for product tour: naming (p05_pt_{{name}}.md), output paths (P05/), size limit 5120B. Product tour."
domain: "product_tour construction"
created: "2026-04-14"
updated: "2026-04-14"
8f: "F1_constrain"
keywords: [limits for product_tour production, product_tour construction, config product tour, output paths, size limit, product tour, product_tour, builder, config, naming convention
pattern]
density_score: 0.85
related:
  - bld_config_api_reference
  - bld_config_ab_test_config
  - bld_config_agents_md
  - bld_config_collaboration_pattern
  - bld_config_repo_map
---

## Naming Convention
Pattern: p05_pt_{{name}}.md
Examples: p05_pt_onboarding.md, p05_pt_feature_x.md

## Paths
/artifacts/p05/product_tours/{{name}}.md

## Limits
max_bytes: 5120
max_turns: 0
effort_level: 0

## Hooks
pre_build: null
post_build: null
on_error: null
on_quality_fail: null

## Domain-Specific Constraints

| Constraint | Value |
|-----------|-------|
| Boundary | Product tour |
| Dependencies | user_journey, knowledge_card |
| Primary 8F function | F6_produce |
| Max artifact size | 5120 bytes |

## Edge Cases

| Scenario | Handling |
|----------|---------|
| Missing required frontmatter field | Fail H01 gate; return to F6 |
| ID collision with existing artifact | Append version suffix (_v2) |
| Body exceeds 5120 bytes | Trim prose sections; preserve tables |
| Dependency user_journey not found | Warn; proceed with defaults |

## Properties

| Property | Value |
|----------|-------|
| Kind | `config` |
| Pillar | P09 |
| Domain | product tour construction |
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
| [[bld_config_ab_test_config]] | sibling | 0.53 |
| [[bld_config_agents_md]] | sibling | 0.52 |
| [[bld_config_collaboration_pattern]] | sibling | 0.52 |
| [[bld_config_repo_map]] | sibling | 0.52 |
