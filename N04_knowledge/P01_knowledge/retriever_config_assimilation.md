---
id: p01_retr_assimilation_n04
kind: retriever_config
8f: F3_inject
pillar: P01
version: "1.0.0"
created: "2026-05-29"
updated: "2026-05-29"
author: n04_knowledge
title: "Assimilation Retriever Config"
search_type: hybrid
top_k: 5
score_threshold: 0.75
quality: null
tags: [retriever, config, n04, assimilation, rag, offline, hybrid, P01]
tldr: "Retrieval config for assimilated vertical brains: offline hybrid search (TF-IDF cosine + keyword) over a scoped knowledge_index, top_k 5 at a 0.75 threshold. Read by cex_distill_orchestrator.py and the scoped brain index."
keywords: [hybrid, top_k, score_threshold, tfidf, offline retrieval, scoped index, fallback chain, assimilation]
density_score: null
related:
  - retriever-builder
---

# Assimilation Retriever Config

## 1. Purpose
Controls how a query is matched against a freshly-assimilated vertical brain.
This config sits between a user query and the scoped `knowledge_index` emitted by
`cex_distill_orchestrator.py`. It is **offline-first**: no provider call is
required to retrieve from a distilled brain.

## 2. Configuration
| Parameter | Value | Rationale |
|-----------|-------|-----------|
| `search_type` | `hybrid` | blends TF-IDF cosine with keyword overlap; robust on small per-brain corpora |
| `top_k` | `5` | enough context without flooding the window for a single vertical |
| `score_threshold` | `0.75` | drops low-relevance chunks; relaxed by the fallback chain when recall is empty |

## 3. Ranking Pipeline (offline)
```
query -> tokenize -> tfidf vector (brain vocab) -> cosine over scoped index
      -> keyword overlap boost -> threshold filter -> top_k
```
The brain's vocabulary is the one built at distill time (`cex_retriever.build_tfidf`),
so retrieval needs no external embedding service.

## 4. Fallback Chain (degrade-never)
When primary retrieval returns nothing above `score_threshold`:
1. Lower `score_threshold` by 0.1 (down to 0.5 floor).
2. Switch `semantic` -> `hybrid` if not already hybrid.
3. Drop metadata/section filters.
4. Return a "no grounded context" disclaimer rather than hallucinate.

## 5. Quality Gate
- [ ] `top_k` <= 20 (window budget)
- [ ] `score_threshold` >= 0.5 after any relaxation
- [ ] fallback chain has >= 2 levels
- [ ] retrieval works with no API key (offline proof)

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[kc_retriever]] | related | 0.32 |
| [[retriever-builder]] | related | 0.30 |
| p10_bi_bm25_knowledge | related | 0.28 |
