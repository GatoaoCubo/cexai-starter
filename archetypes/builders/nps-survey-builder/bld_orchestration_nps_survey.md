---
kind: collaboration
id: bld_collaboration_nps_survey
pillar: P12
llm_function: COLLABORATE
purpose: How nps_survey-builder works in crews with other builders
quality: null
title: "Collaboration Nps Survey"
version: "1.0.0"
author: n05_wave6
tags: [nps_survey, builder, collaboration]
tldr: "How nps_survey-builder works in crews with other builders"
domain: "nps_survey construction"
created: "2026-04-14"
updated: "2026-04-14"
8f: "F8_collaborate"
keywords: [nps_survey construction, collaboration nps survey, nps_survey, builder, collaboration, crew role
configures, receives from, produces for, boundary
does, related artifacts]
density_score: 0.85
related:
  - nps-survey-builder
  - bld_config_nps_survey
---
## Crew Role
Configures NPS survey mechanics (question, scale, segmentation, cadence, routing).
Produces validated YAML survey configs consumed by CS platforms and retention pipelines.

## Receives From
| Source                        | What                                 | Format   |
|-------------------------------|--------------------------------------|----------|
| churn_prevention_playbook     | At-risk segment definitions          | Markdown |
| customer_segment builder      | Audience filters (tenure, tier, ARR) | YAML     |
| product_analytics (N01)       | Trigger events (feature adoption)    | JSON     |

## Produces For
| Consumer                      | What                                 | Format   |
|-------------------------------|--------------------------------------|----------|
| CS platform (Gainsight)       | Survey config with routing rules     | YAML     |
| churn_prevention_playbook     | Detractor signal + score             | JSON     |
| content_monetization (N06)    | NPS-segmented expansion targets      | CSV      |

## Boundary
Does NOT handle:
- Customer segment definitions -> customer_segment kind
- Cohort retention analysis -> cohort_analysis kind
- Win-back sequences -> churn_prevention_playbook kind
- Survey UI/visual design -> handled by front-end team

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[nps-survey-builder]] | upstream | 0.41 |
| [[bld_config_nps_survey]] | upstream | 0.32 |
