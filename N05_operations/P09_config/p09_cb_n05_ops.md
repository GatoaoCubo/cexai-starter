---
id: p09_cb_n05_ops
kind: cost_budget
8f: F1_constrain
pillar: P09
title: "N05 Operations Cost Budget"
version: "1.0.0"
created: "2026-07-20"
updated: "2026-07-20"
author: n05_operations
scope: "nucleus"
providers:
  - anthropic
  - google
  - ollama
quality: null
tags: [cost_budget, n05-operations, spend-tracking, P09]
tldr: "N05 operations spend limits: per-provider token ceilings, per-dispatch-mode caps, warn at 80%, block at 100%."
description: "Token and USD budget policy for the N05 operations nucleus across solo, grid, and overnight dispatch modes with provider-level tracking."
currency: token_units
reset_policy: rolling_30d
alert_enabled: true
total_budget: 6000000
overage_action: block
keywords: [operations spend limits, per-dispatch-mode caps, cost_budget, spend-tracking, cex_token_budget.py]
density_score: 1.0
related:
  - cost-budget-builder
  - p09_env_n05
  - p09_rl_n05
  - nucleus_def_n05
---

## Overview

N05 (Gating Wrath) governs its own LLM spend with the same discipline it applies to
operational gates: hard limits per dispatch mode, real-time alerts at 80%, and a hard
block at 100% -- no grace, no override without an explicit manifest change. Enforced by
`_tools/cex_token_budget.py` at each LLM call boundary.

## Budget Catalog

| Provider | Model | Token Limit | Alert % | Reset | Overage Action |
|----------|-------|-------------|---------|-------|----------------|
| anthropic | sonnet-tier | 6000000 | 80% | rolling_30d | block |
| anthropic | opus-tier | 500000 | 75% | rolling_30d | block |
| google | flash-tier | 4000000 | 80% | rolling_30d | warn |
| ollama | * (local) | 20000000 | 90% | rolling_30d | log |

**Per-dispatch-mode token envelope (informational -- enforced at call site):**

| Dispatch Mode | Token Ceiling | Notes |
|---------------|---------------|-------|
| nucleus boot | 30000 | Fixed overhead; escalate if exceeded |
| solo task | 200000 | 50K-200K range; 200K hard cap |
| grid cell (1 of N) | 200000 | Each N05 cell budgeted independently |
| overnight evolve | 1000000 | Session cap; runner halts on breach |

## Alert Policy

| Threshold | Level | Channel | Action |
|-----------|-------|---------|--------|
| 75% | warn | log | Write to `.cex/runtime/cost_alerts.jsonl` with provider + tokens used |
| 80% | warn | log + webhook | Notify ops channel; drop to a conservative rate profile |
| 95% | warn | log | Log critical; block all non-incident calls immediately |
| 100% | block | log | Budget-exceeded error raised; caller receives a graceful deny |

Escalation: an 80% warn fires the webhook + rate-profile downgrade. A 100% block halts
all N05 LLM calls for the remainder of the rolling window. An incident-burst override
requires an explicit `overage_action: warn` recorded in a signed manifest entry -- never a
silent runtime bypass.

## Overage Rules

- Breach behavior: the budget guard raises a hard error; no call is made to the provider;
  N05 returns a structured error to the caller.
- Grace period: none -- Gating Wrath does not negotiate after the gate closes.
- Increase request: edit `total_budget` and merge via PR; no runtime mutation without a
  version bump.

## Why per-provider AND per-dispatch-mode

A single global ceiling hides WHICH surface burned the budget. Splitting by provider
catches a runaway model choice; splitting by dispatch mode catches a runaway loop (e.g. an
overnight `evolve` session that should halt at 1M tokens but keeps calling). Both views are
checked at the call site -- whichever ceiling is closer to breach wins.

## References

- `.cex/config/nucleus_models.yaml` -- model routing + fallback chain for N05
- `_tools/cex_token_budget.py` -- budget enforcement at the call boundary

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[cost-budget-builder]] | upstream | 0.32 |
| [[p09_env_n05]] | sibling | 0.30 |
| [[p09_rl_n05]] | sibling | 0.28 |
| [[nucleus_def_n05]] | upstream | 0.22 |
