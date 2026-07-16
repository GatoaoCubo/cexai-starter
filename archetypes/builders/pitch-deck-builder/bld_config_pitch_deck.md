---
kind: config
id: bld_config_pitch_deck
pillar: P09
llm_function: CONSTRAIN
purpose: Naming, paths, limits for pitch_deck production
quality: null
title: "Config Pitch Deck"
version: "1.0.0"
author: wave1_builder_gen_v2
tags: [pitch_deck, builder, config]
tldr: "Production constraints for pitch deck: naming (p05_pd_{{name}}.md), output paths (P05/), size limit 6144B. Pitch deck."
domain: "pitch_deck construction"
created: "2026-04-14"
updated: "2026-04-14"
8f: "F1_constrain"
keywords: [limits for pitch_deck production, pitch_deck construction, config pitch deck, output paths, size limit, pitch deck, pitch_deck, builder, config, naming convention]
density_score: 0.85
related:
  - bld_config_api_reference
  - bld_config_ab_test_config
  - bld_config_collaboration_pattern
  - bld_config_integration_guide
  - bld_config_repo_map
---

## Naming Convention (pitch deck artifacts)
Pattern: p05_pd_<project_name>.md (e.g., p05_pd_innovateX.md, p05_pd_neuroFlow.md) for each pitch deck

## Paths
/artifacts/p05/pd/<project_name>/output.md

## Limits
max_bytes: 6144
max_turns: 5
effort_level: high

## Hooks
pre_build: null
post_build: null
on_error: null
on_quality_fail: null

## Domain-Specific Constraints

| Constraint | Value |
|-----------|-------|
| Boundary | Pitch deck |
| Dependencies | knowledge_card, customer_segment |
| Primary 8F function | F6_produce |
| Max artifact size | 6144 bytes |

## Edge Cases

| Scenario | Handling |
|----------|---------|
| Missing required frontmatter field | Fail H01 gate; return to F6 |
| ID collision with existing artifact | Append version suffix (_v2) |
| Body exceeds 6144 bytes | Trim prose sections; preserve tables |
| Dependency knowledge_card not found | Warn; proceed with defaults |

## Properties

| Property | Value |
|----------|-------|
| Kind | `config` |
| Pillar | P09 |
| Domain | pitch deck construction |
| Pipeline | 8F (F1-F8) |
| Scorer | cex_score.py |
| Compiler | cex_compile.py |
| Retriever | cex_retriever.py |
| Quality target | 9.0+ |
| Density target | 0.85+ |

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[bld_config_api_reference]] | sibling | 0.51 |
| [[bld_config_ab_test_config]] | sibling | 0.50 |
| [[bld_config_collaboration_pattern]] | sibling | 0.49 |
| [[bld_config_integration_guide]] | sibling | 0.49 |
| [[bld_config_repo_map]] | sibling | 0.49 |
