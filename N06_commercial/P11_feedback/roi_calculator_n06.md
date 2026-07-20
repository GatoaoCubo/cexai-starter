---
id: roi_calculator_n06
kind: roi_calculator
pillar: P11
nucleus: n06
title: "ROI Calculator -- Customer Value Proof Model"
version: 1.0.0
quality: null
tags: [roi, value, calculator, sales, proof, commercial, ltv]
tldr: "Customer value proof model -- quantifies hours/dollars your product saves a buyer by tier and persona -- so value > price is undeniable in sales, pricing, and renewal."
when_to_use: "Load when producing an ROI case for a prospect or renewal. Consult for 'how much does this product save the buyer and what is the payback period'."
slots:
  team_size: "<INTEGER -- number of people who would use the product>"
  hourly_rate_usd: "<INTEGER -- fully-loaded hourly cost per person>"
  tier_price_monthly: "<INTEGER -- the tier price being justified against>"
  builds_per_week: "<INTEGER -- units of work produced manually today>"
density_score: 1.0
related:
  - nucleus_def_n06
  - subscription_tier_n06
  - p06_enum_pricing_tiers_n06
updated: "2026-07-20"
---

# ROI Calculator: Customer Value Proof Model

**Every dollar figure in this file is illustrative or an `{{open_var}}`.**
This artifact ships the STRUCTURE of a value-proof model -- fill every
placeholder from your own product's real numbers before you quote it to a
prospect. Per the RACI rule "N06 never prices without market research (N01
dependency)" (`.claude/rules/raci-matrix.md`), the `tier_price_monthly`
input should come from a priced, market-researched tier model (see
[[subscription_tier_n06]] / [[p06_enum_pricing_tiers_n06]]), not be invented
here.

## Purpose

Quantifies the value a product delivers to customers by tier and persona. Used in sales conversations, pricing pages, and renewal negotiations. Strategic Greed principle: customers buy when value > price is undeniable.

### How to use

```text
You are N06 (Strategic-Greed commercial) building an ROI proof for one buyer.
This is a roi_calculator; its verb is PRODUCE -- it generates the value case.

- Bind the act-time slots (team_size, hourly_rate_usd, tier_price_monthly,
  builds_per_week) from the prospect's real numbers, never defaults.
- Run calculate_roi() to get hours_saved, dollar_saved, net_value, payback_days.
- Pick the matching Pre-Computed Scenario as the anchor, then adjust to the buyer.
- Read the buyer's ROI band and use the matching objection handler.
- Never quote ROI without the inputs visible -- a transparent model closes; a
  black-box number invites disbelief.
```

### Procedure

```text
1. Collect the four slot values from the prospect (team, rate, builds, tier price).
2. Compute manual_build_time and product_build_time for one unit of work.
3. Scale to monthly: builds_per_month = builds_per_week * 4.33.
4. Derive hours_saved_monthly, dollar_saved_monthly, net_value, roi_pct, payback_days.
5. Select the closest Pre-Computed Scenario as the credibility anchor.
6. Deliver via the Sales Conversation Script; gate the claim on payback_days < 30.
```

## Input Variables

```yaml
inputs:
  # Customer profile
  team_size: integer          # number of people who would use the product
  hourly_rate_usd: integer    # average hourly fully-loaded cost per person

  # Current state (before the product)
  builds_per_week: integer    # units of work produced manually
  hours_per_build: float      # avg hours to produce one unit manually
  revision_cycles: integer    # avg revision rounds per unit
  hours_per_revision: float   # avg hours per revision round

  # Product performance
  product_build_time_hours: float         # e.g. 0.05 (3 minutes) -- your real number
  product_revision_time_hours: float      # e.g. 0.02 (1 minute) -- your real number
  product_quality_improvement_pct: float  # e.g. 40 (fewer revision cycles) -- your real number
```

## Calculation Model

```python
def calculate_roi(inputs: dict, tier_price_monthly: int) -> dict:
    # Weekly time saved per build
    manual_build_time = (
        inputs["hours_per_build"] +
        (inputs["revision_cycles"] * inputs["hours_per_revision"])
    )
    product_build_time = (
        inputs["product_build_time_hours"] +
        (inputs["revision_cycles"] * (1 - inputs["product_quality_improvement_pct"] / 100)
         * inputs["product_revision_time_hours"])
    )
    hours_saved_per_build = manual_build_time - product_build_time

    # Monthly savings
    builds_per_month = inputs["builds_per_week"] * 4.33
    hours_saved_per_month = hours_saved_per_build * builds_per_month
    dollar_saved_per_month = hours_saved_per_month * inputs["hourly_rate_usd"]

    # ROI
    net_value = dollar_saved_per_month - tier_price_monthly
    roi_pct = (net_value / tier_price_monthly) * 100
    payback_days = (tier_price_monthly / dollar_saved_per_month) * 30

    return {
        "hours_saved_monthly": round(hours_saved_per_month, 1),
        "dollar_saved_monthly": round(dollar_saved_per_month, 0),
        "net_value_monthly": round(net_value, 0),
        "roi_pct": round(roi_pct, 0),
        "payback_days": round(payback_days, 0),
        "annual_savings": round(dollar_saved_per_month * 12, 0)
    }
```

## Illustrative Worked Example (replace every number)

Do not quote these numbers to a real prospect -- they exist only to show how
the formula flows from inputs to a sales-ready claim.

```
Inputs: team=1, rate=$75/hr, builds=10/week, hours_per_build=2.5, revisions=2, rev_hours=1
        product_build_time_hours=0.05, product_revision_time_hours=0.02, quality_improvement=40%
        tier_price_monthly={{TIER_PRICE_MONTHLY}}  (use your real tier price, not a guess)

Result (illustrative, at a hypothetical $99/mo tier price):
  Hours saved/month: ~92 hours
  Dollar saved/month: ~$6,900
  Product cost: $99/month
  Net value: ~$6,801/month
  Payback: same-day
```

The magnitude of the result scales with `hourly_rate_usd` and
`builds_per_week` -- a solo user, a small team, and a large department will
land in very different ROI bands even on the same tier price. Compute all
three off your own real inputs; do not reuse this example's numbers.

## Sales Conversation Script

```
"Let me show you the math on YOUR situation.

 [Input their numbers]

 So right now, your team spends [X] hours/month on [work type].
 At [$Y] fully loaded cost, that's [$Z] per month.

 With {{YOUR_PRODUCT}}, that drops to [X * product_build_time_hours] hours.
 You'd save [$savings] per month. {{YOUR_PRODUCT}} costs [$price].

 That's a [ROI%] return. Your payback period: [days].

 Even if we're only half right, you're still up [net_value/2].

 The question isn't whether {{YOUR_PRODUCT}} pays for itself -- it's how much
 faster you want to capture [annual_savings] in annual value."
```

## Objection Handlers by ROI Band

| ROI Band | Typical Objection | Response |
|----------|-------------------|---------|
| <500% | "Not sure if it's worth it" | Focus on non-quantified value: quality, consistency, brand voice |
| 500-2000% | "Seems high, is this realistic?" | Share the scenario most similar to their size. Offer a trial. |
| >2000% | "I need to show this to my manager" | Offer an ROI one-pager export. Offer a pilot on 1 use case. |

## Pricing Page Integration

The calculator embeds on the pricing page with default values pre-filled by detected company size (from IP lookup or signup form):
- Solo -> default: team=1, rate={{SOLO_RATE_DEFAULT}}, builds=10/week
- SMB -> default: team=5, rate={{SMB_RATE_DEFAULT}}, builds=25/week
- Enterprise -> default: team=20, rate={{ENT_RATE_DEFAULT}}, builds=100/week

## Related Artifacts
| Artifact | Relationship |
|----------|-------------|
| [[nucleus_def_n06]] | upstream |
| [[subscription_tier_n06]] | upstream (this calculator's `tier_price_monthly` input must come from a real tier model, not a guess) |
| [[p06_enum_pricing_tiers_n06]] | related |
