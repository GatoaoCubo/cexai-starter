---
id: p10_bi_bm25_knowledge
kind: knowledge_index
8f: F3_inject
pillar: P10
title: "BM25/TF-IDF Knowledge Index -- Sparse Retrieval Baseline"
version: 1.0.0
created: "2026-07-20"
updated: "2026-07-20"
author: n04_knowledge
domain: knowledge-retrieval
quality: null
tags: [knowledge-index, bm25, sparse-retrieval, tf-idf, baseline, retrieval]
tldr: "TF-IDF sparse index over the repo's typed artifacts. Baseline for retrieval; enables benchmarking against a future dense or hybrid index."
keywords: [knowledge index, sparse retrieval baseline, sparse index, knowledge-index, bm25, sparse-retrieval, tf-idf, baseline, okapi, k1, b, recall, precision]
density_score: null
related:
  - knowledge-index-builder
  - p01_gl_rag
  - p01_gl_embedding
  - kc_knowledge_vocabulary
  - p10_em_n04_knowledge
---

# TF-IDF Knowledge Index

## Configuration

| Parameter | Value | Rationale |
|-----------|-------|-----------|
| Algorithm | TF-IDF (stdlib `math.log` + `collections.Counter`) | Industry-standard sparse retrieval, zero external dependency |
| Corpus size | `{{corpus_doc_count}}` artifacts | All `.md` with valid frontmatter (grows as the repo grows) |
| Vocabulary | `{{corpus_vocab_size}}` terms | After stop-word removal + lowercasing (grows with new kinds) |
| Tokenizer | regex, 2+ chars incl. >=1 letter, lowercased | Simple, language-agnostic |
| Stop words | English standard + structural noise (`---`, `yaml`, `md`, frontmatter keys) | Reduce noise |
| Storage | `.cex/retriever_index.json` | In-process JSON |

## Index Scope (what gets indexed)

| Source | Content |
|--------|---------|
| `archetypes/builders/{kind}-builder/` | 12 ISOs per builder -- the taxonomy backbone |
| `N00_genesis/P{01-12}_*/` | Pillar schemas + kind knowledge cards |
| `N{01-07}_*/` (all subdirs) | Nucleus artifacts -- agents, prompts, schemas, KCs |
| `_docs/` | Specification documents |
| `compiled/*.yaml` | Excluded -- redundant with source `.md` |

## Implementation

The current implementation lives in `_tools/cex_retriever.py`:
- Builds a TF-IDF matrix in pure Python (no numpy, no scikit-learn)
- Persists to `.cex/retriever_index.json`
- Query: tokenize -> cosine similarity over sparse vectors -> top-K
- Rebuild: `python _tools/cex_retriever.py --build` (the real, complete flag)
- Used by: the 8F runner's F3 INJECT step, the `/build` skill, spec compilers

## BM25 vs TF-IDF (a real limitation, stated plainly)

Plain TF-IDF is `tf(t,d) * idf(t)` -- linear in term frequency. True BM25
saturates term frequency and normalizes for document length:
`((k1+1) * tf) / (k1 * ((1-b) + b * (|d| / avg_dl)) + tf) * idf(t)`.

Practical impact: TF-IDF over-weights common terms in long documents; BM25
balances doc-length normalization better. For short, mostly-tabular typed
artifacts the gap is small. A real BM25 implementation (e.g. via the
`rank_bm25` package) is a documented upgrade path, not current behavior.

## Performance Baseline

| Metric | Value | Context |
|--------|-------|---------|
| Index build time | `{{build_time_seconds}}`s | scales with corpus size, single-threaded |
| Query latency P50 | `{{p50_latency_ms}}`ms | Top-10 retrieval (in-process) |
| Memory footprint | `{{index_memory_mb}}`MB | Sparse matrix + vocabulary in RAM |

Re-run `python _tools/cex_retriever.py --stats` for current numbers on your
own checkout -- corpus size and vocabulary size drift as you add artifacts.

## Planned Upgrades

| Upgrade | Kind | Impact | Status |
|---------|------|--------|--------|
| Dense counterpart | `vector_store` | Semantic retrieval | not started |
| Hybrid fusion (RRF) | `retriever_config` | Best of sparse + dense | not started |
| Incremental updates | tool enhancement | No full rebuild on single KC add | not started |
| Real BM25 (not TF-IDF) | retriever swap | modest recall gain on long docs | not started |
| Query expansion (synonyms) | `retriever_config` | Handle vocab mismatches | not started |

## Failure Modes

| Failure | Symptom | Mitigation |
|---------|---------|------------|
| Stale index | Recent KCs absent from results | Re-run `--build` after adding artifacts |
| Cold start | First query slow | Pre-warm on session boot |
| Vocab mismatch | Query terms not in corpus | Rephrase query with corpus vocabulary |
| Frontmatter drift | Index includes broken artifacts | Run the doctor/validator before indexing |
| Long-doc bias | Long documents dominate top-K | Length normalization tuning (future BM25 `b` parameter) |

## Cross-Pillar References

| Pillar | Artifact | Why it matters |
|--------|----------|----------------|
| P01 | [[p01_gl_rag]] | RAG glossary -- terms this index's queries use |
| P01 | [[p01_gl_embedding]] | Dense counterpart context |
| P10 | [[p10_em_n04_knowledge]] | Entity registry referencing this index's building blocks |

## Related Files

- `_tools/cex_retriever.py` -- the real TF-IDF implementation
- `p01_gl_rag.md` -- RAG glossary entry

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[knowledge-index-builder]] | related | 0.32 |
| [[p01_gl_rag]] | upstream | 0.40 |
| [[p01_gl_embedding]] | related | 0.30 |
| [[kc_knowledge_vocabulary]] | related | 0.32 |
| [[p10_em_n04_knowledge]] | sibling | 0.30 |
