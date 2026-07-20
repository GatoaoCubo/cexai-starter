# N01 Intelligence / P12 Orchestration

Workflows, crews, and the handoff protocols this nucleus uses to coordinate work.

## Ships with
- `p12_sc_research_n01.md` -- schedule
- `p12_wf_intelligence.md` -- workflow
- `crews/` -- research_sprint crew (sequential, 3 roles)

## Example kinds (in P12, this checkout)
- `schedule` -- Time-based trigger that starts a workflow
- `workflow` -- Workflow (sequential/parallel steps)
- `crew_template` -- CrewAI/AutoGen-style reusable crew blueprint (roles, process, memory, success)

## Schema
See [N00_genesis/P12_orchestration/_schema.yaml](../../N00_genesis/P12_orchestration/_schema.yaml) for this pillar's field contract.

---
This pillar ships with the working exemplars above -- it fills further the first time your own `/build` writes here. See [HOME -> Anatomy](../../HOME.md#anatomy-each-nucleus-is-a-department).
