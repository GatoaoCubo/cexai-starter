---
id: kc_cohort_analysis
kind: knowledge_card
8f: F3_inject
title: Cohort Analysis for Retention and LTV Modeling
version: 1.0.0
quality: null
pillar: P01
tldr: "Statistical technique grouping users by shared traits to measure retention curves and lifetime value"
when_to_use: "When analyzing user retention, churn patterns, or LTV trajectories across acquisition cohorts"
keywords: [cohort analysis, retention rate, lifetime value (ltv), churn rate, cohort segmentation, time-to-event analysis, decay rates, cohort heatmaps]
density_score: 1.0
related:
  - cohort-analysis-builder
  - bld_instruction_cohort_analysis
  - p10_mem_cohort_analysis_builder
  - bld_knowledge_card_cohort_analysis
  - n00_cohort_analysis_manifest
---

## How to use

You are a cohort-analysis-builder at **F3 INJECT**. Use this card to design a
retention/LTV study; pick the cohort type that matches the question.

1. Choose a cohort axis from **Analysis Types** (time, behavior, demographic, funnel).
2. Compute the **Key Metrics** (churn, retention curve, LTV per cohort).
3. Hold time intervals constant across cohorts so comparison is valid.
4. Visualize as a retention heatmap; segment by an actionable dimension.

**Definition**: Cohort analysis is a statistical technique that groups users by shared characteristics (e.g., acquisition date, behavior patterns) to measure retention rates and lifetime value (LTV) over time.

**Purpose**:
- Track user retention across time intervals
- Model lifetime value trajectories
- Identify at-risk cohorts
- Optimize marketing strategies

**Key Metrics**:
- Churn rate (percentage of users lost per period)
- Cohort retention curve (retention rate over time)
- Average LTV per cohort
- Customer lifetime value (CLV) by acquisition channel

**Analysis Types**:
1. Time-based cohorts (e.g., monthly cohorts)
2. Behavior-based cohorts (e.g., first purchase behavior)
3. Demographic cohorts (e.g., age groups)
4. Funnel-stage cohorts (e.g., conversion paths)

**Tools**:
- SQL/Python for cohort segmentation
- Retention tables with time-to-event analysis
- LTV models incorporating cohort-specific decay rates
- Visualization tools for cohort heatmaps

**Example**:
A 30-day cohort might show:
- 65% retention at 30 days
- 40% retention at 90 days
- Average LTV of $120 for this cohort
- 25% higher churn in users who didn't complete onboarding

**Best Practices**:
- Use consistent time intervals for comparison
- Include both absolute numbers and percentages
- Segment by relevant dimensions (e.g., product usage)
- Combine with customer journey mapping

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[cohort-analysis-builder]] | downstream | 0.54 |
| [[bld_instruction_cohort_analysis]] | downstream | 0.52 |
| [[p10_mem_cohort_analysis_builder]] | downstream | 0.50 |
| [[bld_knowledge_card_cohort_analysis]] | sibling | 0.49 |
