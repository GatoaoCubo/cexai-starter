---
kind: collaboration
id: bld_collaboration_content_filter
pillar: P12
llm_function: COLLABORATE
purpose: How content_filter-builder works in crews with other builders
quality: null
title: "Collaboration Content Filter"
version: "1.0.0"
author: wave1_builder_gen
tags: [content_filter, builder, collaboration]
tldr: "How content_filter-builder works in crews with other builders"
domain: "content_filter construction"
created: "2026-04-13"
updated: "2026-04-13"
8f: "F8_collaborate"
keywords: [content_filter construction, collaboration content filter, content_filter, builder, collaboration, crew role  

this, receives from, content generator, policy manager, analytics module]
density_score: 0.85
related:
  - content-filter-builder
  - bld_config_content_filter
---
## Crew Role  

This ISO defines a content filter -- the moderation rules that gate output or input.
Filters content based on predefined criteria, ensuring compliance with policies and removing inappropriate or irrelevant material.  

## Receives From  
| Builder          | What              | Format  |  
|------------------|-------------------|---------|  
| Content Generator| Raw content       | JSON    |  
| Policy Manager   | Filtering rules   | YAML    |  
| Analytics Module | Metadata          | CSV     |  

## Produces For  
| Builder           | What              | Format  |  
|-------------------|-------------------|---------|  
| Content Processor | Filtered content  | JSON    |  
| Compliance Checker| Filtering reports | XML     |  
| Monitoring System | Logs              | Log files |  

## Boundary  
Does not enforce broad safety constraints (Guardrail) or validate output schemas (Output Validator). Those are handled by respective components.

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[content-filter-builder]] | upstream | 0.36 |
| [[bld_config_content_filter]] | upstream | 0.26 |
| [[bld_prompt_content_filter]] | upstream | 0.25 |
