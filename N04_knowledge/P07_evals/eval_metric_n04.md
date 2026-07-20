---
id: p07_em_n04_knowledge
kind: eval_metric
8f: F7_govern
pillar: P07
nucleus: n04
title: "Eval Metric -- N04 Retrieval Quality Metrics"
version: "1.0.0"
quality: null
tags: [eval_metric, n04, MRR, NDCG, precision, recall, P07, retrieval]
domain: knowledge management
status: active
created: "2026-07-20"
updated: "2026-07-20"
author: n04_knowledge
tldr: "Formal metric definitions for retrieval quality evaluation: MRR@K, NDCG@K, Precision@K, Recall@K, and a composite Knowledge Quality Score (KQS). Includes formulas, interpretation, and alert thresholds."
keywords: [knowledge management, eval metric, retrieval quality metrics, retrieval quality evaluation, includes formulas, and alert thresholds, eval_metric, ndcg, precision]
density_score: null
related:
  - bld_knowledge_retrieval_evaluator
  - p01_kc_information_retrieval_fundamentals
  - bld_schema_retrieval_evaluator
  - p04_retr_n04_knowledge
slots:
  candidate: "<the artifact under evaluation>"
  threshold: "<the pass cutoff>"
---

# Eval Metric: N04 Retrieval Quality Metrics

## Metric Taxonomy

| Metric | Type | Measures | Higher is Better |
|--------|------|---------|-----------------|
| MRR@K | Ranking | First relevant document rank | YES |
| NDCG@K | Ranking | Graded relevance, position-discounted | YES |
| Precision@K | Relevance | Fraction of top-K that are relevant | YES |
| Recall@K | Relevance | Fraction of relevant docs in top-K | YES |
| KQS | Composite | Overall knowledge retrieval quality | YES |

---

## Metric Definitions

### MRR@K (Mean Reciprocal Rank)

**Formula**:
```
MRR@K = (1/|Q|) * sum_{q=1}^{|Q|} (1 / rank_q)

where rank_q = rank of first relevant document for query q
      if no relevant document in top-K: 1/rank_q = 0
```

**Interpretation**:
- 1.0 = perfect (relevant document always ranked #1)
- 0.5 = relevant document typically at rank 2
- < 0.25 = poor (relevant result not in top-4 on average)

**Suggested target**: >= 0.83 | **Alert**: < 0.75 | **Revert**: < 0.70

---

### NDCG@K (Normalized Discounted Cumulative Gain)

**Formula**:
```
DCG@K = sum_{i=1}^{K} (rel_i / log2(i + 1))
NDCG@K = DCG@K / IDCG@K

where rel_i = relevance score at rank i (binary: 0 or 1; or graded: 0-3)
      IDCG = ideal DCG (perfect ranking)
```

**Graded relevance**: 3 = exact answer source, 2 = closely related, 1 =
tangentially relevant, 0 = not relevant.

**Suggested target**: >= 0.80 | **Alert**: < 0.72

---

### Precision@K

```
Precision@K = (# relevant documents in top-K) / K
```

**Suggested target**: >= 0.76 | **Alert**: < 0.68

---

### Recall@K

```
Recall@K = (# relevant documents in top-K) / (# total relevant documents)
```

**Note**: when total relevant documents = 1, Recall@K = Hit Rate@K.

**Suggested target**: >= 0.76 | **Alert**: < 0.68

---

### Knowledge Quality Score (KQS) -- Composite

```
KQS = 0.40 * MRR@10
    + 0.30 * NDCG@10
    + 0.15 * Precision@5
    + 0.10 * Recall@10
    + 0.05 * (1 - latency_penalty)

latency_penalty = min(1.0, max(0.0, (p95_ms - 500) / 1000))
```

**Interpretation**:
- >= 0.90 = excellent knowledge retrieval
- 0.80-0.89 = good, production-ready
- 0.70-0.79 = acceptable, improvement queued
- < 0.70 = poor, self-improvement loop triggered

---

## Metric Calculation

```python
def calculate_mrr(queries: list[dict], retriever) -> float:
    reciprocal_ranks = []
    for q in queries:
        results = retriever.query(q["query"], top_k=10)
        rank = next(
            (i+1 for i, r in enumerate(results)
             if r["source"] in q["ground_truth_sources"]),
            None
        )
        reciprocal_ranks.append(1/rank if rank else 0.0)
    return sum(reciprocal_ranks) / len(reciprocal_ranks)

def calculate_ndcg_at_k(queries: list[dict], retriever, k: int = 10) -> float:
    ndcg_scores = []
    for q in queries:
        results = retriever.query(q["query"], top_k=k)
        dcg = sum(
            relevance(r["source"], q) / log2(i+2)
            for i, r in enumerate(results[:k])
        )
        idcg = sum(1 / log2(i+2) for i in range(min(len(q["ground_truth_sources"]), k)))
        ndcg_scores.append(dcg / idcg if idcg > 0 else 0.0)
    return sum(ndcg_scores) / len(ndcg_scores)
```

No eval-running CLI flag ships with `_tools/cex_retriever.py` in this starter
today (verify with `--help` -- the real flags are `--build`, `--query`,
`--kind`, `--pillar`, `--top-k`, `--min-score`, `--stats`, `--examples`,
`--intent`, `--output`, `--verbose`). Score a retriever by calling the
functions above directly against an `eval_dataset` of `{query,
ground_truth_sources}` pairs, not by assuming a benchmark flag exists.

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[bld_knowledge_retrieval_evaluator]] | upstream | 0.44 |
| [[p01_kc_information_retrieval_fundamentals]] | upstream | 0.39 |
| [[bld_schema_retrieval_evaluator]] | upstream | 0.25 |
| [[p04_retr_n04_knowledge]] | downstream | 0.30 |
