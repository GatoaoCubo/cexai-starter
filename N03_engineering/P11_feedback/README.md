# N03 Engineering / P11 Feedback

Quality gates, guardrails, and the revision loops that govern this nucleus's retries.

## Example kinds (in P11, this checkout)
- `guardrail` -- Safety restriction (safety boundary)
- `lifecycle_rule` -- Lifecycle rule (freshness, archive, promote)
- `quality_gate` -- Quality barrier (pass/fail with score)

## Schema
See [N00_genesis/P11_feedback/_schema.yaml](../../N00_genesis/P11_feedback/_schema.yaml) for this pillar's field contract.

---
This pillar is empty by design -- it fills the first time one of your builds writes here. See [HOME -> Anatomy](../../HOME.md#anatomy-why-nuclei-look-incomplete).
