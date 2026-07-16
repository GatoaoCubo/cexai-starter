---
kind: config
id: bld_config_prompt_optimizer
pillar: P09
llm_function: CONSTRAIN
purpose: Naming, paths, limits for prompt_optimizer production
quality: null
title: "Config Prompt Optimizer"
version: "1.0.0"
author: wave1_builder_gen_v2
tags:
  - "prompt_optimizer"
  - "builder"
  - "config"
tldr: "Production constraints for prompt optimizer: naming (p03_po_{{name}}.md), output paths (P03/), size limit 5120B. Prompt optimizer."
domain: "prompt_optimizer construction"
created: "2026-04-14"
updated: "2026-04-14"
8f: "F1_constrain"
keywords:
  - "limits for prompt_optimizer production"
  - "prompt_optimizer construction"
  - "config prompt optimizer"
  - "output paths"
  - "size limit"
  - "prompt optimizer"
  - "prompt_optimizer"
  - "builder"
  - "config"
  - "|/ _"
density_score: 0.85
related:
  - bld_config_ab_test_config
  - bld_config_prompt_technique
  - bld_config_agents_md
  - bld_config_api_reference
  - bld_config_collaboration_pattern
---

## Naming Convention  
Pattern: p03_po_{{name}}.md  
Examples: p03_po_chatbot.md, p03_po_summarizer.md  

## Paths  
Artifacts: /opt/cex/prompt_optimizers/artifacts/{{name}}  
Logs: /var/log/cex/po/{{name}}  

## Limits  
max_bytes: 5120  
max_turns: 20  
effort_level: 3  

## Hooks  
pre_build: null  
post_build: null  
on_error: null  
on_quality_fail: null  

```
   __  __           _       _           
  |  \/  |         | |     | |          
  | \  / | __ _  __| | __ _| |_ ___ _ __
  | |\/| |/ _` |/ _` |/ _` | __/ _ \ '__|
  | |  | | (_| | (_| | (_| | ||  __/ |   
  |_|  |_|\__,_|\__,_|\__,_|\__\___|_|   
```

## Domain-Specific Constraints

| Constraint | Value |
|-----------|-------|
| Boundary | Prompt optimizer |
| Dependencies | prompt_template, scoring_rubric |
| Primary 8F function | F6_produce |
| Max artifact size | 5120 bytes |

## Edge Cases

| Scenario | Handling |
|----------|---------|
| Missing required frontmatter field | Fail H01 gate; return to F6 |
| ID collision with existing artifact | Append version suffix (_v2) |
| Body exceeds 5120 bytes | Trim prose sections; preserve tables |
| Dependency prompt_template not found | Warn; proceed with defaults |

## Properties

| Property | Value |
|----------|-------|
| Kind | `config` |
| Pillar | P09 |
| Domain | prompt optimizer construction |
| Pipeline | 8F (F1-F8) |
| Scorer | cex_score.py |
| Compiler | cex_compile.py |
| Retriever | cex_retriever.py |
| Quality target | 9.0+ |
| Density target | 0.85+ |

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[bld_config_ab_test_config]] | sibling | 0.52 |
| [[bld_config_prompt_technique]] | sibling | 0.51 |
| [[bld_config_agents_md]] | sibling | 0.51 |
| [[bld_config_api_reference]] | sibling | 0.51 |
| [[bld_config_collaboration_pattern]] | sibling | 0.49 |
