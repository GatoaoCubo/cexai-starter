---
kind: quality_gate
id: p11_qg_fallback_chain
pillar: P11
llm_function: GOVERN
purpose: Golden and anti-examples of fallback_chain artifacts
pattern: few-shot learning — LLM reads these before producing
quality: null
title: "Gate: fallback_chain"
version: "1.0.0"
author: "builder_agent"
tags: [quality-gate, fallback-chain, resilience, model-degradation, P11]
tldr: "Validates fallback_chain artifacts: step sequence integrity, timeout/threshold coverage, and cost-aware degradation design."
domain: "fallback_chain — model degradation sequences with timeouts, circuit breakers, and cost controls"
created: "2026-03-27"
updated: "2026-03-27"
8f: "F7_govern"
density_score: 0.92
related:
  - fallback-chain-builder
  - bld_instruction_fallback_chain
  - p11_qg_chain
  - bld_architecture_fallback_chain
  - p11_qg_quality_gate
---
## Quality Gate

# Gate: fallback_chain
## Definition
| Field     | Value |
|-----------|-------|
| metric    | composite score across SOFT dimensions |
| threshold | >= 7.0 to publish; >= 9.5 for golden |
| operator  | weighted average after all HARD gates pass |
| scope     | all artifacts where `kind: fallback_chain` |
All HARD gates are AND-logic: one failure rejects the artifact regardless of SOFT score.
## HARD Gates
| ID  | Check | Fail Condition |
|-----|-------|----------------|
| H01 | Frontmatter parses as valid YAML | Any YAML syntax error |
| H02 | ID matches `^p02_fc_[a-z][a-z0-9_]+$` | Wrong format or namespace |
| H03 | ID equals filename stem (no extension) | Mismatch between id field and file name |
| H04 | Kind equals literal `fallback_chain` | Any other value |
| H05 | `quality` field is null | Any non-null value |
| H06 | Required fields present: id, kind, pillar, version, created, updated, author, steps_count, timeout_per_step_ms, quality_threshold, domain, quality, tags, tldr | Any missing field |
## SOFT Scoring
| Dim | Dimension | Weight | Scoring Guide |
|-----|-----------|--------|---------------|
| S01 | `tldr` <= 160 chars, non-empty, names the degradation path | 0.10 | Accurate + concise=1.0, vague=0.4, absent=0.0 |
| S02 | Tags list len >= 3, includes `fallback_chain` | 0.05 | Met=1.0, partial=0.5 |
| S03 | Chain table has all columns filled per step | 0.10 | All filled=1.0, gaps=0.5 |
| S04 | Degradation Logic section: trigger conditions per step | 0.12 | All triggers=1.0, partial=0.5, absent=0.0 |
| S05 | Circuit Breaker section: open/half-open/closed thresholds and recovery | 0.12 | Fully specified=1.0, partial=0.5, absent=0.0 |
| S06 | Cost Analysis section: per-step cost implications | 0.10 | All steps costed=1.0, partial=0.5, absent=0.0 |
**Weight sum: 1.00**
## Actions
| Score | Action |
|-------|--------|
| >= 9.5 | GOLDEN — reference artifact for fallback_chain calibration |
| >= 8.0 | PUBLISH — pool-eligible; circuit breaker and cost docs present |
| >= 7.0 | REVIEW — usable but missing threshold detail or cost analysis |
| < 7.0  | REJECT — redo; likely missing circuit breaker or step ordering |
## Bypass
| Field | Value |
|-------|-------|
| conditions | Emergency hotfix only; chain replaces a failing production route with no time to complete all gates |
| approver | Senior engineer with model cost authority |
| audit trail | Required: incident link, timestamp, approver ID |
| expiry | 48 hours; full gate review must follow |
| never bypass | H01 (corrupt YAML breaks all parsing), H05 (self-scored quality is invalid data) |

## Examples

# Examples: fallback-chain-builder
## Golden Example
INPUT: "Create fallback chain for research tasks: opus->sonnet->haiku"
OUTPUT:
```yaml
id: p02_fc_research_model
kind: fallback_chain
pillar: P02
version: "1.0.0"
created: "2026-03-26"
updated: "2026-03-26"
author: "builder"
steps_count: 3
timeout_per_step_ms: 30000
quality_threshold: 7.0
domain: "research_resilience"
quality: 8.9
tags: [fallback_chain, research, resilience, P02, model-degradation]
tldr: "3-step research fallback: opus(30s)->sonnet(20s)->haiku(10s) with 7.0 quality gate"
retry_count: 1
circuit_breaker_threshold: 3
cost_ceiling_usd: 0.50
logging_level: "errors"
alert_on_final_fallback: true
keywords: [research, fallback, degradation, opus, sonnet, haiku]
density_score: 0.90
```
## Chain
| Position | Model | Provider | Timeout (ms) | Quality Min | Cost/1M tokens (USD) | Retry |
|----------|-------|----------|-------------|-------------|---------------------|-------|
| 1 | claude-opus-4-7 | anthropic | 30000 | 8.0 | 15.00 | 1 |
| 2 | claude-sonnet-4-6 | anthropic | 20000 | 7.0 | 3.00 | 1 |
| 3 | claude-haiku-4-5 | anthropic | 10000 | 5.0 | 0.25 | 2 |
## Degradation Logic
Step transition trigger: timeout exceeded OR quality below quality_min OR 5xx error.
Quality evaluation: automatic scoring via quality_gate after each response.
Transition: exhaust retry_count at current step, then move to next step immediately.
## Circuit Breaker
Threshold: 3 consecutive failures across all steps.
State when tripped: open (reject all new requests for cooldown period).
Recovery: automatic after 60 seconds cooldown, test with step 1.
Cooldown: 60 seconds.
## Cost Analysis
| Step | Cost/1M tokens | Expected usage | Projected cost |
|------|---------------|----------------|----------------|
| opus | $15.00 | 80% of requests | $0.30/request |
| sonnet | $3.00 | 15% of requests | $0.06/request |
| haiku | $0.25 | 5% of requests | $0.005/request |
| Total | - | - | ~$0.27/request avg |
Ceiling: $0.50 per request chain execution.
## Integration
- Activated by: agent request with model_preference or router timeout
- Provides to: researcher (research agent), any agent needing resilient model selection
- Signals: `p12_sig_model_degraded` on step transition, `p12_sig_chain_exhausted` on final fail

### S_RELATED: Cross-Reference Check (SOFT)
- [ ] `related:` frontmatter field populated (3-15 entries)
- [ ] `## Related Artifacts` section present in artifact body
- [ ] At least 1 upstream and 1 downstream reference
- Penalty: -0.3 if empty (does not block, encourages wiring)
