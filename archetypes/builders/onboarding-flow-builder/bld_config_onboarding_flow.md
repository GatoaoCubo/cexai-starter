---
kind: config
id: bld_config_onboarding_flow
pillar: P09
llm_function: CONSTRAIN
purpose: Naming, paths, limits for onboarding_flow production
quality: null
title: "Config Onboarding Flow"
version: "1.0.0"
author: wave1_builder_gen_v2
tags: [onboarding_flow, builder, config]
tldr: "Production constraints for onboarding flow: naming (p05_of_{{name}}.md), output paths (P05/), size limit 5120B. Activation flow."
domain: "onboarding_flow construction"
created: "2026-04-14"
updated: "2026-04-14"
8f: "F1_constrain"
keywords: [limits for onboarding_flow production, onboarding_flow construction, config onboarding flow, output paths, size limit, activation flow, onboarding_flow, builder, config, naming convention
pattern]
density_score: 0.85
related:
  - bld_config_integration_guide
  - bld_config_api_reference
  - bld_config_agents_md
  - bld_config_pricing_page
  - bld_config_collaboration_pattern
---

p05_of_{{name}}.md
Pillar: P05

## Naming Convention
Pattern: p05_of_{{name}}.md
Examples: p05_of_user_onboarding.md, p05_of_payment_setup.md

## Paths
/opt/cex/flows/p05/{{name}}
Example: /opt/cex/flows/p05/user_onboarding

## Limits
max_bytes: 5120
max_turns: 10
effort_level: medium

## Hooks
pre_build: null
post_build: null
on_error: null
on_quality_fail: null

## Domain-Specific Constraints

| Constraint | Value |
|-----------|-------|
| Boundary | Activation flow |
| Dependencies | user_journey, knowledge_card |
| Primary 8F function | F6_produce |
| Max artifact size | 5120 bytes |

## Edge Cases

| Scenario | Handling |
|----------|---------|
| Missing required frontmatter field | Fail H01 gate; return to F6 |
| ID collision with existing artifact | Append version suffix (_v2) |
| Body exceeds 5120 bytes | Trim prose sections; preserve tables |
| Dependency user_journey not found | Warn; proceed with defaults |

## Properties

| Property | Value |
|----------|-------|
| Kind | `config` |
| Pillar | P09 |
| Domain | onboarding flow construction |
| Pipeline | 8F (F1-F8) |
| Scorer | cex_score.py |
| Compiler | cex_compile.py |
| Retriever | cex_retriever.py |
| Quality target | 9.0+ |
| Density target | 0.85+ |

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[bld_config_integration_guide]] | sibling | 0.48 |
| [[bld_config_api_reference]] | sibling | 0.47 |
| [[bld_config_agents_md]] | sibling | 0.47 |
| [[bld_config_pricing_page]] | sibling | 0.47 |
| [[bld_config_collaboration_pattern]] | sibling | 0.46 |
