---
kind: tools
id: bld_tools_pricing_page
pillar: P04
llm_function: CALL
purpose: Tools available for pricing_page production
quality: null
title: "Tools Pricing Page"
version: "1.0.0"
author: wave1_builder_gen_v2
tags: [pricing_page, builder, tools]
tldr: "Tools available for pricing_page production"
domain: "pricing_page construction"
created: "2026-04-14"
updated: "2026-04-14"
8f: "F5_call"
keywords: [pricing_page construction, tools pricing page, pricing_page, builder, tools, production tools, validation tools, external references, stripe pricing page, linear pricing]
density_score: 0.85
related:
  - bld_tools_onboarding_flow
  - bld_tools_referral_program
  - bld_tools_usage_quota
  - bld_tools_rbac_policy
  - bld_tools_churn_prevention_playbook
---

## Production Tools
| Tool | Purpose | When |
|------|---------|------|
| cex_compile.py | Compile artifact after save | F8 COLLABORATE |
| cex_score.py | Score artifact against 5D rubric | F7 GOVERN |
| cex_retriever.py | Fetch similar pricing_page artifacts for Template-First | F3 INJECT |
| cex_doctor.py | Validate builder health and ISO completeness | Post-edit check |

## Validation Tools
| Tool | Purpose | When |
|------|---------|------|
| cex_wave_validator.py | Validate builder ISO set (13-file check, frontmatter gates) | Pre-commit |
| cex_hygiene.py | Artifact CRUD rules, naming pattern enforcement | Post-save |

## External References
- Stripe Pricing Page (industry standard tier comparison)
- Linear Pricing (PLG-optimized, annual toggle, most-popular badge)
- Vercel Pricing (usage-based + tiered hybrid reference)

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[bld_tools_onboarding_flow]] | sibling | 0.41 |
| [[bld_tools_referral_program]] | sibling | 0.39 |
| [[bld_tools_usage_quota]] | sibling | 0.35 |
| [[bld_tools_rbac_policy]] | sibling | 0.33 |
| [[bld_tools_churn_prevention_playbook]] | sibling | 0.30 |
