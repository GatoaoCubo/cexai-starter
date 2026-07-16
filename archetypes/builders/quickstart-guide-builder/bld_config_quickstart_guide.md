---
kind: config
id: bld_config_quickstart_guide
pillar: P09
llm_function: CONSTRAIN
purpose: Naming, paths, limits for quickstart_guide production
quality: null
title: "Config Quickstart Guide"
version: "1.0.0"
author: wave1_builder_gen_v2
tags: [quickstart_guide, builder, config]
tldr: "Production constraints for quickstart guide: naming (p05_qs_{{name}}.md), output paths (P05/), size limit 8192B. Quickstart doc."
domain: "quickstart_guide construction"
created: "2026-04-14"
updated: "2026-04-14"
8f: "F1_constrain"
keywords: [limits for quickstart_guide production, quickstart_guide construction, config quickstart guide, output paths, size limit, quickstart doc, quickstart_guide, builder, config, naming convention
pattern]
density_score: 0.85
related:
  - bld_config_integration_guide
  - bld_config_agents_md
  - bld_config_collaboration_pattern
  - bld_config_api_reference
  - bld_config_repo_map
---

## Naming Convention
Pattern: p05_qs_{{name}}.md
Examples: p05_qs_quickstart.md, p05_qs_tutorial.md

## Paths
Artifacts stored in: /cex/quickstart/guides/p05_qs_{{name}}.md
Intermediate files: /cex/artifacts/quickstart/p05/

## Limits
max_bytes: 8192
max_turns: 5
effort_level: medium

## Hooks
pre_build -- null
post_build -- null
on_error -- null
on_quality_fail -- null

## Domain-Specific Constraints

| Constraint | Value |
|-----------|-------|
| Boundary | Quickstart doc |
| Dependencies | knowledge_card, context_doc |
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
| Domain | quickstart guide construction |
| Pipeline | 8F (F1-F8) |
| Scorer | cex_score.py |
| Compiler | cex_compile.py |
| Retriever | cex_retriever.py |
| Quality target | 9.0+ |
| Density target | 0.85+ |

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[bld_config_integration_guide]] | sibling | 0.54 |
| [[bld_config_agents_md]] | sibling | 0.52 |
| [[bld_config_collaboration_pattern]] | sibling | 0.50 |
| [[bld_config_api_reference]] | sibling | 0.50 |
| [[bld_config_repo_map]] | sibling | 0.50 |
