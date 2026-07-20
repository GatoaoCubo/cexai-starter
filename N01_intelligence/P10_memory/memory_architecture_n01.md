---
id: memory_architecture_n01
kind: memory_architecture
pillar: P10
nucleus: n01
title: "N01 Intelligence Memory Architecture"
version: 1.0.0
created: 2026-07-20
author: n01_intelligence
domain: research-intelligence
quality: null
tags: [memory_architecture, n01, memory_layers, persistence, retrieval, analytical_envy]
tldr: "4-layer memory architecture for N01: working (session context), episodic (research sessions), semantic (KCs + entities), procedural (methods). Maps storage, retrieval, and decay rules for each layer."
keywords: [working memory, episodic memory, semantic memory, procedural memory, knowledge index, entity memory, memory summary, runtime state]
density_score: 0.91
updated: "2026-07-20"
related:
  - procedural_memory_n01
  - p04_retr_n01
  - reasoning_strategy_n01
  - self_improvement_loop_n01
  - nucleus_def_n01
---

<!-- 8F: F1 constrain=P10/memory_architecture F4 reason=Analytical Envy compounding requires a memory architecture, not just ad-hoc storage -- the structure IS the strategic advantage F8 collaborate=N01_intelligence/P10_memory/memory_architecture_n01.md -->

## Purpose

Four types of memory serve different N01 research needs:
1. What am I doing RIGHT NOW? (working memory)
2. What did I find LAST TIME? (episodic memory)
3. What do I KNOW? (semantic memory)
4. HOW do I do this? (procedural memory)

Without explicit architecture, N01 conflates these -- slow, expensive, error-prone.
With explicit layers, each memory type has optimal storage, retrieval, and decay.

## Memory Layer Architecture

### Layer 1: Working Memory (Session Context)

| Property | Value |
|----------|-------|
| Storage | in-context (no disk write during session) |
| Scope | current session only |
| Capacity | model context window subset |
| Content | task goal, active sources, interim findings, chain-of-thought |
| Decay | session end = total loss |
| Persistence | summarize to L2 at session end |

Key contents:
- Current research goal and atomic questions (from the DSTCS DECOMPOSE step, `reasoning_strategy_n01.md`)
- Source pool being triangulated
- Interim confidence scores and findings
- Tool call results not yet synthesized

### Layer 2: Episodic Memory (Research Sessions)

| Property | Value |
|----------|-------|
| Storage | `N01_intelligence/P10_memory/sessions/{date}_{mission}.yaml` |
| Scope | per-session research record |
| Capacity | unlimited (disk) |
| Content | session goal, key findings, entities discovered, quality score |
| Decay | 90 days retention; archive at 365 days |
| Persistence | written at session end (wire a session-lifecycle hook if you want this automatic) |

Schema:
```yaml
session_id: "{date}_{mission_slug}"
goal: "string"
duration_minutes: int
sources_consulted: int
entities_discovered: ["string"]
key_findings: [{finding, confidence, sources}]
quality_score: float
artifacts_created: ["string"]
next_session_context: "string"
```

### Layer 3: Semantic Memory (Persistent Knowledge)

| Property | Value |
|----------|-------|
| Storage | `N01_intelligence/P01_knowledge/*.md` + entity files |
| Scope | permanent (until explicitly updated or archived) |
| Capacity | unlimited |
| Content | knowledge_cards, entity profiles, market data |
| Decay | manual review trigger at 90-day staleness |
| Retrieval | `p04_retr_n01.md` (`_tools/cex_retriever.py`) |

Sub-types:
- Declarative: facts about the world (KCs)
- Entity: profiles of companies, people, products
- Structural: taxonomy, glossary, ontology

### Layer 4: Procedural Memory (Methods)

| Property | Value |
|----------|-------|
| Storage | `N01_intelligence/P03_prompt/*.md` + `P04_tools/*.md` |
| Scope | permanent (versioned) |
| Capacity | unlimited |
| Content | reasoning strategies, search strategies, evaluation protocols |
| Decay | version bump when superseded |
| Retrieval | direct path reference (not indexed search) |

Sub-types:
- Reasoning: `reasoning_strategy_n01.md`
- Retrieval: `p04_retr_n01.md`
- Evaluation: `benchmark_suite_n01.md`, `p07_judge_n01.md`

## Memory Lifecycle

```
SESSION START:
  L4 (procedural) -> load always (fast, deterministic)
  L3 (semantic) -> query retriever for relevant context
  L2 (episodic) -> check for recent sessions on same topic
  L1 (working) -> initialize empty

DURING SESSION:
  L1 -> accumulate findings, chain-of-thought

SESSION END:
  L1 -> summarize to L2 (session record)
  L1 -> update L3 (KCs, entities if new knowledge found)
  L2 -> archive if > 90 days

STALENESS CHECK (weekly):
  L3 -> scan for entities/KCs > 90 days -> flag for refresh
  L2 -> archive sessions > 90 days
```

## Retrieval Priority (by task type)

| Task | L1 | L2 | L3 | L4 |
|------|----|----|----|-----|
| New research topic | empty | check recent | query KCs+entities | load all |
| Follow-up research | session context | load previous session | load related KCs | load strategy |
| Entity lookup | check in-context | no | load entity profile | no |
| Method question | no | no | no | load relevant method |

## Comparison vs. Alternatives

| Architecture | Layers | Retrieval Speed | Staleness Control | N01 Fit |
|-------------|--------|----------------|-----------------|---------|
| No architecture (ad-hoc) | 1 | O(n) scan | none | fail |
| Session-only (no persistence) | 1 | N/A | N/A | loses compounding |
| External vector DB | 2-3 | fast | manual | requires cloud |
| This 4-layer | 4 | L3/L4 fast | built-in decay rules | optimal |

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[procedural_memory_n01]] | sibling | 0.43 |
| [[p04_retr_n01]] | upstream | 0.38 |
| [[reasoning_strategy_n01]] | related | 0.34 |
| [[self_improvement_loop_n01]] | related | 0.30 |
| [[nucleus_def_n01]] | related | 0.26 |
