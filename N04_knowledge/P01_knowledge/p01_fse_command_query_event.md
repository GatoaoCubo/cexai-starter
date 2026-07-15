---
id: p01_fse_command_query_event
kind: few_shot_example
pillar: P01
version: "1.0.0"
created: "2026-06-03"
updated: "2026-06-03"
author: n03_builder
domain: cqrs_domain_operations
difficulty: hard
edge_case: true
format: "CQRS + domain event classification with LABEL -- 1-line rationale"
quality: null
input: "Classify the domain operation 'CreateOrder' as COMMAND, QUERY, or DOMAIN_EVENT and give a 1-line rationale."
output: "COMMAND -- CreateOrder mutates system state (persists a new Order aggregate); it issues intent and expects no return data."
tags: [few-shot, cqrs, command, query, domain-event, ddd, classification]
tldr: "7 I/O pairs teaching LLM to classify a domain operation as COMMAND / QUERY / DOMAIN_EVENT with a 1-line rationale. Sairyss/domain-driven-hexagon (MIT)."
keywords: [command, query, domain-event, cqrs, event-sourcing, ddd, side-effect, classification]
source: "github.com/Sairyss/domain-driven-hexagon"
source_author: "Sairyss"
source_license: "MIT"
related:
  - p01_kc_clean_arch_ddd_in_cex
  - p01_fse_entity_vs_value_object
  - p01_fse_clean_arch_layer_placement
  - p08_pat_hexagonal_ports_adapters
  - domain_event
  - p01_kc_repo_assimilation_candidates
---

# Few-Shot Example -- COMMAND / QUERY / DOMAIN_EVENT (CQRS + Event Split)

> Source grounding: Sairyss/domain-driven-hexagon (MIT). All examples are CEX-original; no verbatim reproduction of source code or docs.
> Classification rules follow CQRS (Fowler 2011) + domain event semantics (Evans 2003, Vernon 2013).

## Explanation

Teaches the three-way split every DDD/CQRS codebase enforces on domain operations:

- **COMMAND**: expresses *intent to change state*. Verb-object imperative name. May fail (validation, invariant). By strict CQS, returns void -- but pragmatic variants return a generated ID (see Pair 4).
- **QUERY**: reads state without side effects. Never mutates. Returns data. Safe to retry and cache.
- **DOMAIN_EVENT**: records a *fact that already happened*. Past-tense noun phrase. Others subscribe and react; the originating bounded context does not orchestrate the reaction.

An LLM learning these pairs learns to: (1) spot imperative verbs as COMMAND, (2) spot Read/Get/Find/List as QUERY, (3) spot past-tense noun phrases as DOMAIN_EVENT, (4) handle the edge cases where the signal is ambiguous.

## Input/Output Pairs

### Pair 1 -- Baseline COMMAND
```
Input: Classify 'CreateOrder'.
Output: COMMAND -- CreateOrder mutates state (persists a new Order aggregate) and issues intent; it expects no return data.
```

### Pair 2 -- Baseline QUERY
```
Input: Classify 'GetOrderById'.
Output: QUERY -- GetOrderById reads an Order by its identity without any state change; safe to retry, cache, or replicate.
```

### Pair 3 -- Baseline DOMAIN_EVENT
```
Input: Classify 'OrderPlaced'.
Output: DOMAIN_EVENT -- OrderPlaced is a past-tense fact recorded after a CreateOrder command succeeds; other bounded contexts (shipping, billing) subscribe and react independently.
```

### Pair 4 -- Edge: command that returns a generated ID
```
Input: Classify 'CreateProduct' in a system where the handler returns the new product_id immediately.
Output: COMMAND -- CreateProduct is still a COMMAND (it mutates state); returning a generated ID is a pragmatic CQS relaxation widely accepted in hexagonal architecture. The key signal is state mutation, not return type.
```

### Pair 5 -- Edge: query that triggers a read-model rebuild
```
Input: Classify 'GetUserDashboard' when the handler detects a stale projection and rebuilds it before returning.
Output: QUERY -- from the caller's perspective GetUserDashboard is a pure read (no domain state changes). Internal projection maintenance is an implementation detail of the read side; the domain model is untouched.
```

### Pair 6 -- Naming trap: event vs command confusion
```
Input: Distinguish 'SubmitOrder' (imperative) from 'OrderSubmitted' (past tense) -- classify each.
Output: SubmitOrder = COMMAND -- imperative verb, expresses intent to transition Order to submitted state. OrderSubmitted = DOMAIN_EVENT -- past-tense noun phrase, records the fact after SubmitOrder succeeds; subscribers (inventory, notification) react without being orchestrated.
```

### Pair 7 -- Hard: symmetric cancel pair
```
Input: Classify 'CancelOrder' and 'OrderCancelled' and explain the causal relationship.
Output: CancelOrder = COMMAND -- intent to cancel; may be rejected (e.g. already shipped). OrderCancelled = DOMAIN_EVENT -- fact emitted only when cancellation succeeds; downstream services (refund, restocking) consume it. The COMMAND is the cause; the DOMAIN_EVENT is the recorded effect.
```

## Edge Cases Covered

| Pair | Edge | Key Teaching |
|------|------|-------------|
| Pair 4 | Command returning a value | Return type does not change classification; mutation is the signal |
| Pair 5 | Query with side effect on read model | Read-model maintenance != domain state change |
| Pair 6 | Same concept, two grammatical forms | Imperative = COMMAND; past-tense = DOMAIN_EVENT |
| Pair 7 | Symmetric COMMAND + EVENT pair | Causal chain: command causes event, event causes reactions |

## Related Artifacts

| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[p01_kc_clean_arch_ddd_in_cex]] | upstream domain KC | 0.91 |
| [[p01_fse_entity_vs_value_object]] | sibling (same classification format) | 0.88 |
| [[p01_fse_clean_arch_layer_placement]] | sibling (same LABEL -- rationale format) | 0.85 |
| p08_pat_hexagonal_ports_adapters | structural context (ports carry commands/queries) | 0.82 |
| domain_event | kind being classified | 0.80 |
| [[p01_kc_repo_assimilation_candidates]] | source registry | 0.75 |
