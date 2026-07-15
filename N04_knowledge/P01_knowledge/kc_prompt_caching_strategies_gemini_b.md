---
id: p01_kc_prompt_caching_strategies_gemini_b
kind: knowledge_card
pillar: P01
title: Prompt Caching Strategies for LLM Applications
version: 1.0.0
quality: null
tags: [prompt-caching, optimization, cost-reduction, llm, infrastructure]
primary_8f: INJECT
slots:
  query_context: "<the question this card is recalled to answer>"
  target_audience: "<who consumes the answer>"
---

## Overview

Prompt caching is a critical optimization technique for LLM applications, designed to prevent redundant API calls by storing and reusing responses to identical or semantically similar prompts. This strategy is essential for managing operational costs and improving application responsiveness, often achieving typical cost reductions of 50-90% on cache hits.

## Cache Key Design

| Strategy        | Key Components                                           | Pros                                                | Cons                                                        |
| :-------------- | :------------------------------------------------------- | :-------------------------------------------------- | :---------------------------------------------------------- |
| Exact Match     | Full prompt string, user ID, model version               | Simple, guaranteed accuracy                         | Low hit rate for minor variations or parameter changes      |
| Prefix Match    | Fixed prompt prefix, variable suffix, model parameters | Higher hit rate than exact match for structured inputs | Still sensitive to suffix changes, may miss semantic matches |
| Semantic Hash   | Prompt embeddings, context embeddings, model parameters  | Captures semantic similarity, high hit rate         | Computationally intensive, requires embedding models, tuning |
| Template-Based  | Prompt template structure, key-value pairs for slots     | Robust for structured prompts, good for dynamic data  | Requires careful template design, struggles with unstructured |

## TTL Policies

| Policy      | TTL Range     | Best For                                        | Risk                                                                  |
| :---------- | :------------ | :---------------------------------------------- | :-------------------------------------------------------------------- |
| Aggressive  | 1-5 minutes   | Rapidly changing data, short-lived user sessions | Cache misses for slightly older but still valid information           |
| Moderate    | 5-30 minutes  | Frequently accessed but not real-time data      | Stale data if underlying facts change within the TTL period           |
| Conservative| 1 hour+       | Stable, infrequently changing factual data      | High risk of stale data, potentially infrequent cache hits            |
| Adaptive    | Dynamic       | Complex scenarios, varying data freshness needs | Complex to implement and tune correctly, potential for misconfiguration |

## Invalidation Triggers

*   Updates to underlying data sources (e.g., database records, document corpus changes).
*   Changes in the LLM model version, parameters, or system configuration.
*   User explicitly requests a fresh response or provides feedback indicating staleness.
*   Significant shifts in the user's session context or conversational history.
*   Detection of data drift, degradation, or inconsistencies in cached content.
*   Scheduled cache refreshes for specific data types or categories.
*   Schema changes in structured prompts, templates, or expected output formats.

## Cost Savings Estimates

| Provider                 | Cache Hit Rate                                 | Cost Reduction | Implementation Effort |
| :----------------------- | :--------------------------------------------- | :------------- | :-------------------- |
| Anthropic (with `cache_control`) | ~90%                                           | ~90%           | Moderate              |
| OpenAI                   | High (for identical prefixes)                  | Variable       | Low (automatic)       |
| Self-hosted (Redis/Memcached) | High (customizable via key strategy)           | High           | High (infra management) |

## When NOT to Cache

*   Prompts requiring highly dynamic, real-time, or user-specific contextual data.
*   Requests for information that changes by the second (e.g., live stock prices, breaking news, current sensor readings).
*   Personalized recommendations, tailored responses, or user-generated content where uniqueness is paramount.
*   Workloads with very low prompt repetition, or where queries are primarily unique and one-off.
*   When the computational cost of generating the prompt is negligible compared to cache lookup overhead and maintenance.


### How to use

```text
You are the consuming agent that acts on this knowledge_card under F3 INJECT.
- Resolve the open slots (query_context, target_audience) from the caller request.
- Honor every constraint and field contract declared above.
- Emit the result in the shape this knowledge_card defines; never improvise the schema.
```

### Procedure

```text
1. Load this artifact and read its contract under F3 INJECT.
2. Bind query_context and target_audience from the incoming request.
3. Validate the inputs against the constraints declared above.
4. Execute the knowledge_card behavior; resolve each open slot at act-time.
5. Verify the output shape, then signal completion to the orchestrator.
```

## Related Artifacts

| Artifact | Relationship | Score |
|----------|-------------|-------|
| p01_kc_caching | related | 0.43 |
| p01_kc_prompt_cache | related | 0.40 |
| prompt-cache-builder | related | 0.38 |
| bld_collaboration_prompt_cache | related | 0.38 |
| ex_knowledge_card_prompt_caching | related | 0.38 |
| bld_knowledge_card_prompt_cache | related | 0.37 |
| p10_lr_prompt_cache_builder | related | 0.29 |
| [[p11_qg_citation]] | related | 0.28 |
| [[p11_qg_golden_test]] | related | 0.28 |
