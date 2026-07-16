---
kind: collaboration
id: bld_collaboration_interactive_demo
pillar: P12
llm_function: COLLABORATE
purpose: How interactive_demo-builder works in crews with other builders
quality: null
title: "Collaboration Interactive Demo"
version: "1.0.0"
author: wave1_builder_gen_v2
tags: [interactive_demo, builder, collaboration]
tldr: "How interactive_demo-builder works in crews with other builders"
domain: "interactive_demo construction"
created: "2026-04-14"
updated: "2026-04-14"
8f: "F8_collaborate"
keywords: [interactive_demo construction, collaboration interactive demo, interactive_demo, builder, collaboration, crew role  
creates, receives from, content writer, design team, engineering team]
density_score: 0.85
related:
  - bld_collaboration_product_tour
  - bld_collaboration_reranker_config
  - bld_collaboration_ab_test_config
  - bld_collaboration_reward_model
  - bld_collaboration_white_label_config
---
## Crew Role  
Creates interactive demo scripts by integrating user stories, technical specs, and design assets into cohesive, executable demo flows. Acts as a bridge between content creators and engineers.  

## Receives From  
| Builder | What | Format |  
|---|---|---|  
| Content Writer | Script outline & user flows | Markdown |  
| Design Team | Visual assets & UI components | ZIP (images, Figma files) |  
| Engineering Team | Technical constraints & API specs | JSON (schema, endpoints) |  

## Produces For  
| Builder | What | Format |  
|---|---|---|  
| Content Writer | Demo script with annotated interactions | Markdown |  
| Engineering Team | Interactive element definitions | JSON (event handlers, state logic) |  
| QA Team | Demo preview link & test scenarios | URL + CSV (test cases) |  

## Boundary  
Does NOT handle hosting/deployment (DevOps), user testing (QA Team), or asset storage management (Design Team).

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[bld_collaboration_product_tour]] | sibling | 0.42 |
| [[bld_collaboration_reranker_config]] | sibling | 0.38 |
| [[bld_collaboration_ab_test_config]] | sibling | 0.38 |
| [[bld_collaboration_reward_model]] | sibling | 0.37 |
| [[bld_collaboration_white_label_config]] | sibling | 0.36 |
