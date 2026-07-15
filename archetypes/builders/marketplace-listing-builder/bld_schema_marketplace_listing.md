---
id: bld_schema_marketplace_listing
kind: schema
pillar: P06
llm_function: CONSTRAIN
8f: F1_constrain
version: 1.0.0
created: "2026-07-02"
updated: "2026-07-02"
author: n03_builder
title: "Schema: marketplace_listing"
domain: marketplace_listing
quality: null
tags: [marketplace_listing, builder, schema, channel-projection, P06]
tldr: "Single source of truth for a marketplace_listing: frontmatter + the 6 FROZEN sections + the embedded ml_listing payload + the readiness gate fields, mirrored 1:1 from the shipped capability generator."
density_score: 0.92
related:
  - marketplace-listing-builder
  - bld_output_marketplace_listing
  - bld_eval_marketplace_listing
  - bld_prompt_marketplace_listing
  - output-validator-builder
---

# Schema: marketplace_listing
Derivation hierarchy: **SCHEMA (this) > TEMPLATE (bld_output) > CONFIG (bld_config)**.
Grounded in the SHIPPED generator `_tools/capability_generators/marketplace_listing.py`
(registered capability slug `marketplace_listing`) + its frontend mirror
`apps/dashboard_web/lib/molds.ts` (`MOLD_MARKETPLACE_LISTING`). `.cex/kinds_meta.json`
supplies naming/max_bytes/pillar; its declared `upstream_source` is a lower-level,
differently-shaped seam (`_tools/cex_channel_adapter.py`) -- see
[[bld_architecture_marketplace_listing]] for the vocabulary reconciliation.

## Frontmatter Fields (required)
| Field | Type | Notes |
|-------|------|-------|
| id | string `p05_ml_{name}` | equals filename stem |
| kind | literal `marketplace_listing` | type integrity |
| pillar | literal `P05` | pillar assignment |
| title | string | "Name -- one-line description" |
| version | semver | start 1.0.0 |
| marketplace | enum, default `mercado_livre` | only channel wired in `CHANNEL_ADAPTERS` today |
| sku | string | the G1 seller SKU this listing projects |
| quality | null | never self-score (CEX meta-quality -- distinct from the readiness `score` below) |
| tags | list >=3 | includes `marketplace-listing` |

## Readiness gate fields (frontmatter -- mirrors the generator's own StructuredOutput)
| Field | Type | Notes |
|-------|------|-------|
| score | float 0.0-1.0 | starts 1.0, deducted per missing/weak field, floored at 0.0 |
| passed | bool | zero missing_required AND score >= 0.70 |
| missing_required | list | subset of `titulo_ml->title`, `categoria_ml->category_id`, `preco->price` only |
| notes | list[str] | `[FAIL]`/`[WARN]`-prefixed; never silently dropped |
| real | bool | always `true` for a builder-authored instance (never the mock/simulated chip) |

## Six FROZEN sections (all mandatory, exact titles + layout + order)
| # | Title | Layout | Rows/Columns |
|---|-------|--------|--------------|
| 1 | Listagem ML | fields | Titulo, Marketplace, Categoria ID, Condicao ML, Tipo de anuncio, Moeda |
| 2 | Preco e Estoque | fields | Preco (R$), Estoque, SKU do vendedor, Marca |
| 3 | Fotos | list | one item per photo URL (or the honest empty-state string) |
| 4 | Atributos | table | columns [Atributo (id), Valor] |
| 5 | Descricao | fields | Descricao completa |
| 6 | Payload ML (pronto para publicar) | fields | Produto interno, Fotos mapeadas, Atributos mapeados, JSON do anuncio |

## Embedded `ml_listing` payload (mirrors the ML Items API body)
`title, category_id, price, currency_id (always BRL), available_quantity, condition
(new|used|refurbished), listing_type_id, description.plain_text, pictures[].url,
attributes[]{id,value_name} (BRAND + SELLER_SKU auto-injected when absent),
seller_custom_field`. Serialized (ASCII, truncated at 900 chars + `...`) into section 6's
`JSON do anuncio` field; the same 4-6 of those fields are ALSO restated human-readably in
sections 1-2 -- keep both representations consistent. No `_meta` block (that belongs to
the OTHER seam -- see [[bld_architecture_marketplace_listing]]).

## Constraints
- max_bytes: 6144 (body); naming `p05_ml_{name}.md` (`.cex/kinds_meta.json`); machine_format md.
- id == filename stem; quality: null always; clean-room (no fabricated URL/price/attribute).
- Title <=60 chars preferred (soft warn only, ML_TITLE_MAX); currency_id always BRL.

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[marketplace-listing-builder]] | sibling | 0.5 |
| [[bld_output_marketplace_listing]] | downstream | 0.5 |
| [[bld_eval_marketplace_listing]] | downstream | 0.48 |
| [[bld_prompt_marketplace_listing]] | downstream | 0.45 |
| [[output-validator-builder]] | related | 0.38 |
