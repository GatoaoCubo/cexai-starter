---
kind: config
id: bld_config_course_module
pillar: P09
llm_function: CONSTRAIN
purpose: Naming, paths, limits for course_module production
quality: null
title: "Config Course Module"
version: "1.0.0"
author: wave1_builder_gen_v2
tags: [course_module, builder, config]
tldr: "Production constraints for course module: naming (p05_cm_{{name}}.md), output paths (P05/), size limit 8192B. Course content module."
domain: "course_module construction"
created: "2026-04-14"
updated: "2026-04-14"
8f: "F1_constrain"
keywords: [limits for course_module production, course_module construction, config course module, output paths, size limit, course content module, course_module, builder, config, "p05_cm_{{name}}.md"]
density_score: 0.85
related:
  - bld_config_integration_guide
  - bld_config_agents_md
  - bld_config_api_reference
  - bld_config_collaboration_pattern
  - bld_config_search_strategy
---

p05_cm_{{name}}.md
Pillar: P05

## Naming Convention
Pattern: `p05_cm_{{name}}.md`
Examples: `p05_cm_intro.md`, `p05_cm_lesson1.md`

## Paths
Artifacts stored in: `/opt/cex/course_modules/p05/{{name}}.md`

## Limits
max_bytes: 8192
max_turns: 5
effort_level: medium

## Hooks
pre_build: null
post_build: null
on_error: null
on_quality_fail: null

## Domain-Specific Constraints

| Constraint | Value |
|-----------|-------|
| Boundary | Course content module |
| Dependencies | knowledge_card, scoring_rubric |
| Primary 8F function | F6_produce |
| Max artifact size | 8192 bytes |

## Edge Cases

| Scenario | Handling |
|----------|---------|
| Missing required frontmatter field | Fail H01 gate; return to F6 |
| ID collision with existing artifact | Append version suffix (_v2) |
| Body exceeds 8192 bytes | Trim prose sections; preserve tables |
| Dependency knowledge_card not found | Warn; proceed with defaults |

## Properties

| Property | Value |
|----------|-------|
| Kind | `config` |
| Pillar | P09 |
| Domain | course module construction |
| Pipeline | 8F (F1-F8) |
| Scorer | cex_score.py |
| Compiler | cex_compile.py |
| Retriever | cex_retriever.py |
| Quality target | 9.0+ |
| Density target | 0.85+ |

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[bld_config_integration_guide]] | sibling | 0.52 |
| [[bld_config_agents_md]] | sibling | 0.52 |
| [[bld_config_api_reference]] | sibling | 0.51 |
| [[bld_config_collaboration_pattern]] | sibling | 0.50 |
| [[bld_config_search_strategy]] | sibling | 0.50 |
