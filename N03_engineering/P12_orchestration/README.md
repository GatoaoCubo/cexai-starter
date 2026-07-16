# N03 Engineering / P12 Orchestration

Workflows, crews, and the handoff protocols this nucleus uses to coordinate work.

## Example kinds (in P12, this checkout)
- `checkpoint` -- Workflow state snapshot
- `dispatch_rule` -- Dispatch rule (keyword > agent_group)
- `workflow` -- Workflow (sequential/parallel steps)

## Schema
See [N00_genesis/P12_orchestration/_schema.yaml](../../N00_genesis/P12_orchestration/_schema.yaml) for this pillar's field contract.

---
This pillar is empty by design -- it fills the first time one of your builds writes here. See [HOME -> Anatomy](../../HOME.md#anatomy-why-nuclei-look-incomplete).
