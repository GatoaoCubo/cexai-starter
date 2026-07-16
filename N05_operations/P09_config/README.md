# N05 Operations / P09 Config

Environment config, feature flags, and runtime settings this nucleus reads at boot.

## Example kinds (in P09, this checkout)
- `deployment_manifest` -- Specification of what artifacts to deploy, where to deploy them, and how to configure the deployment
- `alert_rule` -- Observable threshold condition that triggers a notification or automated response
- `canary_config` -- Gradual traffic rollout configuration for safe deployment with automatic rollback triggers

## Schema
See [N00_genesis/P09_config/_schema.yaml](../../N00_genesis/P09_config/_schema.yaml) for this pillar's field contract.

---
This pillar is empty by design -- it fills the first time one of your builds writes here. See [HOME -> Anatomy](../../HOME.md#anatomy-why-nuclei-look-incomplete).
