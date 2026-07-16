# N04 Knowledge / P12 Orchestration

Workflows, crews, and the handoff protocols this nucleus uses to coordinate work.

## Example kinds (in P12, this checkout)
- `crew_template` -- CrewAI/AutoGen-style reusable crew blueprint (roles, process, memory, success)
- `pipeline_template` -- Scenario-indexed agent pipeline recipe (new-feature, bug-fix, refactor, perf, infra)
- `checkpoint` -- Workflow state snapshot

## Schema
See [N00_genesis/P12_orchestration/_schema.yaml](../../N00_genesis/P12_orchestration/_schema.yaml) for this pillar's field contract.

---
This pillar is empty by design -- it fills the first time one of your builds writes here. See [HOME -> Anatomy](../../HOME.md#anatomy-why-nuclei-look-incomplete).
