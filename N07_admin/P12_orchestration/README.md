# N07 Admin / P12 Orchestration

Workflows, crews, and the handoff protocols this nucleus uses to coordinate work.

## Ships with
- `dispatch_rule_n07.md` -- dispatch_rule
- `p12_ho_n07.md` -- handoff
- `schedule_n07.md` -- schedule
- `signal_admin.md` -- signal
- `workflow_admin.md` -- workflow

## Example kinds (in P12, this checkout)
- `dispatch_rule` -- Dispatch rule (keyword > agent_group)
- `handoff` -- Handoff instruction (task + context + commit)
- `schedule` -- Time-based trigger that starts a workflow

## Schema
See [N00_genesis/P12_orchestration/_schema.yaml](../../N00_genesis/P12_orchestration/_schema.yaml) for this pillar's field contract.

---
This pillar ships with the working exemplars above -- it fills further the first time your own `/build` writes here. See [HOME -> Anatomy](../../HOME.md#anatomy-each-nucleus-is-a-department).
