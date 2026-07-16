---
quality: null
id: p01_kc_langchain
kind: knowledge_card
8f: F3_inject
kc_type: industry_reference
pillar: P01
nucleus: n04
version: 1.0.0
created: "2026-05-05"
updated: "2026-05-05"
author: n04_knowledge
title: "LangChain -- Industry-Standard LLM Composition Framework"
domain: ai_agent_systems
subdomain: industry_reference
tags: [langchain, llm_framework, agent_executor, langgraph, langsmith, industry_reference, comparison]
tldr: "LangChain is the most adopted Python/JS framework for chaining LLM calls, tools, retrieval, and agent loops. Mature ecosystem with LangGraph (state machines), LangSmith (observability), and LCEL (declarative pipelines). CEXAI adopts the chain/tool/retriever vocabulary but rejects runtime-coupled state in favor of typed-artifact persistence."
keywords: [langchain, lcel, langgraph, langsmith, agent executor, tool calling, retriever, vector store, output parser, chain, runnable, callback, tracing]
density_score: 0.89
related:
  - p01_kc_crewai
  - p01_kc_dspy
---

# LangChain — Industry-Standard LLM Composition Framework

## Definition

LangChain is an open-source framework (Python and TypeScript) for building applications powered by large language models. Released October 2022 by Harrison Chase, it became the de-facto reference for "LLM apps" — chains of prompts, tools, retrievers, memory, and agent loops wired into a single runnable graph. The ecosystem has three layers today: **LangChain core** (composition primitives), **LangGraph** (stateful multi-actor workflows), and **LangSmith** (tracing, evaluation, observability).

## Key Concepts

| Primitive | Meaning | CEXAI analogue |
|-----------|---------|----------------|
| `Runnable` / LCEL | Declarative pipe-composable unit; `prompt | model | parser` | `chain` kind (P12) |
| `AgentExecutor` | Loop: model picks tool → tool runs → observation → repeat | `workflow` + `agent` |
| `Tool` | Callable with name/description/schema, invoked by LLM | `mcp_server`, `api_client`, `browser_tool` (P04) |
| `Retriever` | Returns documents for a query (BM25, dense, hybrid) | `retriever` kind (P10) |
| `VectorStore` | Embedding index (Chroma, Pinecone, FAISS, pgvector) | `vector_store` kind (P10) |
| `OutputParser` | Coerces LLM string into typed Python object | `output_validator`, `parser` (P05) |
| `Memory` | Conversation buffer / summary / entity memory | `working_memory`, `entity_memory`, `episodic_memory` (P10) |
| `Callback` | Hook into chain lifecycle for logging/tracing | `hook` kind + `trace_config` (P09) |
| `LangGraph` | Cyclic state graph with checkpointing and human-in-loop | `state_machine` + `dag` (P12) |
| `LangSmith` | Hosted tracing, dataset eval, prompt playground | `trace_config`, `eval_dataset`, `playground_config` |

## What CEXAI Adopts

1. **Vocabulary.** Chain, tool, retriever, vector store, output parser, callback, memory — these are now industry-canonical terms; CEXAI uses them in its taxonomy (P03/P04/P10) instead of inventing synonyms.
2. **Tool-calling protocol.** OpenAI-style `tool_calls` with JSON-Schema arguments is the substrate for the `mcp_server`, `api_client`, and `browser_tool` kinds.
3. **Retrieval-Augmented Generation (RAG) shape.** `query → retriever → top_k docs → prompt → model` is the canonical loop; CEXAI's `agentic_rag`, `chunk_strategy`, `embedding_config`, and `retriever_config` kinds slot directly into this shape.
4. **Tracing as first-class.** LangSmith proved that runs must be inspectable end-to-end. CEXAI's F8 COLLABORATE writes signals + lineage, and `trace_config` is a P09 kind.
5. **Streaming + async by default.** CEXAI inherits the assumption that all chains stream tokens and run async (see `streaming_config`).

## What CEXAI Differs

1. **Knowledge is typed artifacts, not Python objects.** LangChain state lives in process memory and is gone when the runtime dies. CEXAI persists every input/output as a frontmatter-tagged `.md` artifact, version-controlled in git. The chain *is* the file system.
2. **Pillar taxonomy over flat module imports.** LangChain has hundreds of integrations under `langchain.*`. CEXAI organizes the same surface area into 12 pillars (P01..P12) so that LLMs can reason about *where* a capability belongs (a retriever is always P10, never P04).
3. **Runtime-agnostic.** LangChain is Python/JS only. CEXAI runs the same artifacts under Claude, Codex, Gemini, and Ollama via prompt-compiled handoffs — no Python runtime required at the edge.
4. **8F pipeline replaces AgentExecutor.** Instead of an opaque `while not done: think → act` loop, CEXAI mandates F1 CONSTRAIN → F8 COLLABORATE for every artifact. Each step is auditable and gateable.
5. **Quality gates are mandatory and peer-scored.** LangChain ships, CEXAI gates. F7 GOVERN with H01-H06 universal hooks + kind-specific evals + COUNCIL cross-provider review is non-optional.
6. **No global registry of prompt strings.** LangChain Hub centralizes prompts as artifacts you pull. CEXAI ships them inside the repo as `prompt_template` + `system_prompt` + `instruction` kinds, owned by the brand, never fetched at runtime.

## When to Reach for LangChain Directly

Use LangChain when the task is: (a) a quick prototype that doesn't need typed persistence, (b) integration with a LangChain-only vendor (some embedding providers ship LangChain wrappers first), or (c) consuming LangSmith for hosted observability. For everything else inside CEXAI, prefer the native kinds — they compose, they version, they survive a runtime swap.

## Related Artifacts

| Artifact | Relationship |
|----------|-------------|
| [[p01_kc_crewai]] | sibling industry reference |
| [[p01_kc_dspy]] | sibling industry reference |
| p01_kc_8f_pipeline | replaces AgentExecutor |
