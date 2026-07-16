---
kind: config
id: bld_config_contributor_guide
pillar: P09
llm_function: CONSTRAIN
purpose: Naming, paths, limits for contributor_guide production
quality: null
title: "Config Contributor Guide"
version: "1.0.0"
author: wave1_builder_gen_v2
tags: [contributor_guide, builder, config]
tldr: "Production constraints for contributor guide: naming (p05_cg_{{name}}.md), output paths (P05/), size limit 6144B. Contributor guide."
domain: "contributor_guide construction"
created: "2026-04-14"
updated: "2026-04-14"
8f: "F1_constrain"
keywords: [limits for contributor_guide production, contributor_guide construction, config contributor guide, output paths, size limit, contributor guide, contributor_guide, builder, config, contributor-guide-builder.md]
density_score: 0.85
related:
  - bld_config_integration_guide
  - bld_config_repo_map
  - bld_config_api_reference
  - bld_config_collaboration_pattern
  - bld_config_agents_md
---

## Naming Convention
Files: kebab-case (e.g., `contributor-guide-builder.md`). Directories: PascalCase (e.g., `Src`). Classes: PascalCase. Variables: snake_case.
## Paths
Artifacts stored in: `/repo/src/p05`, `/repo/docs/p05`, `/repo/tests/p05`.

## Limits
max_bytes: 6144. max_turns: 5. effort_level: medium.

## Hooks
pre_build: null. post_build: null. on_error: null. on_quality_fail: null.

## Domain-Specific Constraints

| Constraint | Value |
|-----------|-------|
| Boundary | Contributor guide |
| Dependencies | knowledge_card, context_doc |
| Primary 8F function | F8_collaborate |
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
| Domain | contributor guide construction |
| Pipeline | 8F (F1-F8) |
| Scorer | cex_score.py |
| Compiler | cex_compile.py |
| Retriever | cex_retriever.py |
| Quality target | 9.0+ |
| Density target | 0.85+ |

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[bld_config_integration_guide]] | sibling | 0.56 |
| [[bld_config_repo_map]] | sibling | 0.55 |
| [[bld_config_api_reference]] | sibling | 0.50 |
| [[bld_config_collaboration_pattern]] | sibling | 0.48 |
| [[bld_config_agents_md]] | sibling | 0.48 |
