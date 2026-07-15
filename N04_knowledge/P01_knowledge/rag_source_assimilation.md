---
id: n04_rs_assimilation
kind: rag_source
8f: F3_inject
pillar: P01
version: "1.0.0"
created: "2026-05-29"
updated: "2026-05-29"
author: n04_knowledge
url: "ingest://user-sources"
domain: "assimilation-engine"
last_checked: "2026-05-29"
quality: null
embed_mode: tfidf_offline
privacy: lab_only
chunk_strategy_ref: n04_cs_assimilation
retriever_config_ref: n04_rc_assimilation
tags: [rag-source, n04, assimilation, init, ingest, offline, lab-only, P01]
tldr: "The assimilation RAG profile: the default source contract that cex_distill_orchestrator.py reads when turning a user's ingested sources (repo/docs/brandbook) into a typed vertical brain. Offline-by-default, LAB-ONLY, sha-anchored."
keywords: [assimilation, ingest, distill, offline, tfidf, lab-only, provenance, vertical-brain, sha-anchored]
reliability: "high"
format: "normalized-text"
extraction_method: "ingest_contract"
density_score: null
related:
  - p01_chunk_assimilation_n04
  - p01_retr_assimilation_n04
  - p10_em_assimilation_seed
  - bld_collaboration_rag_source
  - kc_reverse_prompt
---

# RAG Source: Assimilation Profile (user sources -> vertical brain)

## 1. Source Identity
This is not a single URL -- it is the **profile** that governs how ANY user
source assimilates into a CEX brain during `/init` Stage 2 (DISTILL). The
`cex_distill_orchestrator.py` runtime reads this artifact (plus the referenced
`chunk_strategy` and `retriever_config`) as its default configuration.

| Field | Value | Why |
|-------|-------|-----|
| **Intake** | normalized text + provenance (the INGEST contract) | Stage 1 hands typed records `{source_id, uri, text, sha256}` |
| **Fallback** | file-list (each file = one source) | runs today before ingest adapters land (Wave B) |
| **Scope** | repo + docs(PDF/office) + brandbook (D1) | best-supported v1 sources; social/CV/media are v2 stubs |
| **Privacy** | `lab_only` (D6) | distilled user knowledge stays in the user's own CEX |

## 2. Embedding Mode (D3 -- offline default, sovereign)
- **`embed_mode: tfidf_offline`** -- the brain MUST build with NO API key.
  Embedding reuses `cex_retriever.build_tfidf` (pure stdlib).
- A provider embedder (`embed_mode: provider`) is OPTIONAL for deep distill and
  **degrades to TF-IDF** when no key is present (degrade-never).

## 3. Depth (D4)
- **LIGHT (default)**: scoped `knowledge_index` + `knowledge_card`(s) + `entity_memory`.
- **DEEP (opt-in)**: adds a `knowledge_graph` (co-occurrence edges) + provider embeddings.
- Default runs MUST NOT require deep.

## 4. Provenance + Idempotency
Every distilled artifact carries `source_uri` + `source_sha` in frontmatter.
The orchestrator keeps a sha-anchored ledger (`_brain_manifest.json`): a re-run
on unchanged sources is a **no-op**. This generalizes the deterministic
transmuter pattern from `spec_cex_ingest_aitmpl_engine`.

## 5. Trust Assessment
| Dimension | Rating | Notes |
|-----------|--------|-------|
| Authority | high | the source is the user's own world (repo/docs/brand) |
| Freshness | med | re-distill on source change; sha-anchored staleness check |
| Accuracy | med | heuristic distill; peer-review/curate before downstream trust |
| Relevance | high | scoped to the user's chosen vertical |

## 6. Indexing Configuration (delegated)
- **Chunk strategy**: [[p01_chunk_assimilation_n04]] (heading_based, 1024/200)
- **Retriever**: [[p01_retr_assimilation_n04]] (hybrid, top_k 5, threshold 0.75)
- **Entity store seed**: p10_em_assimilation_seed

## 7. Consumers
- `cex_distill_orchestrator.py` -- reads this profile as default config
- `/init` assimilate path (Stage 2) -- the entry-door runtime
- scoped `knowledge_index` -- the navigable brain this profile produces

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[p01_chunk_assimilation_n04]] | downstream | 0.42 |
| [[p01_retr_assimilation_n04]] | downstream | 0.40 |
| p10_em_assimilation_seed | downstream | 0.34 |
| [[bld_orchestration_rag_source]] | related | 0.28 |
| kc_reverse_prompt | related | 0.24 |
