---
id: p11_cm_content_monetization_n06
kind: content_monetization
pillar: P11
nucleus: n06
title: "Content Monetization Strategy -- Tiered SaaS + Infoproduct Pattern"
version: 1.0.0
quality: null
tags: [monetization, pricing, saas, infoproducts, revenue, launch]
tldr: "Generic monetization pattern: an open core as the funnel, tiered SaaS subscriptions as primary revenue, infoproducts (courses/certifications) as a secondary line. Every number is an {{open_var}} -- this is the PATTERN, not a filled business plan."
slots:
  target_segment: "the buyer persona being priced (solo | team | enterprise)"
  pricing_experiment: "the A/B lever under test"
  launch_month: "which go-to-market phase is being executed"
density_score: 0.9
related:
  - subscription_tier_n06
  - p06_enum_pricing_tiers_n06
updated: "2026-07-20"
---

# Content Monetization Strategy

## Product Snapshot

| Dimension | Value |
|-----------|-------|
| Model | `{{LICENSE_MODEL}}` (e.g. open core + commercial tiers) |
| Primary revenue | SaaS subscriptions (recurring) |
| Secondary revenue | Infoproducts: courses, workshops, certifications |
| Tertiary revenue | Consulting / implementation services |
| Strategy | Free drives adoption -> infoproducts monetize the methodology -> subscriptions capture teams |

Strategic Greed principle: a free/open core is the funnel, not the ceiling --
give the engine away, sell the driver's education.

## Inputs (act-time slots)

```yaml
slots:
  target_segment: "<solo | team | enterprise>"
  pricing_experiment: "<the A/B lever under test, e.g. {{TIER_NAME}} {{PRICE_A}} vs {{PRICE_B}}>"
  launch_month: "<1 | 2 | 3>"
```

## How to use

Treat this as a PATTERN, not a filled plan. Its 8F verb is PRODUCE -- it
generates a revenue plan; it does not gate.

- Use the tier table below as the packaging shape; never quote a price that is not bound from an `{{open_var}}`.
- Apply the Cannibalization Guard before adding a feature to a lower tier -- see [[subscription_tier_n06]] for the full guard.
- Fill `target_segment`, `pricing_experiment`, and `launch_month` before acting.
- Do not invent ROI numbers -- consult a real roi_calculator instance for the per-tier justification.

## 1. Tier Comparison (shape only)

| Feature | FREE | STARTER | PRO | ENTERPRISE |
|---------|:----:|:-------:|:---:|:----------:|
| Price (monthly) | {{FREE_PRICE}} | {{STARTER_PRICE}} | {{PRO_PRICE}} | {{ENTERPRISE_PRICE}}+ |
| Price (annual) | {{FREE_PRICE}} | {{STARTER_ANNUAL}} | {{PRO_ANNUAL}} | Custom |
| Core usage quota | {{FREE_QUOTA}} | {{STARTER_QUOTA}} | Unlimited | Unlimited |
| Seats | 1 | 1 | {{PRO_SEATS}} | Unlimited |
| API access | No | No | Yes | Yes |
| SSO / audit log | No | No | Partial | Full |

## 2. Revenue Model Shape

| Variable | Value | Basis |
|----------|-------|-------|
| FREE -> STARTER conversion | {{CONV_FREE_STARTER}} | vs. 2-5% industry avg |
| STARTER -> PRO conversion | {{CONV_STARTER_PRO}} | vs. 15-25% industry avg |
| PRO -> ENTERPRISE conversion | {{CONV_PRO_ENT}} | vs. 5-10% industry avg |
| Monthly -> Annual rate | {{CONV_MONTHLY_ANNUAL}} | vs. 20-40% industry avg |

MRR formula: `(STARTER_count x STARTER_price) + (PRO_count x PRO_price) +
(ENTERPRISE_count x ENTERPRISE_avg_deal)`. Never publish a projection
without showing this formula next to it -- an unlabeled number invites
disbelief.

## 3. Infoproduct Catalog (shape only)

| Product | Format | Price | Target |
|---------|--------|:-----:|--------|
| {{COURSE_1_NAME}} | On-demand video | {{COURSE_1_PRICE}} | Free users upgrading to STARTER |
| {{COURSE_2_NAME}} | Live cohort | {{COURSE_2_PRICE}} | STARTER -> PRO fence-sitters |
| {{CERT_NAME}} | Exam + project | {{CERT_PRICE}} | Individual contributors |
| {{CONSULTING_PACKAGE}} | Scoped engagement | {{CONSULTING_PRICE}} | Power users, agency leads |

## 4. Cannibalization Guard

```
{{TIER_LOW}} must NOT satisfy {{TIER_MID}} buyers:
  - name the specific blocker feature(s) withheld from the lower tier

{{TIER_MID}} must NOT satisfy {{TIER_HIGH}} buyers:
  - name the specific blocker feature(s) -- seats cap, SSO, SLA, white-label
```

## 5. Go-to-Market Skeleton (3-phase, fill per launch)

| Phase | Focus | Owner | KPI |
|-------|-------|-------|-----|
| 1 -- Foundation | Pricing page live, checkout wired, launch post | {{OWNER_1}} | {{KPI_1}} |
| 2 -- Community & Conversion | Webinar, community launch, nurture sequence | {{OWNER_2}} | {{KPI_2}} |
| 3 -- Enterprise & Refinement | Outreach, pricing A/B, quarterly review | {{OWNER_3}} | {{KPI_3}} |

## 6. Annual vs Monthly Strategy

Annual discount: `{{ANNUAL_DISCOUNT_PCT}}`% (framed as "N months free").

| Benefit of Annual | Impact |
|------------------|--------|
| Churn reduction | Directionally lower than monthly -- verify against your own cohorts |
| Cash flow | Full-period collection at signup |
| Commitment signal | Annual customers tend to churn less on average |

## Related Artifacts
| Artifact | Relationship |
|----------|-------------|
| [[subscription_tier_n06]] | sibling (this is the strategy layer; that is the tier-data layer) |
| [[p06_enum_pricing_tiers_n06]] | upstream |
