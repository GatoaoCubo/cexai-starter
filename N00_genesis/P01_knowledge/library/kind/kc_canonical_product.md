---
id: kc_canonical_product
kind: knowledge_card
8f: F3_inject
type: kind
pillar: P06
title: "Canonical Product -- Deep Knowledge for canonical_product"
version: 1.0.0
created: 2026-07-02
updated: 2026-07-02
author: builder_agent
domain: canonical_product
quality: null
tags: [canonical_product, P06, CONSTRAIN, kind-kc, golden-record, catalog, provenance, ecommerce]
tldr: "Channel-neutral product golden record: the union of every channel's fields + per-field provenance + conflict flags. NOT marketplace_listing (a per-channel projection) nor product_ad (the rendered buyer page). One SKU = one record."
when_to_use: "Before any channel projection or grounded ad-copy generation -- merge N per-source normalized product records into one typed, provenance-tracked golden record"
keywords: [golden-record, canonical-product, provenance, conflict-flags, channel-neutral, structural-law, catalog-merge]
feeds_kinds: [canonical_product]
density_score: null
aliases: ["golden record", "CanonicalProduct", "product golden record", "channel-neutral product"]
user_says: ["merge my product data from multiple sources", "single source of truth for my catalog", "golden record for products"]
long_tails: ["merge product data from several sources into one record with conflicts flagged", "keep product specs separate from marketing prose in the catalog"]
related:
  - data-contract-builder
  - validation-schema-builder
---

# Canonical Product

## Spec
```yaml
kind: canonical_product
pillar: P06
llm_function: CONSTRAIN
primary_8f: F1_constrain
max_bytes: 6144
naming: p06_cp_{{name}}.md
core: false
status: stable
depends_on: [data_contract, validation_schema]
requires_external_context: false
requires_live_tools: false
```
Source: `.cex/kinds_meta.json` entry `canonical_product`.

## What It Is
The channel-neutral product golden record: the UNION of every channel's fields,
with per-field provenance and cross-source conflict flags carried through. One
SKU = one record (`.cex/kinds_meta.json`). Produced by bridging the multi-source
merge engine (`_tools/cex_catalog_merge.py`) into a fully-typed superset shape
(`_tools/cex_canonical_product.py:canonical_from_merged()`), checked against
`docs/schema/contracts/canonical_product.schema.json`. NOT a catalog store, NOT
a per-channel payload -- the single upstream source every channel adapter and
grounded-copy generator reads from.

**THE STRUCTURAL LAW (Article II).** The typed structured set (`key_features`,
`benefits_functional`, `benefits_emotional`, `attributes`, `colors`,
`materials`, `audience_tags`) is stored SEPARATE from the prose set
(`description`, `long_description`, `why_it_works`). Only a `ChannelAdapter`
may concatenate them, each into that channel's own slot --
`validate_against_schema()` FAILs a record that buries a structured value
verbatim inside prose.

## Field Groups (42 typed fields + 2 meta-trails)
Source: `CANONICAL_FIELDS` tuple, `_tools/cex_canonical_product.py`.

| Group | n | Fields |
|---|---|---|
| core identity | 11 | id, sku, slug, title, subtitle, brand, model, mpn, gtin, gtin_absent_reason, condition |
| classification | 3 | gpc_brick, google_product_category, category_ref |
| prose (separate payload) | 3 | description, long_description, why_it_works |
| structured (never in prose) | 7 | key_features, benefits_functional, benefits_emotional, attributes, colors, materials, audience_tags |
| specs (numeric, drives shipping) | 4 | dim_length_cm, dim_width_cm, dim_height_cm, weight_grams |
| commerce | 3 | price, available_quantity, currency |
| media | 3 | images, image_alt, video_url |
| logistics / warranty | 3 | warranty, shipping_info, free_shipping |
| checkout binding (buyability gate) | 1 | checkout_binding |
| per-channel link state | 4 | meli_item_id, mercadolivre_link, shopify_variant_id, shopify_product_id |
| meta-trails (outside CANONICAL_FIELDS) | 2 | _provenance, _conflicts |

`required` (26 keys, JSON Schema) means "present", not "non-null" -- `id`,
`sku`, `title`, etc. are still typed `["string","null"]`.

## Invariants (`_tools/cex_canonical_product.py` header)
**never-fabricate** -- a field absent in every source becomes `None`/`[]`/`{}`, never invented.
**degrade-never** -- empty/partial input yields an honest empty canonical, never a crash.
**provenance** -- per-field origin tag carried from `_merge_provenance` (see `provenance_coverage()`).
**conflict trail** -- cross-source disagreements carried from `_conflicts`, never silently resolved.

## Boundary (vs Adjacent Kinds)
| Kind | Pillar | What it is | Relationship |
|---|---|---|---|
| **canonical_product** | P06 | THIS kind -- channel-neutral golden record | -- |
| `marketplace_listing` | P05 | Per-channel PROJECTION: `ChannelAdapter.map()` output + readiness report | downstream; `depends_on: [canonical_product, output_validator]` |
| `product_ad` | unregistered | Rendered buyer page built from a canonical_product via grounded copy | downstream; dashboard capability layer (`cex_run_capability.py`), not in `kinds_meta.json` |
| `data_contract` | P06 | Generic cross-team schema + SLA, not product-specific | canonical_product `depends_on` this |
| `validation_schema` | P06 | Generic post-generation output check, not product-specific | canonical_product `depends_on` this |

## The Pipeline (Composition Pattern)
```
RAW tenant data (per-channel exports / imports)
  | cex_product_catalog_adapter.normalize_product()
  v
per-source normalized record   (docs/schema/product_catalog_schema.yaml shape)
  | cex_catalog_merge.merge_records()   [precedence + conflict + provenance]
  v
golden record   (_merge_provenance + _conflicts, source vocabulary)
  | cex_canonical_product.canonical_from_merged()   <- THIS KIND
  v
canonical_product   (42 fields, structural law enforced)
  |-- cex_channel_adapter.ChannelAdapter.map()+.validate() --> marketplace_listing
  |-- cex_grounded_copy.extract_copy() / cex_content_factory --> grounded ad copy
```
`cex_ads_dryrun.py` is the offline demo/self-test harness for the P1+P2 bridge.
`cex_grounded_copy.py` treats a canonical_product as "the fact ground-truth" --
voice shapes the sentence, never the facts.

## Decision Tree
- IF channel-neutral union of every source, with provenance + conflicts -> `canonical_product`
- IF what ONE channel will actually receive (mapped + readiness-checked) -> `marketplace_listing`
- IF the rendered buyer-facing page/HTML -> `product_ad` (capability layer, not a P0-P12 kind)
- IF a generic cross-team schema + SLA, not tied to a product -> `data_contract`
- IF a generic post-generation LLM output check, not tied to a product -> `validation_schema`
- DEFAULT: never skip canonical_product -- reading raw per-source data straight into an adapter or copy generator loses the provenance/conflict trail that gates honesty.

## Anti-Patterns
| Anti-Pattern | Fix |
|---|---|
| Burying `key_features`/`benefits_*` inside prose fields | Structural law: keep separate; only a `ChannelAdapter` concatenates, into its own slot |
| Treating a `marketplace_listing` or raw per-source row as canonical | Always derive from the merged golden record via `canonical_from_merged()` |
| Inventing a value for a field absent in every source | Leave it `None` / `[]` / `{}` (never-fabricate) |
| Silently averaging a cross-source conflict (e.g. weight 900g vs 450g) | Flag it in `_conflicts`; a human resolves it |
| Re-implementing the merge/bridge in another language for a new surface | Bridge `cex_catalog_merge.py` instead (Reuse Over Reinvention) |

## Quality Criteria
- GOOD: all 42 `CANONICAL_FIELDS` keys present (null allowed), `condition` in `{new, used, refurbished}`, no structured value duplicated verbatim (>=12 chars) in prose
- GREAT: + `provenance_coverage()` near 1.0, + every disagreement preserved in `_conflicts`, + `field_union_coverage()` tracked as completeness
- FAIL: missing a `CANONICAL_FIELDS` key, invalid `condition`, a structural-law violation from `validate_against_schema()`, or a populated field absent from `_provenance`

## Grounding Notes (honesty flags)
Builder ISOs now exist (`archetypes/builders/canonical-product-builder/`, 12
ISOs, scaffolded 2026-07-03 per `docs/DECISION_BUILDERLESS_KINDS_2026_07_03.md`
Sec 2.2/4.1, template-first derived from `data-contract-builder`); no
`p06_cp_*.md` **instances** exist yet -- the kind's real usage today is still
the Python bridge + JSON Schema + tests, with the builder now closing the
dispatch-to-dead-F2-BECOME gap. `kinds_meta.json`'s
`spec_version: docs/specs/01_ads_catalog` does not exist in this repo (only
`04_bootstrap_orchestrator`..`10_multitenant_100` + `compiled` do) -- likely
tenant-side. Source files say "the reference commerce app", never a tenant
name; this card keeps that convention since N00_genesis is the archetype
every sovereign tenant distills from.

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[kc_data_contract]] | upstream (depends_on) | 0.55 |
| [[kc_validation_schema]] | upstream (depends_on) | 0.52 |
| [[data-contract-builder]] | sibling | 0.40 |
| [[validation-schema-builder]] | sibling | 0.38 |
| kc_value_object | related (P06 typed-record sibling) | 0.32 |
