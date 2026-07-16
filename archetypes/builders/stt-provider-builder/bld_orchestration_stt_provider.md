---
kind: collaboration
id: bld_collaboration_stt_provider
pillar: P12
llm_function: COLLABORATE
purpose: How stt_provider-builder works in crews with other builders
quality: null
title: "Collaboration Stt Provider"
version: "1.0.0"
author: wave1_builder_gen
tags: [stt_provider, builder, collaboration]
tldr: "How stt_provider-builder works in crews with other builders"
domain: "stt_provider construction"
created: "2026-04-13"
updated: "2026-04-13"
8f: "F8_collaborate"
keywords: [stt_provider construction, collaboration stt provider, stt_provider, builder, collaboration, crew role  
configures, receives from, produces for, boundary  
does, related artifacts]
density_score: 0.85
related:
  - bld_architecture_stt_provider
  - stt-provider-builder
  - bld_memory_voice_pipeline
---
## Crew Role  
Configures and integrates STT provider APIs, ensuring compatibility with system interfaces and handling credential management.  

## Receives From  
| Builder       | What                  | Format   |  
|---------------|-----------------------|----------|  
| config_manager| Provider credentials  | JSON     |  
| audio_engine  | Audio format specs    | YAML     |  
| test_suite    | Sample audio files    | WAV      |  

## Produces For  
| Builder       | What                  | Format       |  
|---------------|-----------------------|--------------|  
| voice_pipeline| STT integration code  | Python module|  
| config_manager| Provider config files | JSON         |  
| test_suite    | Integration test logs | TXT          |  

## Boundary  
Does NOT handle voice_pipeline end-to-end processing (handled by voice_pipeline builder) or VAD sensitivity thresholds (handled by vad_config builder).

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[bld_architecture_stt_provider]] | upstream | 0.29 |
| [[stt-provider-builder]] | upstream | 0.28 |
| [[bld_memory_voice_pipeline]] | upstream | 0.26 |
