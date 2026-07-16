---
kind: config
id: bld_config_healthcare_vertical
pillar: P09
llm_function: CONSTRAIN
purpose: Naming, paths, limits for healthcare_vertical production
quality: null
title: "Config Healthcare Vertical"
version: "1.0.0"
author: wave1_builder_gen_v2
tags: [healthcare_vertical, builder, config]
tldr: "Production constraints for healthcare vertical: naming (p01_hv_{{name}}.md), output paths (P01/), size limit 6144B. Healthcare vertical KC."
domain: "healthcare_vertical construction"
created: "2026-04-14"
updated: "2026-04-14"
8f: "F1_constrain"
keywords: [limits for healthcare_vertical production, healthcare_vertical construction, config healthcare vertical, output paths, size limit, healthcare vertical kc, healthcare_vertical, builder, config, "p01_hv_{{name}}.md"]
density_score: 0.85
related:
  - bld_config_agents_md
  - bld_config_api_reference
  - bld_config_search_strategy
  - bld_config_ab_test_config
  - bld_config_discovery_questions
---

## Naming Convention
Pattern: `p01_hv_{{name}}.md`
Examples:
- `p01_hv_example.md`
- `p01_hv_patient_portal.md`

## Paths
Artifacts stored in: `/cex/verticals/P01/{{name}}/artifacts/`

## Limits
max_bytes: 6144
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
| Boundary | Healthcare vertical KC |
| Dependencies | customer_segment, knowledge_card |
| Primary 8F function | F1_constrain |
| Max artifact size | 6144 bytes |

## Edge Cases

| Scenario | Handling |
|----------|---------|
| Missing required frontmatter field | Fail H01 gate; return to F6 |
| ID collision with existing artifact | Append version suffix (_v2) |
| Body exceeds 6144 bytes | Trim prose sections; preserve tables |
| Dependency customer_segment not found | Warn; proceed with defaults |

## Properties

| Property | Value |
|----------|-------|
| Kind | `config` |
| Pillar | P09 |
| Domain | healthcare vertical construction |
| Pipeline | 8F (F1-F8) |
| Scorer | cex_score.py |
| Compiler | cex_compile.py |
| Retriever | cex_retriever.py |
| Quality target | 9.0+ |
| Density target | 0.85+ |

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[bld_config_agents_md]] | sibling | 0.54 |
| [[bld_config_api_reference]] | sibling | 0.52 |
| [[bld_config_search_strategy]] | sibling | 0.52 |
| [[bld_config_ab_test_config]] | sibling | 0.51 |
| [[bld_config_discovery_questions]] | sibling | 0.51 |
