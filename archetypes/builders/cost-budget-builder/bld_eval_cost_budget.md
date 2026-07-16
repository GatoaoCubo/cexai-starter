---
kind: quality_gate
id: p11_qg_cost_budget
pillar: P11
llm_function: GOVERN
purpose: Golden and anti-examples of cost_budget artifacts
pattern: few-shot learning -- LLM reads these before producing
quality: null
title: "Gate: cost_budget"
version: "1.0.0"
author: "builder_agent"
tags: [quality-gate, cost-budget, token-budget, spend-tracking, cost-alerts, P11]
tldr: "Gates for cost_budget artifacts: validates budget catalog completeness, alert thresholds, reset policy, overage action, and provider accuracy."
domain: "cost_budget -- token budget allocation, spend tracking, and cost alert configuration per provider/model"
created: "2026-04-13"
updated: "2026-04-13"
8f: "F7_govern"
keywords: [spend tracking, gates for cost_budget artifacts, validates budget catalog completeness, alert thresholds, reset policy, overage action, and provider accuracy]
density_score: 0.92
related:
  - cost-budget-builder
  - bld_architecture_cost_budget
  - bld_schema_cost_budget
---
## Quality Gate

# Gate: cost_budget
## Definition
| Field | Value |
|-------|-------|
| metric | Composite score from SOFT dimensions + all HARD gates pass |
| threshold | >= 7.0 to publish; >= 9.5 golden |
| operator | AND (all HARD) + weighted_sum (SOFT) |
| scope | All artifacts where `kind: cost_budget` |

## HARD Gates
All must pass. Any single failure = REJECT regardless of SOFT score.
| ID  | Check | Failure message |
|-----|-------|----------------|
| H01 | Frontmatter parses as valid YAML | "Frontmatter YAML syntax error" |
| H02 | `id` matches `^p09_cb_[a-z][a-z0-9_]+$` | "ID fails cost_budget namespace regex" |
| H03 | `id` value equals filename stem | "ID does not match filename" |
| H04 | `kind` equals literal `"cost_budget"` | "Kind is not 'cost_budget'" |
| H05 | `quality` field is `null` | "Quality must be null at authoring time" |
| H06 | No budget entry contains API keys, billing credentials, or payment method data | "Credential data detected in budget artifact" |

## SOFT Scoring
Dimensions sum to 100%. Score each 0.0-10.0; multiply by weight.
| Dimension | Weight | What to assess |
|-----------|--------|----------------|
| Budget catalog completeness | 1.0 | Each entry has all 7 fields: provider, model, token_limit, usd_limit, alert_threshold_pct, reset_policy, overage_action |
| Alert policy specificity | 1.0 | Channels named, escalation path defined (not just "notify someone") |
| Reset policy correctness | 1.0 | Policy matches workload pattern (rolling for batch jobs, monthly for SaaS) |
| Overage action clarity | 1.0 | Block/warn/log behavior explicitly described per entry |
| Scope accuracy | 0.5 | Scope (global/provider/model) correctly categorizes all entries |
| Provider coverage | 1.0 | All active providers in the deployment are represented |
Weight sum: 1.0+1.0+1.0+1.0+0.5+1.0+1.0+0.5+0.5+0.5+1.0+1.0 = 10.0 (100%)

## Actions
| Score | Tier | Action |
|-------|------|--------|
| >= 9.5 | GOLDEN | Publish to pool as golden exemplar |
| >= 8.0 | PUBLISH | Publish to pool |
| >= 7.0 | REVIEW | Flag for human review before publish |
| < 7.0  | REJECT | Return to author with failure report |

## Bypass
| Field | Value |
|-------|-------|
| conditions | New deployment where provider spend data is not yet available |
| approver | Cost owner approval required (written); alert thresholds never bypassed |

## Examples

# Examples: cost-budget-builder
## Golden Example
INPUT: "Define budget limits for all Anthropic and OpenAI providers, monthly reset, alert at 80%"
OUTPUT:
```yaml
id: p09_cb_multi_provider
kind: cost_budget
pillar: P09
version: "1.0.0"
created: "2026-04-13"
updated: "2026-04-13"
author: "builder_agent"
scope: "global"
```
## Overview
Global monthly cost budget covering anthropic and openai providers.
Enforced by cex_token_budget.py at each LLM call; breach triggers hard block.
## Budget Catalog
| Provider | Model | Token Limit | USD Limit | Alert % | Reset | Overage Action |
|----------|-------|-------------|-----------|---------|-------|----------------|
| anthropic | * | null | 300 | 80% | monthly | block |
| anthropic | claude-opus-4-7 | 5000000 | 200 | 75% | monthly | block |
| openai | * | null | 200 | 80% | monthly | warn |
| openai | gpt-4o | 3000000 | 150 | 75% | monthly | warn |
## Alert Policy
| Threshold | Level | Channel | Action |
|-----------|-------|---------|--------|
| 75% | warn | log | Write to .cex/runtime/cost_alerts.jsonl |
| 80% | warn | webhook | POST to ops-webhook with provider + current spend |
| 100% | block | pagerduty | Page on-call; hard-block all calls to that provider |
Escalation: warn -> log + webhook; block -> pagerduty page + API calls return 429 locally.
## Overage Rules
- Breach behavior: cex_token_budget.py raises BudgetExceededError; caller receives graceful error
- Grace period: none -- hard block on first call that would exceed limit
- Increase request: update total_budget field + PR review; no runtime override without code change
WHY THIS IS GOLDEN:
- quality: null (H05 pass)
- id matches p09_cb_ pattern (H02 pass)
- kind: cost_budget (H04 pass)
- providers list matches Budget Catalog entries (H08 pass)

### S_RELATED: Cross-Reference Check (SOFT)
- [ ] `related:` frontmatter field populated (3-15 entries)
- [ ] `## Related Artifacts` section present in artifact body
- [ ] At least 1 upstream and 1 downstream reference
- Penalty: -0.3 if empty (does not block, encourages wiring)
