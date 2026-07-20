---
id: p12_pt_ci_cd_deploy
kind: pipeline_template
8f: F8_collaborate
nucleus: n05
pillar: P12
title: "N05 Operations -- Pipeline Template (CI/CD)"
scenario: ci_cd_deploy
version: "1.0.0"
created: "2026-07-20"
updated: "2026-07-20"
author: n05_operations
quality: null
tags: [n05, operations, pipeline_template, ci_cd, gating_wrath, P12]
tldr: "N05 CI/CD pipeline recipe: lint, test, scan, build, deploy, verify, monitor -- a gate at every stage, zero tolerance for a skipped validation."
keywords: [pipeline template, ci cd pipeline, stage sequence, quality gates, revision loop, gating wrath]
density_score: 0.95
related:
  - pipeline-template-builder
  - bld_schema_bugloop
  - bld_schema_pipeline_template
  - p12_wf_deploy_pipeline
---

## Scenario: CI/CD Operations Pipeline

N05 owns the operational pipeline scenarios: build, test, deploy, rollback. Every stage
has a mandatory gate. No stage can be skipped. Gating Wrath lens: if a gate fails, the
pipeline stops -- no mercy, no "ship it anyway."

## What a pipeline_template is (and is not)

A `pipeline_template` is a **scenario-indexed agent sequence**: it says which roles run,
in what order, and what gates each stage, for a NAMED situation (here: `ci_cd_deploy`). It
is NOT a `crew_template` (crews have fixed named roles + a handoff protocol for one
coherent deliverable) and it is NOT a `workflow` (a workflow is a fixed DAG of steps with
no revision loop). A pipeline_template's defining feature is that it has a **revision
loop** -- a stage can retry, up to a bound, before it escalates.

## Stage Sequence

| Order | Role | Model Tier | Optional | Gate | Failure Mode | Rollback |
|-------|------|-----------|----------|------|--------------|----------|
| 1 | linter | low | No | syntax clean | block pipeline | n/a |
| 2 | tester | medium | No | all tests pass | block pipeline | n/a |
| 3 | security_scanner | medium | No | no critical CVEs | block pipeline | n/a |
| 4 | builder | medium | No | artifact compiles | block pipeline | n/a |
| 5 | deployer | high | No | health check pass | auto-rollback | revert to last-good |
| 6 | verifier | medium | No | smoke test pass | auto-rollback | revert to last-good |
| 7 | monitor | low | No | no error spike 5min | alert oncall | manual decision |

## Revision Loop

| Parameter | Value | Notes |
|-----------|-------|-------|
| Max iterations | 3 | Proven default (see [[bld_schema_bugloop]] for the same 3-strike shape) |
| Quality floor | 9.0 | N05 demands higher than the generic 8.5 publish floor |
| Priority | security > quality > implementation | Non-negotiable |
| Escalation | orchestrator | Decides after 3 failures |
| SLA target | pipeline complete < 15min | Alert at 12min |

## Quality Gates (Gating-Wrath-Enforced)

| Gate | Stage | Mandatory | Failure Action |
|------|-------|-----------|----------------|
| Lint pass | linter | Yes | Block |
| Test pass | tester | Yes | Block |
| CVE scan clean | security_scanner | Yes | Block |
| Compile success | builder | Yes | Block |
| Health check | deployer | Yes | Auto-rollback |
| Smoke test | verifier | Yes | Auto-rollback |
| Error rate stable | monitor | Yes | Alert + manual |

## Failure Modes

| Failure | Detection | Auto-Response | Escalation |
|---------|-----------|--------------|------------|
| Test flake | >2 flaky runs in 24h | quarantine test | oncall |
| Build timeout | >5min | kill + retry 1x | alert |
| Deploy health fail | HTTP 5xx from health endpoint | instant rollback | page oncall |
| Smoke test fail | assertion error | rollback + dead-letter | orchestrator |
| Post-deploy error spike | error rate >2x baseline | rollback | page oncall |

## Instantiation

```yaml
pipeline:
  template_ref: p12_pt_ci_cd_deploy
  scenario: ci_cd_deploy
  revision_loop:
    max_iterations: 3
    escalation_target: n07_orchestrator
```

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[pipeline-template-builder]] | upstream | 0.30 |
| [[bld_schema_bugloop]] | related | 0.28 |
| [[bld_schema_pipeline_template]] | upstream | 0.26 |
| [[p12_wf_deploy_pipeline]] | sibling | 0.24 |
