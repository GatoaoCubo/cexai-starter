---
kind: knowledge_card
id: bld_knowledge_card_user_model
pillar: P01
llm_function: INJECT
purpose: Domain knowledge for user_model production -- Honcho pattern specification
sources: plastic-labs/honcho, multi-agent, Zep user memory, MemGPT user model, cognitive science mental models
quality: 8.8
title: "Knowledge Card: user_model"
version: "1.0.0"
author: n03_builder
tags: [user_model, builder, knowledge_card, honcho, P10]
tldr: "Honcho dialectic pattern: cross-session peer model with per-turn pre/post-response insight loop, SQLite storage, NL-queryable Collections."
domain: "user model construction"
created: "2026-04-18"
updated: "2026-04-18"
8f: "F3_inject"
keywords: [user model construction, knowledge card, honcho dialectic pattern, post-response insight loop, sqlite storage, nl-queryable collections, user_model, builder, knowledge_card, honcho]
density_score: 0.91
related:
  - kc_user_model
  - user-model-builder
  - bld_architecture_user_model
---
# Domain Knowledge: user_model

## Executive Summary
`user_model` implements the **Honcho dialectic pattern** -- a cross-session representation of a human
peer built by running a per-turn insight loop. Before each response, the system queries what the
current message reveals about the user. After the response, it derives conclusions and writes them
back to the peer's durable Collections. Over time this creates a queryable mental model of the user
that eliminates the need for them to repeat context across sessions.

Upstream sources: **plastic-labs/honcho** (Peer/Session/Collection API) + **multi-agent** (agentic memory substrate).

## Spec Table
| Property | Value |
|----------|-------|
| Pillar | P10 (Memory) |
| llm_function | INJECT |
| ID pattern | `^um_[a-z][a-z0-9_]+$` |
| Max bytes | 4096 |
| Naming | `p10_um_<peer_id>.md` |
| Storage default | SQLite |
| Collections minimum | 3 |
| Compaction default | 50 turns |
| Upstream | plastic-labs/honcho + multi-agent |

## Honcho Pattern
The Honcho dialectic loop creates a self-improving user mental model:

```
[turn] -> add_messages -> pre-insight query -> inject into context
       -> generate response
       -> post-derive query -> write to collections
       -> (every N turns): compact collections into derived facts
```

This enables: "What does this user prefer about code style?" answered by `peer.chat(query)` in
milliseconds from the durable Collections, without LLM inference cost on every lookup.

## Implementation Patterns
- **Honcho SDK** (Python): `from honcho import Honcho; app = Honcho(); peer = app.peers.get_or_create(peer_id=peer_id)`
- **Pre-response**: `session.representation()` -> prepend to system prompt
- **Post-response**: `peer.chat(f"Given this turn, what do we know about the user?")` -> `session.add_messages([derived_msg])`
- **NL query**: `peer.chat("What coding language does this user prefer?")` -> returns derived answer

| Pattern | When to use |
|---------|-------------|
| SQLite backend | Local, dev, single-node; zero-config |
| pgvector backend | Production, Postgres infra, vector search needed |
| Custom collections | Domain-specific fact categories beyond default 3 |
| Short compaction (20 turns) | Support agents with high message volume |
| Long compaction (100 turns) | Low-volume daily copilots |

## Anti-Patterns
| Anti-Pattern | Why it fails |
|-------------|-------------|
| Using entity_memory for the user | entity_memory lacks dialectic loop and workspace isolation |
| Storing raw message content | user_model stores DERIVED facts, not raw transcripts |
| No compaction cadence | Collections grow unbounded; inject cost > grounding benefit |
| Skipping pre-response insight | Defeats the Honcho pattern entirely; stateless behavior |
| Single generic collection | Loss of retrieval precision across fact categories |
| PII in version-controlled artifact | Security violation; store PII only in secure backend |

## Application
1. Create peer: `peer_id` + `workspace` + 3+ Collections
2. Configure dialectic: `pre_response_insight=true`, `post_response_derive=true`, `compaction_cadence_turns=50`
3. Choose storage: SQLite (default) or pgvector (production)
4. Set retention: `messages_ttl_days=365`, `derived_facts_ttl_days=null`
5. Implement loop: add_messages -> representation -> generate -> derive -> write back
6. Validate: id pattern, collections non-empty, dialectic configured, quality null

## References
- plastic-labs/honcho: honcho.dev -- Peer/Session/Collection/Document API
- multi-agent: agentic memory substrate with user modeling
- Zep: zep.dev -- user fact graph, per-session entity extraction
- MemGPT/Letta: memory-augmented agents, archival and working memory
- Cognitive science: mental model theory (Johnson-Laird, 1983) -- internal model predicts behavior

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[kc_user_model]] | sibling | 0.72 |
| [[user-model-builder]] | downstream | 0.58 |
| [[bld_orchestration_user_model]] | downstream | 0.51 |
| [[bld_architecture_user_model]] | downstream | 0.51 |
