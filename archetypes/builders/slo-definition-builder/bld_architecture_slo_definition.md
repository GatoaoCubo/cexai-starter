---
quality: null
quality: null
id: bld_architecture_slo_definition
kind: knowledge_card
pillar: P08
title: "Architecture: slo_definition Relationships"
version: 1.0.0
created: "2026-04-17"
updated: "2026-04-17"
author: builder
domain: slo_definition
tags: [architecture, slo_definition, P09]
llm_function: CONSTRAIN
tldr: "How slo_definition relates to deployment_manifest, quality_gate, benchmark, and enterprise_sla."
8f: "F3_inject"
keywords: [slo_definition relationships, and enterprise_sla, architecture, slo_definition, relationship graph, kind boundaries, integration points, related artifacts, signal slo_breach, quality_gate build-time]
density_score: null
related:
  - bld_architecture_canary_config
  - bld_architecture_deployment_manifest
---
# Architecture: slo_definition

## Relationship Graph
```
[deployment_manifest] --> [slo_definition] --> [signal: slo_breach]
[workflow] ----------^           |
                                 +--> [trace_config] (observability)
                                 +--> [quality_gate] (build-time gate)
                                 +--> [learning_record] (retrospective)
```

## Kind Boundaries
| Kind | Relationship | Boundary |
|------|-------------|---------|
| enterprise_sla | PARENT | SLA is external contract; SLO is internal target (SLA >= SLO) |
| quality_gate | SIBLING | quality_gate governs build-time artifact scores; slo_definition governs runtime reliability |
| benchmark | SIBLING | benchmark is point-in-time measurement; slo_definition is ongoing target |
| deployment_manifest | UPSTREAM | deployment_manifest triggers post-deploy SLO measurement |
| trace_config | DOWNSTREAM | trace_config implements the observability that feeds SLI metrics |
| canary_config | SIBLING | canary_config uses SLO metrics as rollback trigger signals |

## Integration Points
- **Upstream**: deployment_manifest (post-deploy measurement starts), workflow (SLO as step gate)
- **Downstream**: trace_config (SLI data source), signal (slo_breach event)
- **Sibling**: quality_gate (build-time), canary_config (runtime rollback)

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[bld_architecture_canary_config]] | sibling | 0.39 |
| [[bld_architecture_deployment_manifest]] | sibling | 0.34 |
