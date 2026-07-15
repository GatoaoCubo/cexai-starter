---
id: p01_retr_knowledge_n04
title: "Retriever Config Knowledge"
kind: retriever_config
8f: F3_inject
pillar: P01
version: "2.0.0"
created: "2024-03-30"
updated: "2024-03-30"
author: "N04 Knowledge Nucleus"
name: "N04 Default Vector Retriever"
store_type: "vector_db"
search_type: "similarity"
top_k: 5
score_threshold: 0.75
quality: null
tags: [retriever, config, n04, knowledge, rag, p01]
tldr: "Defines the default vector similarity search retriever for N04, configured with a top_k of 5 and a score threshold of 0.75."
keywords: [retriever config knowledge, retriever, config, knowledge, search_type, similarity, vector_db, distance_metric, embedding_config, store_type]
density_score: 0.94
related:
  - p01_retriever_config
  - retriever-builder
  - bld_architecture_retriever
  - p01_kc_retriever
  - n00_retriever_manifest
slots:
  query_text: "<the retrieval query>"
  top_k: "<how many results to return>"
---

# N04 Retriever Configuration

## 1. Overview
Primary retriever for N04 Knowledge Nucleus in RAG pipeline. Fetches relevant context from vector database to augment LLM prompts.

| Aspect | Current | Performance | Use When |
| :--- | :--- | :--- | :--- |
| **Strategy** | Vector similarity | 85% accuracy, <100ms | General knowledge queries |
| **Context Size** | 5 chunks | ~2000 tokens | Balanced coverage without noise |
| **Quality Filter** | 0.75 threshold | Blocks 30% low-quality results | Need high relevance |
| **Latency** | Single-pass | Fast retrieval | Real-time applications |

## 2. Primary Strategy: Vector Similarity Search
The default retrieval strategy is a straightforward vector similarity search.

- **`search_type`**: `similarity`
- **Description**: This method takes the vector embedding of a user's query and searches the `vector_db` for the vectors (and their associated text chunks) that are most similar, based on the `distance_metric` defined in the `embedding_config` (typically Cosine Similarity).

### Parameters
| Parameter | Value | Rationale |
| :--- | :--- | :--- |
| **`store_type`** | `vector_db` | Specifies that the retriever will query the dedicated Vector DB MCP. |
| **`search_type`** | `similarity` | The standard and most effective method for general queries. |
| **`top_k`** | `5` | Retrieves the top 5 most similar chunks. This provides a good balance between sufficient context and minimizing noise or exceeding the LLM's context window. |
| **`score_threshold`** | `0.75`| Chunks with a similarity score below this threshold will be discarded. This prevents low-relevance documents from being passed to the LLM. |

## 3. Advanced & Future Strategies
While similarity search is the default, N04's architecture anticipates more sophisticated retrieval methods for specific use cases. These will be implemented as alternative configurations for the `semantic_search` tool.

### 3.1. Parent Document Retriever
- **Description**: Retrieves small, precise chunks for similarity matching but provides the LLM with the larger "parent" chunk (e.g., the whole section or document) from which the small chunk was derived.
- **Use Case**: When the answer is likely to span multiple, related paragraphs. It balances precision in search with completeness in context.

### 3.2. Self-Querying Retriever
- **Description**: Uses an LLM to parse a user's natural language query into a structured query that includes both semantic (vector) search components and metadata filters.
- **Use Case**: For complex queries like "What are the chunking strategies mentioned in documents tagged 'p01' but not 'archive'?" The LLM generates the metadata filter (`tags: ['p01']`, `NOT tags: ['archive']`) itself.

### 3.3. Ensemble & Reranking
- **Description**: A multi-stage process:
  1.  **Retrieve**: Fetch a large number of initial candidates (`fetch_k: 50`) using a fast but less precise method (e.g., similarity search).
  2.  **Rerank**: Use a more powerful but slower model (like a cross-encoder) to rerank only the top candidates and select the final `top_k`.
- **Use Case**: For "golden tier" applications where the highest possible accuracy is required, and a slight increase in latency is acceptable.

## 4. Integration
This configuration is the default parameter set for the `semantic_search` tool. The N04 agent can override these parameters for specific queries or choose an alternative strategy (once implemented) to optimize retrieval for a given task.


### How to use

```text
You are the consuming agent that acts on this retriever_config under F3 INJECT.
- Resolve the open slots (query_text, top_k) from the caller request.
- Honor every constraint and field contract declared above.
- Emit the result in the shape this retriever_config defines; never improvise the schema.
```

### Procedure

```text
1. Load this artifact and read its contract under F3 INJECT.
2. Bind query_text and top_k from the incoming request.
3. Validate the inputs against the constraints declared above.
4. Execute the retriever_config behavior; resolve each open slot at act-time.
5. Verify the output shape, then signal completion to the orchestrator.
```

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| p01_retriever_config | sibling | 0.36 |
| [[retriever-builder]] | related | 0.36 |
| [[bld_architecture_retriever]] | related | 0.34 |
| [[p01_kc_retriever]] | related | 0.33 |
| n00_retriever_manifest | related | 0.33 |
