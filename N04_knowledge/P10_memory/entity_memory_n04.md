---
id: p10_em_n04_knowledge
kind: entity_memory
8f: F3_inject
pillar: P10
nucleus: n04
title: "Entity Memory -- N04 Knowledge Domain Entities"
version: "1.0.0"
quality: null
tags: [entity_memory, n04, knowledge, rag, taxonomy, P10]
domain: knowledge management
status: active
created: "2026-07-20"
updated: "2026-07-20"
author: n04_knowledge
tldr: "Persistent entity tracker for the knowledge nucleus: canonical entities in the knowledge domain (RAG frameworks, vector stores, embedding models, retrieval algorithms). Each entity includes type, status, key facts, and cross-references."
keywords: [knowledge management, entity memory, knowledge domain entities, rag systems, vector stores, embedding models, retrieval frameworks, each entity includes type, key facts]
density_score: null
related:
  - p10_bi_bm25_knowledge
  - kc_knowledge_vocabulary
  - agent_card_n04
---

# Entity Memory: N04 Knowledge Domain Entities

## About This File

Entity memory tracks canonical entities the knowledge nucleus works with:
systems, products, frameworks, concepts. Update it when a new entity is
encountered or a tracked fact changes -- never overwrite a row's Key Facts
in place without noting what changed; supersede and annotate instead.

---

## Entity Registry

### RAG Frameworks

| Entity | Type | Status | Key Facts |
|--------|------|--------|-----------|
| LlamaIndex | framework | active | Python, 100+ integrations, strong RAG primitives, QueryEngine abstraction |
| LangChain | framework | active | Chains, agents, LCEL; heavy but popular |
| Haystack | framework | active | Production RAG, Pipeline abstraction, strong eval tools |
| DSPy | framework | emerging | Declarative LM programming, auto-prompt optimization (Stanford) |
| Semantic Kernel | framework | active | Microsoft, .NET + Python, enterprise focus, plugin architecture |

### Vector Stores

| Entity | Type | Status | Key Facts |
|--------|------|--------|-----------|
| pgvector | extension | active | PostgreSQL extension, cosine/L2/inner_product, 16K max dims |
| Pinecone | service | active | Serverless, namespaces, metadata filtering, 20K dim limit paid |
| ChromaDB | library | active | Local-first, ephemeral or persistent, Python-native |
| Weaviate | service | active | GraphQL API, multi-modal, built-in hybrid search |
| Qdrant | service | active | Rust-based, payload filters, high-throughput, on-prem option |
| FAISS | library | active | CPU/GPU, pure ANN library (no persistence) |

### Embedding Models

| Entity | Type | Status | Key Facts |
|--------|------|--------|-----------|
| text-embedding-3-small | model | active | OpenAI, 1536 dim, 8191 max tokens |
| text-embedding-3-large | model | active | OpenAI, 3072 dim, higher precision, 2x cost |
| text-embedding-ada-002 | model | deprecated | OpenAI legacy, 1536 dim, superseded by 3-small |
| nomic-embed-text | model | active | Open-source, 8192 token context, strong for long docs |
| mxbai-embed-large | model | active | Open-source, 1024 dim, strong MTEB performance |
| bge-m3 | model | active | Multi-lingual, multi-functional (dense+sparse+colbert) |

### Memory Systems

| Entity | Type | Status | Key Facts |
|--------|------|--------|-----------|
| MemGPT/Letta | framework | active | Hierarchical memory paging, working<->archival, open-source |
| Zep | service | active | Temporal knowledge graphs, session memory, fact extraction |
| mem0 | library | active | Selective memory extraction, 4-layer architecture, provider-agnostic |

### Retrieval Algorithms

| Entity | Type | Status | Key Facts |
|--------|------|--------|-----------|
| BM25 | algorithm | active | Sparse retrieval, TF-IDF variant, industry baseline |
| HNSW | algorithm | active | Approximate nearest neighbor (ANN), used by FAISS/pgvector |
| Reciprocal Rank Fusion | algorithm | active | Merge dense+sparse results, no tuning needed, RRF(k=60) |
| ColBERT | algorithm | active | Late interaction, token-level matching, higher recall than bi-encoder |
| HyDE | technique | active | Hypothetical Document Embeddings, improves zero-shot retrieval |

---

## Update Protocol

When a new entity is encountered:
1. Determine type: framework | service | library | model | algorithm | database
2. Verify the entity is stable (>= 6 months active, not experimental)
3. Add row to appropriate table above
4. Commit: `[N04] entity_memory: add {entity_name}`

When entity status changes:
- Deprecated: update status column, add "superseded_by" note in Key Facts
- Acquired: update status to "acquired by {company}" if major
- Discontinued: update status to "inactive", date in Key Facts

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[p10_bi_bm25_knowledge]] | sibling | 0.35 |
| [[kc_knowledge_vocabulary]] | upstream | 0.30 |
| [[agent_card_n04]] | upstream | 0.28 |
