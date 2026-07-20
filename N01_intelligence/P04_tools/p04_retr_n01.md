---
id: p04_retr_n01
kind: retriever
pillar: P04
nucleus: n01
title: "N01 Intelligence Corpus Retriever"
version: 1.0.0
created: 2026-07-20
author: n01_intelligence
domain: research-intelligence
quality: null
tags: [retriever, rag, semantic_search, n01, knowledge_retrieval, corpus]
tldr: "Retriever for the N01 knowledge corpus: TF-IDF keyword search + cosine similarity is what actually runs (_tools/cex_retriever.py, pure stdlib, repo-wide). No reranking, no dense-embedding layer, no multi-signal fusion implemented yet -- documented honestly below rather than aspirationally."
keywords: [tf_idf, cosine_similarity, knowledge_card, compiled artifacts, prompt cache, session outputs]
density_score: 0.90
updated: "2026-07-20"
related:
  - p04_cli_research_pipeline_n01
  - memory_architecture_n01
  - reasoning_strategy_n01
  - p06_is_n01
  - nucleus_def_n01
---

<!-- 8F: F1 constrain=P04/retriever F4 reason=N01 Analytical Envy: before generating new research, retrieve what N01 already knows -- avoid redundancy, find contradictions F8 collaborate=N01_intelligence/P04_tools/p04_retr_n01.md -->

## Purpose

Analytical Envy drives N01 to ALWAYS compare new findings against existing knowledge.
Before any synthesis, N01 must query its own corpus to:
1. Avoid duplicating research already done
2. Identify contradictions (new data vs. old data = the interesting signal)
3. Build on existing intelligence (compound knowledge, not restart)

## Retrieval Architecture

The table below describes what the backing tool actually runs today, kept
honest rather than aspirational -- a retriever that claims capabilities it
does not have is worse than no retriever at all.

### What runs today

| Component | Technology | Role |
|-----------|-----------|------|
| Index + ranking | TF-IDF, pure Python stdlib (`_tools/cex_retriever.py`) | term-frequency relevance across the whole repo's `.md` artifacts |
| Similarity | Cosine similarity between the query vector and each doc vector (same file) | ranks candidates for a query |
| Store | Local JSON index (`.cex/retriever_index.json`) | no external vector DB, no network call |
| Reranking after retrieval | none implemented | -- |
| Dense / embedding-based retrieval | none implemented | -- |

### Ecosystem options (NOT implemented -- listed for context only)

| Concept | What it would add over what runs today | Status |
|---------|------------------------------------------|--------|
| Keyword-ranking algorithms that add length-normalization and term-saturation tuning on top of raw TF-IDF | better precision on long/short documents | not implemented |
| A learned second-pass model that re-scores a shortlist using the full query+doc pair together | higher precision in the top few results | not implemented -- no reranking step exists |
| A local or hosted embedding model for semantic (meaning-based, not just keyword) retrieval | catches paraphrase/synonym matches TF-IDF misses | not implemented -- this repo's retrieval is keyword-only today |
| An algorithm for merging two independently-ranked lists (e.g. a keyword pass and a semantic pass) into one ranking | would let a keyword layer and a future semantic layer agree on a single order | not applicable yet -- only one layer exists |
| A managed / cloud-hosted vector database service | horizontal scale past local-file limits, managed ops | not used -- N01's corpus (thousands of local `.md` files) fits in a local index at zero infra cost |

## Query Protocol

```
find_similar(query: str, kind: str = None, pillar: str = None,
             top_k: int = 5, min_score: float = 0.05) -> list[dict]:
  1. query_tokens = tokenize(query)                       # lowercase, stopword-filtered
  2. query_vec = tfidf_vector(query_tokens, index.vocab)   # reuses the built index's IDF
  3. for each indexed doc (optionally filtered by kind/pillar):
       score = cosine_similarity(query_vec, doc_vec)
  4. keep docs where score >= min_score, sort descending, return top_k
```

Source: `_tools/cex_retriever.py::find_similar()`. The defaults above
(`top_k=5`, `min_score=0.05`) are the function's real defaults, not aspirational.

## Corpus Coverage

`_tools/cex_retriever.py::scan_artifacts()` walks the WHOLE repo from its
root, not just `N01_intelligence/` -- it indexes every `.md` file anywhere
that parses a `kind` in its frontmatter (skipping `README*`/`_schema*` files).
Directories `.git`, `.obsidian`, `__pycache__`, `node_modules`, `.cex`, and
`compiled` are pruned from the walk, so `.cex/cache/*` and `.cex/runtime/*`
are NOT indexed by this tool today (both live under the skipped `.cex/` dir).

| Source | Indexed by `cex_retriever.py`? |
|--------|-------------------------------|
| Any `*.md` with frontmatter `kind:`, anywhere in the repo (incl. `N01_intelligence/P01_knowledge/*.md`) | yes |
| `N01_intelligence/compiled/*.yaml` | no -- `compiled/` is pruned, and it is `.yaml` not `.md` |
| `.cex/cache/*.json` (prompt cache) | no -- `.cex/` is pruned |
| `.cex/runtime/*` (session outputs) | no -- `.cex/` is pruned |

## Retrieved Document Schema

Exact shape returned by `find_similar()` (`_tools/cex_retriever.py`):

| Field | Type | Description |
|-------|------|--------------|
| `path` | string | artifact path, relative to repo root |
| `id` | string | frontmatter `id` (falls back to filename stem) |
| `kind` | string | CEX kind |
| `pillar` | string | CEX pillar |
| `title` | string | frontmatter `title` |
| `tldr` | string | frontmatter `tldr`, if present |
| `score` | float | TF-IDF cosine similarity, rounded to 4 decimals |

## Pre-Synthesis Check Protocol

Before any research task, N01 runs:

```
existing = find_similar(task_goal, top_k=5)     # _tools/cex_retriever.py
if existing and existing[0]["score"] > 0.85:
    report("HIGH_OVERLAP: similar research found in corpus")
    decision = "extend" if existing is partial else "reuse"
else:
    proceed_with_new_research()
```

| Score | Action |
|-------|--------|
| > 0.85 | reuse or extend existing artifact |
| 0.60 - 0.85 | run targeted gaps, merge into existing |
| < 0.60 | full new research pipeline |

These thresholds are N01's own recommended policy for interpreting the
`score` field above -- they are not hardcoded inside `cex_retriever.py`
itself (its own default filter is `min_score=0.05`, a much looser floor for
"include in results at all").

## Performance Targets (aspirational -- not yet benchmarked)

No benchmark harness exists yet for this tool. The numbers below are targets
to validate against, not measurements taken from a real run.

| Metric | Target | Alert |
|--------|--------|-------|
| Index build time (cold) | < 30s for 200 docs | > 60s |
| Query latency (warm) | < 500ms | > 2s |
| Recall@10 | > 0.80 | < 0.60 |
| Precision@5 | > 0.70 | < 0.50 |

## Comparison vs. Alternatives

| Approach | Precision | Speed | Corpus Type | N01 Fit |
|----------|-----------|-------|-------------|---------|
| Keyword-only sparse ranking (this: TF-IDF cosine) | high on exact terms | fast | local text files | what N01 runs today |
| Semantic embedding search | high on paraphrase/meaning | medium (embedding call cost) | local files + embedding model | not implemented in this repo |
| Managed / cloud-hosted vector database service | high | fast at scale | requires network + hosted infra | ecosystem option N01 does not use -- local files fit N01's corpus size at zero infra cost |

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[p04_cli_research_pipeline_n01]] | sibling | 0.35 |
| [[memory_architecture_n01]] | upstream | 0.33 |
| [[reasoning_strategy_n01]] | related | 0.31 |
| [[p06_is_n01]] | related | 0.29 |
| [[nucleus_def_n01]] | downstream | 0.27 |
