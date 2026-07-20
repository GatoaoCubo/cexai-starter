---
id: kc_marketplace_listing
kind: knowledge_card
8f: F3_inject
type: kind
pillar: P01
title: "Marketplace Listing -- Deep Knowledge for marketplace_listing"
version: 1.0.0
created: 2026-07-20
updated: 2026-07-20
author: n03_builder
domain: marketplace_listing
quality: null
tags: [marketplace_listing, P05, PRODUCE, kind-kc, channel-projection, mercado-livre, ecommerce]
tldr: "Per-channel projection of a canonical_product into an ML-ready listing payload plus a 6-section readiness report; mirrors the shipped capability_generators/marketplace_listing.py 1:1."
when_to_use: "When projecting a canonical_product golden record into a channel-specific (Mercado Livre) publish-ready listing, or when auditing whether a listing is PUBLISH-READY."
keywords: [marketplace listing, channel projection, mercado livre, readiness gate, ml listing payload, publish ready, canonical product]
density_score: null
related:
  - marketplace-listing-builder
  - bld_schema_marketplace_listing
  - kc_canonical_product
  - p01_kc_output_validator
  - kc_opportunity_matrix
---

# Marketplace Listing

## Definition
A `marketplace_listing` is a per-channel PROJECTION of a `canonical_product` golden record into a channel-specific, publish-ready payload -- today the only wired channel is Mercado Livre (ML). It carries the mapped ML Items-API-shaped payload plus an embedded readiness verdict (score/passed/missing_required/notes). Registered `pillar: P05`, owning `nucleus: N06`, `llm_function: PRODUCE`, `primary_8f: F6_produce`, `depends_on: [canonical_product, output_validator]` (`.cex/kinds_meta.json`). `map`/`validate` are pure functions; the actual HTTP publish step is deferred and operator-gated in every layer of this pipeline.

## Boundaries
**What it is:** the outbound projection of one G1 catalog row (or one `canonical_product`) into one channel's listing shape, plus a scored readiness report.

**What it is NOT:**
- NOT `canonical_product` -- the channel-NEUTRAL superset this kind projects FROM (P06, upstream in `depends_on`).
- NOT `partner_listing` -- a directory/sales entry, not a channel-publish payload.
- NOT the live publish call -- publish stays deferred + operator-gated; this kind only maps and validates.

**Honest divergence (read before citing "the" contract):** two modules compute a related-but-different shape for "ML listing". This kind's builder mirrors the SHIPPED `_tools/capability_generators/marketplace_listing.py` (score/passed/missing_required/notes, no `_meta` block, no https-only filter, no stock gate). `.cex/kinds_meta.json`'s own declared `upstream_source` is a DIFFERENT, lower-level module, `cex_channel_adapter.py`'s `MercadoLivreAdapter` (`_meta` block, `PUBLISH-READY`/`NOT-READY` + `missing[]`/`warnings[]` each `{field,severity,message}`, https-only pictures, hard-blocks on zero stock via `buyability()`). Never present one module's behavior as the other's.

## Naming Convention
| Property | Value |
|---|---|
| Naming pattern | `p05_ml_{{name}}.md`; id equals filename stem |
| ID regex (bld_schema) | `p05_ml_{name}` pattern -- id MUST equal filename stem |
| max_bytes | 6144 (body) |
| marketplace enum | default `mercado_livre` -- the only channel wired in `CHANNEL_ADAPTERS` today |

## Key Fields
| Field | Type | Notes |
|---|---|---|
| score | float 0.0-1.0 | starts 1.0, deducted per missing/weak field, floors at 0.0 |
| passed | bool | zero `missing_required` AND `score >= 0.70` |
| missing_required | list | subset of `titulo_ml`, `categoria_ml`, `preco` only |
| notes | list[str] | `[FAIL]`/`[WARN]`-prefixed, never silently dropped |
| ml_listing.condition | enum | `novo`->`new`, `usado`->`used`, `recondicionado`->`refurbished`; unknown->`new` |

6 FROZEN body sections (exact order): Listagem ML (fields) -> Preco e Estoque (fields) -> Fotos (list) -> Atributos (table) -> Descricao (fields) -> Payload ML pronto para publicar (fields, embeds the serialized JSON, truncated at 900 chars).

## When to Use
- After a `canonical_product` exists and a channel target (Mercado Livre) is chosen -- project it into a publish-ready payload.
- When auditing why a listing is NOT-READY -- read `missing_required` and the `[FAIL]`/`[WARN]` notes rather than re-deriving the gate by hand.
- When feeding a passing `sourcing_confiavel` gate (see [[kc_opportunity_matrix]], its inbound twin) forward into a channel listing.

## Related Kinds
- [[kc_canonical_product]] -- the channel-neutral upstream source this kind projects from; never author a listing from raw per-source data directly.
- [[kc_opportunity_matrix]] -- the inbound (buy-side) twin; both meet at exactly one seam, the `canonical_product` record.
- `product_match` -- the shared visual matcher used by the buy-side audit step; not implemented by this kind.

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[marketplace-listing-builder]] | downstream (builder identity) | 0.55 |
| [[bld_schema_marketplace_listing]] | downstream (schema, source of truth) | 0.52 |
| [[kc_canonical_product]] | upstream (depends_on) | 0.46 |
| [[p01_kc_output_validator]] | upstream (depends_on) | 0.40 |
| [[kc_opportunity_matrix]] | sibling (inbound/outbound twin) | 0.38 |
