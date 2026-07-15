---
id: p01_kc_prompt_caching_strategies_codex_b
kind: knowledge_card
pillar: P01
title: Prompt Caching Strategies for LLM Applications
version: 1.0.0
quality: null
tags: [prompt-caching, optimization, cost-reduction, llm, infrastructure]
primary_8f: INJECT
long_tails:
  - "how do I use the knowledge_card P01 in CEX"
  - "which pillar and verb does knowledge_card serve"
slots:
  query_context: "<the question this card is recalled to answer>"
  target_audience: "<who consumes the answer>"
---

## Overview

Prompt caching reuses outputs or provider-managed prompt prefixes when prompt structure repeats, avoiding redundant LLM work. It matters most for stable system prompts, tool schemas, and few-shot blocks, with typical savings of 50-90% on cache hits.

## Cache Key Design

| Strategy | Key Components | Pros | Cons |
|----------|----------------|------|------|
| exact-match | hash(full prompt), model id, schema version | deterministic; easy to audit | breaks on tiny edits; low reuse |
| prefix-match | hash(stable prefix), token boundary, model id | high reuse for shared instructions | needs strict prefix discipline |
| semantic-hash | embedding(prompt), similarity threshold, model family | catches near-duplicates | false positives; embedding overhead |
| template-based | template id, slot values, prompt revision | clear reuse boundaries | needs prompt registry/versioning |

## TTL Policies

| Policy | TTL Range | Best For | Risk |
|--------|-----------|----------|------|
| aggressive | 1-5 min | volatile corpora, live queues | misses rise under churn |
| moderate | 5-30 min | standard RAG, chat prefixes | small edits can stay stale |
| conservative | 1h+ | static instructions, fixed personas | needs explicit invalidation |
| adaptive | dynamic by change rate and hit rate | mixed workloads with telemetry | policy complexity hides stale keys |

## Invalidation Triggers

- Schema change: prompt contract, tool signature, or output format revision.
- Context update: document edits, re-embedding, or source replacement.
- Model version change: new provider snapshot or tokenizer behavior.
- User feedback: corrections, thumbs-down, or manual refresh.
- Drift detection: eval regressions or rising hallucination rate.
- Policy change: safety rules or system instruction updates.

## Cost Savings Estimates

| Provider | Cache Hit Rate | Cost Reduction | Implementation Effort |
|----------|----------------|----------------|----------------------|
| Anthropic | 70-95% on stable blocks | up to ~90% on cached input tokens; 5 min TTL breakpoints | low: add `cache_control` |
| OpenAI | 50-80% on identical prefixes | moderate-to-high on cached prefix tokens | low: automatic, no explicit controls |
| self-hosted (Redis) | 30-70% with good keys | full inference avoided on true hits | medium: key, TTL, eviction, metrics |
| self-hosted (Memcached) | 30-65% on hot prompts | strong latency gain, weaker durability | medium: simpler than Redis |

## When NOT to Cache

- Dynamic user context: per-user memory or fast session state kills reuse.
- Real-time data: feeds, news, telemetry, or inventory go stale quickly.
- Personalized responses: account-specific tone or instructions are unsafe to share.
- Low-repetition workloads: one-off tasks do not justify cache overhead.
- Compliance-sensitive flows: regulated data may forbid prompt retention.


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
