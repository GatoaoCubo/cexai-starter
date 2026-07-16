---
kind: config
id: bld_config_discovery_questions
pillar: P09
llm_function: CONSTRAIN
purpose: Naming, paths, limits for discovery_questions production
quality: null
title: "Config Discovery Questions"
version: "1.0.0"
author: wave1_builder_gen_v2
tags: [discovery_questions, builder, config]
tldr: "Production constraints for discovery questions: naming (p01_dq_{{name}}.md), output paths (P01/), size limit 4096B. Discovery qs."
domain: "discovery_questions construction"
created: "2026-04-14"
updated: "2026-04-14"
8f: "F1_constrain"
keywords: [limits for discovery_questions production, discovery_questions construction, config discovery questions, output paths, size limit, discovery qs, discovery_questions, builder, config, p01_dq_<name>.md]
density_score: 0.85
related:
  - bld_config_api_reference
  - bld_config_repo_map
  - bld_config_ab_test_config
  - bld_config_collaboration_pattern
  - bld_config_agents_md
---

## Naming Convention
Pattern: `p01_dq_<name>.md` (e.g., `p01_dq_customer.md`, `p01_dq_product.md`)

## Paths
`/artifacts/p01/discovery_questions/{{name}}.md`
`/templates/p01/dq_template.md`

## Limits
- max_bytes: 4096
- max_turns: 5
- effort_level: 3

## Hooks
- pre_build: null
- post_build: null
- on_error: null
- on_quality_fail: null

## Domain-Specific Constraints

| Constraint | Value |
|-----------|-------|
| Boundary | Discovery qs |
| Dependencies | customer_segment, knowledge_card |
| Primary 8F function | F4_reason |
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
| Domain | discovery questions construction |
| Pipeline | 8F (F1-F8) |
| Scorer | cex_score.py |
| Compiler | cex_compile.py |
| Retriever | cex_retriever.py |
| Quality target | 9.0+ |
| Density target | 0.85+ |

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[bld_config_api_reference]] | sibling | 0.56 |
| [[bld_config_repo_map]] | sibling | 0.54 |
| [[bld_config_ab_test_config]] | sibling | 0.52 |
| [[bld_config_collaboration_pattern]] | sibling | 0.52 |
| [[bld_config_agents_md]] | sibling | 0.51 |
