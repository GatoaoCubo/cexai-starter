---
quality: null
quality: null
id: bld_instruction_canary_config
kind: instruction
pillar: P09
version: 1.0.0
created: "2026-04-17"
updated: "2026-04-17"
author: builder
title: "Canary Config Builder Instructions"
target: "canary-config-builder agent"
phases_count: 4
prerequisites:
  - "Deployment target and service name are identified"
  - "Traffic stages are defined or can be derived"
  - "Rollback metric and threshold are known"
tags: [instruction, canary_config, P09, rollout]
llm_function: REASON
tldr: "Build a canary_config with traffic stages, analysis intervals, and rollback trigger configuration."
8f: "F6_produce"
keywords: [canary config builder instructions, analysis intervals, and rollback trigger configuration, instruction, canary_config, rollout, service_name, canary_version, stable_version, stages]
density_score: null
related:
  - bld_manifest_canary_config
  - kc_canary_config
  - bld_quality_gate_canary_config
  - bld_knowledge_card_canary_config
  - bld_output_template_canary_config
---
## Context
The canary-config-builder produces a `canary_config` -- a progressive delivery specification that shifts traffic incrementally from stable to canary version with automatic rollback if metrics breach thresholds. NOT feature_flag (boolean toggle), NOT ab_test_config (statistical experiment), NOT deployment_manifest (artifact list).

**Input contract**:
- `service_name`: string -- service being deployed
- `canary_version`: string -- the new version being rolled out
- `stable_version`: string -- the currently running version
- `stages`: list -- each with traffic_percent, pause_duration_minutes
- `rollback_trigger_metric`: string -- metric name
- `rollback_trigger_threshold`: float -- breach value that triggers rollback

## Phases

### Phase 1: Define Traffic Stages
Standard canary progression: 5% -> 25% -> 50% -> 100%.
Each stage:
- `traffic_percent`: int (canary receives this %)
- `pause_duration_minutes`: how long to hold before advancing
- `analysis_interval_minutes`: how often to evaluate metrics during this stage

### Phase 2: Define Rollback Triggers
Conditions that cause automatic rollback to stable_version:
- `error_rate_threshold`: if canary error rate > X%
- `latency_p99_threshold_ms`: if canary p99 latency > X ms
- `slo_breach`: reference to slo_definition id

### Phase 3: Define Analysis Method
- `provider`: Argo Rollouts | Flagger | custom
- `metric_provider`: Prometheus | DataDog | CloudWatch
- `success_condition`: formula to evaluate metric (e.g. `result < 0.05`)

### Phase 4: Compose Artifact
Required frontmatter: id, kind, pillar, service_name, canary_version, stable_version, stages_count, quality: null.
Required body: Traffic Stages, Rollback Triggers, Analysis Configuration.

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[bld_manifest_canary_config]] | related | 0.48 |
| [[kc_canary_config]] | upstream | 0.46 |
| [[bld_quality_gate_canary_config]] | upstream | 0.45 |
| [[bld_knowledge_card_canary_config]] | upstream | 0.42 |
| [[bld_output_template_canary_config]] | upstream | 0.38 |
