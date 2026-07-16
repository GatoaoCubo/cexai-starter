---
id: p11_qg_curation_nudge
kind: quality_gate
pillar: P11
llm_function: GOVERN
purpose: F7 GOVERN quality gates for curation_nudge artifacts
quality: null
title: "Quality Gate: Curation Nudge Builder"
version: "1.0.0"
author: n03_builder
tags: [quality_gate, curation_nudge, builder, p11, memory, f7]
domain: "curation_nudge construction"
created: "2026-04-18"
updated: "2026-04-18"
tldr: "F7 GOVERN quality gates for curation_nudge artifacts"
8f: "F7_govern"
keywords: [curation_nudge construction, quality gate, curation nudge builder, quality_gate, curation_nudge, builder, memory]
density_score: 0.91
target_kind: curation_nudge
delivery_threshold: 0.85
bypass_policy: owner
related:
 - p11_ins_curation_nudge
 - n00_curation_nudge_manifest
 - curation-nudge-builder
 - p11_schema_curation_nudge
 - kc_curation_nudge
---
## Quality Gate

## HARD Gates (all must pass)

| ID | Criterion | Failure Action |
|----|-----------|---------------|
| H01 | `kind == "curation_nudge"` | block |
| H02 | `trigger.threshold >= 5` (positive integer, minimum 5) | block |
| H03 | `trigger.type` in `{turn_count, density_threshold, tool_call_count, user_correction}` | block |
| H04 | `target_memory.destination` in `{MEMORY.md, entity_memory, knowledge_card}` | block |
| H05 | `prompt_template` contains `{{observation}}` | block |
| H06 | `quality == null` (never self-score) | block |

## SOFT Gates (weighted, sum = 1.0)

| ID | Criterion | Weight | Scoring Method |
|----|-----------|--------|---------------|
| S01 | Boundaries section present with all 4 NOT-items | 0.25 | binary |
| S02 | `cadence.min_interval_turns >= 5` AND `cadence.max_per_session <= 5` | 0.25 | binary |
| S03 | Usage in agent session code block present in body | 0.25 | binary |
| S04 | `tags` includes `hermes_origin` | 0.25 | binary |

## Scoring Formula

```
aggregate_score = S01*0.25 + S02*0.25 + S03*0.25 + S04*0.25
PASS: all H gates pass AND aggregate_score >= 0.85
FAIL: any H gate fails OR aggregate_score < 0.85
```

## Actions

| Outcome | Consequence |
|---------|-------------|
| PASS | Artifact proceeds to F8 COLLABORATE (compile + commit + signal) |
| H-FAIL | Artifact returned with specific HARD gate failure detail; fix and retry |
| S-FAIL | Artifact returned with soft gate breakdown; improve and retry (max 2 retries) |

## Bypass Policy

- Who may override: `owner` (N03 builder or N04 knowledge nucleus)
- Conditions: only H06 (quality: null) may be bypassed in peer-review mode (peer sets actual score)
- All other HARD gates: no bypass permitted
- Audit: log bypass with actor, timestamp, and justification

## Examples

## Golden Example 1: Turn Count Nudge (default)

```yaml
---
id: cn_turn_count
kind: curation_nudge
pillar: P11
title: "Curation Nudge: Every 10 Turns"
trigger:
 type: turn_count
 threshold: 10
```yaml
curation_nudge:
 nudge_ref: cn_turn_count
 fire_every: 10 turns
 on_confirm: write_to MEMORY.md
 on_reject: continue_session
```
```

**Why it works:** threshold=10 is well above the minimum (5), cadence prevents spam,
prompt_template contains the observation placeholder (H05), all 4 boundary NOT-items present.

## Golden Example 2: User Correction Nudge

```yaml
---
id: cn_user_correction
kind: curation_nudge
pillar: P11
title: "Curation Nudge: User Correction"
trigger:
 type: user_correction
 threshold: 1
```
**Why it works:** `user_correction` trigger uses threshold=1 (correct -- fire on every correction).
min_interval_turns=3 prevents rapid-fire corrections from flooding MEMORY.md.
prompt_template includes the observation placeholder required by H05.

## Golden Example 3: Density Threshold for Research Sessions

```yaml
---
id: cn_density_threshold
kind: curation_nudge
pillar: P11
title: "Curation Nudge: High Information Density"
trigger:
 type: density_threshold
 threshold: 5
```
**Why it works:** density_threshold fires when the agent observes 5 new facts -- ideal for
research sessions. max_per_session=2 is conservative; research sessions can be long and
frequent nudges break flow. Destination is entity_memory (structured, not flat text file).

## Anti-Example 1: Threshold Below Minimum

```yaml
---
id: cn_too_frequent
kind: curation_nudge
trigger:
 type: turn_count
 threshold: 2
prompt_template: "Persistir?"
---
```
**Why it fails (H02 + H05):** threshold=2 is below the minimum of 5 -- fires every 2 turns,
spam-level frequency. Also, prompt_template is missing the observation placeholder (H05) --
runtime substitution fails silently, producing generic unactionable nudges.

## Anti-Example 2: Wrong boundary -- using nudge as a guardrail

```yaml
---
id: cn_block_dangerous_action
kind: curation_nudge
trigger:
 type: turn_count
 threshold: 1
prompt_template: "BLOCK: {{observation}} is dangerous"
---
```
**Why it fails:** A nudge that fires every turn and says "BLOCK" is trying to be a guardrail.
Route to `guardrail-builder` instead. Nudges INFORM and ASK; they never block.

### S_RELATED: Cross-Reference Check (SOFT)
-  `related:` frontmatter field populated (3-15 entries)
-  `## Related Artifacts` section present in artifact body
-  At least 1 upstream and 1 downstream reference
- Penalty: -0.3 if empty (does not block, encourages wiring)
