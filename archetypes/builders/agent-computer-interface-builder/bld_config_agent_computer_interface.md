---
kind: config
id: bld_config_agent_computer_interface
pillar: P09
llm_function: CONSTRAIN
purpose: Naming, paths, limits for agent_computer_interface production
quality: null
title: "Config Agent Computer Interface"
version: "1.0.0"
author: wave1_builder_gen
tags: [agent_computer_interface, builder, config]
tldr: "Production constraints for agent computer interface: naming (p08_aci_{{name}}.md), output paths (P08/), size limit 5120B. Agent-computer interface."
domain: "agent_computer_interface construction"
created: "2026-04-13"
updated: "2026-04-13"
8f: "F1_constrain"
keywords: [limits for agent_computer_interface production, agent_computer_interface construction, config agent computer interface, output paths, size limit, agent-computer interface, agent_computer_interface, builder, config, naming convention
pattern]
density_score: 0.85
related:
  - bld_config_agents_md
  - bld_config_agent_profile
  - bld_config_api_reference
  - bld_config_collaboration_pattern
  - bld_config_repo_map
---

## Naming Convention
Pattern: p08_aci_{{name}}.md
Examples:
- p08_aci_auth_module.md
- p08_aci_data_parser.md

## Paths
Artifacts: ./artifacts/p08_aci/

## Limits
max_bytes: 5120
max_turns: 15
effort_level: medium

## Hooks
pre_build: null
post_build: null
on_error: null
on_quality_fail: null

## Domain-Specific Constraints

| Constraint | Value |
|-----------|-------|
| Boundary | Agent-computer interface |
| Dependencies | agent_card, computer_use |
| Primary 8F function | F2_become |
| Max artifact size | 5120 bytes |

## Edge Cases

| Scenario | Handling |
|----------|---------|
| Missing required frontmatter field | Fail H01 gate; return to F6 |
| ID collision with existing artifact | Append version suffix (_v2) |
| Body exceeds 5120 bytes | Trim prose sections; preserve tables |
| Dependency agent_card not found | Warn; proceed with defaults |

## Properties

| Property | Value |
|----------|-------|
| Kind | `config` |
| Pillar | P09 |
| Domain | agent computer interface construction |
| Pipeline | 8F (F1-F8) |
| Scorer | cex_score.py |
| Compiler | cex_compile.py |
| Retriever | cex_retriever.py |
| Quality target | 9.0+ |
| Density target | 0.85+ |

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[bld_config_agents_md]] | sibling | 0.55 |
| [[bld_config_agent_profile]] | sibling | 0.54 |
| [[bld_config_api_reference]] | sibling | 0.54 |
| [[bld_config_collaboration_pattern]] | sibling | 0.53 |
| [[bld_config_repo_map]] | sibling | 0.52 |
