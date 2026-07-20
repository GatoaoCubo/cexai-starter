---
id: p07_sr_commercial_n06
kind: scoring_rubric
pillar: P07
nucleus: n06
title: "N06 Scoring Rubric -- Offer Evaluation (Brand + Monetization)"
version: 1.0.0
quality: null
max_score: 10.0
min_pass: 8.0
golden: 9.0
tags: [scoring_rubric, commercial, offer_evaluation, brand, monetization, dual]
tldr: "Dual scoring for any commercial offer: BRAND (archetype 0-3, voice 0-2, positioning 0-2, visual 0-2, narrative 0-1) + MONETIZATION (pricing 0-3, funnel 0-2, conversion 0-2, revenue 0-2, market 0-1). Average to 10. Min 8.0, golden 9.0."
axioms:
  - "NEVER self-score -- peer nucleus reviews only. quality: null until reviewed."
  - "Min 8.0 to publish, 9.0 is golden. Below 8.0 = rejected, re-work required."
density_score: 0.94
related:
  - nucleus_def_n06
  - subscription_tier_n06
  - p05_pp_pricing_page_n06
updated: "2026-07-20"
---

# N06 Scoring Rubric -- Offer Evaluation

## Scoring Model

N06 produces two categories of artifact. Score is averaged:
`final_score = (brand_score + monetization_score) / 2`

For pure brand artifacts, use the Brand rubric only. For pure monetization
artifacts (e.g. a subscription_tier model), use the Monetization rubric
only. For mixed artifacts (e.g. a branded pricing page), average both.

## BRAND Rubric (10 points)

| Dimension | Points | Criteria |
|-----------|--------|----------|
| **Archetype** | 0-3 | 0=none, 1=named but generic, 2=aligned with tone+visual, 3=deeply integrated with shadow+traits |
| **Voice** | 0-2 | 0=no voice calibration, 1=tone described, 2=full 5D scores + do/don't + calibration phrases |
| **Positioning** | 0-2 | 0=no UVP, 1=generic positioning, 2=specific UVP + differentiator + competitive matrix |
| **Visual** | 0-2 | 0=no colors, 1=palette defined, 2=full palette + fonts + contrast + dark mode |
| **Narrative** | 0-1 | 0=no story, 1=origin + mission + vision + transformation arc present |

### Brand Score Guide

| Score | Quality |
|-------|---------|
| 9-10 | Exceptional -- publication-ready, consistency >= 0.95 |
| 8-8.9 | Strong -- clear archetype alignment, consistency >= 0.85 |
| 7-7.9 | Adequate -- core identity present but gaps in voice or visual |
| 6-6.9 | Weak -- archetype named but not integrated |
| < 6 | Failing -- fundamental identity gaps, re-run brand discovery |

## MONETIZATION Rubric (10 points)

| Dimension | Points | Criteria |
|-----------|--------|----------|
| **Pricing** | 0-3 | 0=no price, 1=flat price only, 2=tiered with rationale, 3=tiered + anchor + psychology + projections |
| **Funnel** | 0-2 | 0=no funnel, 1=basic TOFU/MOFU/BOFU, 2=full sequence with copy + conversion benchmarks |
| **Conversion** | 0-2 | 0=no metrics, 1=benchmarks referenced, 2=stage-specific rates + optimization recommendations |
| **Revenue** | 0-2 | 0=no model, 1=basic projection, 2=MRR/LTV scenarios with sensitivity analysis |
| **Market** | 0-1 | 0=generic, 1=market-specific (currency, payment rail, platform named) |

### Monetization Score Guide

| Score | Quality |
|-------|---------|
| 9-10 | Exceptional -- implementable pricing + funnel + revenue model with projections |
| 8-8.9 | Strong -- tiered pricing, funnel stages defined, conversion benchmarks present |
| 7-7.9 | Adequate -- pricing exists but generic, funnel incomplete |
| 6-6.9 | Weak -- single price, no funnel, no revenue model |
| < 6 | Failing -- no commercial viability analysis |

## Combined Scoring

| Artifact Type | Rubric Used |
|---------------|-------------|
| Brand book / brand_config.yaml / voice guide | Brand only |
| Pricing page | Average(Brand + Monetization) |
| Funnel sequence | Average(Brand + Monetization) |
| subscription_tier / revenue model | Monetization only |

## Thresholds

| Level | Score | Action |
|-------|-------|--------|
| Gold | 9.0+ | Publish, archive as exemplar |
| Pass | 8.0-8.9 | Publish, note improvements |
| Review | 7.0-7.9 | Revise weak dimensions |
| Fail | < 7.0 | Reject, re-build |

## Boundary

Scoring rubric with an evaluation framework. NOT a benchmark (does not
measure runtime performance) and NOT a quality_gate (P11 -- does not
hard-block a pipeline). This rubric provides dimensional scoring criteria
for peer review of N06 commercial artifacts.

## Related Artifacts
| Artifact | Relationship |
|----------|-------------|
| [[nucleus_def_n06]] | upstream |
| [[subscription_tier_n06]] | downstream (this rubric scores that kind's Monetization dimension) |
| [[p05_pp_pricing_page_n06]] | downstream (scored on the Average(Brand+Monetization) row) |
