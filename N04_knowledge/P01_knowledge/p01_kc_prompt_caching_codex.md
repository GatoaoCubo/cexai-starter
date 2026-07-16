---
id: p01_kc_prompt_caching_codex
kind: knowledge_card
pillar: P01
title: Prompt Caching Strategies for LLM Applications
version: 1.0.0
quality: null
tags: [prompt-caching, optimization, cost-reduction, llm, infrastructure]
related:
  - prompt-cache-builder
  - bld_config_prompt_cache
primary_8f: INJECT
slots:
  query_context: "<the question this card is recalled to answer>"
  target_audience: "<who consumes the answer>"
---

## Overview

Prompt caching reuses LLM outputs (or attention KV state) for repeated or
prefix-matching inputs, eliminating redundant inference. Production systems
typically see 60-90% input-token cost reduction on cache hits and 2-5x
latency improvement, depending on provider and prompt-prefix stability.

## Cache Key Design

| Strategy | Key Components | Pros | Cons |
|----------|---------------|------|------|
| exact-match | sha256(full_prompt) | trivial; deterministic | zero hit rate on dynamic tails |
| prefix-match | sha256(system + few_shots) | high hit rate on chat prefixes | requires provider support (Anthropic, OpenAI) |
| semantic-hash | embedding(prompt) -> ANN bucket | catches paraphrases | false positives; needs vector store |
| template-based | sha256(template_id + slot_values) | predictable; auditable | requires structured prompt registry |

## TTL Policies

| Policy | TTL Range | Best For | Risk |
|--------|-----------|----------|------|
| aggressive | 1-5 min | high-volume chat sessions | stale on rapid context shifts |
| moderate | 5-30 min | RAG with stable corpora | mid-window invalidation gaps |
| conservative | 1-24 h | static system prompts, agent personas | drift if upstream content changes |
| adaptive | function(hit_rate, drift_score) | mixed workloads | requires telemetry pipeline |

## Invalidation Triggers

- Schema change: any frontmatter or tool-definition diff in the prompt prefix
- Context update: source document edited or re-embedded (lineage hash changes)
- Model version change: provider rolls a new model snapshot or temperature override
- User feedback: explicit thumbs-down or correction signals on cached responses
- Drift detection: output-distribution shift detected by drift-detector-builder
- Manual flush: operator-triggered purge after policy or guardrail update

## Cost Savings Estimates

| Provider | Cache Hit Rate | Cost Reduction | Implementation Effort |
|----------|---------------|----------------|----------------------|
| Anthropic (cache_control) | 70-95% on stable prefixes | ~90% on cached input tokens | low: 1 header per breakpoint |
| OpenAI (automatic) | 50-80% on >=1024 token prefixes | ~50% on cached input tokens | zero: implicit |
| self-hosted (Redis) | 30-60% on full-prompt match | 100% on hit (no inference) | medium: key design + TTL infra |
| self-hosted (KV-cache reuse) | 60-90% on prefix match | ~70-90% latency cut | high: vLLM/TensorRT integration |

## When NOT to Cache

- Dynamic user context: prompts inject session-specific PII or per-user state
- Real-time data: prices, inventory, time-sensitive feeds where staleness causes errors
- Personalized responses: user-specific tone, memory, or persona that must not bleed across users
- Low-repetition workloads: long-tail unique prompts where hit rate stays under 10%
- Compliance-sensitive flows: medical, legal, or PII contexts where cache may be subpoenaed
- Adversarial inputs: prompt-injection probes that should never be served from cache




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
| ex_knowledge_card_prompt_caching | sibling | 0.43 |
| bld_knowledge_card_prompt_cache | sibling | 0.40 |
| bld_collaboration_prompt_cache | related | 0.39 |
| p01_kc_prompt_cache | sibling | 0.39 |
| prompt-cache-builder | related | 0.37 |
| p01_kc_caching | sibling | 0.33 |
| bld_output_template_prompt_cache | related | 0.31 |
| bld_config_prompt_cache | related | 0.29 |
| p10_lr_prompt_cache_builder | related | 0.29 |
