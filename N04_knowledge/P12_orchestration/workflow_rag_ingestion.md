---
id: p12_wf_rag_ingestion_n04
kind: workflow
8f: F8_collaborate
pillar: P12
nucleus: n04
title: "Workflow -- RAG Corpus Ingestion Pipeline"
version: "1.0.0"
quality: null
tags: [workflow, n04, rag, ingestion, corpus, embedding, indexing, P12]
domain: knowledge management
status: active
created: "2026-07-20"
updated: "2026-07-20"
author: n04_knowledge
tldr: "End-to-end RAG corpus ingestion workflow: source identification -> document loading -> chunking -> embedding -> index rebuild -> verification. Includes error handling and a scheduled-run table."
keywords: [knowledge management, source identification, document loading, index rebuild, includes error handling, workflow, ingestion]
density_score: null
related:
  - p04_loader_n04_knowledge
  - p06_td_document_types
  - p09_rl_n04
  - p10_bi_bm25_knowledge
---

# Workflow: RAG Corpus Ingestion Pipeline

## Overview

This workflow governs how external knowledge enters the semantic corpus. It
is the WRITE side of the read pipeline the retriever serves.

**Trigger**: new documents available, scheduled refresh, or manual ingestion command
**Output**: documents indexed, TF-IDF index rebuilt, integrity verified

---

## Workflow Steps

```
SOURCE IDENTIFICATION
       |
       v
DOCUMENT LOADING (document_loader_n04.md)
       |
       v
QUALITY FILTERING
       |
       v
CHUNKING (chunk_strategy_knowledge.md)
       |
       v
METADATA ENRICHMENT
       |
       v
EMBEDDING GENERATION
       |
       v
DEDUPLICATION CHECK
       |
       v
INDEX REBUILD
       |
       v
POST-INGESTION VERIFICATION
       |
       v
LOG + COMMIT
```

---

## Step Details

### Step 1: Source Identification

Determine source type and corpus namespace:

| Source | Type | Corpus | Trust Level |
|--------|------|--------|-------------|
| Typed `.md` artifacts | markdown | cex_artifacts | 5 |
| External documentation | html/pdf | external_docs | 3 |
| Research papers | pdf | external_docs | 4 |
| User-uploaded files | varies | external_docs | 3 (default) |

### Step 2: Document Loading

Apply `document_loader_n04.md` per source type (see its Per-Format Pipeline
section for the loader functions).

### Step 3: Quality Filtering

Reject documents below quality thresholds:
- PDF: OCR artifact ratio <= 5%
- HTML: text/html ratio >= 0.3 (not mostly markup)
- Markdown: frontmatter must parse without error
- All: min_length = 100 characters

### Step 4: Chunking

Per `chunk_strategy_knowledge.md`:

| Document Type | Strategy | Size | Overlap |
|-------------|---------|------|---------|
| KnowledgeCard | whole document | N/A | N/A |
| ContextDoc | heading-based | 1024 tokens | 0 |
| PDF/HTML/DOCX | sliding window | 512 tokens | 128 tokens |
| Code | function-level | variable | 0 |

### Step 5: Metadata Enrichment

Add: `ingestion_date`, `corpus`, `trust_level`, `token_count`, `language`, `embedding_model`

### Step 6: Embedding Generation (if a dense layer is configured)

```python
embeddings = embedding_client.create(
    model="text-embedding-3-small",
    input=[chunk.content for chunk in chunks]
)
```

This starter ships sparse (TF-IDF) retrieval by default -- see
`p04_retr_n04_knowledge.md`. Embedding generation only applies if you have
wired in a dense layer; treat this step as an extension point, not a
guaranteed part of every ingestion run.

### Step 7: Deduplication Check

Before indexing, check for near-duplicate content against the existing
corpus (exact-match or high lexical overlap). If a near-exact duplicate is
found, skip re-indexing that chunk and log the dedup event instead.

### Step 8: Index Rebuild

```bash
python _tools/cex_retriever.py --build
```

This is the real, complete indexing command this starter ships -- confirm
with `--help` before assuming a narrower "add one document" flag exists.

### Step 9: Post-Ingestion Verification

Verify the just-ingested content is retrievable:
```bash
python _tools/cex_retriever.py --query "{representative_query_from_ingested_content}" --top-k 10
```

PASS: at least 1 result from the ingested batch appears in the top-10.
FAIL: ingestion failed silently -- check the load and index-build logs.

### Step 10: Log + Commit

```bash
# Log ingestion event
echo "{date} | {source} | {n_docs} docs | {corpus}" \
  >> N04_knowledge/P05_output/ingestion_log.md

# Commit
git add N04_knowledge/ && \
git commit -m "[N04] ingest: {n_docs} docs from {source} to {corpus}"
```

---

## Error Handling

| Error | Step | Recovery |
|-------|------|---------|
| Low OCR quality | 3 | Skip document, log to `P07_evals/` |
| Embedding API rate limit | 6 | Exponential backoff (1s, 2s, 4s) -- see `p09_rl_n04.md` |
| Dedup threshold exceeded | 7 | Skip re-index, log duplicate pair |
| Verification fails | 9 | Alert: check step 8 index-build logs, re-run |

---

## Scheduled Runs

| Trigger | Source | Corpus |
|---------|--------|--------|
| After a compile-all pass | N04_knowledge/ | cex_artifacts |
| Weekly cron | All nuclei | cex_artifacts |
| Manual trigger | Any | Any |

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[p04_loader_n04_knowledge]] | upstream | 0.40 |
| [[p06_td_document_types]] | upstream | 0.32 |
| [[p09_rl_n04]] | sibling | 0.28 |
| [[p10_bi_bm25_knowledge]] | downstream | 0.30 |
