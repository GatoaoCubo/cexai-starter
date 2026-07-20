---
id: p12_ct_incident_response
kind: crew_template
8f: F2_become
pillar: P12
llm_function: CALL
crew_name: incident_response
purpose: "Coordinate a 4-role sequential crew that detects, contains, analyzes, and documents production incidents end-to-end"
process: sequential
roles_count: 4
crewai_equivalent: "Process.sequential"
autogen_equivalent: "GroupChat.round_robin"
swarm_equivalent: "detector -> responder -> analyst -> reporter"
handoff_protocol_id: a2a-task-sequential
quality: null
keywords: [incident response crew, production incident management, detect scope, apply fix, root cause, incident report, crew_template]
density_score: 0.9
title: "Incident Response Crew Template"
version: "1.0.0"
author: n05_operations
tags: [crew_template, incident_response, operations, composable, N05]
tldr: "4-role sequential crew: detect scope -> apply fix -> root cause -> incident report."
domain: "production incident management"
created: "2026-07-20"
updated: "2026-07-20"
related:
  - p02_ra_detector
  - p02_ra_responder
  - p02_ra_incident_analyst
  - p02_ra_reporter
  - p12_tc_incident_default
  - p12_ct_release_gate
---

## Overview
Instantiate when a production incident requires structured triage, containment,
root-cause analysis, and documentation. Owner is N05 (operations); consumers are
on-call engineers, SRE leads, and the post-incident review process. Each role
emits a discrete artifact consumed by the next; no role begins without reading
the upstream output. Handoff is via a2a Task with artifact path attached.

## Roles
| Role | Role Assignment ID | Reason |
|------|---------------------|--------|
| detector | p02_ra_detector.md | Scans logs/metrics, triages severity, scopes impact |
| responder | p02_ra_responder.md | Applies fix, validates resolution, documents actions taken |
| analyst | p02_ra_incident_analyst.md | Root cause analysis, identifies systemic patterns, failure modes |
| reporter | p02_ra_reporter.md | Writes incident report, updates runbooks, creates regression checks |

Role assignments live beside this crew_template in
`N05_operations/P12_orchestration/crews/` -- the layout `cex_crew.py`
resolves natively (their `id:` keeps pillar P02, per the `role_assignment`
kind registration).

## Process
Topology: `sequential`. Rationale: each role strictly depends on the previous
artifact. Responder needs detector's triage brief; analyst needs responder's
remediation log; reporter needs analyst's RCA. Parallelism introduces
consistency risk (responder must not guess scope; analyst must not fabricate
timeline from scratch).

## Memory Scope
| Role | Scope | Retention |
|------|-------|-----------|
| detector | shared | per-crew-instance (triage brief consumed by all downstream) |
| responder | shared | per-crew-instance (remediation log consumed by analyst) |
| analyst | shared | persistent (RCA persists to the P01 knowledge base) |
| reporter | shared | persistent (incident report + runbook updates persist cross-session) |

## Handoff Protocol
`a2a-task-sequential` -- each role writes a completion signal with
`artifact_path` + `quality_score`. The next role reads the prior artifact before
starting its own work. Signal path: `.cex/runtime/signals/`.

## Success Criteria
- [ ] All 4 role deliverables exist under `.cex/runtime/crews/{instance_id}/`
- [ ] detector triage brief includes severity level (P0/P1/P2/P3) and impact scope
- [ ] responder log documents every action taken with timestamps
- [ ] analyst RCA identifies at least 1 contributing factor and 1 systemic pattern
- [ ] reporter artifact: incident report saved, runbook updated, regression_check created
- [ ] Handoff protocol signals present for 4/4 roles
- [ ] No role produced an artifact without reading its upstream input

## Instantiation
```bash
python _tools/cex_crew.py show incident_response

python _tools/cex_crew.py run incident_response \
    --charter N05_operations/P12_orchestration/crews/team_charter_incident_default.md

python _tools/cex_crew.py run incident_response \
    --charter N05_operations/P12_orchestration/crews/team_charter_incident_default.md \
    --execute
```

The charter referenced above is a TEMPLATE (`{{open_vars}}` throughout) --
fill in the mission-specific values before running with `--execute`.

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[p02_ra_detector]] | upstream | 0.42 |
| [[p02_ra_responder]] | upstream | 0.40 |
| [[p02_ra_incident_analyst]] | upstream | 0.38 |
| [[p02_ra_reporter]] | upstream | 0.37 |
| [[p12_tc_incident_default]] | downstream | 0.35 |
| [[p12_ct_release_gate]] | sibling_pattern | 0.30 |
