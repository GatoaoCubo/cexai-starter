# N03 Engineering / P12 Orchestration

Workflows, crews, and the handoff protocols this nucleus uses to coordinate work.

## Ships with
- `dag_engineering.md` -- dag
- `workflow_engineering.md` -- workflow
- `crews/` -- build_review crew (sequential, 3 roles)
- `crews/` -- cross_provider_council crew (consensus, 4 roles)

## Example kinds (in P12, this checkout)
- `dag` -- Acyclic dependency graph
- `workflow` -- Workflow (sequential/parallel steps)
- `crew_template` -- CrewAI/AutoGen-style reusable crew blueprint (roles, process, memory, success)

## Schema
See [N00_genesis/P12_orchestration/_schema.yaml](../../N00_genesis/P12_orchestration/_schema.yaml) for this pillar's field contract.

---
This pillar ships with the working exemplars above -- it fills further the first time your own `/build` writes here. See [HOME -> Anatomy](../../HOME.md#anatomy-each-nucleus-is-a-department).
