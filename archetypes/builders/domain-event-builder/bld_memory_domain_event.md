---
id: bld_memory_domain_event
kind: entity_memory
pillar: P10
llm_function: INJECT
version: 1.0.0
quality: null
tags: [domain_event, memory, patterns]
title: "Memory Patterns: domain_event"
author: builder
tldr: "Domain Event memory: context persistence, recall triggers, and state management"
8f: "F3_inject"
keywords: [memory patterns, domain event memory, context persistence, recall triggers, and state management, domain_event, memory, patterns, common mistakes, kind memory]
density_score: 0.99
created: "2026-04-17"
updated: "2026-04-17"
related:
  - p01_kc_domain_event
  - bld_memory_data_contract
  - bld_memory_bounded_context
  - bld_memory_aggregate_root
  - bld_rules_domain_event
---
# Memory Patterns: domain_event
## What to Remember
- Event naming: ALWAYS past tense. OrderPlaced NOT PlaceOrder
- Aggregate ownership: each event belongs to EXACTLY ONE aggregate root
- Payload immutability: record state AT occurrence_time, never current state
- Causation chain: event_id -> causation_id -> correlation_id (tracing backbone)

## Common Mistakes to Avoid
| Mistake | Correction |
|---------|-----------|
| Command as event name (ProcessPayment) | Past tense (PaymentProcessed) |
| Missing aggregate_root | Always name the DDD aggregate |
| Mutable payload field | Snapshot only, freeze at occurred_at |
| Conflating with signal | Check: is it business-meaningful? -> domain_event |

## Cross-Kind Memory
- data_contract: publish domain_event schema to consumers via data_contract
- bounded_context: domain_events are scoped to their bounded_context
- workflow: domain_events trigger workflows (one-way dependency)
- audit_log: downstream consumers may convert domain_events to audit_log

## Reuse Signals
Search for existing domain_events before creating new ones:
- grep P12 for de_ prefix files
- check bounded_context event catalog if it exists

## Memory Persistence Checklist

- Verify memory type matches taxonomy (entity, episodic, procedural, working)
- Validate retention policy aligns with data lifecycle rules
- Cross-reference with memory_scope for boundary correctness
- Check for stale entries that need decay or pruning

## Memory Pattern

```yaml
# Memory lifecycle
type: classified
retention: defined
scope: bounded
decay: configured
```

```bash
python _tools/cex_compile.py {FILE}
python _tools/cex_memory_update.py --check
```

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[p01_kc_domain_event]] | upstream | 0.41 |
| [[bld_memory_data_contract]] | sibling | 0.40 |
| [[bld_memory_bounded_context]] | sibling | 0.39 |
| [[bld_memory_aggregate_root]] | upstream | 0.38 |
| [[bld_rules_domain_event]] | downstream | 0.37 |
