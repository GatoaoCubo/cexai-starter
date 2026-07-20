---
id: p09_env_n06
kind: env_config
pillar: P09
nucleus: n06
title: Commercial Env Config
version: 1.0.0
quality: null
tags:
  - "config"
  - "env"
  - "pricing"
  - "funnel"
  - "revenue"
density_score: 1.0
related:
  - nucleus_def_n06
  - p06_enum_pricing_tiers_n06
updated: "2026-07-20"
---

# Commercial Env Config

## Purpose

| Field | Value |
|-------|-------|
| Goal | Define the environment variable contract for N06 pricing, funnel, monetization, and renewal systems |
| Business Lens | Strategic Greed uses env vars to make revenue experiments fast while keeping premium defaults protected |
| Primary Use | Configure pricing engines, checkout routing, offer cadence, budget thresholds, and retention alerts |
| Failure Prevented | hidden defaults, unsafe free-tier leakage, and environment drift across commercial surfaces |
| Scope | local, staging, production |
| Precedence | runtime env -> managed secret injection -> safe default |

## Values

Every default below is an `{{open_var}}` -- this ships the config *contract*,
not a filled deployment. Bind each `{{...}}` from your own product's
brand_config / ops runbook before deploying.

| Variable | Type | Default | Required | Validation | Commercial Intent |
|----------|------|---------|----------|------------|-------------------|
| N06_ENV | string | `local` | yes | `local\|staging\|prod` | environment-specific greed level |
| N06_DEFAULT_CURRENCY | string | `{{DEFAULT_CURRENCY}}` | yes | ISO 4217 | normalize monetization reports |
| N06_DEFAULT_REVENUE_STATE | string | `lead_captured` | yes | must match enum | safe first funnel state |
| N06_MIN_CHECKOUT_VALUE | decimal | `{{MIN_CHECKOUT_VALUE}}` | yes | `>= 0` | blocks low-value custom work |
| N06_ANNUAL_DISCOUNT_CAP_PCT | integer | `20` | yes | `0-40` | prevents margin-eroding discounts |
| N06_FREE_TIER_LIMIT_EVENTS | integer | `{{FREE_TIER_LIMIT}}` | yes | `>= 0` | keeps free usage from cannibalizing paid |
| N06_UPSELL_TRIGGER_USAGE_PCT | integer | `80` | yes | `50-100` | prompt expansion before churn |
| N06_RENEWAL_RISK_WINDOW_DAYS | integer | `14` | yes | `1-45` | start save motions before renewal fails |
| N06_DUNNING_MAX_ATTEMPTS | integer | `4` | yes | `1-10` | balance recovery with customer fatigue |
| N06_MARGIN_FLOOR_PCT | integer | `{{MARGIN_FLOOR_PCT}}` | yes | `1-95` | defend profitability |
| N06_PRIORITY_SEGMENTS | string | `{{PRIORITY_SEGMENTS}}` | yes | comma list | premium demand gets first attention |
| N06_EXPERIMENTS_ENABLED | boolean | `true` | yes | `true\|false` | pricing compounding stays on by default |
| N06_PRICE_ANCHOR_MODE | string | `premium_first` | yes | `premium_first\|mid_first\|off` | anchors buyers toward higher tiers |
| N06_ALERT_WEBHOOK | secret_ref | none | no | secret pointer only | notify revenue-risk systems |
| N06_PAYMENT_PROVIDER | string | `{{PAYMENT_PROVIDER}}` | yes | provider name | select monetization rail |

## Profiles

| Environment | Override | Why |
|-------------|----------|-----|
| local | experiments enabled, low alert noise | fast commercial iteration |
| staging | production-like values, sandbox provider | validates pricing logic safely |
| prod | strict floors and premium-first anchor | protect margin and realized cash |

## Rationale

| Design Choice | Why It Exists |
|---------------|---------------|
| Currency default is explicit | revenue reports fail when currency is implicit |
| Margin floor env var | margin policy changes faster than code -- allows rapid profit defense |
| Annual discount cap | discounting is the fastest way to destroy value -- forces deliberate concessions |
| Priority segment list | not all customers deserve equal latency -- shifts attention to highest LTV |
| Upsell trigger threshold | expansion must happen before plateau |
| Renewal risk window | retention is cheaper than reacquisition -- activates save tactics earlier |

## Example

```env
N06_ENV=prod
N06_DEFAULT_CURRENCY={{DEFAULT_CURRENCY}}
N06_DEFAULT_REVENUE_STATE=lead_captured
N06_MIN_CHECKOUT_VALUE={{MIN_CHECKOUT_VALUE}}
N06_ANNUAL_DISCOUNT_CAP_PCT=20
N06_FREE_TIER_LIMIT_EVENTS={{FREE_TIER_LIMIT}}
N06_UPSELL_TRIGGER_USAGE_PCT=80
N06_RENEWAL_RISK_WINDOW_DAYS=14
N06_DUNNING_MAX_ATTEMPTS=4
N06_MARGIN_FLOOR_PCT={{MARGIN_FLOOR_PCT}}
N06_PRIORITY_SEGMENTS={{PRIORITY_SEGMENTS}}
N06_EXPERIMENTS_ENABLED=true
N06_PRICE_ANCHOR_MODE=premium_first
N06_PAYMENT_PROVIDER={{PAYMENT_PROVIDER}}
```

## Notes

| Topic | Rule |
|-------|------|
| Secrets | webhooks and provider keys come from a secret_config reference, never inline |
| Validation | enum-backed values must match N06 schemas |
| Logging | sensitive values masked, commercial thresholds visible |
| Drift | staging should mirror prod except for payment settlement and alert routing |

## Related Artifacts
| Artifact | Relationship |
|----------|-------------|
| [[nucleus_def_n06]] | upstream |
| [[p06_enum_pricing_tiers_n06]] | related (N06_DEFAULT_REVENUE_STATE and tier gating reference that enum) |
