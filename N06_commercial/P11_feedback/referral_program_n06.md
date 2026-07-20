---
id: referral_program_n06
kind: referral_program
pillar: P11
nucleus: n06
title: "Referral Program -- Customer Acquisition via Word-of-Mouth Engine"
version: 1.0.0
quality: null
tags:
  - "referral"
  - "acquisition"
  - "viral"
  - "growth"
  - "incentive"
  - "commercial"
density_score: 1.0
related:
  - nucleus_def_n06
  - subscription_tier_n06
  - cohort_analysis_n06
updated: "2026-07-20"
---

# Referral Program: Word-of-Mouth Revenue Engine

**Every reward amount below is an `{{open_var}}`.** This artifact ships the
STRUCTURE of a dual-sided referral engine -- bind every placeholder from your
own product's real pricing before you launch it.

## Strategic Intent

Referral programs exploit the highest-trust acquisition channel (peer recommendation) at the lowest CAC. For N06, referral is a primary viral growth loop: satisfied customers become distribution channels. Target: a meaningful share of new paid signups via referral within 12 months -- set your own `{{REFERRAL_SHARE_TARGET}}`.

## Program Structure

### Incentive Model: Dual-Sided

```
Referrer (existing customer) gets:
  - 1 month free on their plan for each referral who converts to paid
  - Credited to next invoice (no cash out needed)
  - Stackable: N referrals = N months free ({{PRO_MONTHLY_PRICE}} x N value)
  - Cap: 12 months credit per year per referrer

Referee (new customer) gets:
  - 1 month free on any paid plan (entry or mid tier)
  - Applied automatically on first invoice
  - Not stackable with other promotions

Enterprise referrals:
  - Cash incentive: {{ENTERPRISE_REFERRAL_BOUNTY}} for a verified Enterprise conversion
  - Paid 30 days post conversion (fraud prevention)
```

### Rationale for Dual-Sided

- Single-sided (referrer only): incentivizes referrer but no pull for referee
- Single-sided (referee only): referee advantage but referrer loses motivation
- Dual-sided: creates social contract -- referrer has skin in game AND gifts value to friend

## Mechanics

### Unique Referral Code

```
Format: {plan_tier}-{customer_id_prefix}-{random_4}
Example: pro-a1b2-x9k3

Generation: on account creation + in dashboard
```

### Attribution Flow

```
1. Referrer shares link: {{APP_DOMAIN}}/signup?ref=pro-a1b2-x9k3
2. Cookie set: ref_code = "pro-a1b2-x9k3" (30-day expiry)
3. Referee signs up -> ref_code persisted to customer.metadata.referral_code
4. Referee converts to paid -> webhook checkout.session.completed fires
5. N06 checks customer.metadata.referral_code
6. If referral_code valid -> credit referrer + send notification
7. Log to referral_ledger (referrer_id, referee_id, reward_type, date)
```

### Tracking Schema

```json
{
  "referral_id": "ref_20260417_a1b2_x9k3",
  "referrer_customer_id": "cus_abc123",
  "referee_customer_id": "cus_def456",
  "referral_code": "pro-a1b2-x9k3",
  "signup_date": "2026-04-17T10:00:00Z",
  "conversion_date": "2026-04-20T14:00:00Z",
  "reward_type": "credit_1_month",
  "reward_value_cents": "{{REWARD_VALUE_CENTS}}",
  "reward_status": "applied",
  "plan_at_conversion": "pro"
}
```

## Activation Points

Prompt referral sharing at high-delight moments:

| Trigger | Channel | Message |
|---------|---------|---------|
| First successful build completed | In-app banner | "Love what you just built? Share {{YOUR_PRODUCT}} with a colleague -- you both get a month free." |
| Usage quota at 50% | Email | "You're halfway through your quota. Know someone who'd love this? Share for free months." |
| Plan upgrade completed | In-app | "Welcome to PRO! As a thanks, here's your referral link..." |
| NPS score >= 9 | In-app | "You gave us 9/10 -- would you share {{YOUR_PRODUCT}} with your network?" |
| Monthly usage anniversary | Email | "1 year with {{YOUR_PRODUCT}}! Refer a friend and keep the momentum going." |

## Anti-Fraud Controls

| Fraud Type | Detection | Prevention |
|-----------|-----------|-----------|
| Self-referral | Same email domain or payment fingerprint | Block if referee_id == referrer_id OR same card |
| Fake signups | Trial account with no activity in 14 days | Only reward on paid conversion, not signup |
| Bulk code sharing | Unusually high conversions/month per referrer | Manual review trigger above your own threshold |
| Refund gaming | Refund after reward credited | 30-day hold before credit release |

## Performance Metrics

| Metric | Formula | Target |
|--------|---------|--------|
| Referral rate | referred_signups / total_signups | `{{REFERRAL_RATE_TARGET}}` |
| Referral conversion | referred_paid / referred_signups | `{{REFERRAL_CONVERSION_TARGET}}` |
| Viral coefficient (K) | referrals_sent per user * referral_conversion | `{{K_FACTOR_TARGET}}` |
| CAC via referral | rewards_paid / referred_paid_customers | `{{REFERRAL_CAC_CEILING}}` |
| Referral revenue share | referral_mrr / total_mrr | `{{REFERRAL_MRR_SHARE_TARGET}}` |

## Cohort Impact Tracking

Referred customers vs organic -- track directionally, then replace the
hypotheses below with your own measured deltas:
- Churn rate (hypothesis: lower, better retention)
- LTV (hypothesis: higher, better ICP match from peer recommendation)
- Time-to-activation (hypothesis: faster, pre-sold by referrer)
- Expansion rate (hypothesis: higher, team context from referrer)

Track via [[cohort_analysis_n06]] with `acquisition_channel = referral`.

## Related Artifacts
| Artifact | Relationship |
|----------|-------------|
| [[nucleus_def_n06]] | upstream |
| [[subscription_tier_n06]] | related (referral reward values are denominated in this tier model's prices) |
| [[cohort_analysis_n06]] | downstream (referral vs organic cohort comparison) |
