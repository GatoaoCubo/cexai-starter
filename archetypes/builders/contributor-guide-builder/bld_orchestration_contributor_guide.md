---
kind: collaboration
id: bld_collaboration_contributor_guide
pillar: P12
llm_function: COLLABORATE
purpose: How contributor_guide-builder works in crews with other builders
quality: null
title: "Collaboration Contributor Guide"
version: "1.0.0"
author: wave1_builder_gen_v2
tags: [contributor_guide, builder, collaboration]
tldr: "How contributor_guide-builder works in crews with other builders"
domain: "contributor_guide construction"
created: "2026-04-14"
updated: "2026-04-14"
8f: "F8_collaborate"
keywords: [contributor_guide construction, collaboration contributor guide, contributor_guide, builder, collaboration, crew role  
drafts, receives from  
builder, contributor guide team, markdown  
code team, text  
design team]
density_score: 0.85
related:
  - bld_collaboration_integration_guide
  - bld_collaboration_white_label_config
  - bld_collaboration_reward_model
  - bld_collaboration_reranker_config
  - bld_config_contributor_guide
---
## Crew Role  
Drafts, maintains, and updates the contributor guide to ensure clarity, consistency, and alignment with team workflows.  

## Receives From  
Builder | What | Format  
--- | --- | ---  
Contributor Guide Team | Feedback on guide improvements | Text/Markdown  
Code Team | Existing contribution workflows | JSON/PlainText  
Design Team | Branding and style guidelines | PDF/Markdown  

## Produces For  
Builder | What | Format  
--- | --- | ---  
Contributor Guide Team | Final contributor guide document | Markdown/HTML  
Onboarding Team | Templates for new contributors | Markdown/PlainText  
Documentation Team | Checklist for guide compliance | JSON/PlainText  

## Boundary  
Does NOT handle code reviews, integration with external tools, or enforcement of norms. Code reviews → Code Team. Tool integrations → Integration Guide. Norm enforcement → Code of Conduct Team.

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[bld_collaboration_integration_guide]] | sibling | 0.40 |
| [[bld_collaboration_white_label_config]] | sibling | 0.38 |
| [[bld_collaboration_reward_model]] | sibling | 0.35 |
| [[bld_collaboration_reranker_config]] | sibling | 0.35 |
| [[bld_config_contributor_guide]] | upstream | 0.33 |
