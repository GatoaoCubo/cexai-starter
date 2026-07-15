---
id: n04_vdb_assimilation
kind: vector_store
8f: F3_inject
pillar: P01
version: "1.0.0"
created: "2026-05-29"
updated: "2026-05-29"
author: n04_knowledge
title: "Assimilation Vector Store"
backend: faiss
connection:
  host: in_process
  port: null
  api_key_env: null
  tls: false
  database: null
collection: "brain_{slug}"
dimensions: 384
distance_metric: cosine
index_type: flat
hnsw: null
max_vectors: null
metadata_filtering: true
metadata_schema:
  source_id: string
  section: string
persistence: manual
namespace_strategy: "collection_per_brain"
cloud_region: null
pricing: null
domain: vector_storage
quality: null
tags: [vector-store, vector_store, n04, assimilation, faiss, offline, sovereign, flat]
tldr: "Offline sovereign store for DEEP brains: faiss IndexFlatIP (exact, 384d, cosine), degrade-never to a pure-stdlib JSON flat index. No key, no cloud. Realized per-run in out_dir by cex_distill_orchestrator."
keywords: [faiss, flat index, cosine, offline, sovereign, per-brain, exact search, degrade-never]
density_score: null
data_source: "https://github.com/facebookresearch/faiss"
linked_artifacts:
  primary: p01_emb_assimilation_n04
  related: [p01_retr_assimilation_n04, n04_rs_assimilation]
related:
  - p01_emb_assimilation_n04
  - p01_retr_assimilation_n04
  - n04_rs_assimilation
  - vector-store-builder
  - p11_qg_vector_store
slots:
  namespace: "<the collection to read or write>"
  query_vector: "<the embedding to search by>"
---

# Assimilation Vector Store

## Boundary
vector_store IS: the storage + index config for DEEP-path dense vectors -- backend,
dimensions, metric, index type, persistence. vector_store IS NOT: the embedding model
([[p01_emb_assimilation_n04]] embedding_config), the search params ([[p01_retr_assimilation_n04]]
retriever_config), nor the source contract ([[n04_rs_assimilation]] rag_source).

## Backend Matrix
| Parameter | Value | Source |
|-----------|-------|--------|
| Backend | faiss (local, in-process, MIT) | https://github.com/facebookresearch/faiss |
| Index type | IndexFlatIP (flat, exact) | https://github.com/facebookresearch/faiss/wiki/Faiss-indexes |
| Dimensions | 384 | Upstream: [[p01_emb_assimilation_n04]] |
| Distance metric | cosine (L2-normalized vectors) | Mathematical property |
| Auth | none (api_key_env: null) | Local/offline -- no key |
| Degrade floor | offline JSON flat (pure stdlib) | Realized by cex_distill_orchestrator.py |

## Index Configuration
Per-brain corpora are small (one vertical's sources), so an EXACT flat index is the
right call -- HNSW overhead is unwarranted below ~10K vectors and flat gives perfect
recall. `IndexFlatIP` over L2-normalized vectors == cosine. When faiss is not
importable the orchestrator writes the same vectors as a JSON flat index and scores
with `cex_embedder.cosine` -- identical results, zero dependency (degrade-never).

## Namespace Strategy
One collection per brain: `brain_{slug}` (e.g. `brain_demo`). The realized index file
is `out_dir/vector_store/vs_{slug}.json`. Never mix embedding models within one
collection -- dimension mismatch silently corrupts search.

## Lifecycle Operations
- **Create/reindex**: `cex_distill_orchestrator.py --brain X --sources DIR --depth deep --execute`.
- **Idempotent**: sha-anchored; an unchanged-source re-run does NOT re-embed or rewrite.
- **Persist**: `manual` -- the JSON sidecar is rewritten only when the aggregate signature changes.
- **Backup/restore**: copy `vs_{slug}.json`; it is self-describing (backend, dim, metric, vectors).
- **Scope**: the realized index lives in the run's out_dir (sandbox), never committed to git.

## Anti-Patterns
- Mixing embedding models in one store -> dimension mismatch breaks every query.
- Choosing HNSW for a tiny per-brain corpus -> needless complexity; flat is exact + fast.
- Committing the realized `vs_*.json` -> it is sandbox runtime state, not a source artifact.
- Assuming a cloud key/region -> this store is offline + sovereign; no api_key, no network.
- Cosine metric on unnormalized vectors -> normalize first (the embedder L2-normalizes).

## References
- faiss: https://github.com/facebookresearch/faiss
- faiss indexes: https://github.com/facebookresearch/faiss/wiki/Faiss-indexes


### How to use

```text
You are the consuming agent that acts on this vector_store under F3 INJECT.
- Resolve the open slots (namespace, query_vector) from the caller request.
- Honor every constraint and field contract declared above.
- Emit the result in the shape this vector_store defines; never improvise the schema.
```

### Procedure

```text
1. Load this artifact and read its contract under F3 INJECT.
2. Bind namespace and query_vector from the incoming request.
3. Validate the inputs against the constraints declared above.
4. Execute the vector_store behavior; resolve each open slot at act-time.
5. Verify the output shape, then signal completion to the orchestrator.
```

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[p01_emb_assimilation_n04]] | upstream | 0.42 |
| [[p01_retr_assimilation_n04]] | downstream | 0.36 |
| [[n04_rs_assimilation]] | related | 0.32 |
| [[vector-store-builder]] | related | 0.26 |
| [[p11_qg_vector_store]] | related | 0.24 |
