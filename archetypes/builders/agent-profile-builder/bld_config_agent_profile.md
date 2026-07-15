---
kind: config
id: bld_config_agent_profile
pillar: P09
llm_function: CONSTRAIN
purpose: Naming, paths, limits for agent_profile production
quality: null
title: "Config Agent Profile"
version: "1.0.0"
author: wave1_builder_gen
tags: [agent_profile, builder, config]
tldr: "Production constraints for agent profile: naming (p02_ap_{{name}}.md), output paths (P02/), size limit 4096B. Agent persona construction."
domain: "agent_profile construction"
created: "2026-04-13"
updated: "2026-04-13"
8f: "F1_constrain"
keywords: [limits for agent_profile production, agent_profile construction, config agent profile, output paths, size limit, agent persona construction, agent_profile, builder, config, "p02_ap_{{name}}.md"]
density_score: 0.85
related:
  - bld_config_agents_md
  - bld_config_collaboration_pattern
  - bld_config_api_reference
  - bld_config_search_strategy
  - bld_config_integration_guide
---

## Naming Convention
Pattern: `p02_ap_{{name}}.md`
Examples: `p02_ap_john.md`, `p02_ap_sarah.md`

## Paths
Artifacts stored in: `/artifacts/p02/profiles/`
Example path: `/artifacts/p02/profiles/john.md`

## Limits
max_bytes: 4096
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
| Boundary | Agent persona construction |
| Dependencies | agent, agent_card |
| Primary 8F function | F2_become |
| Max artifact size | 4096 bytes |

## Edge Cases

| Scenario | Handling |
|----------|---------|
| Missing required frontmatter field | Fail H01 gate; return to F6 |
| ID collision with existing artifact | Append version suffix (_v2) |
| Body exceeds 4096 bytes | Trim prose sections; preserve tables |
| Dependency agent not found | Warn; proceed with defaults |

## Properties

| Property | Value |
|----------|-------|
| Kind | `config` |
| Pillar | P09 |
| Domain | agent profile construction |
| Pipeline | 8F (F1-F8) |
| Scorer | cex_score.py |
| Compiler | cex_compile.py |
| Retriever | cex_retriever.py |
| Quality target | 9.0+ |
| Density target | 0.85+ |

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| bld_config_agents_md | sibling | 0.58 |
| bld_config_collaboration_pattern | sibling | 0.50 |
| bld_config_api_reference | sibling | 0.50 |
| bld_config_search_strategy | sibling | 0.49 |
| bld_config_integration_guide | sibling | 0.49 |
