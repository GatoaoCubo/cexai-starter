---
kind: config
id: bld_config_legal_vertical
pillar: P09
llm_function: CONSTRAIN
purpose: Naming, paths, limits for legal_vertical production
quality: null
title: "Config Legal Vertical"
version: "1.0.0"
author: wave1_builder_gen_v2
tags: [legal_vertical, builder, config]
tldr: "Production constraints for legal vertical: naming (p01_lv_{{name}}.md), output paths (P01/), size limit 6144B. Legal vertical KC."
domain: "legal_vertical construction"
created: "2026-04-14"
updated: "2026-04-14"
8f: "F1_constrain"
keywords: [limits for legal_vertical production, legal_vertical construction, config legal vertical, output paths, size limit, legal vertical kc, legal_vertical, builder, config, naming convention
pattern]
density_score: 0.85
related:
  - bld_config_ab_test_config
  - bld_config_customer_segment
  - bld_config_rl_algorithm
  - bld_config_api_reference
  - bld_config_graph_rag_config
---

p01_lv_{{name}}.md
## Naming Convention
Pattern: p01_lv_{{name}}.md
Examples: p01_lv_compliance_policy.md, p01_lv_data_privacy.md

## Paths
/mnt/artifacts/p01/legal_vertical/{{name}}
/mnt/logs/p01/{{name}}_build.log

## Limits
max_bytes: 6144
max_turns: 5
effort_level: 3

## Hooks
pre_build: null
post_build: null
on_error: null
on_quality_fail: null

## Domain-Specific Constraints

| Constraint | Value |
|-----------|-------|
| Boundary | Legal vertical KC |
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
| Domain | legal vertical construction |
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
| [[bld_config_customer_segment]] | sibling | 0.49 |
| [[bld_config_rl_algorithm]] | sibling | 0.49 |
| [[bld_config_api_reference]] | sibling | 0.49 |
| [[bld_config_graph_rag_config]] | sibling | 0.48 |
