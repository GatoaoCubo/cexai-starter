---
id: kc_referral_program
kind: knowledge_card
8f: F3_inject
title: Referral Program Design
version: 1.0.0
quality: null
pillar: P01
description: Referral program design with viral coefficient and reward structure
tldr: "Referral program blueprint with viral coefficient math, tiered reward structure, and tracking"
when_to_use: "When designing a user acquisition loop driven by participant referrals and incentive tiers"
keywords: [viral coefficient, conversion rate, tiered bonuses, long-term incentives, participant codes, automated email reminders, social sharing incentives]
density_score: 1.0
related:
  - p10_mem_referral_program_builder
  - bld_knowledge_card_referral_program
  - p11_qg_referral_program
  - referral-program-builder
  - bld_instruction_referral_program
---

# Referral Program Design

## How to use

You are a referral-program-builder. Load this card at **F3 INJECT**, then design
the acquisition loop against the math and tiers below.

- Compute the target viral coefficient first; aim for 1.0-2.0 (sustainable, not runaway).
- Set base + tiered rewards so marginal cost stays below referred-customer LTV.
- Instrument unique participant codes BEFORE launch; you cannot attribute retroactively.
- Re-tune tiers quarterly from the measured coefficient, not from assumptions.

A well-structured referral program balances viral growth with participant incentives. Key components include:

## Viral Coefficient
This metric measures program effectiveness:
- **Viral Coefficient = (Referrals per Participant × Conversion Rate)**
- Ideal range: 1.0-2.0 for sustainable growth
- Example: 5 referrals × 20% conversion = 1.0 coefficient

## Reward Structure
Design incentives to drive participation:

### Base Rewards
- 10% commission on referred sign-ups
- $50 bonus for first 3 referrals

### Tiered Bonuses
- 5% bonus for 4-9 referrals
- 10% bonus for 10+ referrals
- 15% bonus for 20+ referrals

### Long-term Incentives
- Monthly leaderboard with top 3 earners
- Annual bonus for 100+ referrals
- Exclusive perks for 500+ referrals

## Implementation Tips
1. Track referrals with unique participant codes
2. Use automated email reminders
3. Monitor viral coefficient quarterly
4. Adjust reward tiers based on participation rates
5. Add social sharing incentives for viral growth

A successful referral program requires balancing immediate rewards with long-term growth goals. Regularly analyze performance metrics to optimize the program structure.

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[p10_mem_referral_program_builder]] | downstream | 0.43 |
| [[bld_knowledge_card_referral_program]] | sibling | 0.42 |
| [[p11_qg_referral_program]] | downstream | 0.42 |
| [[referral-program-builder]] | downstream | 0.39 |
| [[bld_instruction_referral_program]] | downstream | 0.35 |
