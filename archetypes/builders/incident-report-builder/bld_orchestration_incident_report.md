---
kind: collaboration
id: bld_collaboration_incident_report
pillar: P12
llm_function: COLLABORATE
purpose: How incident_report-builder works in crews with other builders
quality: null
title: "Collaboration Incident Report"
version: "1.0.0"
author: wave1_builder_gen
tags: [incident_report, builder, collaboration]
tldr: "How incident_report-builder works in crews with other builders"
domain: "incident_report construction"
created: "2026-04-13"
updated: "2026-04-13"
8f: "F8_collaborate"
keywords: [incident_report construction, collaboration incident report, incident_report, builder, collaboration, crew role  
structures, receives from, incident triage, produces for, boundary  
does]
density_score: 0.85
related:
  - incident-report-builder
  - p11_fb_incident_report
  - n00_incident_report_manifest
  - bld_knowledge_card_incident_report
  - bld_architecture_incident_report
---
## Crew Role  
Structures incident data into post-mortem reports, ensuring clarity, accountability, and actionable insights for teams.  

## Receives From  
| Builder       | What                  | Format      |  
|---------------|-----------------------|-------------|  
| Monitoring    | Raw incident logs     | JSON        |  
| Stakeholders  | Feedback on incident  | Plain text  |  
| Incident Triage | Initial summary     | Markdown    |  

## Produces For  
| Builder       | What                  | Format      |  
|---------------|-----------------------|-------------|  
| Post-Mortem   | Structured report     | Markdown    |  
| Leadership    | Executive summary     | PDF         |  
| Analytics     | Incident data export  | CSV         |  

## Boundary  
Does NOT handle auto-fixes (bugloop) or generic learning (learning_record). Auto-fixes are resolved by bugloop; learning records are managed by learning_record.

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[incident-report-builder]] | upstream | 0.44 |
| [[p11_fb_incident_report]] | upstream | 0.31 |
| [[n00_incident_report_manifest]] | upstream | 0.31 |
| [[bld_knowledge_card_incident_report]] | upstream | 0.30 |
| [[bld_architecture_incident_report]] | upstream | 0.29 |
