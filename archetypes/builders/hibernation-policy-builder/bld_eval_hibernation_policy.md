---
kind: quality_gate
id: bld_quality_gate_hibernation_policy
pillar: P07
llm_function: GOVERN
purpose: F7 GOVERN quality gates for hibernation_policy
quality: null
title: "Quality Gate: hibernation_policy"
version: "1.0.0"
author: n03_engineering
tags:
  - "hibernation_policy"
  - "builder"
  - "quality_gate"
tldr: "F7 GOVERN quality gates for hibernation_policy"
domain: "hibernation_policy construction"
created: "2026-04-18"
updated: "2026-04-18"
8f: "F7_govern"
keywords:
  - "hibernation_policy construction"
  - "quality gate"
  - "hibernation_policy"
  - "builder"
  - "quality_gate"
  - "target_backend"
  - "idle_trigger.type"
density_score: 0.90
related:
  - bld_schema_hibernation_policy
  - bld_instruction_hibernation_policy
  - n00_hibernation_policy_manifest
  - kc_hibernation_policy
  - bld_output_template_hibernation_policy
---
## Quality Gate
## hibernation_policy HARD Gates (must all pass -- H01-H05)
| Gate | Check | Fail action |
|------|-------|------------|
| H01 | Frontmatter present with all required fields | Reject -- missing fields |
| H02 | `target_backend` in {daytona, modal, singularity, generic} | Reject -- invalid backend |
| H03 | `idle_trigger.type` in {no_activity_seconds, no_requests_seconds, explicit_signal} | Reject -- invalid trigger type |
| H04 | `idle_trigger.threshold_seconds` >= 0 | Reject -- negative threshold |
| H05 | `wake_on` list has at least one condition | Reject -- nothing to wake on |

## SOFT Gates (scored 0-10, target >= 8.0)
| Dimension | Weight | Check |
|-----------|--------|-------|
| D1 Structural | 30% | 6+ sections present; all tables populated; no empty cells |
| D2 Correctness | 30% | threshold_seconds reasonable for backend type; state_persistence consistent with backend capabilities |
| D3 Completeness | 20% | wake_latency_sla_seconds set; cost_savings_estimate_pct populated; Notes section present |
| D4 Density | 10% | density >= 0.85; no padding prose; tables > narrative |
| D5 Boundary | 10% | Does not conflate with cost_budget, rate_limit_config, terminal_backend, or runtime_rule |

## Scoring Formula
```
soft_score = (D1*0.30 + D2*0.30 + D3*0.20 + D4*0.10 + D5*0.10) * 10
final = min(soft_score, 10.0)
publish_threshold = 8.0
quality_target = 9.0
```

## Common Failure Patterns
| Pattern | Gate failed | Fix |
|---------|-------------|-----|
| `threshold_seconds: -1` | H04 | Set to 0 for explicit_signal or >= 60 for time-based |
| `wake_on: []` | H05 | Add at least incoming_request or explicit_signal |
| Missing idle_trigger block | H01 | Add both type and threshold_seconds |
| `target_backend: kubernetes` | H02 | Use generic for unsupported backends |
| `cost_budget` field in frontmatter | Semantic | Remove -- cost_budget is a separate kind |

## Examples
## Example 1: Modal GPU serverless (5-minute idle)
**Intent:** Configure Modal serverless container to scale-to-zero after 5 minutes of no requests.

```yaml
---
id: p09_hp_modal
kind: hibernation_policy
pillar: P09
title: "Hibernation Policy: modal"
target_backend: modal
idle_trigger:
  type: no_requests_seconds
```

---

## Example 2: Daytona long-running agent workspace (30-minute idle)
**Intent:** Configure Daytona workspace to hibernate after 30 minutes of agent inactivity, preserving full filesystem state.

```yaml
---
id: p09_hp_daytona
kind: hibernation_policy
pillar: P09
title: "Hibernation Policy: daytona"
target_backend: daytona
idle_trigger:
  type: no_activity_seconds
```

---

## Example 3: Singularity HPC batch (explicit signal)
**Intent:** Configure Singularity job to hibernate only on explicit orchestrator signal after batch completion.

```yaml
---
id: p09_hp_singularity
kind: hibernation_policy
pillar: P09
title: "Hibernation Policy: singularity"
target_backend: singularity
idle_trigger:
  type: explicit_signal
```

---

### S_RELATED: Cross-Reference Check (SOFT)
- [ ] `related:` frontmatter field populated (3-15 entries)
- [ ] `## Related Artifacts` section present in artifact body
- [ ] At least 1 upstream and 1 downstream reference
- Penalty: -0.3 if empty (does not block, encourages wiring)
