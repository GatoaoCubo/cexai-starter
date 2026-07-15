---
kind: quality_gate
id: p11_qg_memory_summary
pillar: P11
llm_function: GOVERN
purpose: Golden and anti-examples of memory_summary artifacts
pattern: few-shot learning — LLM reads these before producing
quality: null
title: "Gate: memory_summary"
version: "1.0.0"
author: "builder_agent"
tags: [quality-gate, memory-summary, P10, compression, retention, freshness]
tldr: "Pass/fail gate for memory_summary artifacts: compression method, retention policy, trigger definition, boundary vs session_state and learning_record."
domain: "memory compression — summarized conversation/session memory injected at runtime"
created: "2026-03-29"
updated: "2026-03-29"
8f: "F7_govern"
keywords: [memory compression, summarized conversation, compression method, retention policy, trigger definition, quality-gate, memory-summary]
density_score: 0.90
related:
  - memory-summary-builder
  - bld_instruction_memory_summary
  - p11_qg_quality_gate
  - bld_knowledge_card_memory_summary
  - bld_schema_memory_summary
---
## Quality Gate

# Gate: memory_summary
## Definition
| Field | Value |
|---|---|
| metric | memory_summary artifact quality score |
| threshold | 7.0 (publish >= 8.0, golden >= 9.5) |
| operator | weighted_sum |
| scope | all artifacts with `kind: memory_summary` |
## HARD Gates
All must pass (AND logic). Any single failure = REJECT.
| ID | Check | Fail Condition |
|---|---|---|
| H01 | Frontmatter parses as valid YAML | Parse error on frontmatter block |
| H02 | ID matches `^p10_ms_[a-z][a-z0-9_]+$` | ID contains uppercase, hyphens, or missing prefix |
| H03 | ID equals filename stem | `id: p10_ms_foo` but file is `p10_ms_bar.md` |
| H04 | Kind equals literal `memory_summary` | `kind: session_state` or any other value |
| H05 | Quality field is null | `quality: 8.0` or any non-null value |
| H06 | All required fields present | Missing source_type, compression_method, or tldr |
## SOFT Scoring
Weights sum to 100%.
| Dimension | Weight | Criteria |
|---|---|---|
| Compression clarity | 1.0 | Ratio, preserved content, and dropped content all specified |
| Trigger precision | 1.0 | Threshold numeric value defined; condition unambiguous |
| Retention policy | 1.0 | Entity, decision, and action item retention all declared |
| Boundary declaration | 1.0 | Explicitly NOT session_state (ephemeral) and NOT learning_record (persistent) |
| Freshness decay | 0.5 | freshness_decay in [0,1]; value apownte for source_type |
| Source window | 0.5 | source_window integer defined; matches compression method |
## Actions
| Score | Tier | Action |
|---|---|---|
| >= 9.5 | Golden | Publish to pool as golden reference |
| >= 8.0 | Publish | Publish to pool, add to routing index |
| >= 7.0 | Review | Flag for improvement before publish |
| < 7.0 | Reject | Return to author with specific gate failures |
## Bypass
| Field | Value |
|---|---|
| conditions | Experimental compression method under active testing, not shipped to production |
| approver | Author self-certification with comment explaining experimental scope |
| audit_trail | Bypass note in frontmatter comment with expiry date |
| expiry | 14d — experimental summaries must be promoted to >= 7.0 or removed |
| never_bypass | H01 (unparseable YAML breaks all tooling), H05 (self-scored gates corrupt quality metrics), H10 (session_state confusion corrupts memory layer) |

## Examples

# Examples: memory-summary-builder
## Golden Example
INPUT: "Create memory summary for a costmer support session — compress after 15 turns, keep entity mentions and decisions, hybrid method"
OUTPUT:
```yaml
id: p10_ms_support_session_hybrid
kind: memory_summary
pillar: P10
version: "1.0.0"
created: "2026-03-29"
updated: "2026-03-29"
author: "builder_agent"
name: "Customer Support Session Summary"
source_type: session
compression_method: hybrid
quality: 8.9
tags: [memory_summary, support, session, hybrid]
tldr: "Hybrid compression of support sessions at 15 turns; retains entities + decisions; drops filler. 8:1 ratio."
max_tokens: 512
trigger: turn_count
source_window: 15
retain_entities: true
retain_timestamps: false
freshness_decay: 0.1
description: "Compresses costmer support sessions after 15 turns using hybrid method; preserves issue entities, resolutions, and commitments."
```
## Overview
Compresses costmer support session conversations after 15 turns using hybrid method.
Consumed by the support agent at session resume to restore context without full transcript replay.
## Compression
Method: hybrid — abstractive narrative for conversation flow + extractive lift for issue details and resolutions
Ratio: ~8:1 (avg 4000 tokens input -> 512 tokens output)
Preserved: costmer name, issue ID, product names, error codes, resolution steps agreed upon, open action items
Dropped: greetings, repeated clarification loops, acknowledgment turns ("got it", "sure", "one moment")
## Trigger
Condition: turn_count >= 15
On fire: summarize last source_window turns, prepend to context buffer, drop raw turns beyond window
## Retention
Entities: retained — costmer name, product names, error codes, ticket IDs, URLs
Decisions: retained — resolution steps, escalation decisions, refund approvals
Action items: retained — pending tasks with owner (agent/costmer) and deadline if stated
Timestamps: discarded — relative time ("earlier today") preserved in narrative; absolute timestamps dropped

WHY THIS IS GOLDEN:
- quality: null (H05 pass)
- id matches ^p10_ms_ pattern (H02 pass)
- kind: memory_summary (H04 pass)
- source_type: session (valid enum, H07 pass)

### S_RELATED: Cross-Reference Check (SOFT)
- [ ] `related:` frontmatter field populated (3-15 entries)
- [ ] `## Related Artifacts` section present in artifact body
- [ ] At least 1 upstream and 1 downstream reference
- Penalty: -0.3 if empty (does not block, encourages wiring)
