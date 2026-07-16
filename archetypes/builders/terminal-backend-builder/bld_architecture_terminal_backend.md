---
quality: null
quality: null
kind: architecture
id: bld_architecture_terminal_backend
pillar: P08
llm_function: CONSTRAIN
purpose: Component map of terminal_backend -- inventory, dependencies, position in P09 stack
title: "Architecture Terminal Backend"
version: "1.0.0"
author: n03_engineering
tags: [terminal_backend, builder, architecture]
tldr: "Component map of terminal_backend: 6 backend adapters, auth layer, cost model, environments/ convention"
domain: "terminal_backend construction"
created: "2026-04-18"
updated: "2026-04-18"
8f: "F1_constrain"
keywords: [position in p, terminal_backend construction, architecture terminal backend, component map of terminal_backend, backend adapters, auth layer, cost model, terminal_backend, builder, architecture]
density_score: 0.90
related:
  - bld_collaboration_terminal_backend
  - n00_terminal_backend_manifest
  - terminal-backend-builder
  - kc_terminal_backend
  - tb_{{backend}}
---
## Component Inventory

| Name | Role | Owner | Status |
|------|------|-------|--------|
| Backend Adapter | Translates terminal_backend YAML to provider-specific config | N05 | Active |
| Auth Resolver | Reads auth.method + secret_ref and resolves credentials | N05 | Active |
| Resource Limit Enforcer | Applies cpu/memory/timeout limits at session start | N05 | Active |
| Cost Model Tracker | Records billing events per session for budget reporting | N05 | Active |
| Hibernation Controller | Triggers suspend/wake for hibernation_capable backends | N05 | Active (daytona only) |
| Environment Switcher | Swaps active backend by reading environments/ directory | N07 | Active |

## Backend Adapter Map

| backend_type | Adapter | Connection Config |
|--------------|---------|-------------------|
| local | LocalAdapter | none (host OS) |
| docker | DockerAdapter | image, registry, runtime (runc/gVisor) |
| ssh | SSHAdapter | host, user, port, key_path |
| daytona | DaytonaAdapter | workspace_id, api_endpoint |
| modal | ModalAdapter | app_name, stub_name, gpu |
| singularity | SingularityAdapter | image_path, bind_mounts |

## Dependencies

| From | To | Type |
|------|----|------|
| Backend Adapter | secret_config | Data (auth credentials) |
| Backend Adapter | sandbox_config | Control (isolation layer wrapping session) |
| Backend Adapter | env_config | Data (env vars injected into session) |
| Cost Model Tracker | runtime_rule | Control (budget rules trigger alerts) |
| Hibernation Controller | hibernation_policy | Control (policy defines idle threshold) |

## Architectural Position

terminal_backend sits at the bottom of the P09 execution stack:

```
N05 agent intent
    |
    v
terminal_backend (WHERE to run)
    |
    +-- sandbox_config (HOW to isolate)
    |
    +-- env_config (WHAT vars to inject)
    |
    +-- runtime_rule (WHEN to timeout/retry)
    |
    +-- secret_config (HOW to authenticate)
```

Switching backends (e.g., local -> modal for GPU) requires only a YAML swap in `environments/`.
No agent code changes. This is the "no code changes required" guarantee .

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[bld_collaboration_terminal_backend]] | downstream | 0.45 |
| [[n00_terminal_backend_manifest]] | downstream | 0.39 |
| [[terminal-backend-builder]] | downstream | 0.36 |
| [[kc_terminal_backend]] | upstream | 0.34 |
| [\[tb_`{{backend}}`\]] | downstream | 0.34 |
