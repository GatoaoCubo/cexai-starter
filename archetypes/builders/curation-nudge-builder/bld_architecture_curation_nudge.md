---
id: p11_arch_curation_nudge
kind: component_map
pillar: P11
llm_function: CONSTRAIN
purpose: F1 CONSTRAIN structural architecture for curation_nudge
quality: null
title: "Architecture: Curation Nudge"
version: "1.0.0"
author: n03_builder
tags: [architecture, curation_nudge, builder, p11, memory]
domain: "curation_nudge construction"
created: "2026-04-18"
updated: "2026-04-18"
tldr: "F1 CONSTRAIN structural architecture for curation_nudge"
8f: "F4_reason"
keywords: [curation_nudge construction, curation nudge, architecture, curation_nudge, builder, memory, component relationships, data flow, pillar placement]
density_score: 0.89
related:
 - curation-nudge-builder
 - cn_{{trigger}}
---
## Position in CEX Architecture

```
P10 Memory
 user_model (Honcho) <-- long-term model that nudges feed
 entity_memory <-- destination for discrete entities
 MEMORY.md <-- primary flat-text destination (CEX auto-memory)

P11 Feedback
 curation_nudge <-- THIS KIND
 triggers -> agent ask <-- proactive self-prompt
 feeds -> entity_memory <-- when destination=entity_memory
 feeds -> MEMORY.md <-- when destination=MEMORY.md
 feeds -> knowledge_card <-- when destination=knowledge_card
 peer -> guardrail <-- blocks (vs. nudge which asks)
 peer -> quality_gate <-- pass/fail (vs. nudge which is informational)

P04 Tools
 notifier <-- external broadcast (vs. nudge which is in-session)
```

## Component Relationships

| Component | Relationship | Direction |
|-----------|-------------|-----------|
| `MEMORY.md` (P10) | primary destination for confirmed nudges | P11 -> P10 |
| `entity_memory` (P10) | structured destination for discrete entities | P11 -> P10 |
| `knowledge_card` (P10) | document destination for rich observations | P11 -> P10 |
| `user_model` (P10) | long-term preference model (Honcho) that aggregates nudge output | P11 -> P10 |
| `guardrail` (P11) | sibling: blocks action (nudge asks) | P11 sibling |
| `quality_gate` (P11) | sibling: pass/fail on score (nudge is informational) | P11 sibling |
| `notifier` (P04) | sibling: external broadcast (nudge is in-session) | P04 sibling |
| `memory_summary` (P10) | companion: compresses after nudges accumulate | P10 companion |

## Lifecycle in 8F Pipeline

```
F3 INJECT (context assembly):
 Agent assembles context from memory, tools, examples
 curation_nudge monitors: has threshold been reached?
 IF threshold_reached AND min_interval_turns_elapsed:
 fire: present prompt_template with {{observation}} substituted

F4 REASON (planning):
 Agent self-evaluates: is this observation worth persisting?
 IF confirmed: write to target_memory.destination
 IF rejected: increment rejection counter, decrement max_per_session budget

F8 COLLABORATE (post-build):
 End-of-session nudge: scan F3-F8 for unpersisted learnings
 fire: "Notei X nesta sessao. Persistir em MEMORY.md?"
 Session summary nudge -- highest-value nudge in the pipeline
```

## Data Flow

```
Trigger event (turn N, fact observed, tool called, correction received)
 |
 v
curation_nudge evaluates:
 - trigger.type matches event type?
 - current_count >= trigger.threshold?
 - turns_since_last_nudge >= cadence.min_interval_turns?
 - session_nudge_count < cadence.max_per_session?
 |
 v
Decision: FIRE | SKIP
 |
 FIRE: present prompt_template ({{observation}} substituted at runtime)
 SKIP: increment counter, check next event
 |
 On confirmation: write to target_memory.destination
 On rejection: log, continue session
```

## Pillar Placement
- **Pillar**: P11 (Feedback) -- proactive quality and learning infrastructure
- **Layer**: governance (not runtime, not content)
- **Owner nucleus**: N04 (knowledge/memory)
- **LLM function**: GOVERN -- evaluates trigger conditions and gates persistence

## Naming Pattern
```
p11_cn_{{trigger_type}}.yaml
```
Lives in nucleus P11 directories or shared `.cex/nudges/` for cross-nucleus use.

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[curation-nudge-builder]] | related | 0.49 |
| [\[cn_`{{trigger}}`\]] | related | 0.48 |
