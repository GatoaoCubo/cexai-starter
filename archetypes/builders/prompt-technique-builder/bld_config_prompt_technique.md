---
kind: config
id: bld_config_prompt_technique
pillar: P09
llm_function: CONSTRAIN
purpose: Naming, paths, limits for prompt_technique production
quality: null
title: "Config Prompt Technique"
version: "1.0.0"
author: wave1_builder_gen_v2
tags: [prompt_technique, builder, config]
tldr: "Production constraints for prompt technique: naming (p03_pt_{{name}}.md), output paths (P03/), size limit 4096B. Prompt technique."
domain: "prompt_technique construction"
created: "2026-04-14"
updated: "2026-04-14"
8f: "F1_constrain"
keywords: [limits for prompt_technique production, prompt_technique construction, config prompt technique, output paths, size limit, prompt technique, prompt_technique, builder, config, "p03_pt_{{name}}.md"]
density_score: 0.85
related:
  - bld_config_reasoning_strategy
  - bld_config_agents_md
  - bld_config_api_reference
  - bld_config_agent_profile
  - bld_config_collaboration_pattern
---

## Naming Convention
Pattern: `p03_pt_{{name}}.md`
Examples:
- `p03_pt_summarization.md`
- `p03_pt_qa.md`

## Paths
Artifacts stored in: `/opt/cex/techniques/p03/{{name}}.md`

## Limits
- max_bytes: 4096
- max_turns: 5
- effort_level: 3

## Hooks
- pre_build: null
- post_build: null
- on_error: null
- on_quality_fail: null

## Domain-Specific Constraints

| Constraint | Value |
|-----------|-------|
| Boundary | Prompt technique |
| Dependencies | prompt_template |
| Primary 8F function | F6_produce |
| Max artifact size | 4096 bytes |

## Edge Cases

| Scenario | Handling |
|----------|---------|
| Missing required frontmatter field | Fail H01 gate; return to F6 |
| ID collision with existing artifact | Append version suffix (_v2) |
| Body exceeds 4096 bytes | Trim prose sections; preserve tables |
| Dependency prompt_template not found | Warn; proceed with defaults |

## Properties

| Property | Value |
|----------|-------|
| Kind | `config` |
| Pillar | P09 |
| Domain | prompt technique construction |
| Pipeline | 8F (F1-F8) |
| Scorer | cex_score.py |
| Compiler | cex_compile.py |
| Retriever | cex_retriever.py |
| Quality target | 9.0+ |
| Density target | 0.85+ |

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[bld_config_reasoning_strategy]] | sibling | 0.54 |
| [[bld_config_agents_md]] | sibling | 0.54 |
| [[bld_config_api_reference]] | sibling | 0.52 |
| [[bld_config_agent_profile]] | sibling | 0.52 |
| [[bld_config_collaboration_pattern]] | sibling | 0.51 |
