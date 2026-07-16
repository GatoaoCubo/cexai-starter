---
quality: null
quality: null
kind: memory
id: bld_memory_terminal_backend
pillar: P10
llm_function: INJECT
purpose: Memory hooks for terminal_backend builder
title: "Memory Terminal Backend"
version: "1.0.0"
author: n03_engineering
tags:
  - "terminal_backend"
  - "builder"
  - "memory"
tldr: "Memory hooks: persist active backend selection, cost alerts, session outcomes for routing decisions"
domain: "terminal_backend construction"
created: "2026-04-18"
updated: "2026-04-18"
8f: "F3_inject"
keywords:
  - "terminal_backend construction"
  - "memory terminal backend"
  - "memory hooks"
  - "persist active backend selection"
  - "cost alerts"
  - "terminal_backend"
  - "builder"
  - "memory"
  - "### on cost alert"
  - "### on auth failure"
density_score: 0.88
related:
  - bld_memory_hibernation_policy
  - bld_config_terminal_backend
---
## What to Persist

| Event | Memory Type | KC to Update |
|-------|------------|-------------|
| Backend switched | entity_memory | Record active backend per nucleus |
| Cost threshold exceeded | entity_memory | Flag backend as high-cost for routing |
| Session timeout hit | learning_record | Log timeout_seconds was too short |
| Auth failure | entity_memory | Mark backend as auth-broken, alert N05 |
| Hibernation trigger | entity_memory | Record idle duration that triggered hibernation |

## Memory Hooks

### On Successful Session
```
entity_memory: {nucleus}_active_backend = {backend_type}
learning_record: session completed, backend={backend_type}, duration_seconds={actual}
```

### On Cost Alert
```
entity_memory: {backend_type}_cost_flagged = true
signal: write_signal('n05', 'cost_alert', backend={backend_type}, usd_per_hour={estimate})
```

### On Auth Failure
```
entity_memory: {backend_type}_auth_status = 'broken'
signal: write_signal('n05', 'auth_failure', backend={backend_type}, secret_ref={ref})
```

## Routing Influence
N07 reads `entity_memory` before dispatching to prefer:
1. Backends with `auth_status != 'broken'`
2. Backends where cost < `cost_alert_threshold_usd_per_hour`
3. Backends matching the task's compute profile (GPU -> modal, HPC -> singularity)

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[bld_memory_hibernation_policy]] | related | 0.37 |
| [[bld_config_terminal_backend]] | upstream | 0.34 |
