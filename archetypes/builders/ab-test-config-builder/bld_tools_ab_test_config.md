---
kind: tools
id: bld_tools_ab_test_config
pillar: P04
llm_function: CALL
purpose: Tools available for ab_test_config production
quality: null
title: "Tools Ab Test Config"
version: "1.0.0"
author: wave1_builder_gen_v2
tags: [ab_test_config, builder, tools]
tldr: "Tools available for ab_test_config production"
domain: "ab_test_config construction"
created: "2026-04-14"
updated: "2026-04-14"
8f: "F5_call"
keywords: [ab_test_config construction, tools ab test config, ab_test_config, builder, tools, production tools, validation tools, external references, related artifacts, tools tool]
density_score: 0.85
related:
  - bld_tools_vad_config
  - bld_tools_prosody_config
  - bld_tools_quickstart_guide
  - bld_tools_transport_config
  - bld_tools_api_reference
---

## Production Tools
| Tool | Purpose | When |
|------|---------|------|
| cex_compile.py | Compiles AB test configurations into executable code | Pre-deployment |
| cex_score.py | Scores variant performance using metrics | Post-experiment |
| cex_retriever.py | Fetches historical AB test data | Analysis phase |
| cex_doctor.py | Diagnoses config conflicts or errors | Debugging |
| cex_retriever.py | Analyzes variant distribution and coverage | Planning phase |

## Validation Tools
| Tool | Purpose | When |
|------|---------|------|
| config_validator.py | Ensures config syntax and structure compliance | Pre-deployment |
| variant_checker.py | Verifies variant uniqueness and validity | Config design |
| data_integrity.py | Cross-checks data sources against config | Post-deployment |

## External References
- ABingo (A/B testing framework)
- JSON Schema (for config validation)
- Statsmodels (statistical analysis library)

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[bld_tools_vad_config]] | sibling | 0.44 |
| [[bld_tools_prosody_config]] | sibling | 0.43 |
| [[bld_tools_quickstart_guide]] | sibling | 0.31 |
| [[bld_tools_transport_config]] | sibling | 0.30 |
| [[bld_tools_api_reference]] | sibling | 0.30 |
