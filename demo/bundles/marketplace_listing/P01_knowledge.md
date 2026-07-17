---
id: bld_knowledge_marketplace_listing
kind: knowledge_card
pillar: P01
llm_function: INJECT
8f: F3_inject
version: 1.0.0
created: "2026-07-02"
updated: "2026-07-02"
author: n03_builder
title: "Domain Knowledge: marketplace_listing"
domain: marketplace_listing
quality: null
tags: [marketplace_listing, builder, knowledge, mercado-livre, P01]
tldr: "Atomic facts for building marketplace_listing: the G1->G2 field mapping, condition vocabulary, BRAND/SELLER_SKU injection, ML title rule, media-slot wiring, and the two-implementation divergence."
density_score: 0.92
related:
  - bld_schema_marketplace_listing
  - bld_architecture_marketplace_listing
  - bld_memory_marketplace_listing
  - bld_config_marketplace_listing
  - output-validator-builder
---

# Domain Knowledge: marketplace_listing
## G1 -> G2 field mapping (from `capability_generators/marketplace_listing.py`)
| G1 field (dashboard) | G2 field (ML payload) | Notes |
|---|---|---|
| titulo_ml | title | <=60 chars preferred (ML_TITLE_MAX); no hard truncation by this builder |
| descricao | description.plain_text | listing body |
| categoria_ml | category_id | ML official category id, e.g. `MLB1055` |
| marca | BRAND attribute | injected into attributes[] only if not already present |
| condicao | condition | novo->new, usado->used, recondicionado->refurbished; unknown->new |
| preco | price | float, R$ |
| estoque | available_quantity | integer >= 0; NOT gate-checked in the shipped generator |
| fotos | pictures[].url | comma-sep string OR JSON array; NO https filter (see divergence below) |
| atributos | attributes[]{id,value_name} | JSON `{"key":"value"}` object |
| sku | seller_custom_field + SELLER_SKU attribute | injected into attributes[] only if not already present |

## ML title rule
Preferred max 60 chars (`ML_TITLE_MAX`). The shipped generator does NOT truncate -- it only
appends a `[WARN]` note and deducts 0.05 from score. (The lower-level
`cex_channel_adapter.py` seam DOES truncate at a word boundary via `clean_ml_title` -- a
different module, not what this builder mirrors.)

## Readiness gate (the score/passed/missing_required/notes contract)
Starts at 1.0; deducts 0.20 (titulo_ml missing), 0.05 (title >60 chars), 0.15 (categoria_ml
missing), 0.15 (preco<=0), 0.05 (descricao missing), 0.10 (no fotos), 0.05 (marca missing);
floors at 0.0. `passed` requires zero `missing_required` (only titulo_ml/categoria_ml/preco
populate that list) AND `score>=0.70`.

## Media-slot wiring (for the dual-output projection, not authored by this builder)
One image slot per foto URL (`foto_N`), or a single `foto_0` upload-fallback slot when no
fotos are given; a `video_demo` slot is ALWAYS declared and NEVER auto-produced
(never-fabricate). This is computed by `listing_media_requests`/`listing_produced_media` in
the same generator module, discovered by `_base.resolve_media` via the `listing_` prefix
convention.

## The two-implementation divergence (read before citing "the" contract)
Two modules compute a related-but-different shape for "ML listing": the SHIPPED
`capability_generators/marketplace_listing.py` (this builder's ground truth: score/passed/
missing_required/notes, no `_meta`, no https filter, no stock gate) and the lower-level
`cex_channel_adapter.py` `MercadoLivreAdapter` (`.cex/kinds_meta.json`'s declared
`upstream_source`: `_meta` block, `PUBLISH-READY`/`NOT-READY` + `missing[]`/`warnings[]`
each `{field,severity,message}`, https-only pictures, hard-blocks on zero stock via
`buyability()`). Never present one module's behavior as the other's.

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[bld_schema_marketplace_listing]] | downstream | 0.5 |
| [[bld_architecture_marketplace_listing]] | upstream | 0.45 |
| [[bld_memory_marketplace_listing]] | sibling | 0.4 |
| [[bld_config_marketplace_listing]] | related | 0.38 |
| [[output-validator-builder]] | related | 0.36 |
