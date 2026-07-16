---
kind: knowledge_card
id: bld_knowledge_card_agent_grounding_record
pillar: P01
llm_function: INJECT
purpose: "Domain knowledge reference for OTel GenAI semconv, C2PA, and per-inference prove"
quality: null
title: "Agent Grounding Record -- Knowledge Card"
version: "1.0.0"
author: wave7_n05
tags: [agent_grounding_record, builder, knowledge_card]
tldr: "OTel v1.37+ GenAI semconv + C2PA v2.3 AI-ML guidance + EU AI Act provenance requirements -- complete domain reference"
domain: "agent_grounding_record construction"
created: "2026-04-14"
updated: "2026-04-14"
8f: "F3_inject"
keywords: [and per-inference provenance standards, agent_grounding_record construction, otel v, genai semconv, ai-ml guidance, agent_grounding_record, builder]
density_score: 0.85
related:
  - bld_manifest_agent_grounding_record
  - kc_agent_grounding_record
  - bld_instruction_agent_grounding_record
  - bld_architecture_agent_grounding_record
  - bld_collaboration_agent_grounding_record
---
# Agent Grounding Record -- Knowledge Card
## Domain Overview
Per-inference provenance is the practice of recording, for each AI inference run, the exact sources and transformations that produced the output. This enables:
1. **Auditability**: Regulators and downstream consumers can verify AI outputs against their stated sources.
2. **EU AI Act compliance**: Article 9 (risk management) and Article 72 (post-market-monitoring) require traceability of high-risk AI system outputs.
3. **Content authenticity**: C2PA content credentials allow consumers to verify the provenance of AI-generated content.
4. **Observability**: OTel GenAI semantic conventions standardize how AI inference is instrumented for distributed tracing.
The grounding record is the per-inference artifact that binds these four concerns into a single, structured, machine-verifiable document.
## Key Concepts
| Concept               | Definition                                                                                             | CEX Field          |
|-----------------------|--------------------------------------------------------------------------------------------------------|--------------------|
| grounding             | The act of anchoring an AI output claim to a traceable external source (RAG chunk or tool result)      | rag_chunks, tool_calls |
| provenance            | The documented origin and transformation history of an AI output                                       | Full record structure |
| per-inference         | One record per inference run; not aggregated across sessions or turns                                  | inference_id        |
| tool-call trace       | Log of every external tool invoked during an inference run, including inputs and outputs               | tool_calls array    |
| RAG-chunk             | A retrieved text segment from a knowledge source used to augment the model's context                   | rag_chunks array    |
| model-signature       | A cryptographic attestation of the model identity, issued by the model provider                        | model.model-signature |
## Industry Standards
| Standard                          | Version     | Relevance                                                                              |
|-----------------------------------|-------------|----------------------------------------------------------------------------------------|
| OTel GenAI Semantic Conventions   | v1.37+ (WG) | Defines span attributes for AI inference: model ID, input tokens, output tokens, tool calls |
| C2PA (Coalition for Content Provenance) | v2.3 | AI-ML guidance: content credentials for AI-generated outputs, model assertions        |
| SHA-256 (FIPS 180-4)              | FIPS 180-4  | Hash standard for output_hash, content_hash, tool input/output hashes                 |
| ISO 8601                          | 2019        | Timestamp format for all time fields                                                   |
| W3C Provenance (PROV-DM)          | 2013        | Conceptual model for provenance: entities, activities, agents                          |
| W3C Trace Context                 | Level 2     | Defines traceparent header format; otel_span_id follows W3C 16-hex-char format         |
| EU AI Act                         | 2024/1689   | Articles 9 + 72 + 73: risk management + post-market-monitoring + incident reporting    |
## OTel GenAI Semantic Conventions -- Key Attributes
The grounding record maps to OTel GenAI semconv attributes. When instrumenting the inference pipeline, these OTel attributes SHOULD be captured and referenced in the grounding record.
| OTel Attribute                     | Type   | Grounding Record Field      | Notes                                              |
|------------------------------------|--------|-----------------------------|----------------------------------------------------|
| gen_ai.system                      | string | model.provider              | "anthropic", "openai", "google", etc.              |
| gen_ai.request.model               | string | model.id                    | Requested model identifier                         |
| gen_ai.response.model              | string | model.id (prefer this)      | Actual model that responded (may differ from request) |
| gen_ai.operation.name              | string | -- (context only)           | "chat", "completions", "embeddings"                |
| gen_ai.usage.input_tokens          | int    | -- (optional extension)     | Input token count                                  |
| gen_ai.usage.output_tokens         | int    | -- (optional extension)     | Output token count                                 |
The OTel span identified by `otel_span_id` SHOULD contain these attributes. The grounding record is a STRUCTURED PROVENANCE LAYER built on top of the raw OTel span -- it is not a replacement for OTel instrumentation.

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[bld_manifest_agent_grounding_record]] | downstream | 0.51 |
| [[kc_agent_grounding_record]] | sibling | 0.43 |
| [[bld_instruction_agent_grounding_record]] | downstream | 0.42 |
| [[bld_architecture_agent_grounding_record]] | downstream | 0.42 |
| [[bld_collaboration_agent_grounding_record]] | downstream | 0.39 |
