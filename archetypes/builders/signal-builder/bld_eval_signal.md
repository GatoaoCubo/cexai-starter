---
kind: quality_gate
id: p11_qg_signal
pillar: P11
llm_function: GOVERN
purpose: Golden and anti-examples of signal artifacts
pattern: few-shot learning for minimal orchestration events
quality: null
title: 'Gate: Signal'
version: 1.0.0
author: builder
tags:
- eval
- P11
- quality_gate
- examples
tldr: Gates ensuring signal specs define an exhaustive status enum, emitter identity,
  timestamp, and minimal payload with no embedded business logic.
domain: signal
created: '2026-03-27'
updated: '2026-03-27'
8f: "F7_govern"
density_score: 0.85
related:
  - signal-builder
  - bld_knowledge_card_signal
  - p03_ins_signal_builder
  - bld_architecture_signal
  - bld_schema_signal
---
## Quality Gate

## Definition
A signal is an atomic event emitted by one agent and consumed by another or a monitor. It carries a status, an emitter identity, a timestamp, and an optional minimal payload. A signal passes this gate when any consumer could parse and act on it without contacting the emitter, the status enum covers all terminal and non-terminal states, and the payload contains no business logic — only status data.
## HARD Gates
Failure on any HARD gate = immediate REJECT regardless of score.
| ID  | Check | Rationale |
|-----|-------|-----------|
| H01 | Frontmatter parses as valid YAML with no syntax errors | Unparseable file cannot be indexed or validated |
| H02 | `id` matches the file's directory namespace (`signal-builder/...`) | Mismatched IDs cause routing failures |
| H03 | `id` value equals the filename stem (slug portion) | Filename and ID must be the same addressable key |
| H04 | `kind` is exactly `signal` (literal match, no variation) | Kind drives the loader; wrong literal silently misroutes |
| H05 | `quality` field is `null` (not filled by author) | Quality is assigned by this gate, not self-reported |
| H06 | All required frontmatter fields present: id, kind, pillar, title, version, created, updated, author, domain, tags, tldr | Incomplete frontmatter breaks downstream consumers |
## SOFT Scoring
Dimensions are weighted; total normalized weight = 100%.
| # | Dimension | Weight | 1 (Poor) | 5 (Good) | 10 (Excellent) |
|---|-----------|--------|----------|----------|----------------|
| 1 | density >= 0.80 (content per token ratio) | 1.0 | Padded with filler prose | Mostly substantive | No filler; every sentence carries information |
| 2 | Payload is minimal JSON (only fields required for consumers to act; no verbose metadata) | 1.0 | Large nested payload | Moderate size | Flat structure, <= 10 fields, no nested objects except optional extension |
| 3 | Status enum is exhaustive (covers all reachable states including error sub-types) | 1.0 | Only happy-path statuses | Happy path + generic error | All terminal states + progress states + known error variants |
| 4 | Consumer expectations documented (who reads this signal and what they do per status) | 1.0 | No consumers listed | Consumers named | Consumers named + action per status per consumer |
| 5 | Idempotency considered (spec states whether duplicate signals are safe or must be deduplicated) | 1.0 | No mention | Noted as a concern | Explicit idempotency ruling with dedup key if required |
| 6 | Tags include `signal` | 0.5 | Missing | Present but misspelled | Exactly `signal` in tags list |

## Examples

# Examples: signal-builder
## Golden Example
INPUT: "Emit completion signal for codex after finishing signal-builder"
OUTPUT (`p12_sig_agent_group_complete.json`):
```json
{
  "agent_group": "codex",
  "status": "complete",

  "quality_score": 9.2,
  "timestamp": "2026-03-26T10:45:00-03:00",
  "task": "signal-builder",
  "artifacts": [

    "archetypes/builders/signal-builder/MANIFEST.md",
    "archetypes/builders/signal-builder/SCHEMA.md"
  ],
  "artifacts_count": 13,

  "commit_hash": "abc1234",
  "message": "13 builder spec files created and validated"
}
```
WHY THIS IS GOLDEN:
1. filename follows `p12_sig_{event}.json`
2. JSON payload is atomic and machine-readable
3. required fields are present and typed correctly
4. optional fields are compact and useful for monitors
5. no handoff instructions, routing rules, or workflow logic
## Golden Progress Example
OUTPUT (`p12_sig_batch_progress.json`):
```json
{
  "agent_group": "edison",
  "status": "progress",

  "quality_score": 8.4,
  "timestamp": "2026-03-26T11:00:00-03:00",
  "task": "wave2_batch",
  "progress_pct": 60,

  "message": "6 of 10 artifacts validated"
}
```
WHY THIS PASSES:
1. `progress_pct` only appears with `status=progress`
2. message stays short
3. payload remains a single event snapshot
## Anti-Example
BAD OUTPUT (`p12_sig_dispatch.yaml`):
```yaml
agent_group: codex
status: complete
keywords:

  - orchestration
  - routing
next_steps:
  - edit README

  - commit changes
```
FAILURES:
1. wrong machine format: YAML instead of JSON
2. no `quality_score`
3. no `timestamp`
4. includes routing keywords -> `dispatch_rule` drift
5. includes action list -> `handoff` drift

### S_RELATED: Cross-Reference Check (SOFT)
- [ ] `related:` frontmatter field populated (3-15 entries)
- [ ] `## Related Artifacts` section present in artifact body
- [ ] At least 1 upstream and 1 downstream reference
- Penalty: -0.3 if empty (does not block, encourages wiring)
