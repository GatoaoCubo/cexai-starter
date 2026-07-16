---
kind: collaboration
id: bld_collaboration_enterprise_sla
pillar: P12
llm_function: COLLABORATE
purpose: How enterprise_sla-builder works in crews with other builders
quality: null
title: "Collaboration Enterprise Sla"
version: "1.0.0"
author: wave1_builder_gen_v2
tags: [enterprise_sla, builder, collaboration]
tldr: "How enterprise_sla-builder works in crews with other builders"
domain: "enterprise_sla construction"
created: "2026-04-14"
updated: "2026-04-14"
8f: "F8_collaborate"
keywords: [enterprise_sla construction, collaboration enterprise sla, enterprise_sla, builder, collaboration, runtime_quality_builder, audit_compliance_builder, crew role  
coordinates, receives from, produces for]
density_score: 0.85
related:
  - enterprise-sla-builder
  - bld_tools_enterprise_sla
  - bld_config_enterprise_sla
---
## Crew Role  
Coordinates SLA contract creation, aligns service expectations, and ensures legal/operational alignment.  

## Receives From  
| Builder         | What                  | Format   |  
|-----------------|-----------------------|----------|  
| service_catalog | Service definitions   | JSON     |  
| legal_team      | Legal terms           | YAML     |  
| operations_team | Performance benchmarks| CSV      |  

## Produces For  
| Builder         | What                  | Format   |  
|-----------------|-----------------------|----------|  
| contract_signing| SLA document          | PDF      |  
| compliance_team | SLA compliance matrix | YAML     |  
| analytics_team  | SLA metrics report    | JSON     |  

## Boundary  
Does NOT enforce runtime quality gates (handled by `runtime_quality_builder`) or audit compliance checklists (handled by `audit_compliance_builder`).

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[enterprise-sla-builder]] | upstream | 0.40 |
| [[bld_tools_enterprise_sla]] | upstream | 0.33 |
| [[bld_config_enterprise_sla]] | upstream | 0.29 |
