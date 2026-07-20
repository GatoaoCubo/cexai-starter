---
id: p12_ct_release_gate
kind: crew_template
pillar: P12
title: "Release Gate Crew"
version: "1.0.0"
created: "2026-07-20"
quality: null
density_score: 0.9
tags: [crew, release_gate, sequential, quality_gate, operations, N05]
related:
  - p02_ra_tester
  - p02_ra_gatekeeper
  - p02_ra_deployer
  - p12_tc_release_gate_v1
  - p12_ct_cross_provider_council
  - p12_ct_product_launch
process: sequential
roles_count: 3
crew_name: release_gate
purpose: "Validate a release candidate through automated testing, gate it against non-negotiable quality thresholds, and deploy only on a clean PASS verdict"
crewai_equivalent: "Process.sequential"
autogen_equivalent: "GroupChat.round_robin"
swarm_equivalent: "tester -> gatekeeper -> deployer"
handoff_protocol_id: a2a-task-sequential
---

## Overview
Instantiate before any release push. Owner is N05 (operations); consumers are
release engineers and the N07 orchestrator. Three roles run in strict
sequence -- each emits one artifact the next role reads before starting its
own work. This is the department's own release discipline, expressed as a
crew: nothing ships without evidence, and the gate does not bend.

## Roles

| Role | Role Assignment ID | Reason |
|------|---------------------|--------|
| tester | p02_ra_tester.md | Runs the test suite (doctor + system tests); emits `test_report.md` |
| gatekeeper | p02_ra_gatekeeper.md | Evaluates `test_report.md` against charter thresholds; issues `release_verdict.md`. The gate is the gate -- quality criteria are never negotiated. |
| deployer | p02_ra_deployer.md | Executes the deploy only on a PASS verdict; ABORTs immediately on FAIL; emits `deploy_log.md` |

Role assignments live beside this crew_template in
`N05_operations/P12_orchestration/crews/` -- the layout `cex_crew.py`
resolves natively (their `id:` keeps pillar P02, per the `role_assignment`
kind registration).

## Process
Topology: `sequential`. Rationale: gatekeeper cannot issue a verdict without
tester's report, and deployer must never run ahead of a PASS verdict.
Sequential ordering keeps the handoff contract simple and makes the
non-negotiable gate structurally impossible to skip.

## Memory Scope

| Role | Scope | Retention |
|------|-------|-----------|
| tester | shared | per-crew-instance (report consumed by gatekeeper) |
| gatekeeper | shared | persistent (verdict saved to a P08 decision record) |
| deployer | shared | per-crew-instance (deploy log is the run's audit trail) |

## Handoff Protocol
`a2a-task-sequential` -- each role writes a completion signal with
`artifact_path` + `quality_score`. The next role reads the prior artifact
before starting its own F1 CONSTRAIN. Signal path: `.cex/runtime/signals/`.

## Success Criteria
- [ ] All 3 role deliverables exist under `.cex/runtime/crews/{instance_id}/`
- [ ] tester report: doctor pass rate + system test pass rate, both with evidence
- [ ] gatekeeper verdict: PASS or FAIL with explicit threshold citations
- [ ] deployer log present only when the verdict was PASS; ABORT report otherwise
- [ ] Handoff protocol signals present for 3/3 roles
- [ ] No role produced an artifact without reading its upstream input

## Instantiation
```bash
python _tools/cex_crew.py show release_gate

python _tools/cex_crew.py run release_gate \
    --charter N05_operations/P12_orchestration/p12_tc_release_gate_v1.md

python _tools/cex_crew.py run release_gate \
    --charter N05_operations/P12_orchestration/p12_tc_release_gate_v1.md \
    --execute
```

The charter referenced above is a TEMPLATE (`{{open_vars}}` throughout) --
fill in the mission-specific values before running with `--execute`.

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[p02_ra_tester]] | upstream | 0.45 |
| [[p02_ra_gatekeeper]] | upstream | 0.45 |
| [[p02_ra_deployer]] | upstream | 0.45 |
| [[p12_tc_release_gate_v1]] | downstream | 0.40 |
| [[p12_ct_cross_provider_council]] | sibling_pattern | 0.35 |
| [[p12_ct_product_launch]] | sibling | 0.30 |
