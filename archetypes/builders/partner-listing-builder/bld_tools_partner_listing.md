---
kind: tools
id: bld_tools_partner_listing
pillar: P04
llm_function: CALL
purpose: Tools available for partner_listing production
quality: null
title: "Tools Partner Listing"
version: "1.0.0"
author: wave1_builder_gen_v2
tags: [partner_listing, builder, tools]
tldr: "Tools available for partner_listing production"
domain: "partner_listing construction"
created: "2026-04-14"
updated: "2026-04-14"
8f: "F5_call"
keywords: [partner_listing construction, tools partner listing, partner_listing, builder, tools, production tools, validation tools, external references, data validation framework, partner schema]
density_score: 0.85
related:
  - partner-listing-builder
  - bld_output_template_partner_listing
  - bld_collaboration_partner_listing
  - bld_knowledge_card_partner_listing
---
## Production Tools
| Tool              | Purpose                  | When                      |
|-------------------|--------------------------|---------------------------|
| cex_compile.py    | Aggregates partner data  | During data collection    |
| cex_score.py      | Assigns partner ratings  | Post-validation phase     |
| cex_retriever.py  | Fetches partner metadata | On-demand queries         |
| cex_doctor.py     | Diagnoses data issues    | Pre-validation checks     |
| cex_doctor.py  | Enforces schema rules    | Data ingestion pipeline   |
| cex_retriever.py   | Generates partner insights | Reporting cycles        |

## Validation Tools
| Tool              | Purpose                  | When                      |
|-------------------|--------------------------|---------------------------|
| val_check.py      | Verifies data consistency| Pre-deployment            |
| val_audit.py      | Cross-references records | Quarterly reviews         |
| val_comparator.py | Detects duplicates       | Merge operations          |
| val_sanitizer.py  | Cleans invalid entries   | Data preprocessing        |

## External References
- Partner API (v3.2): For real-time partner data integration
- Data Validation Framework (DVX): Schema enforcement library
- Partner Schema (v1.1): Standardized structure for listings

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[partner-listing-builder]] | downstream | 0.41 |
| [[bld_output_template_partner_listing]] | downstream | 0.39 |
| [[bld_collaboration_partner_listing]] | downstream | 0.38 |
| [[bld_knowledge_card_partner_listing]] | upstream | 0.35 |
