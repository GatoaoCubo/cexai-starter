---
id: bld_architecture_canonical_product
kind: component_map
pillar: P08
llm_function: CONSTRAIN
version: 1.0.0
quality: null
tags: [canonical_product, architecture, golden-record]
title: "Architecture Canonical Product"
author: builder
tldr: "Canonical Product architecture: component map, pipeline position, and structural constraints"
8f: "F4_reason"
keywords: [architecture canonical product, component map, structural constraints, canonical_product, golden record, pipeline, kind taxonomy]
density_score: 0.95
created: "2026-07-03"
updated: "2026-07-03"
related:
  - kc_canonical_product
  - canonical-product-builder
  - bld_memory_canonical_product
  - marketplace-listing-builder
---
# Architecture: canonical_product
## Position in CEX Kind Taxonomy
```
P06 Schema
  canonical_product   <-- THIS KIND (channel-neutral golden record)
  data_contract         (generic cross-team schema+SLA, not product-specific) -- depends_on
  validation_schema      (generic post-gen LLM output check, not product-specific) -- depends_on
  input_schema           (single-system input spec)
```

## Relationships
| Relation | Kind | Direction | Notes |
|----------|------|-----------|-------|
| bridges | (upstream) `cex_catalog_merge.py` golden record | one-to-one per SKU | N04 multi-source merge engine, not reimplemented |
| depends_on | `data_contract` | prerequisite | P06, schema+SLA boundary concept |
| depends_on | `validation_schema` | prerequisite | P06, post-generation output check concept |
| feeds | `marketplace_listing` | downstream, one-to-many | via `cex_channel_adapter.ChannelAdapter.map()+.validate()` (P05) |
| feeds | grounded ad copy / `product_ad` | downstream | via `cex_grounded_copy.py` / `cex_content_factory.py` (capability layer, unregistered kind) |
| structural closure | `marketplace_listing` | reverse pull | `marketplace_listing.depends_on` names `canonical_product`; `cex_distill.py` `kind_closure` pulls it into EVERY `vertical==retail`/`has_store` tenant distillation |

## The Pipeline (Composition Pattern)
```
RAW tenant data (per-channel exports/imports)
  | cex_product_catalog_adapter.normalize_product()
  v
per-source normalized record  (docs/schema/product_catalog_schema.yaml shape)
  | cex_catalog_merge.merge_records()   [precedence + conflict + provenance]
  v
golden record  (_merge_provenance + _conflicts, source vocabulary)
  | cex_canonical_product.canonical_from_merged()   <-- THIS KIND
  v
canonical_product   (42 fields, structural law enforced)
  |-- cex_channel_adapter.ChannelAdapter.map()+.validate() --> marketplace_listing
  |-- cex_grounded_copy.extract_copy() / cex_content_factory       --> grounded ad copy
```
`cex_ads_dryrun.py` is the offline demo/self-test harness for the merge+bridge (P1+P2).

## When to Use
| Scenario | Use |
|----------|-----|
| Channel-neutral union with provenance + conflicts | `canonical_product` |
| What ONE channel will actually receive (mapped + readiness-checked) | `marketplace_listing` |
| The rendered buyer-facing page | `product_ad` (capability layer, not a P0-P12 kind) |
| Generic cross-team schema + SLA, not product-specific | `data_contract` |
| Generic post-generation LLM output check, not product-specific | `validation_schema` |

## Schema Contract Binding
`docs/schema/contracts/canonical_product.schema.json` (JSON Schema draft-07,
26 required keys of 42 total fields) is the machine-checkable mirror of
`validate_against_schema()` -- both must be read together; the Python function
additionally enforces the structural law, which JSON Schema cannot express alone.

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[kc_canonical_product]] | upstream | 0.50 |
| [[canonical-product-builder]] | upstream | 0.45 |
| [[bld_memory_canonical_product]] | downstream | 0.39 |
| [[marketplace-listing-builder]] | downstream | 0.34 |
