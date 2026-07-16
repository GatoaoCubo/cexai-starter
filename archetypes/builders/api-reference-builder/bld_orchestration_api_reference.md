---
kind: collaboration
id: bld_collaboration_api_reference
pillar: P12
llm_function: COLLABORATE
purpose: How api_reference-builder works in crews with other builders
quality: null
title: "Collaboration Api Reference"
version: "1.0.0"
author: wave1_builder_gen_v2
tags: [api_reference, builder, collaboration]
tldr: "How api_reference-builder works in crews with other builders"
domain: "api_reference construction"
created: "2026-04-14"
updated: "2026-04-14"
8f: "F8_collaborate"
keywords: [api_reference construction, collaboration api reference, api_reference, builder, collaboration, crew role  
generates, receives from, produces for, boundary  
does, related artifacts]
density_score: 0.85
related:
  - api-reference-builder
---
## Crew Role  
Generates and maintains accurate, up-to-date API reference documentation from specifications, ensuring clarity for developers and users.  

## Receives From  
| Builder      | What               | Format       |  
|--------------|--------------------|--------------|  
| spec_builder | API specifications | OpenAPI JSON |  
| code_builder | Code samples       | Markdown     |  
| design_system| UI component specs | Figma        |  

## Produces For  
| Builder      | What                     | Format       |  
|--------------|--------------------------|--------------|  
| docs_team    | API reference docs       | Markdown     |  
| dev_team     | SDK example snippets     | Code blocks  |  
| qa_team      | Test case definitions    | JSON         |  

## Boundary  
Does NOT validate schema correctness (spec_validator handles this) or implement code (code_builder handles this). Deployment of docs is managed by the deployment_team.

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[api-reference-builder]] | upstream | 0.24 |
