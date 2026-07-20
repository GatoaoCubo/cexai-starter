---
id: p06_is_knowledge_query
kind: input_schema
8f: F1_constrain
pillar: P06
nucleus: n04
title: "Input Schema -- Knowledge Query Contract"
version: "1.0.0"
quality: null
tags: [input_schema, knowledge_query, rag, retrieval, n04, P06]
domain: knowledge retrieval
status: active
created: "2026-07-20"
updated: "2026-07-20"
author: n04_knowledge
tldr: "Typed contract for every knowledge query request entering the retrieval pipeline: query text, corpus scope, filters, and output format."
keywords: [knowledge retrieval, retrieval pipeline, query text, corpus scope, output format, input_schema, knowledge_query, retrieval, query_text]
density_score: null
related:
  - p06_td_document_types
  - p04_loader_n04_knowledge
  - p04_retr_n04_knowledge
slots:
  query_payload: "<the request the caller submits>"
  required_fields: "<fields the caller must provide>"
---

# Input Schema: Knowledge Query Contract

## Purpose

Every retrieval request hitting the pipeline MUST conform to this contract.
Untyped queries lead to retrieval ambiguity, wrong corpus selection, and
hallucinated context. This schema prevents those failure modes at the boundary.

## Fields

| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `query_text` | string | YES | -- | Natural language query or structured search string |
| `corpus` | enum | YES | -- | Target corpus: `cex_artifacts`, `brand_knowledge`, `external_docs`, `all` |
| `retrieval_mode` | enum | NO | `sparse` | `sparse`, `dense` (dense requires an extension -- see `p04_retr_n04_knowledge.md`) |
| `top_k` | integer | NO | `10` | Max number of documents to retrieve |
| `score_threshold` | float | NO | `0.05` | Minimum similarity score to include a result |
| `filters` | object | NO | `{}` | Key-value metadata filters: kind, pillar, nucleus, domain |
| `output_format` | enum | NO | `passages` | `passages`, `summaries`, `full_docs`, `citations_only` |
| `max_tokens` | integer | NO | `4096` | Maximum total tokens in retrieved context |
| `include_metadata` | boolean | NO | `true` | Include source path, score, and kind in response |

## Validation Rules

| Field | Rule |
|-------|------|
| `query_text` | min_length=3, max_length=2048, must not be empty string |
| `corpus` | enum: `cex_artifacts`, `brand_knowledge`, `external_docs`, `all` |
| `retrieval_mode` | enum: `sparse`, `dense` |
| `top_k` | integer, range 1-100 |
| `score_threshold` | float, range 0.0-1.0 |
| `filters.kind` | must match a kind in kinds_meta.json if provided |
| `filters.pillar` | must match P01-P12 pattern if provided |
| `output_format` | enum: `passages`, `summaries`, `full_docs`, `citations_only` |
| `max_tokens` | integer, range 128-200000 |

## Coercion Rules

| Condition | Behavior |
|-----------|----------|
| `query_text` is empty | Raise `QueryEmptyError` |
| `top_k` > 100 | Clamp to 100, log warning |
| `score_threshold` outside 0.0-1.0 | Clamp to range |
| `filters.kind` not in taxonomy | Drop filter, log warning |
| `retrieval_mode` = `dense` and no dense layer configured | Fallback to `sparse` |
| `corpus` = `all` | Query all corpora, merge results by score |
| `max_tokens` > 200000 | Clamp to 200000 (context window safety) |

## Error Messages

| Field | Error | Message |
|-------|-------|---------|
| `query_text` | `QueryEmptyError` | "query_text must be a non-empty string of at least 3 characters" |
| `corpus` | `InvalidCorpusError` | "corpus must be one of: cex_artifacts, brand_knowledge, external_docs, all" |
| `retrieval_mode` | `InvalidModeError` | "retrieval_mode must be one of: sparse, dense" |
| `top_k` | `RangeError` | "top_k must be an integer between 1 and 100" |
| `filters.kind` | `UnknownKindWarning` | "Unknown kind filter dropped; check kinds_meta.json for valid kinds" |

## Examples

### Minimal query (required fields only)
```yaml
query_text: "how does the retrieval pipeline chunk long documents"
corpus: cex_artifacts
```

### Full query with filters
```yaml
query_text: "chunking strategy patterns for long-form documents"
corpus: cex_artifacts
retrieval_mode: sparse
top_k: 20
score_threshold: 0.10
filters:
  kind: knowledge_card
  pillar: P01
output_format: passages
max_tokens: 8192
include_metadata: true
```

### Citation-only query for source attribution
```yaml
query_text: "consolidation policy for memory systems"
corpus: cex_artifacts
output_format: citations_only
top_k: 5
include_metadata: true
```

## Constraints

| Constraint | Value |
|-----------|-------|
| Max fields in `filters` object | 10 |
| Max nesting depth | 2 (no nested objects in filters) |
| Max payload size | 16KB |
| `query_text` encoding | UTF-8 |
| Concurrent queries per session | 5 |

## Integration

This schema is the entry point for:
- `p04_retr_n04_knowledge.md` (P04) -- applies `retrieval_mode` from this schema
- `p04_loader_n04_knowledge.md` (P04) -- `corpus` field maps to loader targets
- `p06_td_document_types.md` (P06) -- the types this schema's results are shaped as

### How to use

```text
You are the consuming agent that acts on this input_schema under F1 CONSTRAIN.
- Resolve the open slots (query_payload, required_fields) from the caller request.
- Honor every constraint and field contract declared above.
- Emit the result in the shape this input_schema defines; never improvise the schema.
```

### Procedure

```text
1. Load this artifact and read its contract under F1 CONSTRAIN.
2. Bind query_payload and required_fields from the incoming request.
3. Validate the inputs against the constraints declared above.
4. Execute the input_schema behavior; resolve each open slot at act-time.
5. Verify the output shape, then signal completion to the orchestrator.
```

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[p06_td_document_types]] | sibling | 0.36 |
| [[p04_loader_n04_knowledge]] | downstream | 0.30 |
| [[p04_retr_n04_knowledge]] | downstream | 0.28 |
