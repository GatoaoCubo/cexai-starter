---
id: p04_skill_n07
kind: skill
pillar: P04
title: "Skill Registry: N07 Orchestration"
version: "1.0.0"
quality: null
tags: [orchestration, skill, dispatch, monitor, consolidate]
8f: F5_call
nucleus: n07
created: "2026-07-20"
tldr: "N07 orchestration skills: dispatch, monitor, consolidate, wave-plan, GDP-collect, intent-resolve."
related:
  - p12_wf_admin_orchestration
  - p01_kc_orchestration
  - dispatch
  - agent_card_n07
---

# Skill Registry: N07 Orchestration

## Rationale

N07's skills are orchestration primitives: dispatch, monitor, consolidate. Where
a builder nucleus's skills produce artifacts directly, N07's skills coordinate
other nuclei without touching artifacts themselves.

## Registry

| Skill | Trigger | Input | Output | Tool Chain |
|-------|---------|-------|--------|------------|
| dispatch | `/dispatch`, `/grid`, `/mission` | intent + nucleus | handoff file + PID | dispatch.sh + signal_writer |
| monitor | wave active | PID file | status report | dispatch.sh status + git log |
| consolidate | wave complete | signal files | consolidation report | cex_doctor.py + taskkill |
| wave_plan | `/plan`, `/mission` | user goal | plan.md with waves | mission planner |
| gdp_collect | `/guide`, subjective task | decision points | decision_manifest.yaml | GDP protocol |
| intent_resolve | any user input | natural language | `{kind, pillar, nucleus, verb}` | cex_intent_resolver.py |

## Skill: dispatch

```yaml
name: dispatch
trigger: "/dispatch <nucleus> <task>"
steps:
  1. Resolve intent via the prompt compiler
  2. Write handoff to .cex/runtime/handoffs/
  3. Copy to {{nucleus}}_task.md
  4. Run: bash _spawn/dispatch.sh solo {{nucleus}}
  5. Record PID to spawn_pids.txt
output: "Dispatched {{NUCLEUS}}. PID: {{pid}}. Monitor: dispatch.sh status"
```

## Skill: monitor

```yaml
name: monitor
trigger: wave_active (automatic)
steps:
  1. Check: git log --oneline --since="3 minutes ago"
  2. Check: bash _spawn/dispatch.sh status
  3. Check: ls .cex/runtime/signals/signal_*
  4. Report: "{{completed}}/{{total}} nuclei signaled"
interval: 60-90 seconds
```

## Skill: consolidate

```yaml
name: consolidate
trigger: all_wave_nuclei_signaled
steps:
  1. Verify: all deliverables exist on disk
  2. Run: python _tools/cex_doctor.py
  3. Stop: bash _spawn/dispatch.sh stop
  4. Commit: git add + commit (scoped to this wave's paths)
  5. Archive: move signals to .cex/runtime/archive/
  6. Report: consolidation summary
output: "{{wave}} consolidated. {{files}} files, {{quality}} avg quality."
```

## DO NOT

- Build artifacts (dispatch to the builder nucleus)
- Run tests (dispatch to the operations nucleus)
- Write copy (dispatch to the marketing nucleus)
- Research topics (dispatch to the research nucleus)
- Self-score dispatched work (quality is peer-reviewed, never self-assigned)

## Related Artifacts

| Artifact | Relationship |
|----------|---------------|
| [[p12_wf_admin_orchestration]] | downstream -- the workflow the `dispatch` skill executes |
| [[p01_kc_orchestration]] | upstream -- multi-CLI dispatch knowledge this registry applies |
| [[dispatch]] | related -- the /dispatch command surface |
| [[agent_card_n07]] | sibling -- N07's capability declaration, same nucleus |
