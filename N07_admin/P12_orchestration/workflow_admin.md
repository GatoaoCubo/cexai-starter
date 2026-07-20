---
id: p12_wf_admin_orchestration
kind: workflow
pillar: P12
title: "Orchestration Workflows -- Solo, Grid Static, Grid Continuous"
version: "1.0.0"
quality: null
tags: [workflow, orchestration, dispatch, solo, grid]
8f: F8_collaborate
nucleus: n07
domain: orchestration
created: "2026-07-20"
tldr: "Three dispatch workflows an orchestrator nucleus picks from: solo for one builder, grid-static for a fixed parallel set, grid-continuous for dependency-ordered waves."
slots:
  nucleus: "{{target_nucleus}}"
  mission: "{{mission_codename}}"
  file: "{{handoff_filename}}"
  quality_floor: 8.0
related:
  - p12_dr_admin_orchestration
  - p12_ho_n07
  - p12_sig_admin_orchestration
---

# Orchestration Workflows

## Purpose

Three concrete dispatch workflows an orchestrator nucleus chooses from. Solo for
a single task, Grid Static for a fixed parallel set, Grid Continuous for
dependency-ordered waves. As an 8F unit this workflow is **F6 PRODUCE**: it turns
an intent into dispatched, validated deliverables.

## How to use

1. Classify the request: one nucleus -> A; fixed parallel set -> B; ordered waves -> C.
2. Bind the slots above (`{{target_nucleus}}`, `{{mission_codename}}`, `{{handoff_filename}}`).
3. Execute the steps in order; never skip the quality gate (>= 8.0).
4. Always write the handoff before dispatch; always read the signal before accepting.

## A: Solo Dispatch

| Step | Action | Command |
|---|---|---|
| 1 | Write handoff | `.cex/runtime/handoffs/{{mission}}_{{nucleus}}.md` |
| 2 | Dispatch builder | `bash _spawn/dispatch.sh solo {{nucleus}} "Read {{file}} and execute."` |
| 3 | Monitor signal | `bash _spawn/dispatch.sh status` |
| 4 | Validate quality | `python _tools/cex_doctor.py` |
| 5 | Accept or feedback | quality >= 8.0 -> archive handoff; else re-dispatch with feedback |

## B: Grid Static

Up to 6 parallel builders, one handoff per nucleus, launched together.

1. Write N handoff files: `.cex/runtime/handoffs/{{mission}}_{{nucleus}}_{{seq}}.md`
2. Launch: `bash _spawn/dispatch.sh grid {{MISSION_NAME}}`
3. Monitor: `bash _spawn/dispatch.sh status` until all signal complete or error
4. Mission completes only when every artifact clears quality >= 8.0

## C: Grid Continuous

Multi-wave mission with dependency ordering between waves.

1. Wave 0: independent tasks dispatch in parallel
2. Wait for all Wave 0 signals
3. Wave 1: dependent tasks dispatch, using Wave 0 outputs as context
4. Repeat until all waves complete
5. Finalize: validate outputs, archive handoffs, emit mission-complete signal

## Signals

- On step complete: nucleus emits to `.cex/runtime/signals/{{nucleus}}_complete.json`
- On workflow complete: orchestrator emits `write_signal('{{nucleus}}', 'complete', {{score}}, '{{mission}}')`
- On error: nucleus emits an error signal; orchestrator reads it and decides retry/escalate

## Related Artifacts

| Artifact | Relationship |
|----------|---------------|
| [[p12_dr_admin_orchestration]] | sibling -- routes work before this workflow dispatches it |
| [[p12_ho_n07]] | downstream -- the handoff format each step writes/reads |
| [[p12_sig_admin_orchestration]] | downstream -- the signal format Step 3 polls for |
