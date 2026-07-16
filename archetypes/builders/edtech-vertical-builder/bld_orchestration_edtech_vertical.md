---
kind: collaboration
id: bld_collaboration_edtech_vertical
pillar: P12
llm_function: COLLABORATE
purpose: How edtech_vertical-builder works in crews with other builders
quality: null
title: "Collaboration Edtech Vertical"
version: "1.0.0"
author: wave1_builder_gen_v2
tags: [edtech_vertical, builder, collaboration]
tldr: "How edtech_vertical-builder works in crews with other builders"
domain: "edtech_vertical construction"
created: "2026-04-14"
updated: "2026-04-14"
8f: "F8_collaborate"
keywords: [edtech_vertical construction, collaboration edtech vertical, edtech_vertical, builder, collaboration, crew role  
designs, receives from, produces for, boundary  
does, related artifacts]
density_score: 0.85
related:
  - bld_collaboration_govtech_vertical
  - bld_collaboration_legal_vertical
  - bld_collaboration_healthcare_vertical
  - bld_collaboration_compliance_framework
  - bld_collaboration_fintech_vertical
---
## Crew Role  
Designs and structures vertical-specific components (e.g., K-12, higher ed, corporate training) for EdTech platforms, ensuring alignment with industry standards and stakeholder needs.  

## Receives From  
| Builder         | What                  | Format      |  
|-----------------|-----------------------|-------------|  
| EdTech vertical KC | Vertical requirements | Document    |  
| course_module   | Core framework        | JSON schema |  
| stakeholder team | Feedback priorities   | Email       |  

## Produces For  
| Builder         | What                        | Format      |  
|-----------------|-----------------------------|-------------|  
| platform_dev    | Vertical-specific curriculum | YAML        |  
| UX_design       | Component spec templates    | JSON        |  
| project_mgmt    | Implementation roadmap      | Gantt chart |  

## Boundary  
Does NOT create course content (handled by course_module) or perform compliance audits (handled by compliance_checklist).

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[bld_collaboration_govtech_vertical]] | sibling | 0.31 |
| [[bld_collaboration_legal_vertical]] | sibling | 0.29 |
| [[bld_collaboration_healthcare_vertical]] | sibling | 0.28 |
| [[bld_collaboration_compliance_framework]] | sibling | 0.27 |
| [[bld_collaboration_fintech_vertical]] | sibling | 0.27 |
