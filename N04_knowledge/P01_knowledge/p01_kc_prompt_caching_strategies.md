---
id: p01_kc_prompt_caching_strategies
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

Prompt caching eliminates redundant API calls for identical or similar prompt prefixes, reducing LLM infrastructure costs by 90% on cache hits. This technique is essential for production systems handling repeated queries over static context (documents, system instructions, examples) and for batch inference pipelines that process the same task template against multiple inputs.

## Cache Key Design

| Strategy | Key Components | Pros | Cons |
|----------|---|---|---|
| Exact-match | Full prompt hash (MD5/SHA256) | Simplest, 100% accurate hits | Fails on whitespace changes; fragile to minor edits |
| Prefix-match | First N tokens + hash of remainder | Catches variation in tail; respects cache layers | Requires token-aware hashing; overhead to compute boundaries |
| Semantic-hash | Embedding of full prompt + threshold | Resilient to paraphrasing; finds near-duplicates | Embedding model cost; threshold tuning required; false positives |
| Template-based | Parameterized prompt slots + signature | Reuses expensive preamble across requests; composable | Requires prompt design discipline; token-boundary detection necessary |

## TTL Policies

| Policy | TTL Range | Best For | Risk |
|--------|-----------|----------|------|
| Aggressive | 1-5 minutes | High-volume APIs with fresh contexts; time-sensitive data | Cache invalidation races; stale responses if data changes within TTL |
| Moderate | 5-30 minutes | Typical chatbots, Q&A engines; medium-freshness tolerance | Risk window for schema/data changes; frequent cache misses if query diversity high |
| Conservative | 1-24 hours | Reference documents, system prompts, rarely-changing preambles | Requires explicit invalidation triggers for correctness; storage overhead |
| Adaptive | Dynamic per key | Hybrid: TTL = f(change_frequency, data_age) | Complexity in policy engine; requires monitoring and feedback loops |

## Invalidation Triggers

- **Schema change**: If the context or output schema evolves, invalidate all cached prompts using the old schema
- **Context update**: When source documents, knowledge bases, or reference data change, clear prefix cache for affected sections
- **Model version change**: Switching LLM versions (e.g., Opus 4.6 -> 4.7) requires full flush; embedding spaces differ
- **User feedback**: Negative feedback or correction signals should invalidate cached results for similar queries
- **Drift detection**: Monitor for output degradation over time; auto-invalidate if quality metrics decline below threshold
- **Explicit flag**: Support cache-bypass headers or parameters for debugging and testing

## Cost Savings Estimates

| Provider | Cache Hit Rate | Cost Reduction | Implementation Effort |
|----------|---|---|---|
| Anthropic | 60-75% | 54-67% total API cost | 2-4h: cache_control markup in SDK calls |
| OpenAI | 40-60% | 32-48% total API cost | 3-6h: no native control; requires request deduplication layer |
| Self-hosted (Redis) | 70-85% | 42-56% compute cost (excluding storage) | 1-2d: setup, key/TTL policy design, eviction strategy |
| Self-hosted (Memcached) | 65-80% | 39-52% compute cost | 1d: simpler than Redis; loses durability |

## When NOT to Cache

- **Dynamic user context**: If every request includes unique user state, query history, or personalization, cache hits drop to 0-5%; overhead exceeds savings
- **Real-time data**: Stock prices, weather, live event scores; prompt prefix caching assumes static background; invalidation overhead dominates
- **Personalized responses**: User preferences, custom instructions, or private documents; cannot share cached prefix across users (privacy violation)
- **Low-repetition workloads**: One-shot inference, unique tasks, or exploration phases; cache misses waste memory/latency budget
- **Streaming responses**: Partial cache hits require re-streaming; latency improvements vanish; flush complexity increases


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
