---
id: bld_quality_gate_canary_config
kind: quality_gate
pillar: P07
title: "Gate: canary_config"
version: "1.0.0"
created: "2026-04-17"
updated: "2026-04-17"
author: builder
domain: canary_config
quality: null
tags:
  - "quality_gate"
  - "canary_config"
  - "P09"
llm_function: GOVERN
tldr: "Validates canary configs for gradual rollout, rollback triggers, and analysis configuration."
8f: "F7_govern"
keywords:
  - "rollback triggers"
  - "and analysis configuration"
  - "quality_gate"
  - "canary_config"
  - "^p09_cc_[a-z][a-z0-9_]+$"
  - "quality: null"
  - "soft_score = sum / 2.5 * 10"
density_score: null
related:
  - bld_manifest_canary_config
  - kc_canary_config
  - bld_instruction_canary_config
  - bld_quality_gate_deployment_manifest
  - bld_knowledge_card_canary_config
---
## Quality Gate

## Definition
A canary_config must ensure gradual traffic exposure with defined automatic rollback. Any config that jumps directly to 100% or lacks rollback triggers is not a canary -- it is a direct deploy.

## HARD Gates
| ID  | Check | Rule |
|-----|-------|------|
| H01 | Frontmatter parses | YAML valid |
| H02 | ID matches namespace | `^p09_cc_[a-z][a-z0-9_]+$` |
| H03 | Kind matches literal | `kind` is exactly `canary_config` |
| H04 | Quality is null | `quality: null` |
| H05 | canary_version and stable_version set | Both non-empty, different values |
| H06 | stages_count matches list | frontmatter count = actual stages |

## SOFT Scoring
| Dimension | Weight | Pass Condition |
|-----------|--------|----------------|
| Analysis interval per stage | 1.0 | analysis_interval_minutes present on each stage |
| Provider specified | 0.5 | provider is one of known values |
| Rollback threshold is numeric | 0.5 | threshold is float, not null |
| Pause duration per stage | 0.5 | pause_duration_minutes present on each non-final stage |

Sum of weights: 2.5. `soft_score = sum / 2.5 * 10`

## Actions
| Score | Action |
|-------|--------|
| >= 9.0 | PUBLISH |
| >= 7.0 | REVIEW |
| < 7.0 | REJECT |

## Examples

# Examples: canary_config

## Golden Example 1 -- CEX API Progressive Delivery
INPUT: "Canary rollout for cex-api 2.1.0 with auto rollback on error rate"
OUTPUT:
```yaml
---
id: p09_cc_cex_api_v210
kind: canary_config
pillar: P09
version: 1.0.0
created: "2026-04-17"
updated: "2026-04-17"
service_name: "cex-api"
```
WHY THIS IS GOLDEN:
- 4 progressive stages (not 1-shot) -- real progressive delivery
- Distinct SLO thresholds per stage (tightens as blast radius grows)
- 2 rollback triggers (error_rate + latency) -- defense in depth
- Rollback points to exact version (v2.0.3, not "previous")

## Golden Example 2 -- E-Commerce Checkout Feature Canary
INPUT: "Safe rollout of new checkout flow for peak season -- payment errors are revenue-critical"
OUTPUT:
```yaml
---
id: p09_cc_checkout_v3_peak
kind: canary_config
pillar: P09
version: 1.0.0
created: "2026-04-18"
updated: "2026-04-18"
service_name: "checkout-service"
```
WHY THIS IS GOLDEN:
- Revenue-critical service gets tighter thresholds (0.1% vs 1%)
- 5 stages instead of 4 (extra caution for payment flow)
- Business metrics (conversion_rate) added alongside technical SLOs
- Time constraints encoded (no stage advance during peak hours)

## Anti-Example 1: Single-Stage "Canary" (REJECTED)
```yaml
stages_count: 1
stages:
  - traffic_percent: 100  # FAIL: 100% is not a canary, it's a full deploy
rollback_trigger_metric: null  # FAIL: no rollback trigger = no safety net
provider: "deploy tool"  # FAIL: vague, not a specific provider
```
WHY REJECTED: A single 100% stage is a full deploy with no rollback. This is not progressive delivery -- it eliminates the canary's purpose. No rollback trigger means a bad deploy has to be caught and reverted manually (MTTR > 30min vs < 2min automated).

## Anti-Example 2: Vague Thresholds (REJECTED)
```yaml
rollback_trigger_metric: "errors"    # FAIL: which errors? rate or count?
rollback_trigger_threshold: "high"   # FAIL: "high" is not a number
stages:
  - traffic: "some"   # FAIL: percentage must be a specific integer
    pause: "a while"  # FAIL: duration must be specific (minutes)
```
WHY REJECTED: Canary configs execute in automated pipelines. "High", "some", "a while" cannot be evaluated by Argo Rollouts or Flagger. The rollout will either fail to parse or use defaults, both of which defeat the canary's revenue protection purpose.

### S_RELATED: Cross-Reference Check (SOFT)
- [ ] `related:` frontmatter field populated (3-15 entries)
- [ ] `## Related Artifacts` section present in artifact body
- [ ] At least 1 upstream and 1 downstream reference
- Penalty: -0.3 if empty (does not block, encourages wiring)
