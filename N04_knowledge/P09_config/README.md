# N04 Knowledge / P09 Config

Environment config, feature flags, and runtime settings this nucleus reads at boot.

## Example kinds (in P09, this checkout)
- `tokenizer_config` -- BPE, sentencepiece, or tiktoken tokenizer parameters and vocabulary configuration
- `alert_rule` -- Observable threshold condition that triggers a notification or automated response
- `backpressure_policy` -- Policy defining how a system responds when downstream consumers cannot keep up with upstream producers

## Schema
See [N00_genesis/P09_config/_schema.yaml](../../N00_genesis/P09_config/_schema.yaml) for this pillar's field contract.

---
This pillar is empty by design -- it fills the first time one of your builds writes here. See [HOME -> Anatomy](../../HOME.md#anatomy-why-nuclei-look-incomplete).
