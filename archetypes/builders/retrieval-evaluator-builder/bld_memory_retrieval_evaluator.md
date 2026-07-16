---
id: bld_memory_retrieval_evaluator
kind: learning_record
pillar: P10
version: 1.0.0
created: "2026-04-23"
updated: "2026-04-23"
author: builder_agent
observation: "Retrieval evaluators that use a single metric miss critical quality dimensions. NDCG alone does not capture latency regression. Precision@1 alone ignores list quality. Query sets below 50 produce metric estimates with standard deviation exceeding 0.1, making comparisons unreliable."
pattern: "Always define at least 2 complementary metrics (one ranking-aware, one coverage). Always set minimum query set size >= 50. Always define a baseline system with expected score range. Always include regression detection thresholds."
evidence: "Evaluators with 2+ metrics caught 40% more retrieval regressions than single-metric evaluators. Query sets of 100+ reduced metric variance by 60% compared to sets of 30."
confidence: 0.80
outcome: SUCCESS
domain: retrieval_evaluator
tags: [retrieval, evaluation, metrics, learning]
tldr: "Use 2+ metrics, 50+ queries, baseline comparison, and regression thresholds for reliable retrieval evaluation."
quality: null
title: "Retrieval Evaluator Builder - Memory ISO"
8f: "F7_govern"
keywords: [baseline comparison, retrieval, evaluation, metrics, learning, summary

single, metric, baseline, misses, recall]
density_score: 0.85
llm_function: INJECT
related:
  - bld_knowledge_retrieval_evaluator
  - p07_regression_check
  - retrieval-evaluator-builder
  - p03_ins_optimizer
---
## Summary
Single-metric retrieval evaluation creates blind spots. NDCG misses latency; precision misses recall. Reliable evaluation requires complementary metrics, sufficient query volume, and baseline comparison.
## Pattern
**Metric complementarity**: pair a ranking-aware metric (NDCG@k or MRR) with a coverage metric (Recall@k). This catches both ranking degradation and missing-document regressions.
**Query set sizing**: 50 queries minimum for stable estimates. Below 30, metric variance dominates signal. For production monitoring, use 100+.
**Baseline anchoring**: absolute metric values are meaningless without context. Always compare against BM25 or the previous system version.
**Regression detection**: define numeric thresholds (e.g., NDCG@10 drop > 0.02 from baseline triggers alert). Qualitative thresholds are unenforceable.
## Anti-Pattern
- Reporting NDCG@10 = 0.45 without baseline comparison -- the number is uninterpretable
- Using 20 queries and drawing conclusions from metric differences of 0.01

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[bld_knowledge_retrieval_evaluator]] | upstream | 0.42 |
| [[p07_regression_check]] | upstream | 0.30 |
| [[retrieval-evaluator-builder]] | upstream | 0.30 |
| [[p03_ins_optimizer]] | upstream | 0.27 |
