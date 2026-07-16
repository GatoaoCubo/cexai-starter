---
id: kc_user_model
kind: knowledge_card
8f: F3_inject
pillar: P01
nucleus: n04
title: "KC: user_model"
version: 1.0.0
quality: null
tags: [user_model, honcho, dialectic, P10, cross_session, user_modeling]
keywords: [cross-session, dialectic representation, user_model, honcho dialectic pattern, vector-embedded, derived fact, durable collections, agentic memory substrate]
density_score: 0.91
upstream_sources: null
created: "2026-04-18"
updated: "2026-04-18"
author: n03_builder
tldr: "Cross-session dialectic user representation implementing Honcho pattern. SQLite default, pgvector optional. Pre/post-response insight loop per turn."
when_to_use: "When building persistent per-user memory that grows across sessions via the Honcho dialectic loop"
related:
  - user-model-builder
  - bld_architecture_user_model
---

## Executive Summary

`user_model` is a **cross-session dialectic representation of a human peer** -- preferences,
working style, inferred intent, and accumulated interaction context. It implements the
**Honcho dialectic pattern** (plastic-labs/honcho): after each turn, the agent queries what
the message reveals about the user, injects that insight into the response generation context,
then writes derived conclusions back to the peer's durable Collections.

The result is an AI system that grows a permanent, queryable mental model of each user without
requiring the user to re-explain their context on every session.

## Data Model

| Entity | Role | Cardinality |
|--------|------|-------------|
| Workspace | Top-level tenant namespace | 1 per deployment |
| Peer | Unified user/agent representation (THIS is user_model) | 1 per user |
| Session | Peer <-> Peer interaction container | many per Peer |
| Message | Atomic utterance in a session | many per Session |
| Collection | Named group of derived documents per Peer | 3+ per Peer |
| Document | Vector-embedded derived fact per Peer | many per Collection |

## Dialectic Loop (per conversation turn)

```
1. Turn arrives        -> session.add_messages([user_msg])
2. Pre-response query  -> peer.chat("given <msg>, what does this user want?") -> insight
3. Insight injected    -> prepended to generation context
4. Response generated  -> agent produces response with grounded user context
5. Post-derive         -> conclusions written back to peer.collections
6. Compaction (N turns)-> Collections summarized into durable derived facts
```

This loop creates a **self-improving user model**: the more sessions, the richer the context,
the more personalized the response, without requiring the user to repeat themselves.

## Storage Options

| Backend | Default | When to use |
|---------|---------|-------------|
| SQLite | YES | Local deployment, single-node, development |
| pgvector | optional | Production, vector similarity search at scale |
| turbopuffer | fallback-2 | Serverless vector search |
| lancedb | fallback-3 | Embedded vector DB, edge deployments |

Fallback chain: `sqlite -> turbopuffer -> lancedb`. pgvector is opt-in via `pgvector_enabled: true`.

## API Surface

| Method | Signature | Purpose |
|--------|-----------|---------|
| `peer.chat` | `peer.chat(query: str) -> str` | NL query against the user's derived fact graph |
| `session.context` | `session.context(token_limit: int) -> str` | Bounded context extraction |
| `session.add_messages` | `session.add_messages(msgs: list) -> None` | Ingest turn into session |
| `search` | `search(query: str, top_k: int) -> list[Document]` | Hybrid FTS + vector |
| `session.representation` | `session.representation() -> str` | Static insight string for prompt injection |

## Standard Collections

| Collection | Contents | Retention |
|------------|---------|-----------|
| preferences | Communication style, format preferences, output length | never purge |
| working_style | Domain knowledge level, tool preferences, workflow patterns | never purge |
| context_history | Per-session derived insights (compacted) | configurable TTL |

## Spec Table

| Property | Value |
|----------|-------|
| Pillar | P10 (Memory) |
| llm_function | INJECT |
| ID pattern | `^um_[a-z][a-z0-9_]+$` |
| Max bytes | 4096 |
| Naming | `p10_um_{{peer_id}}.md` |
| Storage default | SQLite |
| Quality target | 9.0+ |
| Upstream | Honcho dialectic pattern (peer/collection/document API) |

## Boundary Table (explicit distinctions)

| user_model IS | user_model IS NOT |
|--------------|-------------------|
| Cross-session dialectic record of a specific human | `entity_memory` (any entity -- org, product, place) |
| Derived from conversation turns via Honcho loop | `session_state` (ephemeral, resets each session) |
| One layer in the memory stack | `memory_architecture` (whole stack definition) |
| Description of a human peer | `agent_profile` (describes the AI, not the human) |
| Queryable via NL (`peer.chat`) | `episodic_memory` (raw event log, not derived model) |
| Workspace-scoped, multi-tenant | `entity_memory` (global, no workspace tenant) |

## Implementation Patterns

- **Pre-response injection**: before generating, call `session.representation()` -> prepend to system prompt as "What I know about this user: ..."
- **Post-response derivation**: after generating, call `peer.chat("What did this turn reveal about the user's preferences/working style?")` -> write result to Collection
- **Compaction**: every N turns, summarize collection documents into consolidated facts; discard raw turn data beyond TTL
- **Cold start**: new peers start with empty collections; dialectic loop begins accumulating from turn 1

## Anti-Patterns

| Anti-Pattern | Why it fails |
|-------------|-------------|
| Storing session_state in user_model | Pollutes durable record with ephemeral flags |
| Pre-populating without consent | Privacy violation; user_model must derive from actual interactions |
| Single collection for all facts | Loss of retrieval precision; separate preferences / style / history |
| No compaction cadence | Collection grows unbounded; inject cost exceeds grounding benefit |
| Skipping pre-response insight | Defeats the dialectic loop; reverts to stateless behavior |

## References
- Honcho: honcho.dev -- Peer/Session/Collection/Document API
- Zep memory server: similar per-user fact graph (different API, same pattern)
- MemGPT/Letta: memory-augmented agents with user modeling layer

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[bld_knowledge_user_model]] | sibling | 0.54 |
| [[bld_orchestration_user_model]] | downstream | 0.53 |
| [[user-model-builder]] | downstream | 0.53 |
| [[bld_architecture_user_model]] | downstream | 0.50 |
