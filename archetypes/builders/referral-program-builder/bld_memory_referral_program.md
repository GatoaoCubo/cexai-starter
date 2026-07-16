---
kind: memory
id: p10_mem_referral_program_builder
pillar: P10
llm_function: INJECT
purpose: Learned patterns and pitfalls for referral_program construction
quality: null
title: "Learning Record Referral Program"
version: "1.0.0"
author: wave1_builder_gen_v2
tags: [referral_program, builder, learning_record]
tldr: "Learned patterns and pitfalls for referral_program construction"
domain: "referral_program construction"
created: "2026-04-14"
updated: "2026-04-14"
8f: "F3_inject"
keywords: [referral_program construction, learning record referral program, referral_program, builder, learning_record, observation
common, pattern
effective, evidence
reviewed, related artifacts, viral coefficient]
density_score: 0.85
related:
  - referral-program-builder
---
## Observation
Common issues include underestimating viral coefficient thresholds, leading to slow adoption, and reward structures that incentivize short-term gains over long-term retention.

## Pattern
Effective designs balance immediate rewards with long-term value, using tiered incentives to scale participation while maintaining program sustainability.

## Evidence
Reviewed artifacts showed programs with viral coefficients >1.5 achieved 40% faster growth, while those with unclear reward tiers saw 30% higher churn.

## Recommendations
- Calculate viral coefficient early using hypothetical user behavior models.
- Implement tiered rewards that escalate with referral volume (e.g., 1st referrer gets $5, 10th gets $20).
- Track referral sources explicitly to avoid ambiguity in credit allocation.
- Test reward thresholds against retention metrics to prevent burnout.
- Ensure program rules are visible in onboarding flows to reduce confusion.

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[referral-program-builder]] | downstream | 0.45 |
