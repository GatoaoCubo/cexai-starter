---
kind: tools
id: bld_tools_subscription_tier
pillar: P04
llm_function: CALL
purpose: Tools available for subscription_tier production
quality: null
title: "Tools Subscription Tier"
version: "1.0.0"
author: wave1_builder_gen_v2
tags: [subscription_tier, builder, tools]
tldr: "Tools available for subscription_tier production"
domain: "subscription_tier construction"
created: "2026-04-14"
updated: "2026-04-14"
8f: "F5_call"
keywords: [subscription_tier construction, tools subscription tier, subscription_tier, builder, tools, production tools, validation tools, external references, related artifacts, tools tool]
density_score: 0.85
related:
  - bld_instruction_subscription_tier
  - kc_subscription_tier
  - bld_tools_edit_format
  - bld_tools_vad_config
  - bld_collaboration_subscription_tier
---
## Production Tools
| Tool | Purpose | When |
|---|---|---|
| tier_compile.py | Compiles subscription tier configurations | During tier creation |
| tier_score.py | Scores tiers based on user engagement metrics | During tier evaluation |
| tier_retriever.py | Retrieves tier data from external systems | When syncing with payment platforms |
| tier_doctor.py | Diagnoses tier configuration issues | During validation phase |
| tier_optimizer.py | Optimizes tier pricing and benefits | During tier refinement |
| tier_validator.py | Validates tier compliance with policies | Before deployment |

## Validation Tools
| Tool | Purpose | When |
|---|---|---|
| tier_linter.py | Checks tier syntax and structure | During development |
| tier_comparator.py | Compares tiers for consistency | During audits |
| tier_stress_tester.py | Simulates high-load tier scenarios | Before deployment |

## External References
- Stripe API (payment processing)
- TieredAccess framework (subscription management)
- SchemaValidator (configuration schema checks)

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[bld_instruction_subscription_tier]] | upstream | 0.33 |
| [[kc_subscription_tier]] | upstream | 0.32 |
| bld_tools_edit_format | sibling | 0.30 |
| bld_tools_vad_config | sibling | 0.30 |
| [[bld_collaboration_subscription_tier]] | downstream | 0.30 |
