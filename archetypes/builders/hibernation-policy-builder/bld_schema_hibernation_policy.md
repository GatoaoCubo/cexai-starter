---
kind: validation_schema
id: bld_schema_hibernation_policy
pillar: P06
llm_function: CONSTRAIN
purpose: F6 CONSTRAIN schema for hibernation_policy
quality: null
title: "Schema: hibernation_policy"
version: "1.0.0"
author: n03_engineering
tags:
  - "hibernation_policy"
  - "builder"
  - "schema"
tldr: "F6 CONSTRAIN schema for hibernation_policy"
domain: "hibernation_policy construction"
created: "2026-04-18"
updated: "2026-04-18"
8f: "F1_constrain"
keywords:
  - "constrain schema for hibernation_policy"
  - "hibernation_policy construction"
  - "hibernation_policy"
  - "builder"
  - "schema"
  - "p09_hp_[a-z]+"
  - "daytona"
  - "modal"
  - "singularity"
  - "generic"
density_score: 0.90
related:
  - hp_{{backend}}
---
## Required Fields

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | string | pattern: `p09_hp_[a-z]+` | Unique artifact identifier |
| kind | string | const: `hibernation_policy` | Kind discriminator |
| pillar | string | const: `P09` | Pillar assignment |
| title | string | min 5 chars | Human-readable policy name |
| target_backend | enum | daytona\|modal\|singularity\|generic | Target backend type |
| idle_trigger.type | enum | no_activity_seconds\|no_requests_seconds\|explicit_signal | Idle detection method |
| idle_trigger.threshold_seconds | integer | >= 0 | Idle duration before hibernation |
| wake_on | list | min 1 item | Wake conditions list |
| state_persistence.keep_memory | bool | -- | Snapshot in-process memory |
| state_persistence.snapshot_disk | bool | -- | Checkpoint filesystem |
| wake_latency_sla_seconds | integer | > 0 | Max wake latency in seconds |
| version | semver | x.y.z | Artifact version |
| quality | float\|null | null or 0.0-10.0 | Peer-review score |

## Optional Fields

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| state_persistence.checkpoint_cadence_seconds | integer\|null | null | Periodic checkpoint interval (null = on-hibernate only) |
| cost_savings_estimate_pct | integer | null | Estimated idle-cost reduction (0-100) |
| tags | list | [] | Classification tags |

## Enum Values

### target_backend
- `daytona` -- Daytona workspace (workspace pause/resume API)
- `modal` -- Modal serverless (container scaling-to-zero)
- `singularity` -- Singularity HPC container (SLURM job suspend)
- `generic` -- Abstract policy; backend resolves at runtime

### idle_trigger.type
- `no_activity_seconds` -- No tool calls, agent messages, or I/O for N seconds
- `no_requests_seconds` -- No inbound HTTP/gRPC requests for N seconds (serverless only)
- `explicit_signal` -- External signal from orchestrator triggers hibernate

### wake_on items
- `incoming_request` -- Any inbound HTTP/WebSocket request
- `scheduled_cron` -- Pre-warm cron expression fires
- `explicit_signal` -- Orchestrator issues wake command via backend API

## HARD Gates (H01-H05)
- H01: frontmatter present with all required fields
- H02: `target_backend` is one of the 4 allowed enum values
- H03: `idle_trigger.type` is one of the 3 allowed enum values
- H04: `idle_trigger.threshold_seconds` >= 0
- H05: `wake_on` list is non-empty

## Naming Convention
```
p09_hp_{{backend}}.yaml

Examples:
  p09_hp_modal.yaml
  p09_hp_daytona.yaml
  p09_hp_singularity.yaml
  p09_hp_generic.yaml
```

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [\[hp_`{{backend}}`\]] | downstream | 0.41 |
