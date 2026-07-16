---
kind: collaboration
id: bld_collaboration_data_residency
pillar: P12
llm_function: COLLABORATE
purpose: How data_residency-builder works in crews with other builders
quality: null
title: "Collaboration Data Residency"
version: "1.0.0"
author: wave1_builder_gen_v2
tags: [data_residency, builder, collaboration]
tldr: "How data_residency-builder works in crews with other builders"
domain: "data_residency construction"
created: "2026-04-14"
updated: "2026-04-14"
8f: "F8_collaborate"
keywords: [data_residency construction, collaboration data residency, data_residency, builder, collaboration, crew role  
defines, receives from, produces for, boundary  
does, related artifacts]
density_score: 0.85
related:
  - p10_mem_data_residency_builder
  - data-residency-builder
  - bld_knowledge_card_data_residency
  - p01_kc_data_residency
  - bld_instruction_data_residency
---
## Crew Role  
Defines data residency rules and maps data assets to geographic regions based on regulatory requirements.  

## Receives From  
| Builder         | What                  | Format  |  
|-----------------|-----------------------|---------|  
| data_inventory  | List of data assets   | CSV     |  
| compliance_officer | Regulatory requirements | JSON  |  
| geography_mapper | Region mappings       | YAML    |  

## Produces For  
| Builder         | What                  | Format  |  
|-----------------|-----------------------|---------|  
| data_governance | Residency policies    | JSON    |  
| infrastructure  | Region-specific configs | YAML  |  
| compliance_team | Validation reports    | PDF     |  

## Boundary  
Does NOT manage credentials (secret_config) or access control (rbac_policy). These are handled by dedicated builders.

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[p10_mem_data_residency_builder]] | upstream | 0.33 |
| [[data-residency-builder]] | upstream | 0.32 |
| [[bld_knowledge_card_data_residency]] | upstream | 0.30 |
| [[p01_kc_data_residency]] | upstream | 0.29 |
| [[bld_instruction_data_residency]] | upstream | 0.26 |
