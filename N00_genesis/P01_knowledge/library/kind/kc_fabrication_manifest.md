---
id: kc_fabrication_manifest
kind: knowledge_card
8f: F3_inject
type: kind
pillar: P12
title: "Fabrication Manifest — Deep Knowledge for fabrication_manifest"
version: 1.0.0
created: 2026-07-20
updated: 2026-07-20
author: knowledge_agent
domain: fabrication_manifest
quality: null
tags: [fabrication_manifest, P12, COLLABORATE, kind-kc]
tldr: "A resumable, per-run ledger of fabrication stages, gates, and provenance -- references its config rather than duplicating it."
when_to_use: "Building, reviewing, or reasoning about fabrication_manifest artifacts"
keywords: [fabrication manifest, stage status, resumable pipeline, provenance ledger, run record]
feeds_kinds: [fabrication_manifest]
density_score: null
aliases: ["fabrication run record", "bootstrap ledger", "stage status file", "resume anchor"]
user_says: ["track the status of this build run", "resume a fabrication that got interrupted", "record which stages finished for this tenant", "what happened during this bootstrap run"]
long_tails: ["I need to know exactly which stages of a fabrication run finished and which failed", "resume a bootstrap run without redoing the stages that already succeeded", "keep a per-run ledger that references the config instead of copying it", "avoid re-running a stage that already passed its quality gate"]
cross_provider:
  terraform: "State file -- tracks what has been provisioned; this kind tracks what has been fabricated"
  github_actions: "Workflow run -- per-job status, re-run only failed jobs"
  airflow: "DAG run state -- per-task status with idempotent re-run semantics"
related:
  - kc_white_label_config
  - kc_capability_registry
  - kc_team_charter
  - kc_deployment_manifest
  - white-label-config-builder
  - capability-registry-builder
---

# Fabrication Manifest

## Spec
```yaml
kind: fabrication_manifest
pillar: P12
llm_function: COLLABORATE
max_bytes: 4096
naming: p12_fm_{{tenant}}.yaml
id_pattern: "^p12_fm_[a-z][a-z0-9_]*$"
core: false
```

## What It Is
A `fabrication_manifest` is a typed, per-run RECORD of one fabrication run: which stages have
executed, whether each stage's quality gate passed, and a resumable ledger tying the run to its
provenance. It REFERENCES a brand/white-label config and the set of chosen capabilities for the
run -- it does NOT define either, only points at them. Unlike many hand-authored CEX kinds, it is
typically WRITTEN BY the fabrication process itself as stages complete -- treat an existing
manifest as something to read and interpret, not to freely compose from imagination. It is NOT
`team_charter` (a crew's mission contract -- budget, deadline, roles), NOT `deployment_manifest`
(what deploys where, with rollback), and NOT `white_label_config` (the branding spec it
references).

## Cross-Framework Map
| Framework/Provider | Class/Concept | Notes |
|---|---|---|
| Terraform | State file | Tracks what has been provisioned; this kind tracks what has been fabricated |
| GitHub Actions / GitLab CI | Pipeline run record | Per-job status; a re-run repeats only failed jobs |
| Airflow / dbt | DAG run state / run results | Per-task state with idempotent re-run semantics |

## Key Fields
| Field | Type | Required | Notes |
|---|---|---|---|
| run_id / tenant_id | string | yes | Identity key for this one fabrication run |
| config_ref | string or null | yes | A REFERENCE to the source config -- never duplicated values |
| chosen_capabilities | list | yes | Capability set for this run; union-merged on resume |
| stage_status | object | yes | One entry per pipeline stage, each `pending \| done \| skipped \| error` |
| targets | object | yes | Per-output-layer result, filled in as stages complete |
| hosting_target | string | yes | A registered hosting/deploy target id |
| status | enum | yes | Overall run status, e.g. `draft -> in_progress -> complete` |

## Patterns
| Pattern | When to Use | Example |
|---|---|---|
| Reference, never duplicate | Any manifest pointing at config owned by another kind | `config_ref` is a pointer; the actual brand values live in `white_label_config` |
| Idempotent resume | Any multi-stage run that might be interrupted | Re-running the pipeline only executes stages not already `done` |
| Per-stage gate | Any pipeline where partial failure must not look like success | Each stage records its own status; a downstream stage cannot claim `done` if its inputs are not |

## Anti-Patterns
| Anti-Pattern | Why It Fails | Fix |
|---|---|---|
| Duplicating config values inline | Drifts from the source of truth the moment either copy changes | Store a reference (`config_ref`) only; resolve real values at read time |
| Hand-writing a stage as `done` | Corrupts the resume anchor; later runs skip work that never happened | Only the process that executed a stage may mark it `done` |
| Treating this like a mission contract | Confuses a run's LEDGER with a crew's BUDGET/DEADLINE/ROLES contract | Use `team_charter` for crew mission contracts; keep this kind to stage/gate/provenance tracking |
| Treating this like a deployment target list | Confuses WHAT HAPPENED with WHAT SHOULD DEPLOY WHERE | Use `deployment_manifest` for deploy targets and rollback plans |

## Integration Graph
```
[white_label_config] --config_ref--> [fabrication_manifest] <--chosen_capabilities-- [capability_registry]
                                              |
                                   [stage_status ledger, resumable]
```

## Decision Tree
- IF you need a per-run ledger of stages/gates/provenance for ONE fabrication THEN fabrication_manifest
- IF you need the branding spec being referenced THEN white_label_config
- IF you need the crew's mission contract (budget/deadline/roles) THEN team_charter
- IF you need what deploys where, with rollback THEN deployment_manifest
- DEFAULT: fabrication_manifest for any resumable, gated, per-run fabrication record

## Quality Criteria
- GOOD: config referenced (not duplicated); chosen_capabilities recorded; stage_status present for every pipeline stage
- GREAT: fully resumable (idempotent re-run); every stage's gate recorded; provenance traceable per stage
- FAIL: config values duplicated inline; a stage marked done without its gate passing; no resume anchor (a re-run restarts from zero)

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[kc_white_label_config]] | upstream (referenced config) | 0.50 |
| [[kc_capability_registry]] | upstream (capability universe) | 0.48 |
| [[kc_team_charter]] | sibling (contrast: mission contract) | 0.35 |
| [[kc_deployment_manifest]] | sibling (contrast: deploy target list) | 0.35 |
| [[white-label-config-builder]] | related | 0.30 |
| [[capability-registry-builder]] | related | 0.30 |
