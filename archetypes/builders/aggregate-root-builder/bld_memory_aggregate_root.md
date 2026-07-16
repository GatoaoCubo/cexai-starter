---
id: bld_memory_aggregate_root
kind: knowledge_card
pillar: P06
title: "Aggregate Root Builder -- Memory"
version: 1.0.0
quality: null
tags: [builder, aggregate_root, memory, ddd, session_patterns]
llm_function: INJECT
8f: "F3_inject"
keywords: [session patterns for aggregate_root, size limits, invariant quality, repository constraints, concurrency defaults, event sourcing, builder, aggregate_root, memory, session_patterns]
density_score: 0.90
created: "2026-04-17"
updated: "2026-04-22"
author: builder
domain: domain_driven_design
tldr: "Session patterns for aggregate_root: size limits, invariant quality, repository constraints, concurrency defaults, event sourcing."
related:
  - kc_aggregate_root
  - bld_memory_domain_event
  - bld_architecture_aggregate_root
  - bld_rules_aggregate_root
  - bld_output_template_aggregate_root
---
# Memory: aggregate_root
## Session Patterns to Remember
- Aggregate size: most production aggregates have 2-5 members. >7 is a smell.
- Invariant quality signal: if an invariant says "must be valid" -- it is not concrete. Push for specific field constraints.
- Repository rule: find_by_id and save are the only methods on the aggregate repository. Queries belong in read models.
- Concurrency: optimistic locking (version field) is the default. Use pessimistic only when contention is proven high.
- Event sourcing: if the domain uses event sourcing, `commands` list becomes `apply(event)` handlers.
## Common Mistakes Seen
- Defining repository with list/query methods: redirect to read model or query service
- Putting domain logic in the repository: domain logic belongs in the root, not the repo
- Forgetting to list domain_events: every command that changes state emits at least one event
- Using service IDs as cluster members: cluster_members must be entities or value objects, not foreign aggregates
## Boundary Vocabulary
- "Cluster" = set of objects inside the aggregate boundary
- "Root" = the single entity with global identity that owns the cluster
- "Invariant" = a business rule that must hold true after every command
- "Command" = a request to change state (may fail if invariant would be violated)
- "Domain event" = a fact that state changed (never fails, past tense)

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
| [[kc_aggregate_root]] | sibling | 0.36 |
| [[bld_memory_domain_event]] | downstream | 0.36 |
| [[bld_architecture_aggregate_root]] | sibling | 0.36 |
| [[bld_rules_aggregate_root]] | sibling | 0.34 |
| [[bld_output_template_aggregate_root]] | related | 0.33 |
