---
kind: collaboration
id: bld_collaboration_integration_guide
pillar: P12
llm_function: COLLABORATE
purpose: How integration_guide-builder works in crews with other builders
quality: null
title: "Collaboration Integration Guide"
version: "1.0.0"
author: wave1_builder_gen_v2
tags: [integration_guide, builder, collaboration]
tldr: "How integration_guide-builder works in crews with other builders"
domain: "integration_guide construction"
created: "2026-04-14"
updated: "2026-04-14"
8f: "F8_collaborate"
keywords: [integration_guide construction, collaboration integration guide, integration_guide, builder, collaboration, crew role  
creates, receives from, product team, support team, produces for]
density_score: 0.85
related:
  - bld_collaboration_reward_model
  - bld_collaboration_sdk_example
  - bld_collaboration_reranker_config
  - bld_collaboration_cohort_analysis
  - bld_collaboration_subscription_tier
---
## Crew Role  
Creates and maintains comprehensive integration guides, ensuring alignment with product capabilities and developer needs. Collaborates with API, product, and support teams to validate accuracy and completeness.  

## Receives From  
| Builder       | What                  | Format      |  
|---------------|-----------------------|-------------|  
| API Team      | API specifications    | JSON        |  
| Product Team  | Integration scenarios | Markdown    |  
| Support Team  | Common user issues    | Ticket system |  

## Produces For  
| Builder           | What                  | Format      |  
|-------------------|-----------------------|-------------|  
| Product Team      | Integration guides    | Markdown    |  
| Developer Portal  | Diagrams and workflows| SVG         |  
| Support Team      | Troubleshooting notes | Markdown    |  

## Boundary  
Does NOT handle code implementation (dev teams), quickstart tutorials (quickstart_guide-builder), or API schema details (api_reference-builder).

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[bld_collaboration_reward_model]] | sibling | 0.35 |
| [[bld_collaboration_sdk_example]] | sibling | 0.35 |
| [[bld_collaboration_reranker_config]] | sibling | 0.34 |
| [[bld_collaboration_cohort_analysis]] | sibling | 0.34 |
| [[bld_collaboration_subscription_tier]] | sibling | 0.33 |
