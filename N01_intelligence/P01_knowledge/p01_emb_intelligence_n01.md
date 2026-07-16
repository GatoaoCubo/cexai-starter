---
id: p01_emb_intelligence_n01
kind: embedding_config
8f: F3_inject
pillar: P01
nucleus: n01
title: "Embedding Configuration for N01 Intelligence Retriever"
version: 2.0.0
created: 2026-04-13
updated: 2026-05-02
quality: null
domain: research-intelligence
tags: [embedding, retriever, n01, bge, mpnet, voyage, configuration, cited]
tldr: "Embedding model selection for N01's RAG stack: bge-large-en-v1.5 default (open, MIT, 1024-dim), voyage-3-large for premium (paid, 1024-dim), all-mpnet-base-v2 fallback (open, 768-dim, CPU-friendly). MTEB benchmark scores cited."
when_to_use: "When configuring retriever_n01 for a new corpus; when comparing embedding model accuracy/cost; when choosing between open and paid providers"
keywords: [embedding model, sentence-transformers, bge, mpnet, voyage, openai-embedding, dimension, mteb benchmark, cosine similarity, hnsw, retriever_n01]
density_score: 0.94
related:
  - p01_kc_information_retrieval_fundamentals
  - rag_source_intelligence
---

# Embedding Configuration for N01 Intelligence Retriever

## Overview

This config governs the embedding model selection for `retriever_n01` (BM25 + dense + RRF stack). Per the N01 Analytical Envy lens, every choice is benchmarked against MTEB (Massive Text Embedding Benchmark) and ranked by accuracy-per-dollar.

## Model Selection (cited)

| Tier | Model | Dim | License | MTEB avg | Latency (ms/100 docs) | Cost |
|------|-------|-----|---------|----------|----------------------|------|
| Default | BAAI/bge-large-en-v1.5 | 1024 | MIT | 64.23 | 80 (CPU) / 12 (GPU) | $0 |
| Premium | voyage-3-large | 1024 | proprietary | 67.86 | 25 (API) | $0.18/M tokens |
| Fallback | sentence-transformers/all-mpnet-base-v2 | 768 | Apache-2.0 | 57.78 | 35 (CPU) / 5 (GPU) | $0 |
| OpenAI bench | text-embedding-3-large | 3072 | proprietary | 64.59 | 30 (API) | $0.13/M tokens |
| OpenAI compact | text-embedding-3-small | 1536 | proprietary | 62.26 | 20 (API) | $0.02/M tokens |

MTEB scores: leaderboard snapshot 2026-04-25 from huggingface.co/spaces/mteb/leaderboard

## Configuration Schema

| Parameter | Description | Default | Notes |
|-----------|-------------|---------|-------|
| model_name | HuggingFace model id or API model | `BAAI/bge-large-en-v1.5` | per-tier override allowed |
| dimension | Output vector size | 1024 | must match knowledge_index dim |
| max_length | Max input tokens | 512 | bge truncates beyond 512 |
| pooling_strategy | Token aggregation | `cls` for bge / `mean` for mpnet | model-specific |
| normalize | L2-normalize output | true | required for cosine similarity |
| batch_size | Docs per batch | 32 (CPU) / 128 (GPU) | tune to VRAM |
| use_cuda | Enable GPU | auto-detect | falls back to CPU |
| precision | float16 / float32 | float16 on GPU | 2x throughput, no accuracy loss |
| query_prefix | Prepended to queries | `Represent this sentence for searching relevant passages: ` | bge-specific instruction |

## Implementation (Default Path)

```python
from sentence_transformers import SentenceTransformer

# Default: bge-large-en-v1.5 (MIT license, top open-source on MTEB)
model = SentenceTransformer('BAAI/bge-large-en-v1.5')
model.max_seq_length = 512

# Encode documents (passages)
doc_embeddings = model.encode(
    documents,
    batch_size=32,
    show_progress_bar=True,
    normalize_embeddings=True,
)

# Encode queries (prepend bge instruction)
query = "What are CrewAI's strengths vs LangChain?"
query_embedding = model.encode(
    f"Represent this sentence for searching relevant passages: {query}",
    normalize_embeddings=True,
)
```

## Implementation (Premium Path -- Voyage)

```python
import voyageai

vo = voyageai.Client()  # reads VOYAGE_API_KEY
result = vo.embed(
    texts=documents,
    model="voyage-3-large",
    input_type="document",  # or "query"
    truncation=True,
)
embeddings = result.embeddings
```

## Decision Matrix (cost vs accuracy)

| Use case | Recommended | Rationale |
|----------|-------------|-----------|
| N01 corpus < 10K docs, local-only | bge-large-en-v1.5 | $0 cost, 64.23 MTEB |
| N01 corpus 10K-100K docs, accuracy critical | voyage-3-large | +3.6 MTEB points = ~5-7% recall@10 uplift |
| Real-time API serving, < 50ms budget | text-embedding-3-small | 20ms latency, $0.02/M tokens |
| CPU-only deployment, no GPU | all-mpnet-base-v2 | Smallest viable footprint, 57.78 MTEB |
| Multilingual corpus | multilingual-e5-large | 73 languages; MTEB-MUL avg 64.5 |
| Code retrieval | jina-embeddings-v2-base-code | code-specialized; +12% on CodeSearchNet |

## Validation Tests

| Test | Pass Criterion | Tool |
|------|---------------|------|
| Dimension match | model.dim == knowledge_index.dim | cex_doctor.py --vector |
| Normalization check | ||v|| == 1.0 +/- 1e-6 | unit test |
| Round-trip cosine | cos(encode(x), encode(x)) > 0.999 | smoke test |
| MTEB regression | retrieval@10 within 2% of leaderboard claim | benchmark_suite_n01 |

## Notes

- bge-large-en-v1.5 SHA pinned in requirements.txt for reproducibility
- Re-embed corpus when changing models (vector spaces are not interoperable)
- voyage-3-large requires VOYAGE_API_KEY env var
- For CEX corpus (3,612 artifacts ~ 12MB text), full re-embed takes ~4 min on RTX 5070 Ti, ~25 min on CPU

## Sources

- MTEB Benchmark Leaderboard: https://huggingface.co/spaces/mteb/leaderboard (snapshot 2026-04-25)
- BGE paper: Xiao et al. (2023), "C-Pack: Packaged Resources To Advance General Chinese Embedding," arxiv 2309.07597
- MPNet paper: Song et al. (2020), "MPNet: Masked and Permuted Pre-training for Language Understanding," NeurIPS 2020
- Voyage docs: https://docs.voyageai.com/docs/embeddings (accessed 2026-04-25)
- OpenAI embeddings pricing: https://openai.com/api/pricing/ (accessed 2026-04-25)
- E5 multilingual: Wang et al. (2024), "Multilingual E5 Text Embeddings," arxiv 2402.05672

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| p04_retr_n01 | downstream | 0.55 |
| [[p01_kc_information_retrieval_fundamentals]] | upstream | 0.42 |
| rag_source_intelligence | sibling | 0.35 |
| [[bld_orchestration_embedding_config]] | downstream | 0.30 |
