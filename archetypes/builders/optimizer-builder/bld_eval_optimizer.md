---
kind: quality_gate
id: p11_qg_optimizer
pillar: P11
llm_function: GOVERN
purpose: Golden and anti-examples of optimizer artifacts
quality: null
title: "Gate: optimizer"
version: "1.0.0"
author: "builder_agent"
tags:
  - "quality-gate"
  - "optimizer"
  - "P11"
  - "governance"
  - "performance"
  - "continuous-improvement"
tldr: "Gates for optimizer artifacts — metric direction, threshold ordering, and automatable action definitions."
domain: optimizer
created: "2026-03-27"
updated: "2026-03-27"
8f: "F7_govern"
keywords:
  - "gates for optimizer artifacts"
  - "metric direction"
  - "threshold ordering"
  - "and automatable action definitions"
  - "quality-gate"
  - "optimizer"
  - "governance"
density_score: 0.85
related:
  - optimizer-builder
---
## Quality Gate

# Gate: optimizer
## Definition
| Field     | Value                                             |
|-----------|---------------------------------------------------|
| metric    | threshold coherence + action automation coverage  |
| threshold | 8.0                                               |
| operator  | >=                                                |
| scope     | all optimizer artifacts (P11)                     |
## HARD Gates
All must pass. Failure on any = final score 0.
| Gate | Check | Why |
|------|-------|-----|
| H01 | YAML frontmatter parses valid YAML | Broken YAML = optimizer never triggers |
| H02 | id matches `^p11_opt_[a-z][a-z0-9_]+$` | Namespace compliance |
| H03 | id == filename stem | Brain search relies on this |
| H04 | kind == "optimizer" | Type integrity |
| H05 | quality == null | Never self-score |
| H06 | All required fields present: id, kind, pillar, version, created, updated, author, domain, quality, tags, tldr | Completeness |
## SOFT Scoring
| Gate | Check | Weight |
|------|-------|--------|
| S01 | tldr <= 160 chars, non-empty | 1.0 |
| S02 | tags is list, len >= 3, includes "optimizer" | 0.5 |
| S03 | density_score >= 0.80 | 0.5 |
| S04 | thresholds are correctly ordered: minimize → trigger < target < critical; maximize → trigger > target > critical | 1.0 |
| S05 | At least one action has automated: true with stated trigger condition | 1.0 |
| S06 | baseline block has value and conditions (measurement context documented) | 1.0 |
Weights sum: 9.5. Normalize: divide each by 9.5 before scoring.
## Actions
| Score | Action |
|-------|--------|
| >= 9.5 | GOLDEN — pool as reference optimization loop |
| >= 8.0 | PUBLISH — wire to monitoring and enable automated triggers |
| >= 7.0 | REVIEW — complete baseline, rollback plan, or threshold ordering |
| < 7.0  | REJECT — rework metric definition and action list |
## Bypass
| Field | Value |
|-------|-------|
| conditions | Production incident requiring immediate threshold override without full review cycle |
| approver | p11-chief |
| audit_trail | Log in records/audits/ with current metric value, override value, and timestamp |
| expiry | 24h — must revalidate thresholds and rerun gates before expiry |
| never_bypass | H01 (YAML), H05 (quality null) |

## Examples

# Examples: optimizer-builder
## Golden Example
INPUT: "Crie optimizer para latency de geraction de knowledge cards"
OUTPUT:
```yaml
id: p11_opt_kc_generation_latency
kind: optimizer
pillar: P11
version: "1.0.0"
created: "2026-03-26"
updated: "2026-03-26"
author: "system"
domain: "knowledge_card_pipeline"
```

### S_RELATED: Cross-Reference Check (SOFT)
- [ ] `related:` frontmatter field populated (3-15 entries)
- [ ] `## Related Artifacts` section present in artifact body
- [ ] At least 1 upstream and 1 downstream reference
- Penalty: -0.3 if empty (does not block, encourages wiring)
