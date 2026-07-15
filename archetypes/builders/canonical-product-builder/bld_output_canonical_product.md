---
id: bld_output_canonical_product
kind: output_template
pillar: P05
llm_function: PRODUCE
version: 1.0.0
quality: null
tags: [canonical_product, template, output]
title: "Output Template: canonical_product"
author: builder
tldr: "Canonical Product prompt: output template, formatting rules, and structure"
8f: "F6_produce"
keywords: [output template, canonical product prompt, formatting rules, and structure, canonical_product, template, output, golden record, provenance, structural law]
density_score: 0.95
created: "2026-07-03"
updated: "2026-07-03"
related:
  - bld_schema_canonical_product
  - bld_instruction_canonical_product
  - kc_canonical_product
  - canonical-product-builder
  - bld_qg_canonical_product
---
# Output Template: canonical_product
```markdown
---
id: cp_{{sku_snake}}
kind: canonical_product
pillar: P06
title: "{{Title}} -- Canonical Product ({{SKU}})"
version: 1.0.0
quality: null
sku: {{SKU}}
condition: {{new|used|refurbished}}
depends_on: [data_contract, validation_schema]
tags: [{{brand}}, canonical-product, golden-record]
---

# {{Title}} -- Canonical Product

## Core Identity
| Field | Value |
|-------|-------|
| id / sku / slug | {{id}} / {{sku}} / {{slug}} |
| title / subtitle | {{title}} / {{subtitle}} |
| brand / model / mpn | {{brand}} / {{model}} / {{mpn}} |
| gtin | {{gtin or null; gtin_absent_reason if null}} |
| condition | {{new\|used\|refurbished}} |

## Classification
gpc_brick: {{gpc_brick}} | google_product_category: {{google_product_category}}
category_ref: {{ per-channel category id map }}

## Prose (separate payload -- NEVER contains structured values)
description: {{short prose}}
long_description: {{long prose}}
why_it_works: {{prose}}

## Structured Attributes (typed, NEVER in prose)
key_features: {{list}} | benefits_functional: {{list}} | benefits_emotional: {{list}}
attributes: {{ key-value bag }} | colors: {{list}} | materials: {{list}} | audience_tags: {{list}}

## Specs
dim_length_cm / dim_width_cm / dim_height_cm: {{L}} / {{W}} / {{H}}
weight_grams: {{grams}}

## Commerce
price: {{price}} | available_quantity: {{qty}} | currency: {{ISO-4217, default BRL}}

## Media
images: {{gallery urls, first = cover}} | image_alt: {{list}} | video_url: {{url or null}}

## Logistics / Checkout
warranty: {{text}} | shipping_info: {{text}} | free_shipping: {{true/false/null}}
checkout_binding: {{buyability key, e.g. shopify_variant_id}}

## Link State (per-channel bookkeeping)
meli_item_id / mercadolivre_link / shopify_variant_id / shopify_product_id

## Provenance & Conflicts (carried from the merge, never invented)
_provenance: {{ per-field origin: winner_source + present_sources }}
_conflicts: {{ per-field cross-source disagreement, surfaced for human review }}
```

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[bld_schema_canonical_product]] | downstream | 0.39 |
| [[bld_prompt_canonical_product]] | related | 0.37 |
| [[kc_canonical_product]] | upstream | 0.36 |
| [[canonical-product-builder]] | downstream | 0.35 |
| [[bld_qg_canonical_product]] | downstream | 0.30 |
