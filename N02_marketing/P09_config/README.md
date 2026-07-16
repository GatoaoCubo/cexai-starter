# N02 Marketing / P09 Config

Environment config, feature flags, and runtime settings this nucleus reads at boot.

## Example kinds (in P09, this checkout)
- `prosody_config` -- Voice personality and emotion settings
- `backpressure_policy` -- Policy defining how a system responds when downstream consumers cannot keep up with upstream producers
- `quantization_config` -- Model quantization and compression settings

## Schema
See [N00_genesis/P09_config/_schema.yaml](../../N00_genesis/P09_config/_schema.yaml) for this pillar's field contract.

---
This pillar is empty by design -- it fills the first time one of your builds writes here. See [HOME -> Anatomy](../../HOME.md#anatomy-why-nuclei-look-incomplete).
