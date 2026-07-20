---
id: subscription_tier_n06
kind: subscription_tier
pillar: P11
nucleus: n06
title: "Subscription Tier Architecture -- Revenue Model and Upgrade Logic"
version: 1.0.0
quality: null
tags: [subscription, tier, pricing, revenue, saas, upgrade, expansion]
density_score: 1.0
related:
  - p06_enum_pricing_tiers_n06
  - p07_sr_commercial_n06
updated: "2026-07-20"
---

# Subscription Tier Architecture

**Every price in this file is an `{{open_var}}`.** This artifact ships the
STRUCTURE of a tier-driven revenue model -- fill every placeholder from your
own product's real numbers before you publish or price against it.

## Revenue Model Philosophy

Strategic Greed principle: every tier must earn its keep AND create
conditions for the next upgrade. Tiers are not just price buckets -- they
are upgrade funnels. FREE creates desire, STARTER creates dependency, PRO
creates team adoption, ENTERPRISE creates contracts.

## Tier Revenue Architecture

| Tier | Monthly Price | Annual Price | Target MRR/Customer | LTV Target |
|------|:---:|:---:|:---:|:---:|
| FREE | {{FREE_PRICE}} | {{FREE_PRICE}} | {{FREE_PRICE}} | {{FREE_LTV}} (convert target) |
| STARTER | {{STARTER_PRICE_MONTHLY}} | {{STARTER_PRICE_ANNUAL}} | {{STARTER_PRICE_MONTHLY}} | {{STARTER_LTV_RANGE}} |
| PRO | {{PRO_PRICE_MONTHLY}} | {{PRO_PRICE_ANNUAL}} | {{PRO_PRICE_MONTHLY}} | {{PRO_LTV_RANGE}} |
| ENTERPRISE | {{ENTERPRISE_PRICE_FLOOR}}+ | custom | {{ENTERPRISE_MRR_RANGE}} | {{ENTERPRISE_LTV_RANGE}} |

## Feature Matrix

| Feature | FREE | STARTER | PRO | ENTERPRISE |
|---------|:----:|:-------:|:---:|:----------:|
| Usage quota/month | {{FREE_QUOTA}} | {{STARTER_QUOTA}} | Unlimited | Unlimited |
| Core feature set | Minimal | Standard | Full | Full + custom |
| API access | No | No | Yes ({{PRO_API_RPM}} RPM) | Yes ({{ENT_API_RPM}} RPM) |
| Seats | 1 | 1 | {{PRO_SEATS}} | Unlimited |
| Priority support | No | No | Yes | Yes + CSM |
| SSO | No | No | No | Yes |
| Audit log | No | No | Yes | Yes |
| SLA uptime | No | No | No | {{ENT_SLA_PCT}}% |

## Upgrade Triggers (Automated)

```yaml
upgrade_triggers:
  free_to_starter:
    - event: quota_exhausted
      action: show_upgrade_modal
    - event: core_config_attempted
      action: gate_with_upgrade_prompt

  starter_to_pro:
    - event: api_access_requested
      action: show_upgrade_modal
    - event: second_seat_invited
      action: show_upgrade_modal

  pro_to_enterprise:
    - event: seats_at_capacity
      action: trigger_sales_touchpoint
    - event: sso_requested
      action: trigger_sales_touchpoint
    - event: compliance_document_requested
      action: trigger_sales_touchpoint
```

## Conversion Benchmarks (industry avg vs. your target)

| Conversion | Industry Avg | Your Target |
|-----------|:---:|:---:|
| FREE -> STARTER | 2-5% | {{TARGET_FREE_TO_STARTER}} |
| STARTER -> PRO | 15-25% | {{TARGET_STARTER_TO_PRO}} |
| PRO -> ENTERPRISE | 5-10% | {{TARGET_PRO_TO_ENTERPRISE}} |
| Monthly -> Annual | 20-40% | {{TARGET_MONTHLY_TO_ANNUAL}} |

## Annual vs Monthly Pricing Strategy

Annual discount: `{{ANNUAL_DISCOUNT_PCT}}`% (frame as "N months free" -- it
converts better than the same math shown as a percent).

Directional annual-customer benefits (verify against your own cohort data
before quoting as fact):
- Predictable revenue: annual tends to reduce churn vs. monthly
- Cash flow: upfront collection improves runway
- Commitment signal: annual customers tend to churn less than monthly

## Cannibalization Guard

```
PRO must NOT compete with the ENTERPRISE floor:
  - PRO caps seats below Enterprise's unlimited
  - PRO lacks SSO (Enterprise blocker)
  - PRO lacks SLA (Enterprise requirement)

STARTER must NOT feel "good enough" for power users:
  - No API access (developer workflow blocker)
  - 1 seat (no team use)
```

## Related Artifacts
| Artifact | Relationship |
|----------|-------------|
| [[p06_enum_pricing_tiers_n06]] | upstream (this model fills that enum's structure with a revenue view) |
| [[p07_sr_commercial_n06]] | downstream (Monetization rubric scores this kind) |
