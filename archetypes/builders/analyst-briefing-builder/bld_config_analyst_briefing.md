---
kind: config
id: bld_config_analyst_briefing
pillar: P09
llm_function: CONSTRAIN
purpose: Naming, paths, limits for analyst_briefing production
quality: null
title: "Config Analyst Briefing"
version: "1.0.0"
author: n01_wave6
tags: [analyst_briefing, builder, config]
tldr: "Production constraints for analyst briefing: naming (p05_ab_{{name}}.md), output paths (P05/), size limit 6144B. Analyst briefing."
domain: "analyst_briefing construction"
created: "2026-04-14"
updated: "2026-04-14"
8f: "F1_constrain"
keywords: [limits for analyst_briefing production, analyst_briefing construction, config analyst briefing, output paths, size limit, analyst briefing, analyst_briefing, builder, config, p05_ab_acme_gartner_2026.md]
density_score: 0.85
related:
  - bld_config_repo_map
  - bld_config_agents_md
  - bld_config_integration_guide
  - bld_config_api_reference
  - bld_config_vc_credential
---

## Naming Convention
Pattern: `p05_ab_`{{vendor_slug}}`_`{{analyst_firm}}`_`{{year}}`.md`
Examples: `p05_ab_acme_gartner_2026.md`, `p05_ab_techco_forrester_2026.md`

## Paths
Artifacts stored in: `/artifacts/p05/analyst_briefings/`{{vendor_slug}}`/`

## Limits
max_bytes: 6144
max_turns: 6
effort_level: 4

## Hooks
pre_build: validate proof_point_count >= 3
post_build: run bld_quality_gate (HARD gates H01-H08)
on_error: log to ar_error_log.md
on_quality_fail: escalate to AR team lead

## Domain-Specific Constraints

| Constraint | Value |
|-----------|-------|
| Boundary | Analyst briefing |
| Dependencies | knowledge_card, scoring_rubric |
| Primary 8F function | F4_reason |
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
| Domain | analyst briefing construction |
| Pipeline | 8F (F1-F8) |
| Scorer | cex_score.py |
| Compiler | cex_compile.py |
| Retriever | cex_retriever.py |
| Quality target | 9.0+ |
| Density target | 0.85+ |

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[bld_config_repo_map]] | sibling | 0.50 |
| [[bld_config_agents_md]] | sibling | 0.50 |
| [[bld_config_integration_guide]] | sibling | 0.50 |
| [[bld_config_api_reference]] | sibling | 0.50 |
| [[bld_config_vc_credential]] | sibling | 0.49 |
