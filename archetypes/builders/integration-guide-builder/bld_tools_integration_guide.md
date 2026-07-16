---
kind: tools
id: bld_tools_integration_guide
pillar: P04
llm_function: CALL
purpose: Tools available for integration_guide production
quality: null
title: "Tools Integration Guide"
version: "1.0.0"
author: wave1_builder_gen_v2
tags: [integration_guide, builder, tools]
tldr: "Tools available for integration_guide production"
domain: "integration_guide construction"
created: "2026-04-14"
updated: "2026-04-14"
8f: "F5_call"
keywords: [integration_guide construction, tools integration guide, integration_guide, builder, tools, production tools, validation tools, external references, salesforce app, related artifacts]
density_score: 0.85
related:
  - bld_tools_playground_config
  - bld_tools_sandbox_spec
  - bld_tools_github_issue_template
  - bld_tools_rbac_policy
  - bld_tools_usage_quota
---

## Production Tools
| Tool | Purpose | When |
|------|---------|------|
| cex_compile.py | Compile .md artifact to .yaml | Post-write (F8) |
| cex_retriever.py | TF-IDF similarity over 2184 docs | Find prior integration_guide artifacts (F3) |
| cex_score.py | 3-layer scoring (structural + rubric + semantic) | Quality gate (F7) |
| cex_doctor.py | Builder health check across 13 ISOs | Pre-dispatch validation |
| cex_hygiene.py | Frontmatter + ASCII + naming enforcement | Pre-commit (F7) |
| cex_prompt_optimizer.py | Analyze builder ISOs for drift | When quality < 9.0 |

## Validation Tools
| Tool | Purpose | When |
|------|---------|------|
| cex_wave_validator.py | D01-D15 defect checks across ISOs | After bulk generation |
| cex_sanitize.py --check | ASCII-only enforcement on .py/.ps1 | Pre-commit hook |
| cex_hooks.py pre-commit | YAML frontmatter + schema compliance | Git pre-commit |

## External References
- Diataxis framework (How-To guide quadrant, not reference/tutorial/explanation)
- Auth0 quickstarts + deep-dive integration patterns
- OAuth 2.1 / OIDC / SAML 2.0 federated identity standards
- Salesforce AppExchange partner certification checklist
- Slack app directory submission requirements
- OpenAPI 3.1 (API contract reference)
- Webhook vs polling trade-off analysis (Stripe, GitHub, Shopify patterns)

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[bld_tools_playground_config]] | sibling | 0.52 |
| [[bld_tools_sandbox_spec]] | sibling | 0.46 |
| [[bld_tools_github_issue_template]] | sibling | 0.41 |
| [[bld_tools_rbac_policy]] | sibling | 0.40 |
| [[bld_tools_usage_quota]] | sibling | 0.39 |
