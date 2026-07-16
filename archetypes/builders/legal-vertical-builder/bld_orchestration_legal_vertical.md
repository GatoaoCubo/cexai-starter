---
kind: collaboration
id: bld_collaboration_legal_vertical
pillar: P12
llm_function: COLLABORATE
purpose: How legal_vertical-builder works in crews with other builders
quality: null
title: "Collaboration Legal Vertical"
version: "1.0.0"
author: wave1_builder_gen_v2
tags: [legal_vertical, builder, collaboration]
tldr: "How legal_vertical-builder works in crews with other builders"
domain: "legal_vertical construction"
created: "2026-04-14"
updated: "2026-04-14"
8f: "F8_collaborate"
keywords: [legal_vertical construction, collaboration legal vertical, legal_vertical, builder, collaboration, crew role  
assembles, receives from, template repo, case law, produces for]
density_score: 0.85
related:
  - bld_collaboration_govtech_vertical
  - bld_collaboration_compliance_framework
  - bld_collaboration_healthcare_vertical
  - bld_collaboration_compliance_checklist
  - bld_collaboration_fintech_vertical
---
## Crew Role  
Assembles structured legal frameworks, templates, and regulatory-compliant documents for vertical-specific use cases.  

## Receives From  
| Builder       | What                  | Format  |  
|---------------|-----------------------|---------|  
| Template Repo | Legal document templates | JSON    |  
| Regulator     | Regulatory guidelines  | XML     |  
| Case Law DB   | Precedent data         | CSV     |  

## Produces For  
| Builder       | What                  | Format  |  
|---------------|-----------------------|---------|  
| Legal Team    | Customized contracts   | PDF     |  
| Compliance    | Framework checklists   | YAML    |  
| Risk Mgmt     | Scenario analyses      | DOCX    |  

## Boundary  
Does NOT handle audit trails (compliance_checklist) or case study analysis (case_study). Audits and case studies are managed by their respective specialized builders.

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[bld_collaboration_govtech_vertical]] | sibling | 0.38 |
| [[bld_collaboration_compliance_framework]] | sibling | 0.34 |
| [[bld_collaboration_healthcare_vertical]] | sibling | 0.32 |
| [[bld_collaboration_compliance_checklist]] | sibling | 0.28 |
| [[bld_collaboration_fintech_vertical]] | sibling | 0.28 |
