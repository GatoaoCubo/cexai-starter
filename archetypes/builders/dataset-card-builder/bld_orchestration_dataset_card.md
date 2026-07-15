---
kind: collaboration
id: bld_collaboration_dataset_card
pillar: P12
llm_function: COLLABORATE
purpose: How dataset_card-builder works in crews with other builders
quality: null
title: "Collaboration Dataset Card"
version: "1.0.0"
author: wave1_builder_gen
tags: [dataset_card, builder, collaboration]
tldr: "How dataset_card-builder works in crews with other builders"
domain: "dataset_card construction"
created: "2026-04-13"
updated: "2026-04-13"
8f: "F8_collaborate"
keywords: [dataset_card construction, collaboration dataset card, dataset_card, builder, collaboration, crew role
standardizes, receives from, produces for, finalized dataset card, related artifacts]
density_score: 0.85
related:
  - dataset-card-builder
  - bld_collaboration_llm_evaluation_scenario
  - bld_collaboration_self_improvement_loop
  - bld_collaboration_agent_profile
  - bld_collaboration_agent_computer_interface
---
## Crew Role
Standardizes and automates the creation of dataset documentation, transforming raw metadata, schema definitions, and legal constraints into structured, human-readable dataset cards.

## Receives From
| Builder | What | Format |
| :--- | :--- | :--- |
| data_auditor | Data statistics and distributions | JSON |
| legal_agent | Licensing and usage restrictions | Text |
| data_engineer | Schema and structural metadata | YAML |

## Produces For
| Builder | What | Format |
| :--- | :--- | :--- |
| data_scientist | Finalized Dataset Card | Markdown |
| compliance_officer | Privacy and usage summary | Markdown |
| model_trainer | Data provenance and lineage info | JSON |

## Boundary
- Does NOT generate evaluation benchmarks or metrics (handled by eval_dataset-builder).
- Does NOT define general domain knowledge or facts (handled by knowledge_card-builder).
- Does NOT perform data cleaning or preprocessing (handled by data_pipeline-agent).

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[dataset-card-builder]] | upstream | 0.30 |
| bld_collaboration_llm_evaluation_scenario | sibling | 0.28 |
| bld_collaboration_self_improvement_loop | sibling | 0.27 |
| [[bld_orchestration_agent_profile]] | sibling | 0.27 |
| bld_collaboration_agent_computer_interface | sibling | 0.27 |
