---
id: p12_tc_perf_audit_default
kind: team_charter
pillar: P12
title: "Team Charter Template -- Performance Audit"
version: "1.0.0"
created: "2026-07-20"
updated: "2026-07-20"
author: n05_operations
quality: null
tags: [team_charter, perf_audit, operations, template, N05]
tldr: "Reusable team_charter TEMPLATE for the perf_audit crew -- fill {{open_vars}} at instantiation time, then run with --execute."
domain: "performance audit orchestration"
charter_id: "{{charter_id}}"
crew_template_ref: "N05_operations/P12_orchestration/crews/p12_ct_perf_audit.md"
mission_statement: "Benchmark {{perf_target_ref}} through the profiler -> perf_engineer -> perf_reporter crew and either confirm it meets SLO or flag it with a cited, ranked remediation path, by {{deadline}}."
deadline: "{{deadline}}"
related:
  - p12_ct_perf_audit
  - p02_ra_profiler
  - p02_ra_perf_engineer
---

## TEMPLATE -- fill before instantiation

This file is a TEMPLATE, not an instantiated charter. Every `{{open_var}}`
below must be replaced with a real value before `cex_crew.py run perf_audit
--charter <this-file> --execute` is safe to run. Copy this file to a new
`p12_tc_perf_audit_v{{n}}.md` per real audit rather than editing this
template in place, mirroring the versioned-instance pattern the `team_charter`
kind's own ID pattern expects.

## Mission Statement
Benchmark `{{perf_target_ref}}` (a service, endpoint, or pipeline stage) through the
3-role sequential [[p12_ct_perf_audit]] crew. The crew completes when perf_reporter's
report + regression_check are committed -- on either a PASS or a FAIL verdict, the
evidence chain is what closes the mission, not a particular outcome.

## Deliverables
1. **Perf data** (`perf_data.md`) -- p50/p95/p99 per case, iteration + warmup counts,
   environment description, produced by profiler
2. **Perf verdict** (`perf_verdict.md`) -- PASS or FAIL with a per-case table (metric,
   threshold, actual, status) and ranked bottleneck candidates, produced by perf_engineer
3. **Perf report** (`perf_report.md`) + **regression check** -- ranked, owner-assignable
   recommendations and an automated SLO guard, produced by perf_reporter

## Success Metrics
| Objective | Key Result |
|-----------|------------|
| Every deliverable is evidence-backed | 0 recommendations without a cited metric |
| The SLO gate is never bypassed silently | perf_engineer verdict present for 100% of runs |
| Regressions get an automated guard | 1 regression_check artifact per completed audit |
| Quality gate | perf_report quality >= {{quality_gate_threshold}} (charter default: 8.5) |

## Budget
| Field | Value |
|-------|-------|
| tokens | {{budget_tokens}} |
| wall_clock_seconds | {{budget_wall_clock_seconds}} |
| usd | {{budget_usd}} |

## Stakeholders
| Role | Nucleus / User | Responsibility |
|------|-----------------|-----------------|
| Crew owner | n05_operations | Accountable for the crew's evidence chain |
| Dispatcher | n07_orchestrator | Dispatches, monitors, and consolidates |
| Target owner | {{target_owner}} | Accountable for acting on the recommendations |

## Quality Gate
- Floor: 8.0 (system-wide publish floor)
- Target for this charter: `{{quality_gate_threshold}}` (charter default: 8.5)
- Per-deliverable: `perf_data.md` and `perf_verdict.md` must each cite a reproducible
  command or measured value for every claim -- no unverified summary passes perf_engineer.

## Escalation Protocol
If any role crosses its token ceiling or fails 3 consecutive attempts, emit
`signal_{role}_escalate.json` to `.cex/runtime/signals/`. N07 reads it and
either extends the budget or pages `{{escalation_contact}}`.

## Termination Criteria
ANY of:
1. perf_reporter's `perf_report.md` + `regression_check` are committed (mission complete)
2. Token or wall-clock budget exhausted (emit a partial-completion signal)
3. `{{deadline}}` passed -- save work-in-progress artifacts before exit
4. 3 consecutive failures on the same artifact (stuck loop -- escalate immediately)

## Instantiation Override
Fill the open vars above directly, or override at run time:
```bash
python _tools/cex_crew.py run perf_audit \
    --charter N05_operations/P12_orchestration/crews/p12_tc_perf_audit_default.md \
    --override deadline="2026-08-01T17:00:00Z" \
    --override budget.tokens=60000 \
    --execute
```

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[p12_ct_perf_audit]] | upstream | 0.55 |
| [[p02_ra_profiler]] | related | 0.32 |
| [[p02_ra_perf_engineer]] | related | 0.32 |
