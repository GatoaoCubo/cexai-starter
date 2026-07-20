---
id: kc_query_optimizer
kind: knowledge_card
8f: F3_inject
title: Query Optimizer -- RAG Query Rewriting and Decomposition
version: 1.0.0
quality: null
pillar: P01
tags:
  - query-rewriting
  - rag
  - retrieval
  - decomposition
  - P01
tldr: "RAG query rewriting and decomposition strategies like HyDE, expansion, multi-hop, and routing"
when_to_use: "When user queries underperform in retrieval due to vocabulary mismatch or query complexity"
keywords: [hyde, hypothetical document embedding, query expansion, multi-hop decomposition, sub-query planning, vector similarity, vocabulary mismatch, semantic layer]
related:
  - bld_knowledge_query_optimizer
  - bld_orchestration_query_optimizer
  - query-optimizer-builder
  - bld_architecture_query_optimizer
  - bld_feedback_query_optimizer
density_score: 0.94
updated: "2026-05-27"
---

# Query Optimizer

A query optimizer transforms user queries into forms that maximize retrieval quality in RAG systems. The user's raw question is almost never the optimal retrieval query -- it may be ambiguous, use different vocabulary than the corpus, require multiple sub-queries, or need a hypothetical answer to find the right documents.

## Description

The gap between what the user asks and what the retriever needs is the query optimization problem. A user asking "why is my API slow?" needs the retriever to search for terms like "latency," "rate limiting," "connection pooling," and "timeout configuration" -- none of which appear in the original query.

Query optimization operates at the semantic layer between user intent and vector similarity. It bridges the vocabulary mismatch problem (the user's words differ from the corpus's words), the specificity problem (the query is too broad or too narrow), and the complexity problem (the query requires multiple retrievals that must be composed).

This is distinct from search_strategy (which defines the retrieval algorithm -- dense, sparse, hybrid) and from prompt_optimizer (which tunes the LLM's generation prompt, not the retrieval query). Query optimization sits between the user and the retriever; prompt optimization sits between the retriever and the generator.

## Key Concepts

| Concept | Definition | When to Use |
|---------|-----------|-------------|
| HyDE (Hypothetical Document Embedding) | Generate a hypothetical answer, embed it, use it as the query vector | When user queries are short and the corpus uses technical language |
| Query Expansion | Add synonyms, related terms, and domain vocabulary to the query | When vocabulary mismatch is the primary failure mode |
| Multi-hop Decomposition | Break a complex question into sequential sub-questions | When the answer requires combining facts from multiple documents |
| Sub-query Planning | Identify independent information needs and retrieve for each | When the question contains multiple implicit constraints |
| Query Routing | Classify the query type and route to specialized retrieval pipelines | When the corpus has heterogeneous sections (code, docs, tables) |
| Step-back Prompting | Rephrase the query at a higher abstraction level before retrieval | When the specific query is too narrow to find relevant context |
| Reciprocal Rank Fusion | Combine results from multiple query variants using rank-based scoring | When no single query formulation reliably finds all relevant docs |
| Query Classification | Determine query type (factoid, comparison, how-to, diagnostic) | When different query types need different retrieval strategies |

## Related Kinds

| Kind | Pillar | Relationship |
|------|--------|-------------|
| search_strategy | P01 | Sibling -- search_strategy defines how to search; query_optimizer defines what to search for |
| prompt_optimizer | P03 | Sibling -- prompt_optimizer tunes generation prompts; query_optimizer tunes retrieval queries |
| retriever_config | P01 | Downstream -- the retriever executes the optimized query |
| rag_source | P01 | Upstream -- the corpus determines which optimization strategies are effective |
| retrieval_evaluator | P07 | Downstream -- measures whether optimization improved retrieval quality |
| chunk_strategy | P01 | Upstream -- chunk boundaries affect what queries can retrieve |
| embedding_config | P01 | Constraint -- the embedding space determines how queries are matched |

## Anti-Patterns

- **Rewriting every query**: Simple, specific queries ("what is the max_tokens parameter?") do not need rewriting. Unnecessary rewriting adds latency and can introduce drift from the user's intent.
- **HyDE without validation**: Generating a hypothetical answer that is factually wrong, then using it as the retrieval query. The retriever finds documents that match the wrong answer. Always validate HyDE outputs against basic consistency checks.
- **Infinite decomposition**: Breaking every query into sub-queries regardless of complexity. A single-fact question decomposed into 5 sub-queries wastes retrieval budget and produces redundant results.
- **Ignoring query routing**: Sending all queries through the same pipeline. Code questions, conceptual questions, and diagnostic questions need different retrieval strategies and chunk sizes.
- **No fallback to original**: Rewriting the query and discarding the original. If the rewritten query finds nothing, the original query should be tried as a fallback. Use reciprocal rank fusion to combine results from both.
- **Optimizing query without measuring retrieval**: Applying sophisticated rewriting without measuring whether MRR, NDCG, or recall@k actually improved. Complexity without measurement is cargo-culting.

## How to use

```text
ROLE: you are improving retrieval quality between a user query and a RAG corpus.
1. Diagnose the failure mode: vocabulary mismatch, specificity, or complexity (see Description).
2. Select the matching strategy from Key Concepts (HyDE / expansion / decomposition / routing).
3. Do NOT rewrite simple specific queries; always keep the original as a fallback (RRF).
4. Measure MRR / NDCG / recall@k before and after -- complexity without measurement is cargo-culting.
Primary 8F verb: INJECT (this card grounds the F3 retrieval step; retriever_config executes the query).
```

## Properties

| Property | Value |
|----------|-------|
| Kind | knowledge_card |
| Pillar | P01 |
| Domain | RAG query processing, information retrieval |
| Pipeline | 8F (F1-F8) |
| Quality target | 9.0+ |
| Density target | 0.85+ |

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[bld_knowledge_query_optimizer]] | sibling | 0.55 |
| [[bld_orchestration_query_optimizer]] | downstream | 0.51 |
| [[query-optimizer-builder]] | downstream | 0.50 |
| [[bld_architecture_query_optimizer]] | downstream | 0.43 |
| [[bld_feedback_query_optimizer]] | downstream | 0.40 |
