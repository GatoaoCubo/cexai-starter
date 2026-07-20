---
id: p11_cn_research_n01
kind: curation_nudge
pillar: P11
nucleus: n01
title: "N01 Research Curation Nudges"
version: 1.0.0
quality: null
tags: [curation_nudge, n01, research, memory_persistence]
tldr: "Proactive nudges that fire when N01 detects an opportunity to strengthen the knowledge base: new source found, claim missing a citation, stale fact, or a competitive gap. Nudges ASK -- they never block."
keywords: [knowledge base, curation_backlog, nudge_false_positive_rate, stale_fact_detected, new_source_detected]
density_score: 0.92
related:
  - curation-nudge-builder
  - p11_qg_research_n01
  - p07_bm_research_quality
  - kc_research_methods
updated: "2026-04-22"
---

## Purpose

N01 nudges are intelligence-oriented: they fire when the system detects an
opportunity to strengthen the knowledge base, not just to persist conversation
state. The Analytical Envy lens means every new source triggers a question:
"Do we have this? Is ours better? Do we need it?"

Nudges ASK. They never block a build the way a `guardrail` does, and they
never carry a pass/fail score the way a `quality_gate` does -- see the
boundary note in the kind registry.

## Nudge Flavors

| Flavor | Trigger | Prompt Template |
|--------|---------|----------------|
| `new_source_detected` | URL/DOI not in existing knowledge corpus | "New source found: {{source}}. Add to intelligence KC?" |
| `claim_without_citation` | Assertion lacking provenance | "Claim made: '{{claim}}'. Source needed -- add citation?" |
| `stale_fact_detected` | last_verified > 90 days | "Fact '{{fact}}' unverified since {{date}}. Refresh?" |
| `gap_vs_peer` | A peer/competitor artifact has data this corpus lacks | "Coverage gap: {{gap}}. Harvest and persist?" |

## Priority Escalation Rules

Not all nudges are equal. N01 ranks nudge urgency by research impact:

| Priority | Flavor | Escalation Action | SLA |
|----------|--------|-------------------|-----|
| P1 (high) | `stale_fact_detected` on high-traffic knowledge cards | Nudge + flag for next improvement sweep | Within 48h |
| P2 (normal) | `claim_without_citation` in any N01 artifact | Standard nudge cycle | Within 1 week |
| P3 (low) | `new_source_detected` for low-priority topics | Batch into periodic supplement update | Next cycle |

## Integration with Research Workflow

```
Nudge fires -> N01 evaluates priority
 |
 P0: gap_vs_peer (active research thread)
 | -> auto-read the peer/competitor artifact
 | -> compare with current knowledge
 | -> if gap confirmed: create a knowledge-card update task
 | -> if gap false positive: log to nudge_false_positive_rate
 |
 P1-P3: standard curation
 -> queue in curation_backlog
 -> process during next research session
```

## Anti-Patterns (Nudge Fatigue)

| Anti-Pattern | Symptom | Mitigation |
|-------------|---------|-----------|
| Nudge storm | >5 nudges in 3 turns, user ignores all | Batch related nudges into single summary |
| False positive spiral | >40% of nudges dismissed as irrelevant | Tighten threshold by +2 per dismissal; reset after 10 sessions |
| Stale-fact churn | Same fact re-nudged after user confirmed it | Mark fact as `user_verified` with 180-day TTL |
| Single-flavor fixation | All nudges are `gap_vs_peer` | Cap that flavor at 2/session; interleave with source quality |

## Cadence

| Parameter | Value | Reason |
|-----------|-------|--------|
| `min_interval_turns` | 3 | Research sessions are shorter, denser than generic sessions |
| `max_per_session` | 5 | More nudge types warrant a higher cap |
| `threshold` | 7 | N01 fires earlier -- envy is impatient |
| `false_positive_cap` | 0.40 | Above 40%, auto-tighten threshold |

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[curation-nudge-builder]] | related | 0.34 |
| [[p11_qg_research_n01]] | sibling | 0.30 |
| [[p07_bm_research_quality]] | related | 0.26 |
| [[kc_research_methods]] | upstream | 0.22 |
