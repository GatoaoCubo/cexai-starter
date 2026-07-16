---
kind: tools
id: bld_tools_safety_hazard_taxonomy
pillar: P04
llm_function: CALL
purpose: Tools available for safety_hazard_taxonomy production
quality: null
title: "Tools Safety Hazard Taxonomy"
version: "1.0.0"
author: n01_wave7
tags: [safety_hazard_taxonomy, builder, tools, MLCommons, AILuminate, Llama-Guard]
tldr: "Tools available for safety_hazard_taxonomy production"
domain: "safety_hazard_taxonomy construction"
created: "2026-04-14"
updated: "2026-04-14"
8f: "F5_call"
keywords: [safety_hazard_taxonomy construction, tools safety hazard taxonomy, safety_hazard_taxonomy, builder, tools, mlcommons, ailuminate, llama-guard, production tools, validation tools]
density_score: 0.85
related:
  - bld_tools_gpai_technical_doc
  - bld_tools_churn_prevention_playbook
  - bld_tools_ai_rmf_profile
  - bld_tools_nps_survey
  - bld_tools_competitive_matrix
---

## Production Tools
| Tool | Purpose | When |
|------|---------|------|
| cex_compile.py | Compile .md to .yaml after save | Post-production |
| cex_score.py | Peer-review quality scoring | Post-production |
| cex_retriever.py | Fetch similar safety_hazard_taxonomy artifacts | During production |
| cex_doctor.py | Diagnose builder health | Pre-validation |
| cex_wave_validator.py | Validate 13-ISO completeness | Pre-commit |

## Validation Tools
| Tool | Purpose | When |
|------|---------|------|
| val_check.py | Verify all 12 hazard categories present | Pre-deployment |
| cex_score.py --apply | Apply peer review quality score | Post-review |

## External References
- MLCommons AILuminate: mlcommons.org/benchmarks/ailuminate/ (taxonomy reference)
- Meta Llama Guard 4: ai.meta.com/research/llama-guard/ (S1-S13 label definitions)
- Anthropic RSP ASL-3: anthropic.com/responsible-scaling-policy (CBRN threshold reference)
- EU AI Act Article 5: artificialintelligenceact.eu/article/5/ (prohibited AI practices -- CSAM, subliminal)

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[bld_tools_gpai_technical_doc]] | sibling | 0.41 |
| [[bld_tools_churn_prevention_playbook]] | sibling | 0.36 |
| [[bld_tools_ai_rmf_profile]] | sibling | 0.35 |
| [[bld_tools_nps_survey]] | sibling | 0.34 |
| [[bld_tools_competitive_matrix]] | sibling | 0.32 |
