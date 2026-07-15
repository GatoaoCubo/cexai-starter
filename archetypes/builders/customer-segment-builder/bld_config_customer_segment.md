---
kind: config
id: bld_config_customer_segment
pillar: P09
llm_function: CONSTRAIN
purpose: Naming, paths, limits for customer_segment production
quality: null
title: "Config Customer Segment"
version: "1.0.0"
author: wave1_builder_gen_v2
tags: [customer_segment, builder, config]
tldr: "Production constraints for customer segment: naming (p02_cs_{{name}}.md), output paths (P02/), size limit 4096B. ICP artifact."
domain: "customer_segment construction"
created: "2026-04-14"
updated: "2026-04-14"
8f: "F1_constrain"
keywords: [limits for customer_segment production, customer_segment construction, config customer segment, output paths, size limit, icp artifact, customer_segment, builder, config, "p02_cs_{{name}}"]
density_score: 0.85
related:
  - bld_config_api_reference
  - bld_config_repo_map
  - bld_config_ab_test_config
  - bld_config_agents_md
  - bld_config_collaboration_pattern
---

## Naming Convention
Pattern: `p02_cs_{{name}}`
Examples: `p02_cs_high_value`, `p02_cs_churn_risk`

## Paths
Artifacts: `/data/segments/p02/{{name}}/artifacts`
Logs: `/logs/p02/{{name}}`

## Limits
max_bytes: 4096
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
| Boundary | ICP artifact |
| Dependencies | knowledge_card |
| Primary 8F function | F4_reason |
| Max artifact size | 4096 bytes |

## Edge Cases

| Scenario | Handling |
|----------|---------|
| Missing required frontmatter field | Fail H01 gate; return to F6 |
| ID collision with existing artifact | Append version suffix (_v2) |
| Body exceeds 4096 bytes | Trim prose sections; preserve tables |
| Dependency knowledge_card not found | Warn; proceed with defaults |

## Properties

| Property | Value |
|----------|-------|
| Kind | `config` |
| Pillar | P09 |
| Domain | customer segment construction |
| Pipeline | 8F (F1-F8) |
| Scorer | cex_score.py |
| Compiler | cex_compile.py |
| Retriever | cex_retriever.py |
| Quality target | 9.0+ |
| Density target | 0.85+ |

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| bld_config_api_reference | sibling | 0.52 |
| bld_config_repo_map | sibling | 0.52 |
| bld_config_ab_test_config | sibling | 0.52 |
| bld_config_agents_md | sibling | 0.51 |
| bld_config_collaboration_pattern | sibling | 0.50 |
