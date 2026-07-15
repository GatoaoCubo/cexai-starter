---
id: bld_memory_data_contract
kind: entity_memory
pillar: P10
llm_function: INJECT
version: 1.0.0
quality: null
tags: [data_contract, memory, patterns]
title: "Memory Patterns: data_contract"
author: builder
tldr: "Data Contract memory: context persistence, recall triggers, and state management"
8f: "F3_inject"
keywords: [memory patterns, data contract memory, context persistence, recall triggers, and state management, data_contract, memory, patterns, common mistakes, kind memory]
density_score: 0.88
created: "2026-04-17"
updated: "2026-04-17"
related:
  - data-contract-builder
  - p01_kc_data_contract
  - bld_rules_data_contract
  - bld_architecture_data_contract
  - bld_context_sources_data_contract
---
# Memory Patterns: data_contract
## What to Remember
- Contract versioning is INDEPENDENT from service versioning
- SLA must be numeric -- not "fast" or "reliable" but "< 200ms" and "99.9%"
- Producer owns the schema; consumer specifies what they need (CDC pattern)
- data_contract boundary: schema+SLA between systems, NOT LLM output validation

## Common Mistakes
| Mistake | Correction |
|---------|-----------|
| Conflating with validation_schema | data_contract = cross-system; validation_schema = LLM output |
| Vague SLA ("near real-time") | Numeric: "< 5 seconds", "99.9%", "< 200ms p99" |
| Contract version tied to service | Contract v1.2.0 independent from service v3.5.1 |
| Missing consumer_system | Always name both sides of the agreement |

## Cross-Kind Memory
- domain_event: events crossing BC boundaries need data_contracts
- bounded_context: contracts formalize BC-to-BC communication
- validation_schema: downstream consumers use this to validate incoming data
- dataset_card: separate concern -- data asset metadata, not exchange agreement

## Reuse Signals
- Check existing contracts: grep P06 for dc_ prefix files
- Check schema registry (if configured) before creating new contract
- Consumer-driven: ask consumer team what fields they actually need

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
| [[data-contract-builder]] | upstream | 0.43 |
| [[p01_kc_data_contract]] | upstream | 0.41 |
| [[bld_rules_data_contract]] | downstream | 0.38 |
| [[bld_architecture_data_contract]] | upstream | 0.36 |
| [[bld_context_sources_data_contract]] | related | 0.35 |
