---
id: p01_kc_prompt_caching_strategies_mode_b
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
related:
  - prompt-cache-builder
---

## Overview

Prompt caching is a crucial technique in LLM application development that stores the results of expensive LLM API calls. It significantly reduces redundant computations and associated costs by serving cached responses for identical or highly similar prompts, often achieving cost reductions of 70-90% for cacheable query patterns.

## Cache Key Design

| Strategy        | Key Components                                                              | Pros                                                         | Cons                                                              |
|-----------------|-----------------------------------------------------------------------------|--------------------------------------------------------------|-------------------------------------------------------------------|
| Exact Match     | Full prompt string, model name, parameters                                  | Simple to implement, high cache hit rate for identical inputs | Fails for minor variations, misses semantic similarities          |
| Prefix Match    | First N characters of prompt, model name, parameters                        | Catches minor variations, simpler than semantic hashing        | Can lead to cache misses if variation is in the prefix, still brittle |
| Semantic Hash   | Embeddings of prompt, model parameters (e.g., using sentence transformers) | Captures semantic similarity, robust to phrasing changes      | Computationally expensive to generate hashes, requires embedding model |
| Template-Based  | Prompt template structure + filled variables, model name, parameters        | Good for structured prompts, separates logic from data         | Requires careful template design, struggles with unstruct. input  |

## TTL Policies

| Policy       | TTL Range | Best For                                                                    | Risk                                                                        |
|--------------|-----------|-----------------------------------------------------------------------------|-----------------------------------------------------------------------------|
| Aggressive   | 1-5 min   | High-frequency, low-volatility data (e.g., common FAQs, standard reports)   | Stale data if underlying info changes rapidly; missed updates              |
| Moderate     | 5-30 min  | Moderately dynamic data, standard business logic, API responses             | Small window for stale data, potential for minor inconsistencies            |
| Conservative | 1h+       | Infrequently changing data, historical trends, stable reference information | Significant risk of serving outdated information if changes are frequent    |
| Adaptive     | Dynamic   | Based on data recency signals, update frequency, user feedback              | Complex to implement; requires robust monitoring and re-validation logic |

## Invalidation Triggers

*   Schema change in data sources feeding the prompt.
*   Update to underlying knowledge base or reference documents.
*   Model version upgrade or significant parameter change.
*   User explicit feedback indicating a cached response was incorrect.
*   Drift detection in input data distribution or expected output characteristics.
*   Time-based expiration (TTL) reached.
*   Deployment of new application code that modifies prompt generation logic.

## Cost Savings Estimates

| Provider     | Cache Hit Rate | Cost Reduction | Implementation Effort |
|--------------|----------------|----------------|-----------------------|
| Anthropic    | ~70-95%        | 70-90%         | Low to Medium         |
| OpenAI       | ~70-95%        | 70-90%         | Low to Medium         |
| Self-Hosted  | ~60-90%        | 60-85%         | Medium to High        |

## When NOT to Cache

*   Prompts that include highly dynamic or user-specific context (e.g., personalized recommendations, chat history).
*   Requests for data that must be absolutely current (e.g., stock prices, live news feeds).
*   Prompts where the output is intended to be unique for each interaction (e.g., creative writing prompts with unique generative constraints).
*   Workloads with very low prompt repetition, where cache hits would be minimal.
*   When serving stale data poses a significant risk (e.g., critical safety information, legal advice).



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
| kc_prompt_caching_strategies | sibling | 0.85 |
| kc_prompt_caching_strategies_gemini | sibling | 0.47 |
| kc_prompt_caching_codex | sibling | 0.43 |
| ex_knowledge_card_prompt_caching | sibling | 0.29 |
| bld_knowledge_card_prompt_cache | sibling | 0.28 |
| p01_kc_prompt_cache | sibling | 0.27 |
| bld_collaboration_prompt_cache | downstream | 0.27 |
| prompt-cache-builder | downstream | 0.27 |
| n00_prompt_cache_manifest | sibling | 0.25 |
| p01_kc_caching | sibling | 0.23 |
