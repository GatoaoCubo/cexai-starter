---
kind: config
id: bld_config_voice_pipeline
pillar: P09
llm_function: CONSTRAIN
purpose: Naming, paths, limits for voice_pipeline production
quality: null
title: "Config Voice Pipeline"
version: "1.0.0"
author: wave1_builder_gen
tags: [voice_pipeline, builder, config]
tldr: "Production constraints for voice pipeline: naming (p04_vp_{{name}}.md), output paths (P04/), size limit 5120B. Voice pipeline architecture."
domain: "voice_pipeline construction"
created: "2026-04-13"
updated: "2026-04-13"
8f: "F1_constrain"
keywords: [limits for voice_pipeline production, voice_pipeline construction, config voice pipeline, output paths, size limit, voice pipeline architecture, voice_pipeline, builder, config, "p04_vp_{{name}}.md"]
density_score: 0.85
related:
  - bld_config_collaboration_pattern
  - bld_config_api_reference
  - bld_config_ab_test_config
  - bld_config_agents_md
  - bld_config_customer_segment
---

## Naming Convention  
Pattern: `p04_vp_{{name}}.md`  
Examples: `p04_vp_speech.md`, `p04_vp_tts.md`  

## Paths  
Base: `/artifacts/p04/vp/{{name}}/`  
Audio: `{{base}}/audio/`  
Logs: `{{base}}/logs/`  
Metadata: `{{base}}/meta/`  

## Limits  
max_bytes: 5120  
max_turns: 10  
effort_level: 3  

## Hooks  
pre_build: null  
post_build: null  
on_error: null  
on_quality_fail: null

## Properties

| Property | Value |
|----------|-------|
| Kind | `config` |
| Pillar | P09 |
| Domain | voice_pipeline construction |
| Pipeline | 8F (F1-F8) |
| Scorer | cex_score.py |
| Compiler | cex_compile.py |
| Retriever | cex_retriever.py |
| Quality target | 9.0+ |
| Density target | 0.85+ |

## Domain-Specific Constraints

| Constraint | Value |
|-----------|-------|
| Boundary | Voice pipeline architecture |
| Dependencies | stt_provider, tts_provider, vad_config |
| Primary 8F function | F5_call |
| Max artifact size | 5120 bytes |

## Edge Cases

| Scenario | Handling |
|----------|---------|
| Missing required frontmatter field | Fail H01 gate; return to F6 |
| ID collision with existing artifact | Append version suffix (_v2) |
| Body exceeds 5120 bytes | Trim prose sections; preserve tables |
| Dependency stt_provider not found | Warn; proceed with defaults |

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[bld_config_collaboration_pattern]] | sibling | 0.50 |
| [[bld_config_api_reference]] | sibling | 0.49 |
| [[bld_config_ab_test_config]] | sibling | 0.48 |
| [[bld_config_agents_md]] | sibling | 0.48 |
| [[bld_config_customer_segment]] | sibling | 0.47 |
