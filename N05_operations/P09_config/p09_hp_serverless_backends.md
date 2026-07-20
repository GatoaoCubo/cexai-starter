---
id: p09_hp_serverless_backends
kind: hibernation_policy
8f: F1_constrain
pillar: P09
nucleus: n05
title: "N05 Operations -- Hibernation Policy (Idle Cost Guard)"
version: "1.0.0"
created: "2026-07-20"
updated: "2026-07-20"
author: n05_operations
quality: null
tags: [n05, operations, hibernation_policy, P09, cost-guard]
tldr: "N05-owned idle-cost guard: per-backend hibernation triggers, wake SLA, state persistence, cost-savings enforcement."
keywords: [hibernation policy, idle cost guard, per-backend hibernation triggers, wake sla, state persistence, cost savings]
density_score: 0.95
related:
  - hibernation-policy-builder
  - kc_hibernation_policy
  - bld_config_hibernation_policy
  - p09_cb_n05_ops
---

## Ownership

N05 OWNS this kind. Operations controls hibernation behavior for all serverless and
hibernation-capable backends. Gating Wrath lens: idle resources are wasted money -- a
backend that stays warm with nothing to do is a silent cost leak, not a convenience.

## Per-Backend Hibernation Matrix

| Backend | Idle Trigger | Threshold (s) | Wake Latency SLA | State Persist | Cost Savings Est |
|---------|-------------|---------------|------------------|---------------|------------------|
| sandbox platform A | no_activity | 600 | 8s | memory + disk | 75% |
| serverless compute B | no_requests | 300 | 5s | disk only | 80% |
| container platform C | explicit_signal | 900 | 15s | disk snapshot | 60% |
| generic / {{deploy_target}} | no_activity | 900 | 10s | configurable | 70% |

## Idle Trigger Rules (Gating-Wrath-Enforced)

| Trigger Type | Detection Method | Grace Period | Failure Mode |
|-------------|-----------------|-------------|--------------|
| no_activity_seconds | no tool calls, agent messages, or I/O | 0 (immediate after threshold) | hibernate + log |
| no_requests_seconds | no inbound HTTP/gRPC requests | 0 | hibernate + log |
| explicit_signal | orchestrator sends a hibernate command | n/a | hibernate + log |

## Wake Conditions

| Condition | Priority | Max Latency | Failure Mode |
|-----------|----------|-------------|--------------|
| incoming_request | 1 (highest) | per SLA | queue request, wake, retry |
| scheduled_cron | 2 | SLA + 5s | alert if wake fails |
| explicit_signal | 3 | SLA + 10s | alert + fallback to fresh start |

## State Persistence (Per Backend)

| Backend | keep_memory | snapshot_disk | checkpoint_cadence (s) | Restore Verified |
|---------|------------|---------------|----------------------|-----------------|
| sandbox platform A | true | true | 60 | health check on wake |
| serverless compute B | false | true | 120 | function test on wake |
| container platform C | false | true | 60 | bind-mount verify |
| generic / {{deploy_target}} | true | true | 60 | configurable |

## Failure Modes

| Failure | Detection | Response | Escalation | SLA |
|---------|-----------|----------|------------|-----|
| Wake timeout | latency > SLA | retry 2x, then fresh start | oncall | SLA + 30s |
| State corruption | health check fail on wake | discard state, cold start | alert | 2min |
| Checkpoint failure | write error during snapshot | retry 1x, then skip | log + alert | 30s |
| Orphan hibernated instance | no wake in 24h | terminate + cleanup | log | 24h |
| Cost overshoot | billing > 2x estimate | force-hibernate + alert | orchestrator | 1h |

## Monitoring

| Metric | Threshold | Alert |
|--------|-----------|-------|
| Wake latency p99 | per backend SLA | warn at 80% SLA, page at 110% |
| Hibernation frequency | >20/hour/backend | warn (possible thrashing) |
| State restore failures | >0 | immediate alert |
| Cost savings actual vs estimate | <50% of estimate | weekly report |

## Rollback Procedure

| Step | Action | Gate |
|------|--------|------|
| 1 | Disable hibernation (set `enabled: false`) | config applied |
| 2 | Wake all hibernated instances | all instances healthy |
| 3 | Investigate root cause | cause identified |
| 4 | Re-enable with corrected thresholds | health check pass |

## Integration Points

- `terminal_backend` (P09) -- each hibernation policy pairs with a specific backend
- `sandbox_config` (P09) -- hibernated instances must respect sandbox rules on wake
- `schedule` (P12) -- pre-warm schedules prevent cold-start latency for known workloads
- `cost_budget` (P09) -- hibernation savings feed into budget tracking, see [[p09_cb_n05_ops]]

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[hibernation-policy-builder]] | related | 0.45 |
| [[kc_hibernation_policy]] | upstream | 0.42 |
| [[bld_config_hibernation_policy]] | related | 0.37 |
| [[p09_cb_n05_ops]] | sibling | 0.30 |
