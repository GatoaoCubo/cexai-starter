---
id: p11_mem_curation_nudge
kind: procedural_memory
pillar: P10
llm_function: INJECT
purpose: Learned patterns and anti-patterns for curation_nudge builder
quality: null
title: "Memory: Curation Nudge Builder"
version: "1.0.0"
author: n03_builder
tags: [memory, curation_nudge, builder, p10, anti_patterns]
domain: "curation_nudge construction"
created: "2026-04-18"
updated: "2026-04-18"
tldr: "Learned patterns and anti-patterns for curation_nudge builder"
8f: "F3_inject"
keywords: [curation_nudge construction, curation nudge builder, memory, curation_nudge, builder, anti_patterns, learned patterns, destination affinity, session profile tuning]
density_score: 0.88
related:
 - cn_{{trigger}}
 - curation-nudge-builder
---
## Learned Patterns

### Pattern 1: Trigger-Destination Affinity
```
turn_count -> MEMORY.md (general preferences, conventions)
density_threshold -> entity_memory (structured entities accumulate under research)
tool_call_count -> MEMORY.md (agentic conventions, tool preferences)
user_correction -> MEMORY.md (preference corrections are flat-text entries)
```
**Why:** Each trigger type reflects a different observation modality. Matching destination
to trigger prevents over-engineering (e.g., don't create a knowledge_card for a simple preference).

### Pattern 2: Session Profile Tuning
```
Long research session: density_threshold=5, max_per_session=2 (few high-signal nudges)
Short coding session: tool_call_count=15, max_per_session=1 (one end-of-session nudge)
Preference learning: user_correction=1, min_interval_turns=3 (every correction, not spam)
General conversation: turn_count=10, max_per_session=3 (default)
```
**Why:** One-size nudge degrades all session types. Session profile awareness maximizes nudge value.

### Pattern 3: Prompt Template Localization
```
PT-BR sessions: "Notei [observation]. Devo persistir em MEMORY.md?"
EN sessions: "I noticed [observation]. Should I persist this to MEMORY.md?"
Mixed: Use PT-BR (CEX default); agents understand both
```
**Why:** Native-language prompts reduce agent processing overhead. CEX defaults to PT-BR.

## Anti-Patterns (do NOT repeat)

| Anti-Pattern | Root Cause | Fix |
|-------------|-----------|-----|
| Threshold below 5 | Misunderstanding of minimum | Enforce H02: threshold >= 5 |
| Missing observation placeholder | Template copy-paste without observation var | Enforce H05: must contain placeholder |
| destination=slack_channel | Confusion with notifier pattern | Enforce H04: only 3 valid destinations |
| Nudge that blocks | Trying to use nudge as guardrail | Route to guardrail-builder |
| max_per_session=0 | Attempting to disable nudging via nudge | Use lifecycle_rule or env var CN_MAX_PER_SESSION=0 |

## Calibration Data ( deployments)

| Parameter | Too Low | Optimal | Too High |
|-----------|---------|---------|---------|
| threshold (turn_count) | <5: spam | 8-12: good | >20: misses knowledge |
| min_interval_turns | <3: chained spam | 5-7: good | >15: gaps persist |
| max_per_session | 0: disabled | 2-4: good | >6: context saturation |

## Collaboration Lessons

1. **N04 owns destinations** -- always coordinate with N04 when creating new memory sinks
2. **MEMORY.md is the default** -- unless caller explicitly needs structured data, use flat text
3. **user_correction is highest signal** -- even one correction warrants immediate nudge
4. **End-of-session is the best nudge slot** -- F8 COLLABORATE should always fire a nudge

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [\[cn_`{{trigger}}`\]] | downstream | 0.53 |
| [[curation-nudge-builder]] | downstream | 0.51 |
