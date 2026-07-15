---
kind: config
id: bld_config_role_assignment
pillar: P09
llm_function: CONSTRAIN
purpose: Naming, paths, limits for role_assignment production
quality: null
title: "Config Role Assignment"
version: "1.0.0"
author: n03_wave8_builder
tags: [role_assignment, builder, config, composable, crewai]
tldr: "Production constraints for role assignment: naming (p02_ra_{{role}}.md), output paths (P02/), size limit 3072B. Binds builder/sub-agent to crew role (CrewAI Agent class)."
domain: "role_assignment construction"
created: "2026-04-14"
updated: "2026-04-14"
8f: "F1_constrain"
keywords: [limits for role_assignment production, role_assignment construction, config role assignment, output paths, size limit, binds builder, sub-agent to crew role, crewai agent class, role_assignment, builder]
density_score: 0.86
related:
  - bld_config_agent_profile
  - bld_config_agents_md
  - bld_config_vc_credential
  - bld_config_crew_template
  - bld_config_api_reference
---

## Naming Convention
Pattern: `p02_ra_`{{role_name}}`.md`
Examples: `p02_ra_domain_researcher.md`, `p02_ra_peer_reviewer.md`, `p02_ra_brief_editor.md`, `p02_ra_research_manager.md`

## Paths
Artifacts stored in: `P02_model/role_assignments/`{{role_name}}`.md`
Compiled YAML: `P02_model/role_assignments/compiled/`{{role_name}}`.yaml`
Index entry: `.cex/indices/roles.json`

## Limits
max_bytes: 3072
max_turns: 3
effort_level: 2
max_responsibilities: 5
max_tools_allowed: 12
backstory_max_chars: 300
goal_max_chars: 150

## Hooks
pre_build: resolve_agent_id_against_registry
post_build: compile_to_yaml
on_error: null
on_quality_fail: rebuild_with_peer_review

## Domain-Specific Constraints

| Constraint | Value |
|-----------|-------|
| Boundary | Binds builder/sub-agent to crew role (CrewAI Agent class) |
| Dependencies | agent_card, capability_registry |
| Primary 8F function | F2_become |
| Max artifact size | 3072 bytes |

## Edge Cases

| Scenario | Handling |
|----------|---------|
| Missing required frontmatter field | Fail H01 gate; return to F6 |
| ID collision with existing artifact | Append version suffix (_v2) |
| Body exceeds 3072 bytes | Trim prose sections; preserve tables |
| Dependency agent_card not found | Warn; proceed with defaults |

## Properties

| Property | Value |
|----------|-------|
| Kind | `config` |
| Pillar | P09 |
| Domain | role assignment construction |
| Pipeline | 8F (F1-F8) |
| Scorer | cex_score.py |
| Compiler | cex_compile.py |
| Retriever | cex_retriever.py |
| Quality target | 9.0+ |
| Density target | 0.85+ |

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[bld_config_agent_profile]] | sibling | 0.50 |
| bld_config_agents_md | sibling | 0.50 |
| bld_config_vc_credential | sibling | 0.47 |
| [[bld_config_crew_template]] | sibling | 0.46 |
| bld_config_api_reference | sibling | 0.46 |
