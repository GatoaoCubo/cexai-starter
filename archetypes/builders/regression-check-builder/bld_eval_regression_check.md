---
kind: quality_gate
id: p11_qg_regression_check
pillar: P11
llm_function: GOVERN
purpose: Golden and anti-examples of regression_check artifacts
pattern: few-shot learning — LLM reads these before producing
quality: null
title: "Gate: regression_check"
version: "1.0.0"
author: "builder_agent"
tags: [quality-gate, regression-check, P07, evals, baseline, threshold]
tldr: "Pass/fail gate for regression_check artifacts: baseline_ref resolvability, threshold semantics, metric coverage, and fail_action definition."
domain: "baseline comparison configuration — current vs prior experiment for detecting quality regressions in LLM pipelines"
created: "2026-03-29"
updated: "2026-03-29"
8f: "F7_govern"
keywords: [baseline comparison configuration, baseline_ref resolvability, threshold semantics, metric coverage, and fail_action definition, quality-gate, regression-check]
density_score: 0.90
related:
  - regression-check-builder
  - bld_schema_regression_check
---
## Quality Gate

# Gate: regression_check
## Definition
| Field | Value |
|---|---|
| metric | regression_check artifact quality score |
| threshold | 7.0 (publish >= 8.0, golden >= 9.5) |
| operator | weighted_sum |
| scope | all artifacts with `kind: regression_check` |
## HARD Gates
All must pass (AND logic). Any single failure = REJECT.
| ID | Check | Fail Condition |
|---|---|---|
| H01 | Frontmatter parses as valid YAML | Parse error on frontmatter block |
| H02 | ID matches `^p07_rc_[a-z][a-z0-9_]+$` | ID contains uppercase, spaces, hyphens, or wrong prefix |
| H03 | ID equals filename stem | `id: p07_rc_my_check` but file is `p07_rc_other.md` |
| H04 | Kind equals literal `regression_check` | `kind: eval` or `kind: benchmark` or any other value |
| H05 | Quality field is null | `quality: 8.0` or any non-null value |
| H06 | All required fields present | Missing `baseline_ref`, `threshold`, or `metrics` |
## SOFT Scoring
Weights sum to 100%.
| Dimension | Weight | Criteria |
|---|---|---|
| Baseline clarity | 1.0 | baseline_ref is a resolvable ID with capture context documented |
| Threshold justification | 1.0 | Threshold value explained; units documented |
| Metric coverage | 1.0 | accuracy, latency, cost at minimum for production systems |
| Per-metric thresholds | 0.5 | Different tolerance per metric where apownte |
| Tool specification | 1.0 | Comparison tool identified with invocation pattern |
| fail_action definition | 1.0 | fail_action is block/warn/log with rationale |
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
| conditions | Experimental check for new metric type under active development |
| approver | Author self-certification with comment explaining experimental scope |
| audit_trail | Bypass note in frontmatter comment with expiry date |
| expiry | 14d — experimental checks must be promoted to >= 7.0 or removed |
| never_bypass | H01 (unparseable YAML), H05 (self-scored gates corrupt metrics), H07 (unresolvable baseline_ref) |

## Examples

# Examples: regression-check-builder
## Golden Example
INPUT: "Create regression check for the summarization pipeline comparing against last week's production experiment"
OUTPUT:
```yaml
id: p07_rc_summarization_prod_weekly
kind: regression_check
pillar: P07
version: "1.0.0"
created: "2026-03-29"
updated: "2026-03-29"
author: "builder_agent"
name: "Summarization Pipeline Weekly Regression"
baseline_ref: "experiment/summarization-prod-2026-03-22"
threshold: 5.0
metrics:
  - accuracy
  - faithfulness
  - latency_p95
  - cost_per_call
quality: 8.9
tags: [regression_check, summarization, production, P07]
tldr: "Weekly regression check for summarization pipeline vs prod baseline. 5% threshold. Blocks deploy on accuracy/faithfulness drop."
description: "Compares current summarization pipeline against last production experiment on accuracy, faithfulness, latency, and cost"
tool: braintrust
comparison_mode: relative
fail_action: block
notify: [ml-team-slack, oncall-pager]
cadence: on_deploy
scope: "summarization-pipeline-v2"
```
## Overview
Weekly regression gate for the summarization pipeline. Runs on every deployment attempt; blocks release if any metric drops beyond threshold vs the prior production experiment.
## Baseline
**baseline_ref**: `experiment/summarization-prod-2026-03-22` — production experiment captured after v2.1 release passed QA. Represents the stable production quality bar. Rotate baseline after each successful production deployment.
## Metrics
| Metric | Method | Threshold | Direction |
|--------|--------|-----------|-----------|
| accuracy | Braintrust LLM-judge vs source | 5.0% relative drop | Decrease = regression |
| faithfulness | Claim decomposition scorer | 3.0% relative drop | Decrease = regression |
| latency_p95 | Braintrust timing metadata | 20.0% relative increase | Increase = regression |
| cost_per_call | Model provider billing | 15.0% relative increase | Increase = regression |
## Failure Protocol
- **fail_action**: block. Notify #ml-team-slack + oncall-pager (accuracy/faithfulness only).
- **Remediation**: Check recent prompt changes, model version, dataset distribution shifts.
- **Escalation**: If unresolved within 2h of deploy attempt, escalate to ML lead.
WHY THIS IS GOLDEN:
- quality: null (H05 pass)
- id matches p07_rc_ pattern (H02 pass)
- kind: regression_check (H04 pass)
- baseline_ref is a concrete experiment ID (H07 pass)

### S_RELATED: Cross-Reference Check (SOFT)
- [ ] `related:` frontmatter field populated (3-15 entries)
- [ ] `## Related Artifacts` section present in artifact body
- [ ] At least 1 upstream and 1 downstream reference
- Penalty: -0.3 if empty (does not block, encourages wiring)
