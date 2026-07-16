---
quality: null
quality: null
id: bld_knowledge_card_saga
kind: knowledge_card
pillar: P01
title: "Knowledge Card: saga"
version: 1.0.0
created: "2026-04-17"
updated: "2026-04-17"
author: builder
domain: saga
tags: [knowledge_card, saga, P12]
llm_function: INJECT
tldr: "Domain knowledge for saga: Garcia-Molina 1987, compensation chains, and choreography vs orchestration."
8f: "F3_inject"
keywords: [knowledge card, domain knowledge for saga, compensation chains, and choreography vs orchestration, knowledge_card, saga, origin
garcia, core concepts, industry implementations, step functions]
density_score: null
related:
  - bld_architecture_saga
---
# Knowledge Card: saga

## Origin
Garcia-Molina & Salem (1987): "SAGAS" - ACM SIGMOD. A saga is a long-lived transaction that can be broken into a sequence of transactions that can be interleaved with other transactions. If a step fails, compensating transactions undo the work of prior steps.

## Core Concepts
| Concept | Definition |
|---------|-----------|
| Forward transaction (T_i) | The step that does the work |
| Compensating transaction (C_i) | The step that undoes T_i |
| Saga completion | All T_i succeed: T1, T2, ..., Tn |
| Saga rollback | Some T_k fails: T1, T2, ..., T_k, C_k-1, ..., C1 |

## Choreography vs Orchestration
| Style | How | Pros | Cons |
|-------|-----|------|------|
| Choreography | Services emit events; each service reacts | Decoupled; no single point of failure | Hard to trace; harder to debug |
| Orchestration | Saga orchestrator sends commands | Centralized logic; easy to trace | Single point of failure; coupling |

## Anti-Patterns
| Anti-Pattern | Fix |
|-------------|-----|
| Step without compensating action | Every step MUST have a compensating action |
| Compensating action that can also fail | Make compensating actions idempotent; retry until success |
| Saga too many steps (>10) | Split into sub-sagas with signal handoffs |
| Using saga for a 2-phase commit | Use 2PC for ACID transactions; saga for eventual consistency |

## Industry Implementations
- AWS Step Functions: Express Workflows with catch/retry
- Apache Camel: Saga EIP (Enterprise Integration Patterns)
- Eventuate Tram: Java-based saga orchestration framework
- MassTransit: .NET saga state machine

## Knowledge Injection Checklist

- Verify domain facts are sourced and citable
- Validate density_score >= 0.85 (no filler content)
- Cross-reference with related KCs for consistency
- Check for outdated facts that need refresh

## Injection Pattern

```yaml
# KC injection at F3
source: verified
density: 0.85+
cross_refs: checked
freshness: current
```

```bash
python _tools/cex_compile.py {FILE}
python _tools/cex_retriever.py --query "{DOMAIN}"
```

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[bld_architecture_saga]] | sibling | 0.48 |
