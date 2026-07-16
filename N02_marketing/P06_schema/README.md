# N02 Marketing / P06 Schema

Type definitions, validation schemas, and contracts this nucleus's artifacts must satisfy.

## Example kinds (in P06, this checkout)
- `canonical_product` -- Channel-neutral product golden record: union of all channel fields (identity codes + numeric specs + typed...
- `design_system` -- Selectable brand design system: concrete color/type/space/motion/form tokens + four component recipes + usa...
- `aggregate_root` -- DDD entry point entity that enforces domain invariants and controls access to its aggregate cluster

## Schema
See [N00_genesis/P06_schema/_schema.yaml](../../N00_genesis/P06_schema/_schema.yaml) for this pillar's field contract.

---
This pillar is empty by design -- it fills the first time one of your builds writes here. See [HOME -> Anatomy](../../HOME.md#anatomy-why-nuclei-look-incomplete).
