---
id: cohort_analysis_n06
kind: cohort_analysis
pillar: P07
nucleus: n06
title: "Cohort Analysis -- Revenue Cohort Framework by Channel, Plan, and Period"
version: 1.0.0
quality: null
tags:
  - "cohort"
  - "analysis"
  - "revenue"
  - "retention"
  - "commercial"
  - "channel"
  - "plan"
tldr: "Revenue cohort framework -- segments customers by acquisition month, channel, and plan to reveal true retention, NRR, and LTV that aggregate churn hides."
when_to_use: "Load when reasoning about retention/LTV by cohort or diagnosing which vintage/channel underperforms. Consult for 'is this cohort healthy and which acquisition source delivers the best LTV'."
slots:
  cohort_dimension: "<acquisition_channel | starting_plan | icp_bucket | company_size | industry>"
  cohort_month: "<YYYY-MM -- the vintage being analyzed>"
  retention_window_months: "<INTEGER -- horizon to track, default 12>"
density_score: 1.0
related:
  - nucleus_def_n06
  - subscription_tier_n06
  - referral_program_n06
updated: "2026-07-20"
---

# Cohort Analysis: Revenue Cohort Framework

## Purpose

Segments customer behavior by acquisition cohort to understand true retention, expansion, and LTV by channel, plan, and signup month. Cohort analysis reveals what aggregate churn rates hide: which customers are thriving, which are churning, and why.

### How to use

```text
You are N06 (Strategic-Greed) reasoning about retention beyond a single churn number.

- Pick a cohort_dimension and bucket customers by acquisition month (the primary cohort).
- Build the Retention and Revenue (NRR) cohort tables; compare to the benchmark curve.
- Run the Cohort Health Signals to flag activation, expansion, and unit-economics risk.
- Test the Key Hypotheses; act only on cohorts with enough age and size to be real.
```

### Procedure

```text
1. Group customers by month of first paid subscription; track 12 months.
2. Run the SQL queries to compute retention, NRR, and LTV per cohort_dimension.
3. Plot retention vs the benchmark curve (M1 >80%, M3 >70%, M6 >60%, M12 >50%).
4. Apply flag_cohort_health() to surface ACTIVATION/EXPANSION/UNIT_ECONOMICS flags.
5. For each confirmed hypothesis, take the stated action and record it as a learning.
```

## Cohort Dimensions

### Primary Cohort: Acquisition Month

```
Group customers by: month of first paid subscription
Track for: 12 months post-acquisition

Why: reveals true retention curve per vintage.
Insight: if January cohort retains better than August cohort,
the product change or acquisition channel shift between those months is the cause.
```

### Segmentation Dimensions

| Dimension | Values | Insight |
|-----------|--------|---------|
| Acquisition channel | organic, paid, referral, outbound, event | Which channels deliver highest-LTV customers |
| Starting plan | starter, pro, enterprise | Which tier has best retention and expansion |
| ICP score bucket | 0-33 (low), 34-66 (med), 67-100 (high) | Confirms ICP qualification value |
| Company size | 1, 2-10, 11-50, 51-200, 200+ | Best-fit company size |
| Industry | your own vertical list | Vertical with best unit economics |
| Trial vs no trial | trial | annual | Does trial experience predict retention |

## Cohort Matrix Structure

### Retention Cohort Table

```
         Month 0  Month 1  Month 2  Month 3  Month 6  Month 12
Jan 2026:  100%     85%      78%      72%      65%      58%
Feb 2026:  100%     88%      82%      77%      [live]   [future]
Mar 2026:  100%     91%      [live]   [future]
Apr 2026:  100%     [live]
```

Target retention curve (benchmark SaaS):
- Month 1: >80%
- Month 3: >70%
- Month 6: >60%
- Month 12: >50%

### Revenue Cohort Table (NRR by vintage)

```
         Month 0   Month 3   Month 6   Month 12
Jan 2026:  100%     105%      112%      118%   <- expansion > churn (healthy)
Feb 2026:  100%     98%       95%       [live] <- contraction > expansion (warning)
```

NRR > 100% at Month 12 means the cohort is growing net revenue despite some churn.
Target: NRR > 110% at Month 12 for each cohort.

## Cohort Analysis Queries

### By Acquisition Channel

```sql
SELECT
    acquisition_channel,
    DATE_TRUNC('month', created_at) AS cohort_month,
    COUNT(*) AS cohort_size,
    AVG(lifetime_revenue_cents) / 100 AS avg_ltv,
    AVG(DATEDIFF(day, created_at, churned_at)) AS avg_lifespan_days,
    SUM(CASE WHEN status = 'active' THEN 1 ELSE 0 END) * 100.0 / COUNT(*) AS current_retention_pct
FROM customers
GROUP BY acquisition_channel, cohort_month
ORDER BY cohort_month DESC, avg_ltv DESC;
```

### By Starting Plan

```sql
SELECT
    starting_plan_tier,
    COUNT(*) AS cohort_size,
    AVG(months_to_upgrade) AS avg_months_to_upgrade,
    SUM(CASE WHEN ever_upgraded THEN 1 ELSE 0 END) * 100.0 / COUNT(*) AS upgrade_rate_pct,
    AVG(lifetime_revenue_cents) / 100 AS avg_ltv
FROM customer_cohorts
GROUP BY starting_plan_tier;
```

### Referral vs Organic Comparison

```sql
SELECT
    CASE WHEN referral_code_used IS NOT NULL THEN 'referral' ELSE 'organic' END AS source_type,
    AVG(monthly_churn_rate) AS avg_churn_rate,
    AVG(time_to_first_value_minutes) AS avg_ttfv,
    AVG(lifetime_revenue_cents) / 100 AS avg_ltv,
    AVG(health_score) AS avg_health_score
FROM customers
GROUP BY source_type;
```

## Key Hypotheses to Test

| Hypothesis | Measurement | Action if True |
|-----------|-------------|---------------|
| Referral customers retain better | 12m retention by source | Increase referral spend; raise K-factor target |
| Annual plan customers churn less | Survival curves by billing_cycle | More aggressively push annual at checkout |
| ICP score predicts 12m LTV | Correlation: icp_score vs 12m revenue | Tighten ICP qualification; exclude low-score leads |
| Faster activation -> better retention | Corr: time_to_first_value vs 6m retention | Prioritize onboarding optimization |
| Multi-feature users don't churn | Churn rate by feature_breadth | Invest in feature onboarding per persona |

## Reporting Cadence

```
Monthly: full cohort matrix refresh + channel comparison
Quarterly: deep dive on oldest cohorts (6m, 12m milestone)
  - Which cohorts are outperforming?
  - What changed in acquisition or product for those cohorts?
  - Where is the bottom of the retention curve?
Ad hoc: after major pricing change, new feature launch, or acquisition channel change
```

## Cohort Health Signals

```python
def flag_cohort_health(cohort: dict) -> list[str]:
    flags = []

    if cohort["month_1_retention"] < 0.75:
        flags.append("ACTIVATION_PROBLEM: early churn suggests onboarding failure")

    if cohort["month_3_nrr"] < 100:
        flags.append("EXPANSION_GAP: expansion < churn in first 90 days")

    if cohort["avg_ltv"] < cohort["avg_cac"] * 3:
        flags.append("UNIT_ECONOMICS_RISK: LTV:CAC below 3x for this cohort")

    if cohort["referral_rate"] < 0.10:
        flags.append("LOW_VIRALITY: cohort not generating referrals, check NPS")

    return flags
```

## Related Artifacts
| Artifact | Relationship |
|----------|-------------|
| [[nucleus_def_n06]] | upstream |
| [[subscription_tier_n06]] | related (starting_plan cohort dimension references this tier model) |
| [[referral_program_n06]] | related (referral vs organic comparison query feeds from this program) |
