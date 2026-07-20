---
id: p07_rc_ops
kind: regression_check
pillar: P07
version: "1.0.0"
created: "2026-07-20"
updated: "2026-07-20"
author: regression-check-builder
title: "N05 Operations Known-Failure Registry"
name: "N05 Operations Known-Failure Registry"
baseline_ref: "incident_log/n05_ops_baseline"
threshold: 0
metrics:
  - unicode_crash
  - orphan_processes
  - signal_storm
  - self_scoring
  - cross_nucleus_write
  - compile_drift
quality: null
tags: [regression_check, n05_operations, known_failure, P07]
tldr: "Six known-failure patterns for N05 ops. Zero-tolerance (threshold=0). Blocks on any detection. Sin lens: Gating Wrath."
description: "Known-failure registry for the N05 operations nucleus. Each pattern has a detection command, prevention control, severity, and source incident class."
comparison_mode: absolute
fail_action: block
notify: [n07_orchestrator, n05_ops_owner]
cadence: on_pr
scope: "N05_operations nucleus -- all .py tools and dispatch workflows"
related:
  - nucleus_def_n05
  - p07_bm_ops_pipeline
  - p11_qg_artifact
---

## Overview

Known-failure registry for N05 operations (sin lens: Gating Wrath). Six
incident-derived and policy-derived patterns that must never recur. Runs on
every PR. Owned by N05; escalates to N07 on any detection.

## Baseline

**baseline_ref**: `incident_log/n05_ops_baseline`
Zero-failure snapshot captured after the ASCII-code rule and orphan-cleanup
policy were both confirmed green.

**Update policy**: Rotate only when a pattern is added or retired after 90
clean runs.

## Metrics

| ID | Detection | Severity | Source |
|----|-----------|----------|--------|
| `unicode_crash` | `cex_sanitize.py --check` exits 1 | critical | encoding incident |
| `orphan_processes` | worker process age > 2h with no signal | high | dispatch incident |
| `signal_storm` | signal files > 100 in 60s | high | design review |
| `self_scoring` | `quality:` field != null in artifact | critical | day-1 rule |
| `cross_nucleus_write` | git diff outside N05_operations/ | high | RBAC policy |
| `compile_drift` | .md newer than .yaml counterpart | medium | operational |

**Threshold**: 0 absolute. Binary violations -- zero tolerance, zero variance.

## Failure Protocol

1. **fail_action**: block. No deploy proceeds with any detector red.
2. **Notify**: n07_orchestrator (immediate), n05_ops_owner (5 min).
3. **Remediation**:
   - `unicode_crash`: `cex_sanitize.py --fix` -> verify -> re-stage.
   - `orphan_processes`: kill the process tree -> audit the dispatch script.
   - `signal_storm`: add a rate-gate (max 10/min) to the signal-writer call site.
   - `self_scoring`: set `quality: null` -> recompile -> recommit.
   - `cross_nucleus_write`: revert to the correct nucleus path -> audit handoff scope.
   - `compile_drift`: `cex_compile.py <path>` on all modified .md files.
4. **Escalation**: unresolved after 30 min -> N07 halts grid dispatch.

## Detection Commands

```bash
# unicode_crash
python _tools/cex_sanitize.py --check --scope _tools/ --scope boot/
# exit 1 = non-ASCII found in executable code

# self_scoring
grep -rn "^quality: [0-9]" N05_operations/ --include="*.md" | grep -v "README"
# any match = violation

# cross_nucleus_write
git diff --name-only HEAD~1 | grep -v "^N05_operations/" | grep -v "^\.cex/"
# any match outside N05 scope = violation

# compile_drift
for f in $(find N05_operations -name "*.md" -newer N05_operations/compiled/ -type f 2>/dev/null); do
  echo "DRIFT: $f"; done
```

## Retirement Policy

A pattern is retired after:
1. 90 consecutive clean runs (no detections)
2. The root cause was architecturally eliminated (not just worked around)
3. N07 approves removal via decision manifest
4. The pattern is moved to a retired-patterns log with retirement date

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[nucleus_def_n05]] | upstream | 0.29 |
| [[p07_bm_ops_pipeline]] | sibling | 0.30 |
| [[p11_qg_artifact]] | related | 0.27 |
