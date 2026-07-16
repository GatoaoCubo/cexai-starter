---
kind: tools
id: bld_tools_legal_vertical
pillar: P04
llm_function: CALL
purpose: Tools available for legal_vertical production
quality: null
title: "Tools Legal Vertical"
version: "1.0.0"
author: wave1_builder_gen_v2
tags: [legal_vertical, builder, tools]
tldr: "Tools available for legal_vertical production"
domain: "legal_vertical construction"
created: "2026-04-14"
updated: "2026-04-14"
8f: "F5_call"
keywords: [legal_vertical construction, tools legal vertical, legal_vertical, builder, tools, production tools, validation tools, external references, related artifacts, tools tool]
density_score: 0.85
related:
  - bld_tools_pricing_page
  - bld_tools_changelog
  - bld_tools_competitive_matrix
  - bld_tools_usage_quota
  - bld_tools_github_issue_template
---

## Production Tools
| Tool | Purpose (legal context) | When |
|---|---|---|
| cex_compile.py | Compile legal_vertical artifact to YAML + validate frontmatter | After authoring |
| cex_score.py | Score artifact against H01-H10 gates and 7D SOFT dimensions | Before publish |
| cex_retriever.py | Retrieve similar privilege/billing/contract artifacts from knowledge library | During research |
| cex_doctor.py | Health-check builder ISO completeness and frontmatter validity | QA pass |

## Validation Tools
| Tool | Purpose | When |
|---|---|---|
| cex_wave_validator.py | Validate all 13 ISOs in builder directory | Post-build |
| cex_hygiene.py | Enforce naming, frontmatter, ASCII rules | Pre-commit |

## External References
- Westlaw / LexisNexis -- primary law research
- iManage / NetDocuments -- DMS integration reference patterns
- Relativity / Everlaw -- eDiscovery platform integration

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[bld_tools_pricing_page]] | sibling | 0.32 |
| [[bld_tools_changelog]] | sibling | 0.31 |
| [[bld_tools_competitive_matrix]] | sibling | 0.31 |
| [[bld_tools_usage_quota]] | sibling | 0.31 |
| [[bld_tools_github_issue_template]] | sibling | 0.31 |
