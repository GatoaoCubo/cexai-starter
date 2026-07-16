---
kind: collaboration
id: bld_collaboration_tts_provider
pillar: P12
llm_function: COLLABORATE
purpose: How tts_provider-builder works in crews with other builders
quality: null
title: "Collaboration Tts Provider"
version: "1.0.0"
author: wave1_builder_gen
tags: [tts_provider, builder, collaboration]
tldr: "How tts_provider-builder works in crews with other builders"
domain: "tts_provider construction"
created: "2026-04-13"
updated: "2026-04-13"
8f: "F8_collaborate"
keywords: [tts_provider construction, collaboration tts provider, tts_provider, builder, collaboration, crew role  
manages, receives from, produces for, boundary  
does, related artifacts]
density_score: 0.85
related:
  - tts-provider-builder
  - voice-pipeline-builder
---
## Crew Role  
Manages integration with external TTS APIs, ensuring compatibility, configuration management, and error handling for text-to-speech synthesis.  

## Receives From  
| Builder       | What                  | Format     |  
|---------------|-----------------------|------------|  
| API_Manager   | API credentials       | JSON       |  
| Config_Reader | Provider-specific settings | YAML     |  
| Text_Handler  | Text input for synthesis | Plain text |  

## Produces For  
| Builder       | What                  | Format     |  
|---------------|-----------------------|------------|  
| File_Exporter | TTS output files      | WAV/MP3    |  
| Error_Handler | Error logs            | JSON       |  
| Config_Validator | Configuration validation results | YAML |  

## Boundary  
Does NOT handle voice pipeline architecture (voice_pipeline_builder) or prosody configuration (prosody_configurator). Voice pipeline design and personality tuning are managed by dedicated components.

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[tts-provider-builder]] | upstream | 0.37 |
| [[voice-pipeline-builder]] | upstream | 0.27 |
