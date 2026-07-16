---
kind: tools
id: bld_tools_usage_quota
pillar: P04
llm_function: CALL
purpose: Tools available for usage_quota production
quality: null
title: "Tools Usage Quota"
version: "1.0.0"
author: wave1_builder_gen_v2
tags: [usage_quota, builder, tools]
tldr: "Tools available for usage_quota production"
domain: "usage_quota construction"
created: "2026-04-14"
updated: "2026-04-14"
8f: "F5_call"
keywords: [usage_quota construction, tools usage quota, usage_quota, builder, tools, production tools, validation tools, external references, related artifacts, tools tool]
density_score: 0.85
related:
  - bld_tools_rbac_policy
  - bld_tools_sso_config
  - bld_tools_integration_guide
  - bld_tools_playground_config
  - bld_tools_github_issue_template
---

## Production Tools
| Tool | Purpose | When |
|------|---------|------|
| cex_compile.py | Compile artifact .md to .yaml | After save |
| cex_score.py --apply | Peer review scoring (D1-D5 weighted) | Before publish |
| cex_doctor.py | Builder health check (validates all 13 ISOs) | Post-build |
| cex_retriever.py | TF-IDF similarity search (find similar artifacts) | F3 INJECT |

## Validation Tools
| Tool | Purpose | When |
|------|---------|------|
| cex_wave_validator.py | Validates frontmatter + kind/pillar/llm_function | CI gate |
| cex_hooks.py pre-commit | ASCII enforcement + schema check | Pre-commit |
| cex_hygiene.py | Artifact CRUD + 8-rule enforcement | Pre-commit |

## External References
- Token bucket / leaky bucket algorithms -- RFC 6585 + IETF rate-limiting headers
- Stripe metered billing -- tiered quota + usage-based pricing model
- AWS API Gateway throttling -- 429 + X-RateLimit-Remaining + retry-after headers

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[bld_tools_rbac_policy]] | sibling | 0.52 |
| [[bld_tools_sso_config]] | sibling | 0.45 |
| [[bld_tools_integration_guide]] | sibling | 0.38 |
| [[bld_tools_playground_config]] | sibling | 0.37 |
| [[bld_tools_github_issue_template]] | sibling | 0.37 |
