---
id: p06_enum_pricing_tiers_n06
kind: enum_def
pillar: P06
nucleus: n06
title: "Enum Definition -- Pricing Tier Taxonomy"
version: 1.0.0
quality: null
tags:
  - "pricing"
  - "tiers"
  - "enum"
  - "commercial"
  - "saas"
  - "packaging"
keywords:
  - "pricing tier enum"
  - "feature gate matrix"
  - "upgrade path"
  - "pricing psychology"
  - "plan tier taxonomy"
density_score: 1.0
related:
  - p06_is_checkout_n06
  - subscription_tier_n06
updated: "2026-07-20"
---

# Enum Definition: Pricing Tier Taxonomy

## Purpose

Canonical enumeration of pricing tiers, their feature gates, limits, and billing-provider price-ID mapping. Every part of a commercial system references this enum -- pricing pages, checkout flow, entity_memory, churn logic, expansion plays.

**Open variables**: every dollar figure and price-ID below is a `{{open_var}}`. This artifact ships the *structure* of a tiering system, not a filled price sheet -- bind every `{{...}}` from your own product's brand_config before use.

## Tier Enum

```typescript
enum PlanTier {
  FREE       = "free",
  STARTER    = "starter",
  PRO        = "pro",
  ENTERPRISE = "enterprise",
  CUSTOM     = "custom"
}
```

## Tier Definitions

### FREE

```yaml
tier: free
price_id: null
monthly_price: 0
annual_price: 0
seats: 1
feature_flags:
  usage_quota: {{FREE_USAGE_QUOTA}}
  feature_set: [{{FREE_FEATURE_1}}]
  api_access: false
  priority_support: false
upgrade_path: starter
conversion_trigger: "quota exhausted OR a gated feature requested"
```

### STARTER

```yaml
tier: starter
price_id_monthly: {{STARTER_PRICE_ID_MONTHLY}}
price_id_annual: {{STARTER_PRICE_ID_ANNUAL}}
monthly_price: {{STARTER_PRICE_MONTHLY}}
annual_price: {{STARTER_PRICE_ANNUAL}}       # ~20% discount = "2 months free" framing
annual_discount_pct: 20
seats: 1
feature_flags:
  usage_quota: {{STARTER_USAGE_QUOTA}}
  feature_set: [{{STARTER_FEATURE_LIST}}]
  api_access: false
  priority_support: false
upgrade_trigger: "quota exhausted OR API access needed OR seats > 1"
churn_risk_signals: ["<20% of quota used", "no core config set", "login <2x/month"]
```

### PRO

```yaml
tier: pro
price_id_monthly: {{PRO_PRICE_ID_MONTHLY}}
price_id_annual: {{PRO_PRICE_ID_ANNUAL}}
monthly_price: {{PRO_PRICE_MONTHLY}}
annual_price: {{PRO_PRICE_ANNUAL}}
annual_discount_pct: 20
seats: {{PRO_SEATS}}
feature_flags:
  usage_quota: unlimited
  feature_set: [{{PRO_FEATURE_LIST}}]
  api_access: true
  api_rate_limit_rpm: {{PRO_API_RPM}}
  priority_support: true
  audit_log: true
upgrade_trigger: "seats exceeded OR SSO required OR custom SLA needed"
expansion_target: enterprise
```

### ENTERPRISE

```yaml
tier: enterprise
price_id: negotiated
monthly_price_floor: {{ENTERPRISE_PRICE_FLOOR}}
seats: unlimited
feature_flags:
  usage_quota: unlimited
  feature_set: all
  api_access: true
  api_rate_limit_rpm: {{ENTERPRISE_API_RPM}}
  priority_support: true
  dedicated_success_manager: true
  sso: true
  audit_log: true
  custom_integrations: true
  sla_uptime_pct: 99.9
  data_residency: true
qualification: "requires sales touch, > {{ENTERPRISE_SEAT_THRESHOLD}} seats OR compliance requirements OR custom SLA"
```

### CUSTOM

```yaml
tier: custom
price_id: bespoke
description: "White-label, OEM, reseller, or usage-based pricing arrangements"
qualification: "legal review required"
```

## Feature Gate Logic

```python
def is_feature_enabled(customer_tier: str, feature: str) -> bool:
    tier_order = ["free", "starter", "pro", "enterprise", "custom"]
    feature_min_tier = {
        "core_config": "starter",
        "api_access": "pro",
        "sso": "enterprise",
        "audit_log": "pro",
        "dedicated_csm": "enterprise",
        "custom_integrations": "enterprise",
    }
    min_tier = feature_min_tier.get(feature, "free")
    return tier_order.index(customer_tier) >= tier_order.index(min_tier)
```

## Upgrade Path Matrix

```
FREE -> STARTER -> PRO -> ENTERPRISE
          ^                   |
          |                   v
          +--- downgrade ------+
                (retention play)
```

## Pricing Psychology Notes

| Principle | Application |
|-----------|-------------|
| Good/Better/Best | FREE anchors value; PRO is the hero tier; ENTERPRISE is the ceiling |
| Annual discount | 20% off framed as "2 months free" -- reads stronger than "20% off" |
| Seat-based expansion | A low per-tier seat cap creates a natural expansion trigger as teams grow |
| Feature gating | Gate the ONE feature power users need (e.g. API) just above the tier you want them to buy |
| Trial-to-paid | FREE needs a real limit to create urgency without a free-rider problem |

## Related Artifacts
| Artifact | Relationship |
|----------|-------------|
| [[p06_is_checkout_n06]] | sibling (checkout validates `plan_tier` against this enum) |
| [[subscription_tier_n06]] | downstream (fills this enum's `{{open_vars}}` into a full revenue model) |
