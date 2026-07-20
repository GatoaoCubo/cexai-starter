---
id: p04_retr_n04_knowledge
kind: retriever
8f: F3_inject
pillar: P04
nucleus: n04
title: "Retriever -- N04 TF-IDF Sparse Retrieval"
version: "1.0.0"
quality: null
tags: [retriever, n04, tf_idf, sparse_retrieval, P04]
domain: knowledge management
status: active
created: "2026-07-20"
updated: "2026-07-20"
author: n04_knowledge
tldr: "N04's retriever: sparse TF-IDF (_tools/cex_retriever.py, stdlib, wired into F3 INJECT) is the primary and only retrieval path shipped in this starter. A dense (embedding-based) layer is a documented extension point, not a claim about what runs today."
keywords: [knowledge management, retriever, tf-idf, sparse retrieval, retriever configuration, dense_retrieval, sparse_retrieval]
density_score: null
related:
  - bld_knowledge_card_retriever_config
  - p01_retr_knowledge_n04
  - p09_kc_retriever_domain
  - bld_architecture_retriever
  - p01_kc_retriever
  - bld_instruction_retriever
---

# Retriever: N04 TF-IDF Sparse Retrieval

## Retriever Identity

| Property | Value |
|----------|-------|
| Primary strategy | Sparse only -- TF-IDF (pure Python stdlib, no numpy, no external ML library) |
| Sparse backend | `_tools/cex_retriever.py` -- wired into F3 INJECT (called by the 8F runner's inject step to find examples for a kind) |
| Dense layer | Not shipped in this starter -- see "Extension Point" below before claiming one exists |
| Fusion step | none implemented -- only one retriever runs per call, so there is nothing to fuse |
| Reranking step | none implemented |
| Manual last resort | `grep` -- human/nucleus-invoked, not code-orchestrated |

> **Honesty note.** It is tempting to describe a retriever config with a
> hosted vector database, a rank-fusion step, and a reranking model, because
> those are the well-known pieces of a mature RAG stack. This artifact
> describes only what `_tools/cex_retriever.py` actually implements today.
> Anything beyond that belongs in the Extension Point section below, labeled
> as an option -- never presented as current behavior.

---

## Sparse Retriever Config (what actually runs)

```yaml
sparse_retriever:                 # _tools/cex_retriever.py
  backend: tfidf                  # stdlib math.log + collections.Counter; no third-party library
  index_path: ".cex/retriever_index.json"      # JSON, built by --build
  corpus_scope: "whole repo -- every .md with frontmatter+kind"
  vocabulary_rule: "term kept if it appears in >=2 docs and <=90% of docs"
  tokenizer: "regex, 2+ chars incl. >=1 letter, lowercased, stopword-filtered"
  similarity: cosine                # over sparse {term: tfidf_score} dict vectors
  top_k_default: 5
  min_score_default: 0.05
```

CLI (the real, complete flag set -- verify with `--help` before assuming more exist):
```bash
python _tools/cex_retriever.py --build
python _tools/cex_retriever.py --query "..." --kind K --pillar P --top-k N --min-score S
python _tools/cex_retriever.py --stats
python _tools/cex_retriever.py --examples <kind> --intent "..."
```

---

## Extension Point (documented, not implemented)

The techniques below are legitimate, well-known retrieval-augmentation
approaches. **None of them ship in this starter's `cex_retriever.py`.**
Listed here so a fork knows where to plug them in, never as current behavior:

| Concept | What it is | Where to start |
|---------|-----------|----|
| Dense / embedding retrieval | Cosine similarity over vector embeddings instead of sparse term counts | [[p01_retr_knowledge_n04]] (worked example, `retriever_config` kind) |
| Rank-fusion | Merges two independently ranked result lists into one, without retraining either retriever | [[p01_retr_knowledge_n04]] |
| Reranking model | A second, more expensive model that re-scores a short list of top candidates from a first-pass retriever | `retriever_config` kind, "Ensemble & Reranking" pattern |
| Hosted vector database | An external vector-search service as an alternative to an in-repo store | see `embedding_config_knowledge.md` for the embedding side of that integration |

## Fallback Chain (what actually happens when the primary retriever can't answer)

```
Level 1: cex_retriever.py TF-IDF (primary, always available)
  |-- pure Python stdlib, no external service, no API key required
  |-- wired into F3 INJECT
  |
  | Nothing below this line is an automated cascade -- reach for it by hand.
  v
Manual last resort: grep
  |-- bash: grep -r --include="*.md" "{query}" ./N04_knowledge/
  |-- no scoring, presence detection only, always available
```

---

## Tuning Reference

| Parameter | CLI flag | Default | Range | Effect |
|-----------|------|-----------------|-------|--------|
| `min_score` | `--min-score` | 0.05 | 0.0-1.0 | Lower = more recall, more noise |
| `top_k` | `--top-k` | 5 | any positive int | Higher = more candidates returned |
| vocabulary doc-frequency bounds | fixed in code | >= 2 docs, <= 90% of docs | not CLI-tunable | Controls vocabulary size vs. noise |

## Performance Targets

No automated retrieval-quality benchmark harness (precision/recall-style
metrics) ships with `cex_retriever.py` today -- confirm with `--help` before
citing a benchmark flag that isn't there. The observable numbers today are
corpus size and vocabulary size via `--stats`, and index-build wall-clock
time via `--build --verbose`. A precision/recall harness would need to be
built first; `eval_metric_n04.md` (P07) defines the formulas to build it against.

---

## Integration

| Artifact | Role |
|---------|------|
| `input_schema_knowledge_query.md` | `retrieval_mode` field this retriever serves |
| `embedding_config_knowledge.md` | Where a future dense layer's model config would live |
| `p01_retr_knowledge_n04.md` | Fuller retriever_config worked example (P01 KC) |
| `eval_metric_n04.md` | Formulas to score this retriever's output quality |

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[bld_knowledge_card_retriever_config]] | upstream | 0.36 |
| [[p01_retr_knowledge_n04]] | upstream | 0.32 |
| [[p09_kc_retriever_domain]] | downstream | 0.30 |
| [[bld_architecture_retriever]] | downstream | 0.28 |
| [[p01_kc_retriever]] | upstream | 0.28 |
| [[bld_instruction_retriever]] | upstream | 0.25 |
