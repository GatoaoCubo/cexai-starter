# N07 Admin / P09 Config

Environment config, feature flags, and runtime settings this nucleus reads at boot.

## Example kinds (in P09, this checkout)
- `kubernetes_ai_requirement` -- CNCF Kubernetes AI Requirement (KAR) conformance artifact: GPU topology, InfiniBand, MIG, DRA, checkpoint P...
- `permission` -- Permission rule (read/write/execute)
- `rbac_policy` -- Role-based access control policy for multi-tenant isolation

## Schema
See [N00_genesis/P09_config/_schema.yaml](../../N00_genesis/P09_config/_schema.yaml) for this pillar's field contract.

---
This pillar is empty by design -- it fills the first time one of your builds writes here. See [HOME -> Anatomy](../../HOME.md#anatomy-why-nuclei-look-incomplete).
