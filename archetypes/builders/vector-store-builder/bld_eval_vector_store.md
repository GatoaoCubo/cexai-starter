---
kind: quality_gate
id: p11_qg_vector_store
pillar: P11
llm_function: GOVERN
purpose: Golden and anti-examples of vector_store artifacts
pattern: few-shot learning — LLM reads these before producing
quality: null
title: "Gate: Vectordb Backend"
version: "1.0.0"
author: builder_agent
tags: [quality-gate, vector-store, vector-database, P01, hnsw]
tldr: "Quality gate for vector_store artifacts: enforces dimensions, distance metric, index type, and persistence fields."
domain: vector_store
created: "2026-04-06"
updated: "2026-04-06"
8f: "F7_govern"
density_score: 0.87
related:
  - bld_memory_vector_store
  - vector-store-builder
  - bld_schema_vector_store
---
## Quality Gate

# Gate: Vectordb Backend
## Definition
A `vector_store` configures vector embedding storage: backend, dimensions, distance metric, index type, HNSW params, persistence. Gates ensure dimension contract, metric alignment, and complete config.
## HARD Gates
All HARD gates must pass. Any single failure sets score to 0 and blocks publish.
| ID  | Check | Failure consequence |
|-----|-------|---------------------|
| H01 | YAML frontmatter parses without error | Artifact unparseable by tooling |
| H02 | `id` matches `^p01_vdb_[a-z][a-z0-9_]+$` | Namespace violation — not discoverable |
| H03 | `id` equals filename stem exactly | Brain search failure — id/file mismatch |
| H04 | `kind` == literal string `"vector_store"` | Type integrity failure |
| H05 | `quality` == `null` | Self-scoring violation — pool metric corruption |
| H06 | Required fields present: `id`, `kind`, `pillar`, `version`, `created`, `updated`, `author`, `backend`, `dimensions`, `distance_metric`, `index_type`, `persistence`, `tags`, `tldr` | Incomplete artifact |
## SOFT Scoring
Weights sum to 100%. Each dimension scores 0 or its full weight.
| ID  | Dimension | Weight | Criteria |
|-----|-----------|--------|----------|
| S01 | tldr quality | 1.0 | `tldr` <= 160 chars, names backend + index type + dimension count |
| S02 | HNSW parameters documented | 1.0 | M, ef_construction, ef_search present with tradeoff explanation |
| S03 | Persistence documented | 1.0 | `persistence` field present; FAISS = manual with save/load instructions |
| S04 | Namespace strategy defined | 1.0 | Body describes collection naming and domain isolation |
| S05 | Lifecycle operations documented | 1.0 | Create, reindex, backup procedures in body |
| S06 | Metadata filtering documented | 0.5 | `metadata_filtering` boolean; body describes supported operations |
## Actions
| Score | Tier | Action |
|-------|------|--------|
| >= 9.5 | GOLDEN | Publish to pool + record in memory |
| >= 8.0 | PUBLISH | Commit to pool |
| >= 7.0 | REVIEW | Acceptable with documented improvement items |
| < 7.0 | REJECT | Revise and resubmit — do not publish |
| 0 (HARD fail) | REJECTED | Fix failing HARD gate(s) first |
## Bypass
Bypasses are logged and expire automatically.
| Field | Value |
|-------|-------|

## Examples

# Examples: vector-store-builder
## Golden Example
INPUT: "Configure Chroma for local RAG development with 1536-dim OpenAI embeddings"
OUTPUT:
```yaml
id: p01_vdb_chroma
kind: vector_store
pillar: P01
version: "1.0.0"
created: "2026-04-06"
updated: "2026-04-06"
author: "builder_agent"
backend: "chroma"
connection:
  host: "localhost"
  port: 8000
  api_key_env: null
  tls: false
  database: null
collection: "cex_knowledge"
dimensions: 1536
distance_metric: cosine
index_type: hnsw
hnsw:
  M: 16
  ef_construction: 200
  ef_search: 100
max_vectors: null
metadata_filtering: true
metadata_schema:
  pillar: string
  kind: string
  created: date
  domain: string
persistence: auto
namespace_strategy: "collection_per_domain"
cloud_region: null
pricing: null
domain: vector_storage
quality: null
tags: [vector-store, chroma, hnsw, local]
tldr: "Chroma — local, HNSW, 1536d (OpenAI), cosine, auto-persist, metadata filtering for RAG dev"
keywords: [chroma, vectordb, hnsw, local, rag]
linked_artifacts:
  primary: null
  related: [p01_emb_openai_text_embedding_3_small]
data_source: "https://docs.trychroma.com/"
## Boundary
vector_store IS: storage and indexing config for Chroma (HNSW index, 1536 dimensions, cosine).
vector_store IS NOT: embedder_provider, model_provider, retriever, chunker.
## Backend Matrix
| Parameter | Value | Source |
|-----------|-------|--------|
| Backend | chroma | https://docs.trychroma.com/ |
| Version | 0.5.x | https://github.com/chroma-core/chroma/releases |
| Host | localhost:8000 | https://docs.trychroma.com/docs/run-chroma/client-server |
| Auth | none (local) | https://docs.trychroma.com/docs/run-chroma/client-server |
| Dimensions | 1536 | Upstream: p01_emb_openai_text_embedding_3_small |
| Distance Metric | cosine (L2-normalized embeddings) | Mathematical property |
## Index Configuration
| Parameter | Value | Effect |
|-----------|-------|--------|
| M | 16 | Connections per node. Higher = better recall, more RAM. 16 optimal for <1M vectors |
| ef_construction | 200 | Build-time search width. Higher = better index quality, slower initial build |
| ef_search | 100 | Query-time search width. Higher = better recall, slower queries. Tune per latency SLA |
Scale guidance:
- < 10K vectors: flat index sufficient, HNSW overhead unnecessary
- 10K-1M vectors: HNSW with M=16, ef_construction=200 (default)
- > 1M vectors: consider Pinecone/Qdrant for distributed scaling
## Namespace Strategy
- One collection per knowledge domain: `cex_knowledge`, `cex_marketing`, `cex_commercial`
- Metadata field `pillar` enables cross-domain queries with filtering
- Never mix embedding models across collections — dimension mismatch breaks everything

### S_RELATED
-0.3 if `related:` < 3 or body lacks Related Artifacts

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[p03_ins_vector_store]] | upstream | 0.52 |
| [[bld_memory_vector_store]] | upstream | 0.46 |
| [[vector-store-builder]] | upstream | 0.46 |
| [[bld_knowledge_vector_store]] | upstream | 0.43 |
| [[bld_schema_vector_store]] | upstream | 0.43 |
