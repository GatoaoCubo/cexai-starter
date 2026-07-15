---
kind: config
id: bld_config_dataset_card
pillar: P09
llm_function: CONSTRAIN
purpose: Naming, paths, limits for dataset_card production
quality: null
title: "Config Dataset Card"
version: "1.0.0"
author: wave1_builder_gen
tags: [dataset_card, builder, config]
tldr: "Production constraints for dataset card: naming (p01_dc_{{name}}.md), output paths (P01/), size limit 5120B. Dataset documentation."
domain: "dataset_card construction"
created: "2026-04-13"
updated: "2026-04-13"
8f: "F1_constrain"
keywords: [limits for dataset_card production, dataset_card construction, config dataset card, output paths, size limit, dataset documentation, dataset_card, builder, config, naming convention
pattern]
density_score: 0.85
related:
  - bld_config_collaboration_pattern
  - bld_config_repo_map
  - bld_config_api_reference
  - bld_config_agents_md
  - bld_config_ab_test_config
---

## Naming Convention
Pattern: p01_dc_{{name}}.md (dataset card id)
Examples: p01_dc_train.md, p01_dc_validation.md

## Paths
Artifacts: ./artifacts/p01/dataset_cards/
Source metadata: ./artifacts/p01/dataset_sources/
Card registry: ./artifacts/p01/dataset_card_registry.yaml

## Limits
max_bytes: 5120
max_turns: 10
effort_level: medium

## Card Fields (HuggingFace dataset_card schema)
required: [dataset_name, source, license, task_categories, languages, size]
optional: [pii_handling, data_collection, annotation_process]

## Hooks
pre_build: validate_dataset_source_accessibility
post_build: register_dataset_card
on_error: null
on_quality_fail: null

## Domain-Specific Constraints

| Constraint | Value |
|-----------|-------|
| Boundary | Dataset documentation |
| Dependencies | citation |
| Primary 8F function | F3_inject |
| Max artifact size | 5120 bytes |

## Edge Cases

| Scenario | Handling |
|----------|---------|
| Missing required frontmatter field | Fail H01 gate; return to F6 |
| ID collision with existing artifact | Append version suffix (_v2) |
| Body exceeds 5120 bytes | Trim prose sections; preserve tables |
| Dependency citation not found | Warn; proceed with defaults |

## Properties

| Property | Value |
|----------|-------|
| Kind | `config` |
| Pillar | P09 |
| Domain | dataset card construction |
| Pipeline | 8F (F1-F8) |
| Scorer | cex_score.py |
| Compiler | cex_compile.py |
| Retriever | cex_retriever.py |
| Quality target | 9.0+ |
| Density target | 0.85+ |

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| bld_config_collaboration_pattern | sibling | 0.47 |
| bld_config_repo_map | sibling | 0.47 |
| bld_config_api_reference | sibling | 0.47 |
| bld_config_agents_md | sibling | 0.47 |
| bld_config_ab_test_config | sibling | 0.47 |
