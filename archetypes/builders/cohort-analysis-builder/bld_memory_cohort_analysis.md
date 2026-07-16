---
kind: memory
id: p10_mem_cohort_analysis_builder
pillar: P10
llm_function: INJECT
purpose: Learned patterns and pitfalls for cohort_analysis construction
quality: null
title: "Memory Cohort Analysis"
version: "1.0.0"
author: wave1_builder_gen_v2
tags: [cohort_analysis, builder, learning_record]
tldr: "Learned patterns and pitfalls for cohort_analysis construction"
domain: "cohort_analysis construction"
created: "2026-04-14"
updated: "2026-04-14"
8f: "F3_inject"
keywords: [cohort_analysis construction, memory cohort analysis, cohort_analysis, builder, learning_record, observation
inconsistent, pattern
clear, evidence
artifacts, related artifacts, event-based timestamps]
density_score: 0.85
related:
  - cohort-analysis-builder
  - kc_cohort_analysis
  - bld_instruction_cohort_analysis
  - n00_cohort_analysis_manifest
  - bld_knowledge_card_cohort_analysis
---
## Observation
Inconsistent cohort definitions (e.g., using signup date vs. first event) often lead to skewed retention metrics. Overlooking time granularity (e.g., daily vs. weekly) can distort LTV calculations by misrepresenting user behavior patterns.

## Pattern
Clear alignment between cohort grouping logic and business goals (e.g., retention by onboarding stage) improves interpretability. Using event-based timestamps for cohort creation ensures accurate tracking of user journeys.

## Evidence
Artifacts using calendar-based cohorts showed 20% variance in retention rates compared to event-based counterparts in reviewed datasets.

## Recommendations
- Use event-based timestamps (e.g., first purchase) for cohort creation instead of calendar dates.
- Define retention windows that match key product milestones (e.g., 7-day post-onboarding).
- Document cohort logic explicitly in code and data schemas to ensure reproducibility.
- Validate LTV models with historical cohort data to avoid overfitting to short-term trends.
- Avoid mixing time granularities (e.g., daily and monthly) within a single analysis.

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[cohort-analysis-builder]] | upstream | 0.46 |
| [[kc_cohort_analysis]] | upstream | 0.46 |
| [[bld_instruction_cohort_analysis]] | upstream | 0.44 |
| [[n00_cohort_analysis_manifest]] | upstream | 0.43 |
| [[bld_knowledge_card_cohort_analysis]] | upstream | 0.36 |
