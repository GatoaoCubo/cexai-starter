---
kind: quality_gate
id: p11_qg_session-state
pillar: P11
llm_function: GOVERN
purpose: Golden and anti-examples of session_state artifacts
pattern: few-shot learning for ephemeral session snapshots
quality: null
title: 'Gate: Session State'
version: 1.0.0
author: builder
tags:
- eval
- P11
- quality_gate
- examples
tldr: Gates ensuring session state specs define minimal checkpoint fields, realistic
  TTL, and a recovery protocol for partial or expired state.
domain: session_state
created: '2026-03-27'
updated: '2026-03-27'
last_reviewed: '2026-04-18'
8f: "F7_govern"
density_score: 0.85
related:
  - session-state-builder
  - bld_collaboration_session_state
  - bld_memory_session_state
  - bld_knowledge_card_session_state
  - p11_qg_runtime_state
---
## Quality Gate

## Definition
A session state spec describes an ephemeral snapshot of an in-progress interaction: which fields to capture, how long the snapshot lives, and how to restore a session from it. A spec passes this gate when the captured fields are the minimum necessary to resume work (not a full database dump), the TTL reflects the realistic session length, and partial or expired state has a defined recovery path rather than a hard failure.
## HARD Gates
Failure on any HARD gate = immediate REJECT regardless of score.
| ID  | Check | Rationale |
|-----|-------|-----------|
| H01 | Frontmatter parses as valid YAML with no syntax errors | Unparseable file cannot be indexed or validated |
| H02 | `id` matches the file's directory namespace (`session-state-builder/...`) | Mismatched IDs cause routing failures |
| H03 | `id` value equals the filename stem (slug portion) | Filename and ID must be the same addressable key |
| H04 | `kind` is exactly `session_state` (literal match, no variation) | Kind drives the loader; wrong literal silently misroutes |
| H05 | `quality` field is `null` (not filled by author) | Quality is assigned by this gate, not self-reported |
| H06 | All required frontmatter fields present: id, kind, pillar, title, version, created, updated, author, domain, tags, tldr | Incomplete frontmatter breaks downstream consumers |
## SOFT Scoring
Dimensions are weighted; total normalized weight = 100%.
| # | Dimension | Weight | 1 (Poor) | 5 (Good) | 10 (Excellent) |
|---|-----------|--------|----------|----------|----------------|
| 1 | density >= 0.80 (content per token ratio) | 1.0 | Padded with filler prose | Mostly substantive | No filler; every sentence carries information |
| 2 | Fields capture minimal necessary state (no redundant or derivable fields) | 1.0 | Many redundant fields | Some redundancy | Only fields that cannot be recomputed from stable data |
| 3 | TTL realistic for session length (not too short causing premature expiry, not too long accumulating stale state) | 1.0 | TTL not justified | Round-number guess | TTL derived from measured or estimated session duration |
| 4 | Recovery handles partial state (spec addresses incomplete snapshots, not just absent ones) | 1.0 | Only absent state handled | Partial noted, no procedure | Explicit partial-state recovery logic per missing field |
| 5 | No persistent data (all captured data is ephemeral; storage backend is volatile) | 1.0 | Persistent writes present or unclear | Noted as ephemeral | Explicit confirmation + storage backend is volatile (memory or cache) |
| 6 | Tags include `session-state` | 0.5 | Missing | Present but misspelled | Exactly `session-state` in tags list |

## Examples

# Examples: session-state-builder
## Golden Example
INPUT: "Capture session state for edison building wave 19 builders"
OUTPUT (`p10_ss_edison_wave19_build.yaml`):
```yaml
id: p10_ss_edison_wave19_build
kind: session_state
lp: P10
version: "1.0.0"
created: "2026-03-26"
updated: "2026-03-26"
author: "codex"
session_id: "edison_20260326_143000"
```
WHY THIS IS GOLDEN (19+ fields present):
- filename follows `p10_ss_{session}.yaml`
- YAML with proper frontmatter delimiters
- all 15 required fields present and typed correctly
- 10 optional fields add meaningful runtime context
## Anti-Example
BAD OUTPUT (`p10_ss_runtime.yaml`):
```yaml
id: p10_rs_edison_state
kind: runtime_state
lp: P10
agent: edison
routing_decisions:
  marketing: lily
  research: shaka
  build: edison
```
FAILURES:
1. wrong id prefix: `p10_rs_` instead of `p10_ss_` — violates H01 naming gate
2. wrong kind: `runtime_state` instead of `session_state` — violates H04 type integrity
3. missing `session_id` required field — violates H03 completeness
4. missing `status` required field — violates H03 and H05 lifecycle contract
5. missing `started_at` required field — violates H03 and H09 temporal integrity
6. missing `quality: null` — violates H03 and H06 self-score gate
7. missing `tags` and `tldr` required fields — violates H03 completeness
8. contains `routing_decisions`: persistent cross-session state — violates H08 boundary
9. contains `accumulated_scores`: cross-session accumulation — violates H08 boundary (learning_record drift)
10. contains `learned_patterns`: accumulated learning — violates H08 boundary (learning_record drift)

### S_RELATED: Cross-Reference Check (SOFT)
- [ ] `related:` frontmatter field populated (3-15 entries)
- [ ] `## Related Artifacts` section present in artifact body
- [ ] At least 1 upstream and 1 downstream reference
- Penalty: -0.3 if empty (does not block, encourages wiring)
