---
kind: config
id: bld_config_repo_map
pillar: P09
llm_function: CONSTRAIN
purpose: Naming, paths, limits for repo_map production
quality: null
title: "Config Repo Map"
version: "1.0.0"
author: wave1_builder_gen
tags: [repo_map, builder, config]
tldr: "Production constraints for repo map: naming (p01_rm_{{name}}.md), output paths (P01/), size limit 5120B. Repo context map."
domain: "repo_map construction"
created: "2026-04-13"
updated: "2026-04-13"
8f: "F1_constrain"
keywords: [limits for repo_map production, repo_map construction, config repo map, output paths, size limit, repo context map, repo_map, builder, config, "p01_rm_{{name}}.md"]
density_score: 0.85
related:
  - bld_config_api_reference
  - bld_config_ab_test_config
  - bld_config_agents_md
  - bld_config_collaboration_pattern
  - bld_config_discovery_questions
---

## Naming Convention  
Pattern: `p01_rm_{{name}}.md`  
Examples:  
- `p01_rm_projectA.md`  
- `p01_rm_dataScience.md`  

## Paths  
- Root: `/repo_maps/`  
- Per Pillar: `/repo_maps/P01/{{name}}/`  

## Limits  
- max_bytes: 5120  
- max_turns: 10  
- effort_level: 3  

## Hooks  
- pre_build: null  
- post_build: null  
- on_error: null  
- on_quality_fail: null

## Domain-Specific Constraints

| Constraint | Value |
|-----------|-------|
| Boundary | Repo context map |
| Dependencies | knowledge_card, context_doc |
| Primary 8F function | F4_reason |
| Max artifact size | 5120 bytes |

## Edge Cases

| Scenario | Handling |
|----------|---------|
| Missing required frontmatter field | Fail H01 gate; return to F6 |
| ID collision with existing artifact | Append version suffix (_v2) |
| Body exceeds 5120 bytes | Trim prose sections; preserve tables |
| Dependency knowledge_card not found | Warn; proceed with defaults |

## Properties

| Property | Value |
|----------|-------|
| Kind | `config` |
| Pillar | P09 |
| Domain | repo map construction |
| Pipeline | 8F (F1-F8) |
| Scorer | cex_score.py |
| Compiler | cex_compile.py |
| Retriever | cex_retriever.py |
| Quality target | 9.0+ |
| Density target | 0.85+ |

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[bld_config_api_reference]] | sibling | 0.55 |
| [[bld_config_ab_test_config]] | sibling | 0.52 |
| [[bld_config_agents_md]] | sibling | 0.52 |
| [[bld_config_collaboration_pattern]] | sibling | 0.52 |
| [[bld_config_discovery_questions]] | sibling | 0.51 |
