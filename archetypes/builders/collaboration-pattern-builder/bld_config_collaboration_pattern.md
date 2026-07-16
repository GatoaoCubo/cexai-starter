---
kind: config
id: bld_config_collaboration_pattern
pillar: P09
llm_function: CONSTRAIN
purpose: Naming, paths, limits for collaboration_pattern production
quality: null
title: "Config Collaboration Pattern"
version: "1.0.0"
author: wave1_builder_gen
tags: [collaboration_pattern, builder, config]
tldr: "Production constraints for collaboration pattern: naming (p12_collab_{{name}}.md), output paths (P12/), size limit 5120B. Coordination pattern."
domain: "collaboration_pattern construction"
created: "2026-04-13"
updated: "2026-04-13"
8f: "F1_constrain"
keywords: [limits for collaboration_pattern production, collaboration_pattern construction, config collaboration pattern, output paths, size limit, coordination pattern, collaboration_pattern, builder, config, naming convention
pattern]
density_score: 0.85
related:
  - bld_config_ab_test_config
  - bld_config_api_reference
  - bld_config_agents_md
  - bld_config_workflow_node
  - bld_config_visual_workflow
---

## Naming Convention
Pattern: p12_collab_{{name}}.md
Examples: p12_collab_projectA.md, p12_collab_featureX.md

## Paths
/artifacts/p12/collab/{{name}}/

## Limits
- max_bytes: 5120
- max_turns: 10
- effort_level: medium

## Hooks
- pre_build: null
- post_build: null
- on_error: null
- on_quality_fail: null

## Properties

| Property | Value |
|----------|-------|
| Kind | `config` |
| Pillar | P09 |
| Domain | collaboration_pattern construction |
| Pipeline | 8F (F1-F8) |
| Scorer | cex_score.py |
| Compiler | cex_compile.py |
| Retriever | cex_retriever.py |
| Quality target | 9.0+ |
| Density target | 0.85+ |

## Domain-Specific Constraints

| Constraint | Value |
|-----------|-------|
| Boundary | Coordination pattern |
| Dependencies | workflow, agent_card |
| Primary 8F function | F8_collaborate |
| Max artifact size | 5120 bytes |

## Edge Cases

| Scenario | Handling |
|----------|---------|
| Missing required frontmatter field | Fail H01 gate; return to F6 |
| ID collision with existing artifact | Append version suffix (_v2) |
| Body exceeds 5120 bytes | Trim prose sections; preserve tables |
| Dependency workflow not found | Warn; proceed with defaults |

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[bld_config_ab_test_config]] | sibling | 0.53 |
| [[bld_config_api_reference]] | sibling | 0.53 |
| [[bld_config_agents_md]] | sibling | 0.52 |
| [[bld_config_workflow_node]] | sibling | 0.51 |
| [[bld_config_visual_workflow]] | sibling | 0.51 |
