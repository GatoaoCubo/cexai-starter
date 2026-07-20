---
id: p07_bm_ops_pipeline
kind: benchmark
pillar: P07
title: "Benchmark: Operations Pipeline"
version: "1.0.0"
created: "2026-07-20"
updated: "2026-07-20"
author: "n05_operations"
metric: "pipeline_latency"
unit: "s"
direction: "lower_is_better"
baseline: 2.0
target: 1.0
iterations: 20
warmup: 3
percentiles: [50, 95, 99]
environment: "local dev machine, Python 3.12"
domain: "operations_pipeline"
quality: null
tags: [benchmark, latency, operations, compile, dispatch, signal, pipeline, P07]
tldr: "Ops pipeline benchmark: compile_single, compile_all, doctor, signal_write, dispatch_solo, dispatch_grid -- each with baseline/acceptable/degraded thresholds."
comparison_subjects: [baseline_target, degraded_threshold]
statistical_test: "median + p95 wall-clock"
confidence_interval: 0.95
related:
  - bld_knowledge_card_benchmark
  - dispatch
  - p07_rc_ops
  - p12_wf_deploy_pipeline
---

## Benchmark Overview

Measures wall-clock latency for the six core operations-pipeline operations
this nucleus runs on every artifact: compilation, health check, inter-nucleus
signaling, and nucleus dispatch (solo and grid).

Business impact: degradation in any of these directly increases feedback-loop
latency. `compile_single` drives the inner edit-compile-verify loop.
`dispatch_grid` determines how fast a multi-nucleus mission can start.

Three tiers define operational health per case:
- **baseline**: acceptable normal operating condition
- **acceptable**: tolerable; investigate if sustained
- **degraded**: block dispatch; trigger ops alert

## Methodology

- **Iterations**: 20 runs per case (cold-ish: new process per run)
- **Warmup**: 3 runs discarded before the measurement window opens
- **Protocol**:
  1. Reset state: clear stale signal files before each run
  2. Time each operation with `time` (bash wall-clock) or `Measure-Command` (PowerShell fallback)
  3. Record p50, p95, p99 across 20 measured runs
  4. Compare p50 to baseline; compare p95 to the acceptable threshold
- **Statistical test**: median (p50) as primary; p95 as tail indicator
- **Outlier handling**: retain all runs; p99 captures tail without discarding

## Metrics

| Case ID | Operation | Unit | Direction | Baseline | Acceptable | Degraded |
|---------|-----------|------|-----------|----------|------------|----------|
| compile_single | `cex_compile.py {file}` (1 artifact) | s | lower_is_better | 2 | 5 | >5 |
| compile_all | `cex_compile.py --all` (full repo) | s | lower_is_better | 60 | 120 | >120 |
| doctor_full | `cex_doctor.py` (full health check) | s | lower_is_better | 30 | 60 | >60 |
| signal_write | `write_signal()` call to file on disk | ms | lower_is_better | 100 | 500 | >500 |
| dispatch_solo | `dispatch.sh solo n05 task` to nucleus boot | s | lower_is_better | 10 | 30 | >30 |
| dispatch_grid | `dispatch.sh grid MISSION` (multi-nucleus) | s | lower_is_better | 30 | 60 | >60 |

## Environment

- **Hardware**: local dev machine
- **Software**: Python 3.12, bash-compatible shell
- **Config**: repo on local disk; no network calls for compile/doctor/signal cases;
  dispatch cases require live-provider auth (network latency included)

## Results Template

| Case | p50 | p95 | p99 | Status |
|------|-----|-----|-----|--------|
| compile_single | -- | -- | -- | -- |
| compile_all | -- | -- | -- | -- |
| doctor_full | -- | -- | -- | -- |
| signal_write (ms) | -- | -- | -- | -- |
| dispatch_solo | -- | -- | -- | -- |
| dispatch_grid | -- | -- | -- | -- |

Status key: `[OK]` = p50 <= baseline | `[WARN]` = p50 <= acceptable | `[FAIL]` = p50 > acceptable

## References

- `_tools/cex_compile.py` -- artifact compiler (md to yaml)
- `_tools/cex_doctor.py` -- builder health check
- `_tools/signal_writer.py` -- inter-nucleus signal writer
- `_spawn/dispatch.sh` -- nucleus dispatch entry point

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[bld_knowledge_card_benchmark]] | upstream | 0.29 |
| [[dispatch]] | downstream | 0.28 |
| [[p07_rc_ops]] | sibling | 0.30 |
| [[p12_wf_deploy_pipeline]] | related | 0.27 |
