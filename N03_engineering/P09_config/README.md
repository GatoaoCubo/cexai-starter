# N03 Engineering / P09 Config

Environment config, feature flags, and runtime settings this nucleus reads at boot.

## Example kinds (in P09, this checkout)
- `effort_profile` -- Effort and thinking level configuration for builder execution
- `batch_config` -- Async batch processing config for bulk API operations (OpenAI Batch, Anthropic Batches)
- `canary_config` -- Gradual traffic rollout configuration for safe deployment with automatic rollback triggers

## Schema
See [N00_genesis/P09_config/_schema.yaml](../../N00_genesis/P09_config/_schema.yaml) for this pillar's field contract.

---
This pillar is empty by design -- it fills the first time one of your builds writes here. See [HOME -> Anatomy](../../HOME.md#anatomy-why-nuclei-look-incomplete).
