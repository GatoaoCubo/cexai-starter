---
id: p03_pt_pricing_strategy_n06
kind: prompt_template
pillar: P03
nucleus: n06
title: "Pricing Strategy Prompt Template"
version: 1.0.0
quality: null
tags: [prompt_template, commercial, pricing, revenue-model, n06]
tldr: "Parametric prompt for a 3-tier pricing strategy -- value-based anchoring, revenue scenarios, and sourced conversion benchmarks. Mustache {{variables}}, no hardcoded platform or price."
variables:
  - name: product_name
    type: string
    required: true
    default: null
    description: Name of the product, course, or subscription tier being priced.
  - name: target_audience
    type: string
    required: true
    default: null
    description: Specific audience segment.
  - name: transformation
    type: string
    required: true
    default: null
    description: Measurable outcome the buyer achieves.
  - name: price_range
    type: string
    required: false
    default: null
    description: Optional price anchor or range to inform tier design.
  - name: platform
    type: string
    required: false
    default: null
    description: Deployment/checkout platform -- caller names their own, no default is assumed.
variable_syntax: mustache
composable: true
domain: commercial-monetization
density_score: 0.92
related:
  - kc_commercial_vocabulary
  - p01_kc_ai_saas_monetization
  - p01_kc_few_shot_examples_pricing_scenarios
updated: "2026-07-20"
---

# Pricing Strategy Prompt Template

One reusable N06 template for pricing a digital product, course, or
subscription tier. Value-based, not cost-plus -- and every rate below is a
sourced anchor, never an invented one (Strategic Greed still needs receipts).

## Template: Pricing Strategy

**Use when**: you need to price a product and want a defensible 3-tier structure with a revenue projection attached.

```
Design a 3-tier pricing strategy for {{product_name}}.

TARGET AUDIENCE: {{target_audience}}
TRANSFORMATION: {{transformation}}
PLATFORM: {{platform}}
{{#price_range}}PRICE ANCHOR: {{price_range}}{{/price_range}}

Deliverables:
1. Transformation Value Assessment -- quantify what the outcome is worth to the buyer
2. 3-Tier Pricing Table (Basic / Pro / VIP) with:
   - Price per tier
   - Inclusions per tier
   - Psychological rationale for each price point
3. Revenue Model -- 3 scenarios (conservative / realistic / optimistic):
   - Units x Price x Conversion Rate = Revenue
4. Recommended launch price with written rationale (2-3 sentences)
5. Payment plan option (installments) if applicable

Apply value-based pricing. Anchor to transformation, not production cost.
```

> **External anchor**: a 1% price increase lifts operating profit ~8-11% on average (vs. 3.3% for a 1% volume gain) -- McKinsey, "The power of pricing" (https://www.mckinsey.com/capabilities/growth-marketing-and-sales/our-insights/the-power-of-pricing).

## Conversion Benchmark Defaults (anchors, not guesses)

When the LLM fills a `[X%]` placeholder in the revenue model, anchor against
sourced defaults instead of inventing a rate:

| Funnel stage | Conservative | Realistic | Aggressive | Source |
|--------------|-------------:|----------:|-----------:|--------|
| Cold ad CTR | 0.5% | 1.5% | 3.0% | Meta/FB Ads avg CTR 1.7-2.6% -- WordStream 2025 Benchmarks |
| Landing page opt-in | 8% | 18% | 30% | Lead-magnet-specific aggregate (narrower than all-pages medians) |
| Email open rate | 22% | 35% | 50% | Mailchimp overall avg ~35.6% open |
| Email CTR | 1.5% | 3.5% | 8% | Mailchimp overall avg ~2.6% click |
| Sales page conversion | 1% | 3% | 6% | Internal heuristic -- not independently source-verified |
| Free -> paid SaaS | 2% | 5% | 10% | Freemium typical ~7% (OpenView / ChartMogul) |
| Trial -> paid SaaS | 15% | 30% | 50% | Blended trial range ~14-30% (ChartMogul) |

Where no independently verifiable public source exists, that gap is flagged
rather than a citation invented -- anti-fabrication discipline applies to
prompt templates too, not just to finished artifacts.

## Revenue Model Formula

```
UNIT ECONOMICS (per sale):
  AOV = Base + (Bump x take%) + (Upsell1 x take%) + (Upsell2 x take%)

REVENUE SCENARIOS:
  | Scenario     | Sales | AOV   | Revenue |
  |--------------|-------|-------|---------|
  | Conservative | [X]   | [AOV] | [{{CURRENCY}}] |
  | Realistic    | [X]   | [AOV] | [{{CURRENCY}}] |
  | Optimistic   | [X]   | [AOV] | [{{CURRENCY}}] |

LTV PROJECTION:
  LTV = AOV x Purchase Frequency x Customer Lifespan
  Target: LTV >= 3x AOV

CAC CEILING:
  Max acceptable CAC = 30% of AOV
```

## Default LTV/CAC Targets

| Metric | Floor | Healthy | Strong | Source |
|--------|------:|--------:|-------:|--------|
| LTV/CAC ratio | 1:1 | 3:1 | 5:1+ | David Skok, SaaS Metrics 2.0 -- a minimum-viability guideline, not a "healthy" target |
| Gross margin | 30% | 70% | 80%+ | General SaaS aggregator range |
| Net Revenue Retention | 80% | 100% | 110%+ | Public best-in-class ceiling runs closer to 120-125% |

## Composability

Chain with a course-outline or funnel-build prompt: outline -> this pricing
template -> revenue model -> funnel copy. Run in sequence, or dispatch to N06
via grid for parallel drafts on independent tiers.

## Related Artifacts
| Artifact | Relationship |
|----------|-------------|
| [[kc_commercial_vocabulary]] | upstream |
| [[p01_kc_ai_saas_monetization]] | upstream |
| [[p01_kc_few_shot_examples_pricing_scenarios]] | related |
