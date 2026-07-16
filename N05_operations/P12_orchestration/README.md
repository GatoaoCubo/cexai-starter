# N05 Operations / P12 Orchestration

Workflows, crews, and the handoff protocols this nucleus uses to coordinate work.

## Example kinds (in P12, this checkout)
- `spawn_config` -- Spawn configuration (solo, grid, continuous)
- `team_charter` -- Mission contract for a specific crew instance. Bridges GDP decisions (WHAT) to autonomous crew execution (H...
- `fabrication_manifest` -- Per-tenant fabrication recipe: {tenant_id, brand_config_ref, chosen_capabilities[], targets{brain,site,admi...

## Schema
See [N00_genesis/P12_orchestration/_schema.yaml](../../N00_genesis/P12_orchestration/_schema.yaml) for this pillar's field contract.

---
This pillar is empty by design -- it fills the first time one of your builds writes here. See [HOME -> Anatomy](../../HOME.md#anatomy-why-nuclei-look-incomplete).
