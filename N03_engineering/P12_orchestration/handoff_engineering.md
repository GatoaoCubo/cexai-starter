---
id: p12_ho_builder_nucleus
kind: handoff
8f: F8_collaborate
pillar: P12
title: Handoff Protocol -- Builder Nucleus
version: 1.0.0
created: 2026-03-30
updated: 2026-03-30
author: builder_agent
domain: meta-construction
quality: null
tags: [handoff, builder, N03]
tldr: "N03 handoff protocol: receive (task+domain+context+quality_target), deliver (path+kind+quality+compiled+indexed+issues), signal 4 events (building/complete/error/retry), crew chains pass artifact paths as context."
keywords: [atomic writes, schema validation, timeout enforcement, audit trail, handoff payload format, temp-file, payload hash, ttl_seconds]
density_score: 0.88
related:
  - p12_wf_builder_8f_pipeline
  - p12_dag_builder_8f
  - p12_ct_build_review
  - bld_schema_handoff
---

# Handoff Protocol: Builder Nucleus

## Receiving Work

| Field | Required | Description |
|-------|----------|-------------|
| task | yes | What to build (natural language or explicit kind) |
| domain | no | Domain context |
| context | no | Additional knowledge to inject |
| quality_target | no (default 9.0) | Minimum quality |
| output_dir | no | Where to save |

## Delivering Results

| Field | Type | Description |
|-------|------|-------------|
| path | string | File path of created artifact |
| kind | string | What kind was built |
| quality | float | Score from F7 |
| compiled | boolean | .yaml generated |
| indexed | boolean | Index updated |
| issues | list | Warnings from validation |

## Signal Protocol

| Event | Signal | Payload |
|-------|--------|---------|
| Build started | building | kind, domain |
| Build complete | complete | path, quality, kind |
| Build failed | error | kind, step, reason |
| Retry triggered | retry | kind, attempt, issues |

## Crew Handoffs

Multi-kind crews chain handoffs:
Builder A produces artifact > hands path to Builder B as context >
Builder B produces next > chain continues until crew complete.
Each step signals independently. Crew done when all signals received.
The `build_review` crew_template (`P12_orchestration/crews/`) is a worked
example of exactly this chain, using the `a2a-task-sequential` protocol below.

## Handoff Protocol Details

Inter-nucleus handoffs follow a strict write-read-acknowledge lifecycle:

- **Atomic writes**: handoff files created via temp-file + rename to prevent partial reads
- **Schema validation**: receiving nucleus validates payload against expected schema before processing
- **Timeout enforcement**: unacknowledged handoffs trigger escalation after configurable TTL
- **Audit trail**: every handoff logged with timestamp, source, target, and payload hash

### Handoff Payload Format

```yaml
# Standard handoff envelope
handoff:
  source: N03
  target: N05
  created: 2026-04-07T15:00:00
  ttl_seconds: 300
  payload_hash: sha256:abc123
  schema_version: 1.0
  task: "Run tests on scaffolded project"
  context:
    artifacts: [project_scaffold.md]
    quality_threshold: 9.0
```

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[p12_wf_builder_8f_pipeline]] | sibling | 0.29 |
| [[p12_dag_builder_8f]] | sibling | 0.26 |
| [[p12_ct_build_review]] | downstream | 0.25 |
| [[bld_schema_handoff]] | related | 0.21 |
