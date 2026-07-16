---
kind: schema
id: bld_schema_agent_grounding_record
pillar: P06
llm_function: CONSTRAIN
purpose: Field-level schema defining all required and optional fields for agent_grounding_record artifacts
quality: null
title: "Agent Grounding Record -- Schema"
version: "1.0.0"
author: wave7_n05
tags: [agent_grounding_record, builder, schema]
tldr: "Complete field schema: inference_id, model block, tool_calls array, rag_chunks array, output-hash, otel_span_id, C2PA ref"
domain: "agent_grounding_record construction"
created: "2026-04-14"
updated: "2026-04-14"
8f: "F1_constrain"
keywords: [agent_grounding_record construction, complete field schema, model block, tool_calls array, rag_chunks array, pa ref, agent_grounding_record]
density_score: 0.85
related:
  - bld_schema_multimodal_prompt
  - bld_schema_usage_report
  - bld_schema_reranker_config
  - bld_schema_dataset_card
  - bld_schema_pitch_deck
---
# Agent Grounding Record -- Schema
## Root Fields
| Field                  | Type    | Required | Format / Constraint                         | Description                                                   |
|------------------------|---------|----------|---------------------------------------------|---------------------------------------------------------------|
| inference_id           | string  | YES      | UUIDv4 (8-4-4-4-12 hex)                    | Unique ID for this inference run -- never reused              |
| session_id             | string  | NO       | Arbitrary string                            | Parent session ID if part of multi-turn conversation          |
| timestamp              | string  | YES      | ISO 8601 with timezone (e.g. 2026-04-14T15:30:00Z) | Start time of the inference run                    |
| downstream_use         | string  | YES      | Enum: production / test / eval              | Intended use of the output -- drives post-market monitoring   |
| grounding_coverage_pct | float   | YES      | 0.0 to 1.0 inclusive                        | Fraction of output claims with traceable grounding source     |
| output_hash            | string  | YES      | SHA-256 hex (64 lowercase hex chars)        | Hash of raw model output bytes before post-processing        |
## Model Object
Nested under `model:` key.
| Field          | Type   | Required | Format / Constraint        | Description                                                          |
|----------------|--------|----------|----------------------------|----------------------------------------------------------------------|
| id             | string | YES      | Exact model identifier     | Provider-assigned model ID (e.g. claude-sonnet-4-6)                |
| version        | string | NO       | Semver or checkpoint hash  | Model version; omit only if provider does not expose it             |
| provider       | string | YES      | Enum: anthropic / openai / google / azure / self-hosted | Model provider                        |
| model-signature| string | NO       | Cryptographic hash or attestation URI | Provider attestation of model identity; null if unavailable |
## tool_calls Array
Each element represents one tool invocation. Empty array [] if no tools were called.
| Field             | Type    | Required | Format / Constraint                  | Description                                              |
|-------------------|---------|----------|--------------------------------------|----------------------------------------------------------|
| tool_name         | string  | YES      | Registered tool name                 | Exact name as registered in the tool registry            |
| tool_input_hash   | string  | YES      | SHA-256 hex (64 chars)               | Hash of the serialized tool input payload                |
| tool_output_hash  | string  | YES      | SHA-256 hex (64 chars)               | Hash of the serialized tool output payload               |
| duration_ms       | integer | YES      | Non-negative integer                 | Wall-clock milliseconds from invocation to response      |
| timestamp         | string  | YES      | ISO 8601 with timezone               | Time the tool was invoked (not session start)            |
| status            | string  | YES      | Enum: success / error                | Outcome of the tool call                                 |
| error_code        | string  | NO       | String                               | Error code if status = error; omit on success            |
## rag_chunks Array
Each element represents one retrieved chunk. Empty array [] if no RAG was used.
| Field            | Type   | Required | Format / Constraint          | Description                                                        |
|------------------|--------|----------|------------------------------|--------------------------------------------------------------------|
| chunk_id         | string | YES      | Unique chunk identifier      | ID from the vector store or document store                         |
| source_url       | string | YES      | Full URL or internal path    | NEVER null or "unknown" -- reject chunk if source cannot be traced |
| retrieval_score  | float  | YES      | 0.0 to 1.0                   | Cosine similarity or BM25 score at retrieval time                  |
| content_hash     | string | YES      | SHA-256 hex (64 chars)       | Hash of chunk text at retrieval time (not current state)           |

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[bld_schema_multimodal_prompt]] | sibling | 0.50 |
| [[bld_schema_usage_report]] | sibling | 0.49 |
| [[bld_schema_reranker_config]] | sibling | 0.48 |
| [[bld_schema_dataset_card]] | sibling | 0.48 |
| [[bld_schema_pitch_deck]] | sibling | 0.48 |
