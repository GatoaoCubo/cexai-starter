---
id: p12_tc_release_gate_v1
kind: team_charter
pillar: P12
title: "Team Charter Template -- Release Gate"
version: "1.0.0"
created: "2026-07-20"
updated: "2026-07-20"
author: n05_operations
quality: null
tags: [team_charter, release_gate, operations, template]
tldr: "Reusable team_charter TEMPLATE for the release_gate crew -- fill {{open_vars}} at instantiation time, then run with --execute."
domain: "release validation orchestration"
charter_id: "{{charter_id}}"
crew_template_ref: "N05_operations/P12_orchestration/p12_ct_release_gate.md"
mission_statement: "Validate {{release_candidate_ref}} through the tester -> gatekeeper -> deployer crew and either ship it or block it with a cited reason, by {{deadline}}."
deadline: "{{deadline}}"
related:
  - p12_ct_release_gate
  - p02_ra_gatekeeper
  - p02_ra_tester
---

## TEMPLATE -- fill before instantiation

This file is a TEMPLATE, not an instantiated charter. Every `{{open_var}}`
below must be replaced with a real value before `cex_crew.py run release_gate
--charter <this-file> --execute` is safe to run. Copy this file to a new
`p12_tc_release_gate_v{{n}}.md` per real release rather than editing this
template in place, mirroring the versioned-instance pattern the `team_charter`
kind's own ID pattern expects (`p12_tc_{{mission}}_v{{n}}.md`).

## Mission Statement
Validate `{{release_candidate_ref}}` (a commit SHA or branch name) through
the 3-role sequential [[p12_ct_release_gate]] crew. The crew completes when
deployer's log is committed (PASS path) or gatekeeper's FAIL verdict is
committed with a cited reason (block path) -- whichever the evidence supports.

## Deliverables
1. **Test report** (`test_report.md`) -- doctor pass rate + system test pass
   rate, both with evidence, produced by tester
2. **Release verdict** (`release_verdict.md`) -- PASS or FAIL with a per-check
   table (metric, threshold, actual, status), produced by gatekeeper
3. **Deploy log** (`deploy_log.md`) -- compile results, doctor check, commit
   SHA, deploy timestamp; present only on a PASS verdict, produced by deployer

## Success Metrics
| Objective | Key Result |
|-----------|------------|
| Every deliverable is evidence-backed | 0 deliverables missing a cited metric |
| The gate is never bypassed silently | gatekeeper verdict present for 100% of runs |
| Deploy never outruns the gate | deployer log absent whenever verdict is FAIL |
| Quality gate | release_verdict quality >= {{quality_gate_threshold}} (charter default: 8.5) |

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
| Release owner | {{release_owner}} | Accountable for the go/no-go outcome |

## Quality Gate
- Floor: 8.0 (system-wide publish floor)
- Target for this charter: `{{quality_gate_threshold}}` (charter default: 8.5)
- Per-deliverable: `test_report.md` and `release_verdict.md` must each cite a
  reproducible command or log line for every claim -- no unverified summary
  passes gatekeeper.

## Escalation Protocol
If any role crosses its token ceiling or fails 3 consecutive attempts, emit
`signal_{role}_escalate.json` to `.cex/runtime/signals/`. N07 reads it and
either extends the budget or pages `{{escalation_contact}}`.

## Termination Criteria
ANY of:
1. deployer's `deploy_log.md` is committed (PASS path complete)
2. gatekeeper's `release_verdict.md` is FAIL and committed with a cited reason (block path complete)
3. Token or wall-clock budget exhausted (emit a partial-completion signal)
4. `{{deadline}}` passed -- save work-in-progress artifacts before exit
5. 3 consecutive failures on the same artifact (stuck loop -- escalate immediately)

## Instantiation Override
Fill the open vars above directly, or override at run time:
```bash
python _tools/cex_crew.py run release_gate \
    --charter N05_operations/P12_orchestration/p12_tc_release_gate_v1.md \
    --override deadline="2026-08-01T17:00:00Z" \
    --override budget.tokens=60000 \
    --execute
```

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[p12_ct_release_gate]] | upstream | 0.55 |
| [[p02_ra_gatekeeper]] | related | 0.35 |
| [[p02_ra_tester]] | related | 0.30 |
