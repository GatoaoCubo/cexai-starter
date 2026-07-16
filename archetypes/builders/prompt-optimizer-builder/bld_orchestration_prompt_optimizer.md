---
kind: collaboration
id: bld_collaboration_prompt_optimizer
pillar: P12
llm_function: COLLABORATE
purpose: How prompt_optimizer-builder works in crews with other builders
quality: null
title: "Collaboration Prompt Optimizer"
version: "1.0.0"
author: wave1_builder_gen_v2
tags: [prompt_optimizer, builder, collaboration]
tldr: "How prompt_optimizer-builder works in crews with other builders"
domain: "prompt_optimizer construction"
created: "2026-04-14"
updated: "2026-04-14"
8f: "F8_collaborate"
keywords: [prompt_optimizer construction, collaboration prompt optimizer, prompt_optimizer, builder, collaboration, crew role  
refines, receives from, produces for, boundary  
does, related artifacts]
density_score: 0.85
related:
  - prompt-optimizer-builder
---
## Crew Role  
Refines prompts for effectiveness, efficiency, and alignment with downstream tasks by iteratively testing, analyzing, and adjusting prompt structures and language.  

## Receives From  
| Builder       | What                  | Format      |  
|---------------|-----------------------|-------------|  
| prompt_compiler | Raw prompts           | JSON        |  
| evaluator     | Performance metrics   | CSV         |  
| user_feedback | User input/feedback   | Text        |  

## Produces For  
| Builder       | What                  | Format      |  
|---------------|-----------------------|-------------|  
| prompt_compiler | Optimized prompts     | JSON        |  
| analyst       | Optimization reports  | Markdown    |  
| template_manager | Updated prompt templates | YAML  |  

## Boundary  
Does NOT compile prompts into code (handled by prompt_compiler) or perform general optimization (handled by generic optimizer). Does NOT manage user feedback collection (handled by evaluator).

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[prompt-optimizer-builder]] | upstream | 0.26 |
