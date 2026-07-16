---
kind: config
id: bld_config_visual_workflow
pillar: P09
llm_function: CONSTRAIN
purpose: Naming, paths, limits for visual_workflow production
quality: null
title: "Config Visual Workflow"
version: "1.0.0"
author: wave1_builder_gen_v2
tags: [visual_workflow, builder, config]
tldr: "Production constraints for visual workflow: naming (p12_vw_{{name}}.md), output paths (P12/), size limit 5120B. Visual workflow editor."
domain: "visual_workflow construction"
created: "2026-04-14"
updated: "2026-04-14"
8f: "F1_constrain"
keywords: [limits for visual_workflow production, visual_workflow construction, config visual workflow, output paths, size limit, visual workflow editor, visual_workflow, builder, config, "p12_vw_{{name}}.md"]
density_score: 0.85
related:
  - bld_config_collaboration_pattern
  - bld_config_workflow_node
  - bld_config_agents_md
  - bld_config_ab_test_config
  - bld_config_api_reference
---

## Naming Convention
Pattern: `p12_vw_{{name}}.md`
Examples: `p12_vw_onboarding.md`, `p12_vw_data_processing.md`

## Paths
Artifacts stored in: `/opt/cex/p12/workflows/{{name}}.md`

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
| Boundary | Visual workflow editor |
| Dependencies | workflow, diagram |
| Primary 8F function | F6_produce |
| Max artifact size | 5120 bytes |

## Edge Cases

| Scenario | Handling |
|----------|---------|
| Missing required frontmatter field | Fail H01 gate; return to F6 |
| ID collision with existing artifact | Append version suffix (_v2) |
| Body exceeds 5120 bytes | Trim prose sections; preserve tables |
| Dependency workflow not found | Warn; proceed with defaults |

## Properties

| Property | Value |
|----------|-------|
| Kind | `config` |
| Pillar | P09 |
| Domain | visual workflow construction |
| Pipeline | 8F (F1-F8) |
| Scorer | cex_score.py |
| Compiler | cex_compile.py |
| Retriever | cex_retriever.py |
| Quality target | 9.0+ |
| Density target | 0.85+ |

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[bld_config_collaboration_pattern]] | sibling | 0.54 |
| [[bld_config_workflow_node]] | sibling | 0.53 |
| [[bld_config_agents_md]] | sibling | 0.52 |
| [[bld_config_ab_test_config]] | sibling | 0.50 |
| [[bld_config_api_reference]] | sibling | 0.50 |
