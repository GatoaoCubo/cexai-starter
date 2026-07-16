---
kind: handoff
id: bld_collaboration_hibernation_policy
pillar: P12
llm_function: COLLABORATE
purpose: F8 signals and collaboration protocol for hibernation_policy
quality: null
title: "Collaboration: hibernation_policy Builder"
version: "1.0.0"
author: n03_engineering
tags: [hibernation_policy, builder, collaboration]
tldr: "F8 signals and collaboration protocol for hibernation_policy"
domain: "hibernation_policy construction"
created: "2026-04-18"
updated: "2026-04-18"
8f: "F8_collaborate"
keywords: [hibernation_policy construction, hibernation_policy builder, hibernation_policy, builder, collaboration, environments/, terminal_backend, environments/p09_hp_modal.yaml, environments/p09_hp_daytona.yaml, replace]
density_score: 0.90
related:
  - bld_tools_terminal_backend
  - bld_architecture_hibernation_policy
  - bld_architecture_terminal_backend
  - n00_hibernation_policy_manifest
  - n00_terminal_backend_manifest
---
## F8 COLLABORATE Protocol

### 1. Save
Save to `environments/` directory alongside the sibling `terminal_backend` artifact.
Example paths: `environments/p09_hp_modal.yaml`, `environments/p09_hp_daytona.yaml`.

### 2. Compile
```bash
python _tools/cex_compile.py environments/p09_hp_BACKEND.yaml
# Or: python _tools/cex_compile.py --all
```
Replace `BACKEND` with the actual backend slug (modal, daytona, singularity, generic).

### 3. Validate
```bash
python _tools/cex_doctor.py
python -m json.tool .cex/kinds_meta.json > /dev/null
echo "JSON valid"
```

### 4. Commit
```bash
git add environments/p09_hp_BACKEND.yaml
git commit -m "[N05] hibernation_policy: p09_hp_BACKEND (TARGET_BACKEND idle guard)"
```

### 5. Signal
```python
from _tools.signal_writer import write_signal
write_signal('n05', 'complete', 9.0, mission='hibernation_policy_BACKEND')
```

## Downstream Consumers

| Consumer | How they use hibernation_policy |
|----------|--------------------------------|
| N07 Orchestrator | Reads wake_latency_sla_seconds to route latency-sensitive tasks to warm instances |
| N05 Operations | Deploys the policy to the backend API at environment setup |
| terminal_backend artifact | Sibling -- references same backend slug |
| cost_budget artifact | Complements -- budget caps total spend; hibernation reduces idle spend |

## Handoff to N07 (on build complete)
When a new hibernation_policy artifact is created, N07 should:
1. Verify the sibling terminal_backend artifact exists (same backend slug)
2. Update the cost model in the backend config to reflect the new savings estimate
3. Route latency-sensitive tasks away from backends with high wake_latency_sla_seconds

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[bld_tools_terminal_backend]] | upstream | 0.36 |
| [[bld_architecture_hibernation_policy]] | upstream | 0.35 |
| [[bld_architecture_terminal_backend]] | upstream | 0.29 |
| [[n00_hibernation_policy_manifest]] | upstream | 0.29 |
| [[n00_terminal_backend_manifest]] | upstream | 0.28 |
