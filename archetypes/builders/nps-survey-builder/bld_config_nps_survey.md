---
kind: config
id: bld_config_nps_survey
pillar: P09
llm_function: CONSTRAIN
purpose: Naming, paths, limits for nps_survey production
quality: null
title: "Config Nps Survey"
version: "1.0.0"
author: n05_wave6
tags: [nps_survey, builder, config]
tldr: "Production constraints for nps survey: naming (p11_nps_{{name}}.yaml), output paths (P11/), size limit 3072B. NPS survey."
domain: "nps_survey construction"
created: "2026-04-14"
updated: "2026-04-14"
8f: "F1_constrain"
keywords: [limits for nps_survey production, nps_survey construction, config nps survey, output paths, size limit, nps survey, nps_survey, builder, config, "p11_nps_{{name}}.yaml"]
density_score: 0.85
related:
  - bld_config_ab_test_config
  - bld_config_api_reference
  - bld_config_agents_md
  - bld_config_discovery_questions
  - bld_config_collaboration_pattern
---

## Naming Convention
Pattern: `p11_nps_{{name}}.yaml`
Examples: `p11_nps_onboarding_30d.yaml`, `p11_nps_post_support.yaml`

## Paths
Artifacts stored in: `P11_feedback/surveys/nps/`

## Limits
max_bytes: 3072
max_turns: 4
effort_level: 2

## Hooks
pre_build: validate segment filters against customer_segment registry
post_build: compile + signal N06 with promoter target list
on_error: log to `.cex/runtime/signals/nps_error.json`
on_quality_fail: rebuild with stricter Bain phrasing

## Domain-Specific Constraints

| Constraint | Value |
|-----------|-------|
| Boundary | NPS survey |
| Dependencies | customer_segment, knowledge_card |
| Primary 8F function | F7_govern |
| Max artifact size | 3072 bytes |

## Edge Cases

| Scenario | Handling |
|----------|---------|
| Missing required frontmatter field | Fail H01 gate; return to F6 |
| ID collision with existing artifact | Append version suffix (_v2) |
| Body exceeds 3072 bytes | Trim prose sections; preserve tables |
| Dependency customer_segment not found | Warn; proceed with defaults |

## Properties

| Property | Value |
|----------|-------|
| Kind | `config` |
| Pillar | P09 |
| Domain | nps survey construction |
| Pipeline | 8F (F1-F8) |
| Scorer | cex_score.py |
| Compiler | cex_compile.py |
| Retriever | cex_retriever.py |
| Quality target | 9.0+ |
| Density target | 0.85+ |

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[bld_config_ab_test_config]] | sibling | 0.48 |
| [[bld_config_api_reference]] | sibling | 0.46 |
| [[bld_config_agents_md]] | sibling | 0.46 |
| [[bld_config_discovery_questions]] | sibling | 0.45 |
| [[bld_config_collaboration_pattern]] | sibling | 0.45 |
