---
id: bld_memory_saga
kind: knowledge_card
pillar: P10
title: "Memory: saga Builder Patterns"
version: 1.0.0
created: "2026-04-17"
updated: "2026-04-17"
author: builder
domain: saga
quality: null
tags: [memory, saga, P12]
llm_function: INJECT
tldr: "Recalled patterns and corrections for saga builder sessions."
8f: "F3_inject"
keywords: [saga builder patterns, memory, saga, persistent patterns, common corrections, memory persistence checklist, memory pattern, related artifacts, python tools, compensating_action]
density_score: null
related:
  - bld_memory_canary_config
  - bld_memory_slo_definition
---
# Memory: saga Builder

## Persistent Patterns
| Pattern | Frequency | Note |
|---------|-----------|------|
| Every step MUST have compensating_action | HIGH | Gate H06 |
| Make compensating actions idempotent | HIGH | Retry safety |
| Rollback is reverse order of completed steps | HIGH | Saga invariant |
| steps_count must match list | HIGH | Gate H07 |

## Common Corrections
| Mistake | Correction |
|---------|-----------|
| User conflates with workflow | Teach: workflow has no compensation; saga does |
| User designs step without undo | Block: every step needs compensating_action |
| User sets compensating_action: null | Reject: must be idempotent undo action |
| User mixes choreography and orchestration | Choose one topology per saga |
| User exceeds 10 steps | Suggest splitting into sub-sagas |

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
| [[bld_memory_canary_config]] | sibling | 0.43 |
| [[bld_memory_slo_definition]] | sibling | 0.35 |
