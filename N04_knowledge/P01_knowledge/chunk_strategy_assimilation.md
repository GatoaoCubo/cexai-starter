---
id: p01_chunk_assimilation_n04
kind: chunk_strategy
8f: F3_inject
pillar: P01
version: "1.0.0"
created: "2026-05-29"
updated: "2026-05-29"
author: n04_knowledge
title: "Assimilation Chunk Strategy"
default_strategy: heading_based
chunk_size: 1024
chunk_overlap: 200
quality: null
tags: [chunk_strategy, n04, assimilation, rag, chunking, offline, P01]
tldr: "Content-aware chunking for the assimilation engine: heading-based splitting for mixed user corpora (Markdown/docs/code), with sentence-boundary windowing for oversize blocks. Read by cex_distill_orchestrator.py."
keywords: [heading_based, chunk_size, chunk_overlap, sentence boundary, mixed corpora, section metadata, assimilation]
density_score: null
related:
  - n04_rs_assimilation
  - p01_retr_assimilation_n04
  - p01_kc_chunk_strategy
  - p01_kc_rag_chunking_strategies
  - bld_collaboration_chunk_strategy
---

# Assimilation Chunk Strategy

## 1. Purpose
Defines how an arbitrary user source is split before offline embedding during
`/init` DISTILL. Unlike the N04 internal strategy (tuned for the CEX repo), this
profile assumes a **mixed, unknown corpus**: Markdown docs, office exports, code,
and brandbook text. It is the chunk layer `cex_distill_orchestrator.py` reads.

## 2. Default Strategy: `heading_based`
| Parameter | Value | Rationale |
|-----------|-------|-----------|
| `default_strategy` | `heading_based` | most user sources carry heading structure; sections are the best semantic boundary |
| `chunk_size` | `1024` | target characters; balances context against retrieval noise for TF-IDF |
| `chunk_overlap` | `200` | continuity across boundaries; kept below `chunk_size / 2` (hard rule) |

## 3. Method Ladder (degrade-never)
1. **heading_based** -- split on Markdown `#..######` markers; the heading becomes
   the chunk's `section` metadata. Used whenever any heading is present.
2. **paragraph** -- fall back to blank-line blocks when a source has no headings.
3. **sentence-window** -- any block larger than `chunk_size` is windowed at the
   nearest sentence boundary with `chunk_overlap` carry-over (no mid-sentence cuts).

## 4. Metadata Propagation
Each chunk carries: `index` (position), `section` (nearest heading), and inherits
`source_id` + `source_sha` from the parent record. This metadata flows into the
distilled `knowledge_card` provenance and the scoped `knowledge_index`.

## 5. Quality Gate
- [ ] `chunk_overlap` < `chunk_size / 2`
- [ ] every chunk non-empty after strip
- [ ] heading retained as section label when `heading_based` fires
- [ ] oversize blocks split on sentence boundaries, never mid-word

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[n04_rs_assimilation]] | upstream | 0.42 |
| [[p01_retr_assimilation_n04]] | sibling | 0.34 |
| [[kc_chunk_strategy]] | related | 0.30 |
| p01_kc_rag_chunking_strategies | related | 0.28 |
| [[bld_orchestration_chunk_strategy]] | related | 0.26 |
