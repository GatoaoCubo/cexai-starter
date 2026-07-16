---
kind: collaboration
id: bld_collaboration_reward_model
pillar: P12
llm_function: COLLABORATE
purpose: How reward_model-builder works in crews with other builders
quality: null
title: "Collaboration Reward Model"
version: "1.0.0"
author: wave1_builder_gen
tags: [reward_model, builder, collaboration]
tldr: "How reward_model-builder works in crews with other builders"
domain: "reward_model construction"
created: "2026-04-13"
updated: "2026-04-13"
8f: "F8_collaborate"
keywords: [reward_model construction, collaboration reward model, reward_model, builder, collaboration, crew role  
designs, receives from, business team, produces for, model team]
density_score: 0.85
related:
  - bld_collaboration_reranker_config
  - bld_collaboration_white_label_config
  - bld_collaboration_ab_test_config
  - bld_collaboration_product_tour
  - bld_collaboration_cohort_analysis
---
## Crew Role  
Designs and configures reward models to align with business objectives, ensuring compatibility with training frameworks and evaluation systems.  

## Receives From  
| Builder       | What                  | Format      |  
|---------------|-----------------------|-------------|  
| Business Team | Objective definitions | Document    |  
| Engineering   | Technical constraints | JSON        |  
| UX Team       | User preference data  | CSV         |  

## Produces For  
| Builder       | What                        | Format      |  
|---------------|-----------------------------|-------------|  
| Model Team    | Reward model config file    | YAML/JSON   |  
| QA Team       | Validation report           | Markdown    |  
| Engineering   | Compatibility check document| PDF/Word    |  

## Boundary  
Does NOT implement training algorithms (handled by RL engineers) or define scoring rubrics (handled by evaluation team).

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[bld_collaboration_reranker_config]] | sibling | 0.42 |
| [[bld_collaboration_white_label_config]] | sibling | 0.38 |
| [[bld_collaboration_ab_test_config]] | sibling | 0.36 |
| [[bld_collaboration_product_tour]] | sibling | 0.36 |
| [[bld_collaboration_cohort_analysis]] | sibling | 0.36 |
