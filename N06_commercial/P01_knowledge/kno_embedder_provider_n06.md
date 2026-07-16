---
id: kno_embedder_provider_n06
kind: embedder_provider
8f: F3_inject
primary_8f: INJECT
pillar: P01
nucleus: n06
title: Commercial Embedder Provider
version: 1.0
quality: null
tags: [knowledge, embedder_provider, vectors, pricing, retrieval, monetization]
keywords: [commercial embedder provider, embedder_provider, vectors, pricing, retrieval, monetization, text-embedding-3-large, text-embedding-3-small, openai, cosine]
tldr: "N06's embedder_provider contract -- OpenAI text-embedding-3-large @ 1024d for revenue-adjacent semantic search -- so commercial nuance survives retrieval (INJECT)."
when_to_use: "Load when configuring embeddings for commercial corpora (pricing/objections/renewal). Consult for 'which embedder + dimensions to use for revenue-near retrieval'."
long_tails:
  - "which embedding model should N06 use for pricing and objection search"
  - "how do I tier embedder cost by revenue potential of the corpus"
slots:
  embedder_model: "text-embedding-3-large (premium) | text-embedding-3-small (fallback)"
  dimensions: "1024 (default) | reduced for low-value corpora"
  corpus_tier: "premium revenue-near | exploratory | archive"
density_score: 1.0
related:
  - kno_embedder_provider_n02
  - p01_chunk_n06
  - kno_vector_store_n06
  - kno_embedder_provider_n01
updated: "2026-05-27"
---
<!-- 8F: F1=P01/embedder_provider F2=embedder-provider-builder F3=nucleus_def_n06.md,kc_embedder_provider.md,P01_knowledge/_schema.yaml,N06 W1 config/schema F4=high_precision_embeddings_for_revenue_adjacent_semantic_search F5=apply_patch;python _tools/cex_compile.py F6=author_dense_markdown_artifact F7=frontmatter_ascii_density_linecount_review F8=N06_commercial/P01_knowledge/kno_embedder_provider_n06.md -->

# Commercial Embedder Provider

## How to use

You are an agent configuring retrieval for N06's commercial corpus. This is an `embedder_provider`; its 8F verb is **INJECT** -- it feeds the embedding contract into the index.

- Use the `Provider Contract` as the canonical config; never mix dimensions inside one collection.
- Apply the `Commercial Tuning Rules` (EP01-EP05) to pick large vs small per corpus value.
- Always normalize so cosine ranking stays reliable across segment-heavy text.
- Re-embed whenever the chunk strategy or model dimensions change.

## Inputs (act-time slots)

The consuming index binds these from the corpus + budget context (open boundary -- dependency inversion):

```yaml
slots:
  embedder_model: "text-embedding-3-large | text-embedding-3-small"
  dimensions: 1024
  corpus_tier: "premium | exploratory | archive"
  api_key_env: OPENAI_API_KEY
```

## Procedure

1. Tier the corpus by revenue potential (premium / exploratory / archive).
2. Pick the model per tier (large for premium, small for archive) via the tuning rules.
3. Set dimensions (1024 default) and pin them in the vector store + knowledge index.
4. Embed chunk text + promoted metadata; exclude secrets/ephemeral fields.
5. Cache by chunk-hash + model + dimension tuple; re-embed on chunk/model drift.

## Purpose

| Field | Value |
|-------|-------|
| Goal | Encode pricing, funnel, and retention text so commercial nuance survives semantic search |
| Business Lens | Strategic Greed pays for embedding quality only when better recall can move revenue |
| Primary Use | vector search over offers, objections, ICP signals, competitor pricing, and renewal plays |
| Failure Prevented | cheap embeddings that collapse intent differences between low-value curiosity and high-value buying intent |
| Provider Choice | OpenAI `text-embedding-3-large` with dimension reduction |
| Fallback | `text-embedding-3-small` for batch reindex under cost pressure |

## Provider Contract

| Setting | Value | Reason |
|---------|-------|--------|
| provider | `openai` | stable API, strong multilingual and domain retrieval quality |
| model | `text-embedding-3-large` | best semantic separation for pricing and persuasion language |
| dimensions | `1024` | trims storage cost while preserving commercial recall |
| max_input_tokens | `8191` | comfortably fits N06 chunk sizes with metadata wrappers |
| batch_size | `64` | balances throughput and retry cost |
| normalize | `true` | cosine similarity becomes reliable across segment-heavy text |
| api_key_env | `OPENAI_API_KEY` | existing env contract likely already supports this |

## Retrieval Fit

| Query Class | Why This Model Fits | Revenue Impact |
|-------------|---------------------|----------------|
| pricing comparison | catches semantic variants of tiering and packaging | better competitive response generation |
| objection matching | maps phrasing differences in buyer resistance | stronger rescue copy and sales prompts |
| expansion triggers | links usage pain to upsell moments | higher ARPU chance |
| renewal risk | retrieves save motions from mixed-language notes | protects retained revenue |
| ICP matching | finds segment-specific proof and outcomes | improves premium offer relevance |

## Commercial Tuning Rules

| Rule ID | Trigger | Action | Why |
|---------|---------|--------|-----|
| EP01 | full reindex on premium knowledge refresh | use large model | key pricing logic deserves max semantic fidelity |
| EP02 | nightly low-risk rebuild | use reduced dimensions only | saves cost without retraining prompts |
| EP03 | margin pressure exceeds threshold | switch to small model for exploratory corpora | budget should follow monetization probability |
| EP04 | enterprise proposal generation | force large-model query embeddings | enterprise retrieval errors are expensive |
| EP05 | broad competitor scraping import | queue with small model first, promote later | spend only after source proves strategic value |

## Data Handling Policy

| Field | Value | Commercial Intent |
|-------|-------|-------------------|
| embed_unit | chunk text plus bounded metadata | stage and segment metadata improve downstream filtering |
| excluded_fields | raw secrets, webhook refs, ephemeral counters | no value in embedding operational noise |
| promoted_fields | offer names, proof metrics, segment labels, objections | these fields are cash-proximate |
| cache_policy | stable hash by chunk body plus metadata subset | avoids paying twice for unchanged revenue knowledge |
| drift_policy | re-embed when chunk strategy or model dims change | protects similarity consistency |

## Cost Logic

| Situation | Embedder Choice | Justification |
|-----------|-----------------|---------------|
| premium pricing refresh | large 1024d | highest-value retrieval surface |
| bundle ideation sprint | large 1024d | nuanced offer adjacency matters |
| archive import | small reduced dims | low-confidence inputs do not deserve premium spend |
| smoke validation | small | enough to catch gross failures |
| enterprise rescue playbooks | large 1024d | one miss can cost more than the API bill |

## Rationale

| Design Choice | Why It Exists | Strategic Greed Impact |
|---------------|---------------|------------------------|
| Large model default | commercial language is subtle and high-leverage | improves precision where money is close |
| Reduced dimensions | brute-force dimension count is not sacred | lowers storage and query cost without abandoning quality |
| Strong fallback path | not all corpora deserve premium treatment | spend allocation stays rational |
| Normalization required | ranking errors compound into weak recommendations | protects retrieval trust |
| Metadata-aware embedding unit | plain text alone misses buying stage cues | improves commercial routing |

## Example

| Scenario | Result |
|----------|--------|
| N06 reindexes pricing pages, competitor battlecards, and renewal save plays before a launch | premium commercial corpus receives high-precision vectors with consistent 1024 dimensions |

```yaml
provider: openai
model: text-embedding-3-large
dimensions: 1024
batch_size: 64
normalize: true
api_key_env: OPENAI_API_KEY
fallback_model: text-embedding-3-small
```

## Risks and Guards

| Risk | Guard |
|------|-------|
| mixed dimensions in one collection | pin dimensions in vector store and knowledge index |
| runaway embedding spend | tier the corpus by revenue potential before reindex |
| stale vectors after chunk changes | enforce full refresh on chunk strategy revision |
| semantic dilution from noisy metadata | embed only monetization-relevant fields |

## Operating Notes

| Topic | Rule |
|-------|------|
| query embedding | use same provider family as document embeddings |
| multilingual text | keep original market phrasing; do not flatten all PT/EN nuance |
| cache invalidation | invalidate by chunk hash, model, and dimension tuple |
| emergency mode | degrade to small model only for low-value or bulk jobs |

## Properties

| Property | Value |
|----------|-------|
| Owner | N06 Commercial |
| Kind | `embedder_provider` |
| Default Provider | `openai` |
| Default Model | `text-embedding-3-large` |
| Default Dimensions | 1024 |
| Cost Posture | premium where revenue is near |
| Fallback Model | `text-embedding-3-small` |
| Related Artifacts | `kno_vector_store_n06`, `mem_knowledge_index_n06`, `kno_retriever_config_n06` |

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[kno_embedder_provider_n02]] | sibling | 0.46 |
| [[p01_chunk_n06]] | upstream | 0.39 |
| [[kno_vector_store_n06]] | related | 0.34 |
| [[kno_embedder_provider_n01]] | sibling | 0.34 |
