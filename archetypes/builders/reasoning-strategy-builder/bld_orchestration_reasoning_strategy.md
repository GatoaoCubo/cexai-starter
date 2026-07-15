---
kind: collaboration
id: bld_collaboration_reasoning_strategy
pillar: P12
llm_function: COLLABORATE
purpose: How reasoning_strategy-builder works in crews with other builders
quality: null
title: "Collaboration Reasoning Strategy"
version: "1.0.0"
author: wave1_builder_gen
tags: [reasoning_strategy, builder, collaboration]
tldr: "How reasoning_strategy-builder works in crews with other builders"
domain: "reasoning_strategy construction"
created: "2026-04-13"
updated: "2026-04-13"
8f: "F8_collaborate"
keywords: [reasoning_strategy construction, collaboration reasoning strategy, reasoning_strategy, builder, collaboration, crew role  

this, receives from, produces for, boundary  
does, related artifacts]
density_score: 0.85
related:
  - bld_output_template_reasoning_strategy
  - reasoning-strategy-builder
  - bld_collaboration_search_strategy
  - kc_reasoning_strategy
  - bld_tools_reasoning_strategy
---
## Crew Role  

This ISO selects a reasoning strategy (e.g. chain-of-thought) and the conditions under which it applies.
Designs structured reasoning approaches to solve complex problems, ensuring alignment with team objectives and technical constraints.  

## Receives From  
| Builder              | What                  | Format          |  
|----------------------|-----------------------|-----------------|  
| Problem_Definition_Builder | Problem scope & constraints | Structured document |  
| Knowledge_Base_Builder     | Relevant data sources   | Dataset schema  |  
| Feedback_Collector         | Prior strategy outcomes | Feedback report |  

## Produces For  
| Builder              | What                  | Format          |  
|----------------------|-----------------------|-----------------|  
| Solution_Architect   | Strategy implementation plan | Technical spec |  
| Evaluation_Framework_Builder | Metrics for success | Assessment config |  
| Documentation_Builder | Strategy rationale    | Technical doc   |  

## Boundary  
Does NOT handle prompt engineering (prompt_technique) or resource allocation (thinking_config). Prompt engineering is managed by Prompt_Engineer; resource allocation by Resource_Allocator.

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[bld_output_template_reasoning_strategy]] | upstream | 0.27 |
| [[reasoning-strategy-builder]] | upstream | 0.27 |
| bld_collaboration_search_strategy | sibling | 0.24 |
| [[kc_reasoning_strategy]] | upstream | 0.24 |
| [[bld_tools_reasoning_strategy]] | upstream | 0.24 |
