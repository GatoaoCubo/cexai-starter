# N06 Commercial / P09 Config

Environment config, feature flags, and runtime settings this nucleus reads at boot.

## Example kinds (in P09, this checkout)
- `marketplace_app_manifest` -- Marketplace app manifest spec for Claude/LangChain/HuggingFace listings (metadata, perms, pricing)
- `playground_config` -- Playground/sandbox config for interactive product evaluation
- `alert_rule` -- Observable threshold condition that triggers a notification or automated response

## Schema
See [N00_genesis/P09_config/_schema.yaml](../../N00_genesis/P09_config/_schema.yaml) for this pillar's field contract.

---
This pillar is empty by design -- it fills the first time one of your builds writes here. See [HOME -> Anatomy](../../HOME.md#anatomy-why-nuclei-look-incomplete).
