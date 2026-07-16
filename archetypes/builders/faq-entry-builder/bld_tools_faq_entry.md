---
kind: tools
id: bld_tools_faq_entry
pillar: P04
llm_function: CALL
purpose: Tools available for faq_entry production
quality: null
title: "Tools Faq Entry"
version: "1.0.0"
author: wave1_builder_gen_v2
tags: [faq_entry, builder, tools]
tldr: "Tools available for faq_entry production"
domain: "faq_entry construction"
created: "2026-04-14"
updated: "2026-04-14"
8f: "F5_call"
keywords: [faq_entry construction, tools faq entry, faq_entry, builder, tools, production tools, validation tools, external references, related artifacts, tools tool]
density_score: 0.85
related:
  - bld_tools_vad_config
  - bld_tools_api_reference
  - bld_tools_quickstart_guide
  - bld_tools_ab_test_config
  - bld_tools_marketplace_app_manifest
---

## Production Tools
| Tool | Purpose | When |
|------|---------|------|
| cex_compile.py | Compiles FAQ entries into structured format | During build |
| cex_score.py | Scores FAQ quality based on relevance | Pre-publishing |
| cex_retriever.py | Fetches external data for entries | When sourcing data |
| cex_doctor.py | Diagnoses entry inconsistencies | On validation failure |
| cex_compile.py | Enforces markdown syntax standards | Pre-export |
| cex_doctor.py | Validates entry schema compliance | During build |

## Validation Tools
| Tool | Purpose | When |
|------|---------|------|
| val_syntax_checker.py | Checks markdown syntax | Pre-publishing |
| val_consistency_checker.py | Ensures cross-entry consistency | During review |
| val_duplicate_finder.py | Detects duplicate entries | On import |

## External References
- Markdownlint (syntax validation)
- JSON Schema (schema validation)
- FAQify (FAQ framework reference)

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[bld_tools_vad_config]] | sibling | 0.37 |
| [[bld_tools_api_reference]] | sibling | 0.36 |
| [[bld_tools_quickstart_guide]] | sibling | 0.35 |
| [[bld_tools_ab_test_config]] | sibling | 0.31 |
| [[bld_tools_marketplace_app_manifest]] | sibling | 0.31 |
