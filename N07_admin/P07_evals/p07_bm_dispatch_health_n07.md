---
id: p07_bm_dispatch_health_n07
kind: benchmark
pillar: P07
title: "Benchmark: Orchestrator Dispatch-Health Cadence"
version: "1.0.0"
quality: null
tags: [benchmark, doctor-health, quality-gate, orchestration]
8f: F7_govern
nucleus: n07
metric: doctor_fail_count
unit: count
direction: lower_is_better
baseline: 0
target: 0
iterations: 1
warmup: 0
percentiles: [50, 95, 99]
environment: "local repo-static analysis via `python _tools/cex_doctor.py`; no network calls"
domain: n07-operations
created: "2026-07-20"
tldr: "The orchestrator checks doctor PASS/WARN/FAIL pre- and post- every dispatch wave; the floor to hold is 0 FAIL."
related:
  - p12_wf_admin_orchestration
  - p11_qg_admin_orchestration
---

# Benchmark: Orchestrator Dispatch-Health Cadence

## Metric

| Field | Value |
|---|---|
| Name | `doctor_fail_count` (companion reads: `doctor_warn_count`, `builders_scanned`) |
| Definition | The PASS/WARN/FAIL triplet a doctor-style health tool reports across all builder/artifact sets, rolled into one `Result: {P} PASS / {W} WARN / {F} FAIL` line |
| Direction | `lower_is_better` for FAIL -- WARN is watched, not gated |
| Baseline / Target | 0 FAIL -- a floor to HOLD, not a number to drive further down |

## Measurement Procedure

| Step | Detail |
|---|---|
| Command | `python _tools/cex_doctor.py` (diagnose only, no `--apply`) |
| When | Pre-wave (baseline) and post-wave (regression check), every dispatch cycle |
| Who reads it | The orchestrator, by hand -- never trusted from a cell's self-report alone |
| Scope | All builder/artifact sets under active development this wave |

## Time Series (fill per wave)

| # | Wave | Doctor reading | Notes |
|---|---|---|---|
| 1 | {{wave_id}} | {{P}} PASS / {{W}} WARN / {{F}} FAIL | {{notes}} |
| 2 | {{wave_id}} | {{P}} PASS / {{W}} WARN / {{F}} FAIL | {{notes}} |

## Thresholds

| Condition | Action |
|---|---|
| FAIL > 0 | BLOCK -- consolidation does not proceed; retry F6 (max 2) or escalate |
| WARN count rises | INVESTIGATE -- diff against the last known-good reading |
| WARN count stable, same items | LOG, no action -- not a regression |

## Why This Benchmark Exists

A dispatch loop that never re-checks health silently accumulates drift: a
builder can "complete" and signal while leaving a broken artifact behind. This
benchmark is the orchestrator's own admission that self-reports are claims, not
facts (see [[p11_qg_admin_orchestration]]) -- disk-first re-verification is what
actually gates the next wave.

## Related Artifacts

| Artifact | Relationship |
|----------|---------------|
| [[p12_wf_admin_orchestration]] | upstream -- the workflow whose steps this benchmark gates |
| [[p11_qg_admin_orchestration]] | sibling -- the quality gate this benchmark's threshold feeds |
