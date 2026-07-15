---
id: bld_kc_canonical_product
kind: knowledge_card
pillar: P01
llm_function: INJECT
version: 1.0.0
quality: null
tags: [canonical_product, golden-record, catalog-merge, knowledge]
title: "Knowledge: Canonical Product Pattern"
author: builder
tldr: "Canonical Product knowledge: golden-record domain knowledge, invariants, and contextual background"
8f: "F3_inject"
keywords: [canonical product pattern, golden record knowledge, domain knowledge, and contextual background, canonical_product, catalog-merge, knowledge, core facts, structural law]
density_score: 0.88
created: "2026-07-03"
updated: "2026-07-03"
related:
  - kc_canonical_product
  - bld_memory_canonical_product
  - canonical-product-builder
  - bld_context_sources_canonical_product
  - bld_architecture_canonical_product
---
# Domain Knowledge: canonical_product
## Core Facts
- Channel-neutral golden record: UNION of every channel's fields, one SKU = one record (`.cex/kinds_meta.json`)
- Bridges the proven `cex_catalog_merge.py` merge engine (precedence + conflict + provenance) into a typed 42-field superset -- Python bridge, TypeScript reference shape (Article VII: Reuse Over Reinvention, never fork the merge)
- THE STRUCTURAL LAW (Article II): the typed structured set is stored SEPARATE from the prose set; only a `ChannelAdapter` may concatenate them, each into its own slot
- 4 carried invariants: never-fabricate, degrade-never, provenance, conflict trail (never silently resolved)
- SC-001 metrics: `field_union_coverage()` (completeness) and `provenance_coverage()` (per-field origin coverage ratio)

## Industry Equivalents (general background)
| Pattern | Equivalent | Notes |
|---------|-----------|-------|
| MDM golden record | "best version of the record" | Master Data Management discipline (Loshin) |
| GS1 GDSN | Global Data Synchronisation Network | Multi-trading-partner product data pool |
| PIM/PXM systems | Product Information Management | Akeneo, Salsify, inRiver -- centralize then project per-channel |
| Schema-on-read merge | Precedence + conflict resolution | This repo's `cex_catalog_merge.py`, N04 |

## Field Groups (42 typed fields + 2 meta-trails)
Source: `CANONICAL_FIELDS` tuple, `_tools/cex_canonical_product.py`.
| Group | n | Example fields |
|---|---|---|
| core identity | 11 | id, sku, slug, title, brand, model, mpn, gtin, condition |
| classification | 3 | gpc_brick, google_product_category, category_ref |
| prose (separate payload) | 3 | description, long_description, why_it_works |
| structured (never in prose) | 7 | key_features, benefits_functional, benefits_emotional, attributes, colors, materials, audience_tags |
| specs (numeric) | 4 | dim_length_cm, dim_width_cm, dim_height_cm, weight_grams |
| commerce | 3 | price, available_quantity, currency |
| media | 3 | images, image_alt, video_url |
| logistics/warranty | 3 | warranty, shipping_info, free_shipping |
| checkout binding | 1 | checkout_binding (buyability gate, FR-012) |
| link state | 4 | meli_item_id, mercadolivre_link, shopify_variant_id, shopify_product_id |
| meta-trails | 2 | _provenance, _conflicts |

## Anti-Patterns
| Anti-Pattern | Fix |
|---|---|
| Burying `key_features`/`benefits_*` inside prose | Structural law: only a `ChannelAdapter` concatenates, into its own slot |
| Treating `marketplace_listing` or a raw per-source row as canonical | Always derive from the merged golden record via `canonical_from_merged()` |
| Inventing a value for a field absent in every source | Leave `None`/`[]`/`{}` (never-fabricate) |
| Silently averaging a cross-source conflict (e.g. weight 900g vs 450g) | Flag in `_conflicts`; a human resolves it |
| Re-implementing the merge in another language | Bridge `cex_catalog_merge.py` instead |

## Knowledge Injection Checklist
- Verify domain facts are sourced and citable (`_tools/cex_canonical_product.py`, the JSON Schema contract)
- Validate density_score >= 0.85
- Cross-reference `kc_canonical_product.md` for consistency
- Check for stale facts (e.g. the dangling `spec_version` -- see `bld_memory_canonical_product.md`)

## Injection Pattern
```yaml
source: verified
density: 0.85+
cross_refs: checked
freshness: current
```
```bash
python _tools/cex_compile.py {FILE}
python _tools/cex_retriever.py --query "channel-neutral product golden record"
```

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[kc_canonical_product]] | sibling | 0.44 |
| [[bld_memory_canonical_product]] | downstream | 0.33 |
| [[canonical-product-builder]] | downstream | 0.33 |
| [[bld_context_sources_canonical_product]] | downstream | 0.30 |
| [[bld_architecture_canonical_product]] | downstream | 0.29 |
