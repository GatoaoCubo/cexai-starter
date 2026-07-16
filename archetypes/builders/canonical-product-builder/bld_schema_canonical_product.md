---
id: bld_schema_canonical_product
kind: input_schema
pillar: P06
llm_function: CONSTRAIN
version: 1.0.0
quality: null
tags: [input_schema, P06, canonical_product]
title: "Schema Canonical Product"
author: builder
tldr: "Canonical Product schema: 42-field golden record, provenance, and structural-law validation rules"
8f: "F1_constrain"
keywords: [schema canonical product, canonical product schema, golden record, field types, and validation rules, input_schema, id pattern, frontmatter fields, body sections, structural law]
density_score: 0.88
created: "2026-07-03"
updated: "2026-07-03"
related:
  - bld_schema_data_contract
  - bld_schema_validation_schema
  - kc_canonical_product
  - bld_output_canonical_product
---
# Schema: canonical_product
## Frontmatter Fields (Required)
| Field | Type | Required | Notes |
|-------|------|----------|-------|
| id | string (`cp_{sku_snake}`) | YES | snake_case |
| kind | literal "canonical_product" | YES | -- |
| pillar | literal "P06" | YES | -- |
| title | string | YES | Human-readable record name |
| version | semver | YES | Artifact version |
| quality | null | YES | Never self-score |
| sku | string | YES | Stable stock-keeping unit |
| condition | enum {new, used, refurbished} | YES | Normalized via `_norm_condition()` |
| depends_on | list | YES | `[data_contract, validation_schema]` |
| tags | list[string] | YES | >= 3 tags |

## Body Sections (Required) -- the 42 CANONICAL_FIELDS in 10 groups
Source: `CANONICAL_FIELDS` tuple, `_tools/cex_canonical_product.py`.
| Group | n | Fields |
|---|---|---|
| core identity | 11 | id, sku, slug, title, subtitle, brand, model, mpn, gtin, gtin_absent_reason, condition |
| classification | 3 | gpc_brick, google_product_category, category_ref |
| prose (separate) | 3 | description, long_description, why_it_works |
| structured (never in prose) | 7 | key_features, benefits_functional, benefits_emotional, attributes, colors, materials, audience_tags |
| specs (numeric) | 4 | dim_length_cm, dim_width_cm, dim_height_cm, weight_grams |
| commerce | 3 | price, available_quantity, currency |
| media | 3 | images, image_alt, video_url |
| logistics/warranty | 3 | warranty, shipping_info, free_shipping |
| checkout binding | 1 | checkout_binding |
| link state | 4 | meli_item_id, mercadolivre_link, shopify_variant_id, shopify_product_id |
| meta-trails (outside CANONICAL_FIELDS) | 2 | _provenance, _conflicts |

`required` in the JSON Schema (26 keys) means "key present", NOT "non-null" --
`id`, `sku`, `title`, etc. remain typed `["string","null"]`.

## ID Pattern
`^cp_[a-z][a-z0-9_]+$`
Example: `cp_demo_sku001` (naming file: `p06_cp_demo_sku001.md`, per kinds_meta `naming: p06_cp_{{name}}.md`)

## Constraints
- max_bytes: 6144 (from `.cex/kinds_meta.json`, REAL value -- not the generic ISO limit)
- THE STRUCTURAL LAW: a structured field's value (>=12 chars) must never appear verbatim inside a prose field -- `validate_against_schema()` FAILs it
- `condition` must normalize to one of `{new, used, refurbished}` (`_norm_condition()`)
- List fields (`key_features`, `benefits_functional`, `benefits_emotional`, `colors`, `materials`, `audience_tags`, `images`, `image_alt`) must be arrays
- Object fields (`category_ref`, `attributes`) must be dicts
- `depends_on: [data_contract, validation_schema]` -- both are prerequisites, neither is this kind

## Schema Validation Checklist
- Verify all 42 fields have the correct type per `_LIST_FIELDS`/`_OBJECT_FIELDS`/`_NUMBER_FIELDS`
- Validate `condition` against the 3-value enum
- Cross-reference `_provenance`/`_conflicts` for consistency with the source merge
- Test with `python _tools/cex_canonical_product.py --self-test` before publishing

## Schema Pattern
```yaml
# Schema validation contract
types_annotated: true
structural_law_checked: true
provenance_carried: true
sample_data_tested: true
```
```bash
python _tools/cex_canonical_product.py --self-test
python _tools/cex_compile.py {FILE}
```

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[bld_schema_data_contract]] | related | 0.50 |
| [[bld_schema_validation_schema]] | related | 0.50 |
| [[kc_canonical_product]] | upstream | 0.48 |
| [[bld_output_canonical_product]] | sibling | 0.44 |
