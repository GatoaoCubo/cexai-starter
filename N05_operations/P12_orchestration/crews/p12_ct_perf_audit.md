---
id: p12_ct_perf_audit
kind: crew_template
pillar: P12
title: "Performance Audit Crew"
version: "1.0.0"
created: "2026-07-20"
quality: null
density_score: 0.9
tags: [crew, perf_audit, sequential, benchmark, slo, operations, N05]
related:
  - p02_ra_profiler
  - p02_ra_perf_engineer
  - p02_ra_perf_reporter
  - p12_tc_perf_audit_default
  - p12_ct_release_gate
process: sequential
roles_count: 3
crew_name: perf_audit
purpose: "Benchmark a target against its performance baseline, gate the result against SLO thresholds, and produce an actionable perf report with a regression-prevention follow-up"
crewai_equivalent: "Process.sequential"
autogen_equivalent: "GroupChat.round_robin"
swarm_equivalent: "profiler -> perf_engineer -> perf_reporter"
handoff_protocol_id: a2a-task-sequential
---

## Overview
Instantiate when a service, endpoint, or pipeline stage needs a structured performance
audit -- after a suspected regression, before a capacity-sensitive release, or on a
recurring cadence. Owner is N05 (operations); consumers are the engineer who owns the
target and the N07 orchestrator. Three roles run in strict sequence, mirroring
[[p12_ct_release_gate]]'s gather-evidence -> judge -> act shape, adapted for performance:
nothing gets called "fast enough" without a measured, threshold-cited verdict.

## Roles

| Role | Role Assignment ID | Reason |
|------|---------------------|--------|
| profiler | p02_ra_profiler.md | Runs the benchmark suite against the perf target; emits `perf_data.md` |
| perf_engineer | p02_ra_perf_engineer.md | Evaluates `perf_data.md` against SLO thresholds; issues `perf_verdict.md`. Verdicts are metric-and-threshold cited, never a "feels slow" judgment call. |
| perf_reporter | p02_ra_perf_reporter.md | Synthesizes both upstream artifacts into `perf_report.md` + a `regression_check` guard |

Role assignments live beside this crew_template in
`N05_operations/P12_orchestration/crews/` -- the layout `cex_crew.py`
resolves natively (their `id:` keeps pillar P02, per the `role_assignment`
kind registration).

## Process
Topology: `sequential`. Rationale: perf_engineer cannot issue a verdict without
profiler's measurements, and perf_reporter must not write recommendations ahead of a
verdict. Sequential ordering keeps the handoff contract simple and makes it structurally
impossible to skip straight from raw numbers to a report with no threshold check in
between.

## Memory Scope

| Role | Scope | Retention |
|------|-------|-----------|
| profiler | shared | per-crew-instance (perf data consumed by perf_engineer and reporter) |
| perf_engineer | shared | per-crew-instance (verdict consumed by reporter) |
| perf_reporter | persistent | report + regression_check persist cross-session as the audit trail |

## Handoff Protocol
`a2a-task-sequential` -- each role writes a completion signal with
`artifact_path` + `quality_score`. The next role reads the prior artifact
before starting its own work. Signal path: `.cex/runtime/signals/`.

## Success Criteria
- [ ] All 3 role deliverables exist under `.cex/runtime/crews/{instance_id}/`
- [ ] profiler data: p50/p95/p99 for every measured case, iteration + warmup counts recorded
- [ ] perf_engineer verdict: PASS or FAIL with explicit per-case threshold citations
- [ ] perf_reporter report: ranked recommendations, each tied to an expected improvement
- [ ] A `regression_check` artifact exists pinning the SLO thresholds as an automated guard
- [ ] Handoff protocol signals present for 3/3 roles
- [ ] No role produced an artifact without reading its upstream input

## Instantiation
```bash
python _tools/cex_crew.py show perf_audit

python _tools/cex_crew.py run perf_audit \
    --charter N05_operations/P12_orchestration/crews/p12_tc_perf_audit_default.md

python _tools/cex_crew.py run perf_audit \
    --charter N05_operations/P12_orchestration/crews/p12_tc_perf_audit_default.md \
    --execute
```

The charter referenced above is a TEMPLATE (`{{open_vars}}` throughout) --
fill in the mission-specific values before running with `--execute`.

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[p02_ra_profiler]] | upstream | 0.45 |
| [[p02_ra_perf_engineer]] | upstream | 0.45 |
| [[p02_ra_perf_reporter]] | upstream | 0.45 |
| [[p12_tc_perf_audit_default]] | downstream | 0.40 |
| [[p12_ct_release_gate]] | sibling_pattern | 0.35 |
