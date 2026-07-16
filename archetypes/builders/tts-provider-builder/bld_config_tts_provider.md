---
kind: config
id: bld_config_tts_provider
pillar: P09
llm_function: CONSTRAIN
purpose: Naming, paths, limits for tts_provider production
quality: null
title: "Config Tts Provider"
version: "1.0.0"
author: wave1_builder_gen
tags: [tts_provider, builder, config]
tldr: "Production constraints for tts provider: naming (p04_tts_{{name}}.md), output paths (P04/), size limit 4096B. TTS provider integration."
domain: "tts_provider construction"
created: "2026-04-13"
updated: "2026-04-13"
8f: "F1_constrain"
keywords: [limits for tts_provider production, tts_provider construction, config tts provider, output paths, size limit, tts provider integration, tts_provider, builder, config, naming convention]
density_score: 0.85
related:
  - bld_config_api_reference
  - bld_config_ab_test_config
  - bld_config_repo_map
  - bld_config_integration_guide
  - bld_config_collaboration_pattern
---

## Naming Convention  
p04_tts_{{name}}.md (e.g., p04_tts_azure.md, p04_tts_google.md)  

## Paths  
/artifacts/tts/{{name}}/  
/config/tts/{{name}}.yaml  

## Limits  
max_bytes: 4096  
max_turns: 5  
effort_level: 3  

## Hooks  
pre_build: null  
post_build: null  
on_error: null  
on_quality_fail: null

## Domain-Specific Constraints

| Constraint | Value |
|-----------|-------|
| Boundary | TTS provider integration |
| Dependencies | api_client |
| Primary 8F function | F6_produce |
| Max artifact size | 4096 bytes |

## Edge Cases

| Scenario | Handling |
|----------|---------|
| Missing required frontmatter field | Fail H01 gate; return to F6 |
| ID collision with existing artifact | Append version suffix (_v2) |
| Body exceeds 4096 bytes | Trim prose sections; preserve tables |
| Dependency api_client not found | Warn; proceed with defaults |

## Properties

| Property | Value |
|----------|-------|
| Kind | `config` |
| Pillar | P09 |
| Domain | tts provider construction |
| Pipeline | 8F (F1-F8) |
| Scorer | cex_score.py |
| Compiler | cex_compile.py |
| Retriever | cex_retriever.py |
| Quality target | 9.0+ |
| Density target | 0.85+ |

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[bld_config_api_reference]] | sibling | 0.58 |
| [[bld_config_ab_test_config]] | sibling | 0.52 |
| [[bld_config_repo_map]] | sibling | 0.51 |
| [[bld_config_integration_guide]] | sibling | 0.50 |
| [[bld_config_collaboration_pattern]] | sibling | 0.50 |
