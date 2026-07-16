---
kind: collaboration
id: bld_collaboration_onboarding_flow
pillar: P12
llm_function: COLLABORATE
purpose: How onboarding_flow-builder works in crews with other builders
quality: null
title: "Collaboration Onboarding Flow"
version: "1.0.0"
author: wave1_builder_gen_v2
tags: [onboarding_flow, builder, collaboration]
tldr: "How onboarding_flow-builder works in crews with other builders"
domain: "onboarding_flow construction"
created: "2026-04-14"
updated: "2026-04-14"
8f: "F8_collaborate"
keywords: [onboarding_flow construction, collaboration onboarding flow, onboarding_flow, builder, collaboration, crew role  
orchestrates, receives from, user onboarding, config service, auth service]
density_score: 0.85
related:
  - onboarding-flow-builder
  - quickstart-guide-builder
  - bld_knowledge_card_onboarding_flow
  - n00_onboarding_flow_manifest
  - kc_onboarding_flow
---
## Crew Role  
Orchestrates activation steps, validates prerequisites, and triggers system readiness checks for new users or entities.  

## Receives From  
| Builder       | What                  | Format      |  
|---------------|-----------------------|-------------|  
| User Onboarding | Initial user data     | JSON        |  
| Config Service  | Activation rules      | YAML        |  
| Auth Service    | Authentication token  | JWT         |  

## Produces For  
| Builder         | What                    | Format      |  
|-----------------|-------------------------|-------------|  
| User Profile    | Activated user state    | JSON        |  
| Notification    | Onboarding confirmation | Email       |  
| Analytics       | Activation event        | Event       |  

## Boundary  
Does NOT handle long-term user data storage (User Profile Service), authentication (Auth Service), or post-activation workflows (Workflow Engine).

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[onboarding-flow-builder]] | upstream | 0.29 |
| [[quickstart-guide-builder]] | upstream | 0.27 |
| [[bld_knowledge_card_onboarding_flow]] | upstream | 0.26 |
| [[n00_onboarding_flow_manifest]] | upstream | 0.25 |
| [[kc_onboarding_flow]] | upstream | 0.24 |
