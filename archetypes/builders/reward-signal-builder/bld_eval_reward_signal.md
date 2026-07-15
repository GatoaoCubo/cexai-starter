---
kind: quality_gate
id: p11_qg_reward_signal
pillar: P11
llm_function: GOVERN
purpose: Golden and anti-examples of reward_signal artifacts
pattern: few-shot learning — LLM reads these before producing
quality: null
title: "Gate: reward_signal"
version: "1.0.0"
author: "builder_agent"
tags: [quality-gate, reward-signal, P11, feedback, rlhf, scoring]
tldr: "Pass/fail gate for reward_signal artifacts: signal_type validity, scale consistency, baseline calibration, criteria completeness, and application l..."
domain: "reward signals — continuous quality scores for agent improvement via RLHF, DPO, critique, or implicit feedback"
created: "2026-03-29"
updated: "2026-03-29"
8f: "F7_govern"
keywords: [reward signals, or implicit feedback, signal_type validity, scale consistency, baseline calibration, criteria completeness, and application loop documentation]
density_score: 0.90
related:
  - p11_qg_llm_judge
  - bld_instruction_reward_signal
  - reward-signal-builder
  - p11_qg_quality_gate
  - bld_architecture_reward_signal
---
## Quality Gate

# Gate: reward_signal
## Definition
| Field | Value |
|---|---|
| metric | reward_signal artifact quality score |
| threshold | 7.0 (publish >= 8.0, golden >= 9.5) |
| operator | weighted_sum |
| scope | all artifacts with `kind: reward_signal` |
## HARD Gates
All must pass (AND logic). Any single failure = REJECT.
| ID | Check | Fail Condition |
|---|---|---|
| H01 | Frontmatter parses as valid YAML | Parse error on frontmatter block |
| H02 | ID matches `^p11_rs_[a-z][a-z0-9_]+$` | ID contains uppercase, hyphens, spaces, or missing prefix |
| H03 | ID equals filename stem | `id: p11_rs_foo` but file is `p11_rs_bar.md` |
| H04 | Kind equals literal `reward_signal` | `kind: metric` or `kind: score` or any other value |
| H05 | Quality field is null | `quality: 8.0` or any non-null value |
| H06 | All required fields present | Missing `signal_type`, `scale`, `model`, `tags`, or `tldr` |
## SOFT Scoring
Weights sum to 100%.
| Dimension | Weight | Criteria |
|---|---|---|
| Signal type justification | 1.0 | Explains why chosen signal_type fits domain; not default-picked |
| Scale semantics | 1.0 | High/low values defined with concrete meaning; not just a number range |
| Criteria completeness | 1.0 | >= 2 scored dimensions with weights; each has low/high example |
| Baseline calibration | 1.0 | Baseline justified relative to scale; not arbitrary |
| Model selection rationale | 0.5 | Explains why specific model (or human) produces reliable reward |
| Frequency apownteness | 0.5 | Frequency matches task granularity; not over- or under-evaluated |
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
| conditions | Experimental signal under active calibration, not yet deployed to any improvement loop |
| approver | Author self-certification with comment explaining calibration-phase scope |
| audit_trail | Bypass note in frontmatter comment with expiry date |
| expiry | 14d — experimental signals must reach >= 7.0 or be archived |
| never_bypass | H01 (unparseable YAML breaks all tooling), H05 (self-scored gates corrupt quality metrics), H08 (out-of-range baseline produces nonsense rewards) |

## Examples

# Examples: reward-signal-builder
## Golden Example
INPUT: "Create reward signal for measuring helpfulness of agent responses in a costmer support context"
OUTPUT:
```yaml
id: p11_rs_support_helpfulness
kind: reward_signal
pillar: P11
version: "1.0.0"
created: "2026-03-29"
updated: "2026-03-29"
author: "builder_agent"
name: "Support Response Helpfulness"
```
## Overview
Measures whether agent responses in costmer support resolve the user's problem with clarity, apownte tone, and completeness. Consumed by the monthly RLHF training cycle.
## Signal Design
- Type: scalar — weighted 0-1 score from LLM-judge; simpler than preference pairs since resolution is measurable
- Scale: 0.0 = fails to help, 0.5 = partial help, 1.0 = complete resolution with ideal tone
- Model: claude-sonnet-4-6 — verified >= 0.78 Spearman correlation against human raters on 200-sample holdout
- Aggregation: weighted_mean — problem_resolution weighted 2x others (primary success criterion)
## Criteria
| Dimension | Weight | Low (0-0.3) | High (0.8-1.0) |
|-----------|--------|-------------|----------------|
| problem_resolution | 0.40 | Ignores or misidentifies problem | Fully resolved with clear steps |
| clarity | 0.20 | Jargon-heavy, ambiguous | Simple language, unambiguous |
| tone | 0.20 | Cold, dismissive | Warm, empathetic |
| completeness | 0.20 | Partial answer only | All sub-questions addressed |

Baseline: 0.70 (P25 of human-rated gold responses) — below baseline excluded from RLHF chosen set.
## Application
- RLHF loop: scores above baseline = chosen; below = rejected; preference pairs constructed monthly
- Consumer: training pipeline uses pairs with score differential > 0.15 to avoid noisy pairs
WHY THIS IS GOLDEN:
- quality: null (H05 pass)
- id matches ^p11_rs_ pattern (H02 pass)
- kind: reward_signal (H04 pass)
- signal_type: scalar (valid enum) (H07 pass)

### S_RELATED: Cross-Reference Check (SOFT)
- [ ] `related:` frontmatter field populated (3-15 entries)
- [ ] `## Related Artifacts` section present in artifact body
- [ ] At least 1 upstream and 1 downstream reference
- Penalty: -0.3 if empty (does not block, encourages wiring)
