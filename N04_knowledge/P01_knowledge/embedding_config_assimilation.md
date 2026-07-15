---
id: p01_emb_assimilation_n04
kind: embedding_config
8f: F3_inject
pillar: P01
version: "1.0.0"
created: "2026-05-29"
updated: "2026-05-29"
author: n04_knowledge
title: "Assimilation Embedding Config"
model: all-MiniLM-L6-v2
provider: local
dimensions: 384
chunk_size: 1024
chunk_overlap: 200
tokenizer: bert-wordpiece
distance_metric: cosine
batch_size: 32
normalize: true
max_tokens: 512
cost_per_1m_tokens: null
domain: "assimilation-engine"
quality: null
tags: [embedding, embedding_config, n04, assimilation, offline, sovereign, local, P01]
tldr: "DEEP-path embed profile: dense vectors with NO API key. Local model (all-MiniLM-L6-v2, 384d) preferred, degrade-never to a deterministic hashing floor. Read by cex_embedder + cex_distill_orchestrator --depth deep."
keywords: [embedding, offline, all-MiniLM-L6-v2, hashing fallback, cosine, sovereign, deep distill, degrade-never]
density_score: null
related:
  - n04_rs_assimilation
  - p01_chunk_assimilation_n04
  - p01_retr_assimilation_n04
  - n04_vdb_assimilation
  - embedding-config-builder
  - p11_qg_embedding_config
---

# Assimilation Embedding Config

## Boundary
This configures the EMBEDDING MODEL for the DEEP distill path -- NOT the index
(that is [[n04_vdb_assimilation]] vector_store) and NOT search params (that is
[[p01_retr_assimilation_n04]] retriever_config). It governs `cex_embedder.py`, which
`cex_distill_orchestrator.py --depth deep` calls to turn chunks into dense vectors.
LIGHT distill never reads this: it stays TF-IDF (sparse) and is the default.

## Model (sovereign ladder, degrade-never -- D3 offline)
The embedder resolves ONE backend at runtime; ALL produce vectors with NO API key:
1. **ollama** (local daemon) -- nomic-embed-text / mxbai-embed-large if present.
2. **all-MiniLM-L6-v2** (sentence-transformers, 384d) -- the documented default;
   offline once cached.
3. **hashing floor** -- deterministic feature-hashing at `dimensions` (384), pure
   stdlib. ALWAYS returns vectors: no model, no network, no key.
A cloud **provider** (OpenAI/Voyage) is an OPTIONAL opt-in tier behind an env key,
never required.

## Chunking
Inherits the [[p01_chunk_assimilation_n04]] chunk_strategy: `heading_based`, `chunk_size`
1024 chars, `chunk_overlap` 200 (< chunk_size, H08-safe). One vector per chunk.

## Performance
- Cost: zero (local/offline); `cost_per_1m_tokens: null`.
- Vectors are L2-normalized -> `cosine` is the correct `distance_metric`.
- The hashing floor is O(tokens) and dependency-free; the local model adds quality
  when available without changing the contract (same `dimensions`, same metric).

## Integration
```python
from cex_embedder import get_embedder
emb = get_embedder(dim=384)          # resolves the best offline backend
vectors = emb.embed(chunk_texts)     # feeds the vector_store flat index
```
Downstream: vectors land in [[n04_vdb_assimilation]] (the realized index lives in
the run's out_dir, sandbox); recall is governed by [[p01_retr_assimilation_n04]].

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[n04_vdb_assimilation]] | downstream | 0.42 |
| [[n04_rs_assimilation]] | upstream | 0.38 |
| [[p01_chunk_assimilation_n04]] | sibling | 0.34 |
| [[p01_retr_assimilation_n04]] | sibling | 0.33 |
| [[embedding-config-builder]] | related | 0.26 |
| [[p11_qg_embedding_config]] | related | 0.24 |
