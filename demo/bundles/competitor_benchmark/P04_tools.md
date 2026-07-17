---
kind: tools
id: bld_tools_competitive_matrix
pillar: P04
llm_function: CALL
purpose: Tools available for competitive_matrix production
quality: null
title: "Tools Competitive Matrix"
version: "1.1.0"
author: wave1_builder_gen_v2
tags: [competitive_matrix, builder, tools]
tldr: "CEX tools available for competitive_matrix production and validation"
domain: "competitive_matrix construction"
created: "2026-04-14"
updated: "2026-04-14"
8f: "F5_call"
keywords: [competitive_matrix construction, tools competitive matrix, competitive_matrix, builder, tools, production tools, validation tools, external references, gartner magic quadrant, forrester wave]
density_score: 0.85
related:
  - bld_tools_changelog
  - bld_tools_case_study
  - bld_tools_api_reference
  - bld_tools_rbac_policy
  - bld_tools_nps_survey
---

## Production Tools
| Tool | Purpose | When |
|------|---------|------|
| cex_compile.py | Compile .md artifact to .yaml sidecar | After write |
| cex_score.py | Score matrix against quality gate dimensions | Pre-publish |
| cex_retriever.py | Find existing matrices for cross-reference | During research |
| cex_doctor.py | Validate frontmatter, ID pattern, kind compliance | Pre-publish |

## Validation Tools
| Tool | Purpose | When |
|------|---------|------|
| cex_wave_validator.py | Check all builder ISOs for schema compliance | Post-build |
| cex_hooks.py | Pre-commit YAML validation and quality gate enforcement | On git commit |

## External References
- Gartner Magic Quadrant methodology (ability to execute x vision dimensions)
- Forrester Wave scoring methodology (feature weighting and benchmarking)
- G2 Grid (verified user review data for feature comparison)
- Battlecard.io / Klue / Crayon (battle card structure references)

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| bld_tools_changelog | sibling | 0.43 |
| bld_tools_case_study | sibling | 0.43 |
| bld_tools_api_reference | sibling | 0.36 |
| [[bld_tools_rbac_policy]] | sibling | 0.35 |
| bld_tools_nps_survey | sibling | 0.35 |
