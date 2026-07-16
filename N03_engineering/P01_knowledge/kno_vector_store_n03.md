---
id: kno_vector_store_n03
kind: vector_store
8f: F3_inject
primary_8f: INJECT
pillar: P01
nucleus: N03
title: "N03 Vector Store"
version: "1.1.0"
created: "2026-04-16"
updated: "2026-04-16"
author: n03_engineering
domain: engineering retrieval architecture
quality: null
tldr: "N03's vector-store posture: pgvector + rich mandatory metadata + source/compiled namespace split -- so engineering retrieval (F3 INJECT) is filterable, traceable, and boring to operate."
when_to_use: "Load when configuring or querying N03's retrieval backend. Consult for 'which vector store + metadata + index settings does N03 use, and why pgvector over FAISS/Chroma/Qdrant?'"
tags: [vector_store, p01, n03, pgvector, metadata, inventive_pride]
keywords: [vector store, pgvector, hnsw, cosine similarity, metadata rich, operational posture, hybrid retrieval, sql discipline, vector silos]
density_score: 0.98
related:
  - kno_vector_store_n01
  - kno_vector_store_n05
  - kno_vector_store_n02
---
<!-- 8F: F1=vector_store/P01 F2=vector-store-builder F3=nucleus_def_n03+kc_vector_store+P01_schema F4=metadata-rich store for engineering retrieval
     F5=Get-Content+rg+apply_patch+cex_compile.py F6=bytes:5830 F7=self-check:frontmatter+8f+properties+80l+ascii F8=N03_engineering/P01_knowledge/kno_vector_store_n03.md -->

# N03 Vector Store

## Properties

| Property | Value |
|----------|-------|
| Kind | `vector_store` |
| Pillar | `P01` |
| Nucleus | `N03` |
| Lens | `Inventive Pride` |
| Preferred backend | `pgvector` |
| Distance metric | cosine |
| Index family | HNSW where available |
| Namespace model | per pillar plus corpus role |
| Metadata policy | mandatory rich filters |
| Reliability stance | operationally boring, semantically sharp |

### Config schema (bind at provisioning)

The retriever instantiates a collection by filling these open slots:

```yaml
backend: {{backend}}                 # default pgvector
collection: {{collection}}           # one of the Storage Topology names below
dimensions: {{dimensions}}           # default 1024 (match the embedder)
distance_metric: {{distance_metric}} # cosine
namespace: {{namespace}}             # per pillar + corpus role
metadata_filters: {{metadata_filters}}  # the Required Metadata keys (mandatory)
```

### How to use

```text
8F verb: INJECT (F3). This card grounds how N03 stores + retrieves vectors;
read it before building a retriever_config or embedding_config. Always filter
by metadata first, then similarity -- unfiltered nearest-neighbor is rejected.
Keep source and compiled corpora in separate namespaces; rebuild on embedder
or dimension change. Pairs with kno_embedder_provider_n03 (the 1024-dim model).
```

## Position

N03 should not use a vector store chosen only for trend value.
It needs a backend that respects metadata, supports disciplined operations, and coexists with the rest of CEX.
Inventive Pride favors a store that is elegant under maintenance, not merely impressive in benchmarks.

## Recommended Backend

`pgvector` is the primary recommendation for N03.

Reasons:
- relational metadata is first-class
- operational posture is familiar
- collections can be organized with SQL discipline
- backups, migrations, and audit are straightforward
- hybrid retrieval integration is simpler than with isolated vector silos

## Rejected Defaults

| Backend | Why not primary | When acceptable |
|--------|------------------|-----------------|
| FAISS | fast but operationally isolated | local experiments |
| Chroma | convenient but lighter governance story | prototypes |
| Qdrant | strong option, but adds another service tier | high-scale vector specialization |
| Pinecone | capable, but more vendor-bound than needed | managed scale burst |

## Storage Topology

| Collection | Scope | Notes |
|-----------|-------|-------|
| `cex_p01_source` | knowledge markdown chunks | source-of-truth retrieval |
| `cex_p10_memory` | memory chunks and digests | separate volatility profile |
| `cex_compiled_shadow` | compiled yaml/json derivatives | searchable but lower rank |
| `cex_eval_holdout` | evaluation corpus | never mixed with production rank tests |

## Required Metadata

- `source_path`
- `artifact_id`
- `kind`
- `pillar`
- `nucleus`
- `section_h1`
- `section_h2`
- `chunk_role`
- `updated`
- `content_hash`

Without this metadata, semantic search becomes decorative.
N03 requires filtered retrieval, not blind nearest-neighbor theatrics.

## Index Settings

| Setting | Default | Rationale |
|--------|---------|-----------|
| dimensions | `1024` | aligned with primary embedder |
| distance_metric | `cosine` | matches normalized vectors |
| hnsw_m | medium | balanced graph density |
| ef_construction | `128` | strong recall during build |
| ef_search | `64` | practical query latency |
| batch_upsert | moderate | stable nightly indexing |

## Lifecycle Rules

1. Rebuild collection on [[kc_embedding_config|embedding]] family or dimension change.
2. Soft refresh on content hash drift.
3. Keep source and compiled corpora logically separated.
4. Archive deleted-source vectors rather than silently orphaning them.
5. Run evaluation queries after every significant index rebuild.

## Pride Lens

Inventive Pride changes the storage question.
The issue is not only where vectors live.
The issue is whether the store lets N03 retrieve authoritative construction context with composure.
A proud vector store is traceable, filterable, and boring to operate.
If recovery is messy or provenance is weak, it is beneath the nucleus.

## Query Patterns

| Pattern | Store expectation |
|--------|-------------------|
| exact kind lookup | metadata filter then similarity |
| cross-kind comparison | broad vector search with pillar constraint |
| local nucleus search | `nucleus=N03` boost |
| memory recovery | separate memory collection with freshness prior |
| evaluation benchmark | isolated holdout collection |

## Failure Modes

| Failure | Consequence | Response |
|--------|-------------|----------|
| mixed dimensions | invalid similarity | block writes immediately |
| no metadata filters | precision collapse | reject retrieval config |
| compiled and source duplicates merged | prompt redundancy | split namespaces |
| index drift after edits | stale retrieval | hash-driven refresh |
| service complexity beyond need | maintenance drag | simplify to primary SQL path |

## Security and Operations

- credentials should live in standard secret config
- backups should follow database backup policy
- access should be read-mostly for retrievers
- write paths should be limited to indexing workflows
- schema changes should be versioned and reversible

## Growth Policy

Move beyond the primary backend only if one of these becomes true:
- corpus scale materially exceeds current query latency targets
- multi-tenant isolation becomes dominant
- vector-only workloads outgrow relational convenience
Until then, elegance is restraint.

## Integration Notes

This store is paired with:
- header-aware chunking
- normalized `1024`-dimension embeddings
- hybrid retriever fusion
- reranking before prompt assembly

The vector store is infrastructure, but it still reflects taste.
N03 chooses a backend that can survive scale without becoming a side project.

## Final Position

Use `pgvector` as the N03 primary vector store, with rich metadata and separated source versus compiled namespaces.
That is the proud architecture: strong retrieval, low drama, clean operations.

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[kno_vector_store_n01]] | sibling | 0.44 |
| [[kno_vector_store_n05]] | sibling | 0.42 |
| [[bld_orchestration_vector_store]] | related | 0.41 |
| [[kno_vector_store_n02]] | sibling | 0.37 |
