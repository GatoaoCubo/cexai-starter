---
quality: null
id: bld_architecture_aggregate_root
kind: knowledge_card
pillar: P06
title: "Aggregate Root Builder -- Architecture"
version: 1.1.0
quality: null
tags: [builder, aggregate_root, architecture, ddd, consistency_boundary]
llm_function: CONSTRAIN
8f: "F3_inject"
keywords: [architecture constraints for aggregate_root, evans topology, invariant enforcement, event emission, repository pattern, builder, aggregate_root, architecture, consistency_boundary, pattern origin

evans]
density_score: 0.93
created: "2026-04-17"
updated: "2026-04-22"
author: builder
domain: domain_driven_design
tldr: "Architecture constraints for aggregate_root: Evans topology, invariant enforcement, event emission, repository pattern."
related:
  - bld_knowledge_aggregate_root
---
# Architecture: aggregate_root

## Pattern Origin

Evans DDD (2003): Aggregate = cluster of domain objects treated as a unit for data changes.
Aggregate Root = single entity responsible for maintaining cluster invariants.

## Structural Topology

```
AggregateRoot (identity + invariant enforcer)
  |-- Entity_A (child, no direct external access)
  |-- Entity_B (child, accessed only via root)
  |-- ValueObject_X (immutable, no identity)
  |-- ValueObject_Y (immutable, no identity)
  repository: AggregateRootRepository (find_by_id + save only)
```

## Invariant Enforcement

- Commands mutate state inside the boundary
- Root checks invariants AFTER applying command, BEFORE returning
- If invariant violated: raise domain exception, rollback state
- Repository saves ENTIRE aggregate atomically (one transaction)

## Event Emission

- Each command that succeeds emits one or more domain events
- Events are facts about what happened (past tense)
- Subscribers react to events outside the aggregate boundary

## Relationship to Other Kinds

| Kind | Relationship | Boundary role |
|------|-------------|---------------|
| value_object | Internal member | Immutable, no identity |
| interface | External contract | Repository or service impl |
| input_schema | Validation layer | Data validated BEFORE entering |
| domain_event | Output signal | Fact emitted on state change |
| bounded_context | Parent scope | Aggregate lives inside one BC |
| saga | Cross-boundary | Coordinates multiple aggregates |

## Anti-Patterns

| Anti-pattern | Signal | Fix |
|-------------|--------|-----|
| God aggregate | Root owns everything | Split by consistency boundary |
| Cross-aggregate object refs | Direct object pointers | Use IDs only |
| Anemic aggregate | No invariants, just getters | Add domain rules to root |
| Large aggregate | >7 members | Decompose by transaction need |

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[bld_knowledge_aggregate_root]] | sibling | 0.60 |
