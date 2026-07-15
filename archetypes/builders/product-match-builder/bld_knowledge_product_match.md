---
kind: knowledge_card
id: bld_knowledge_card_product_match
pillar: P01
llm_function: INJECT
purpose: Domain knowledge for product_match production -- visual record-linkage and catalog-audit specification
sources: _tools/capability_generators/product_match.py, apps/dashboard_web/lib/molds.ts (MOLD_PRODUCT_MATCH), apps/dashboard_web/lib/capability_contracts_v1.0.md (section 16), _tools/cex_run_capability.py (_BASE_CAPABILITIES), N06_commercial/P08_architecture/p08_adr_opportunity_matrix_kind.md, _docs/specs/contract/n01_sourcing_rigor.md
quality: null
title: "Knowledge Card Product Match"
version: "1.0.0"
author: n03_builder
tags: [product_match, builder, examples]
tldr: "Golden and anti-examples for product_match construction, demonstrating ideal structure and common pitfalls."
domain: "product match construction"
created: "2026-07-02"
updated: "2026-07-02"
8f: "F3_inject"
keywords: [product match construction, knowledge card product match, product_match, builder, examples, [record_linkage, catalog_audit], domain knowledge, executive summary product match, spec table, match engine status matrix]
density_score: 0.90
related:
  - bld_schema_product_match
  - bld_knowledge_card_vision_tool
  - p08_adr_opportunity_matrix_kind
  - n01_sourcing_rigor
  - n03_schema
---

# Domain Knowledge: product_match
## Executive Summary
`product_match` is entity resolution / record-linkage: it joins a supplier item to a marketplace
listing by a composite NON-key (photo + dimension + supplier_code), with EAN/GTIN/barcode
deliberately EXCLUDED because every reseller recodes them (the hard-won rule from a real-world
sourcing run that motivated this kind -- `p08_adr_opportunity_matrix_kind.md`). It doubles as a
catalog auditor: even fully offline, it flags text-vs-photo cadastral divergence and low-res /
missing photos on LOCAL item data. It fills a genuine taxonomy gap -- CEX had no entity-resolution
kind before this ADR (driver c). It is the shared matcher behind BOTH the `sourcing_opportunity`
(N06) buy-side audit step and, per the ADR, the outbound TUDAO golden-record merge.
## Spec Table
| Property | Value |
|----------|-------|
| Pillar | P04 (tools) |
| Nucleus | N03 (`_tools/cex_run_capability.py` `_BASE_CAPABILITIES["product_match"]`) |
| Verb | analyze |
| llm_function | CALL (kinds_meta.json) |
| primary_8f | F4_reason (kinds_meta.json -- NOT F5, despite llm_function=CALL) |
| RUN_MODE | offline-deterministic (product_match.py `RUN_MODE` constant) |
| contract_version | "1.0.0" (module const) / "1.0" (MOLD_PRODUCT_MATCH.contract_version) |
| Output sections | 4, frozen order: table, list, fields, fields |
| Named gate | `match_confiavel` (Veredito section) |
| Max body bytes | 5120 |
## Match Engine Status Matrix (grounded in product_match.py:340-406 -- read before citing "reverse_image" as functional)
| Engine | In closed enum? | Actually implemented in build()? | Row emitted |
|--------|:---:|:---:|-------------|
| none | YES (default) | N/A -- forces `offline=True` | "NAO", "nao executado -- sem motor de match", 0.0 |
| reverse_image | YES | NO | "NAO", "pendente -- run live com motor 'reverse_image'", 0.0 |
| embedding | YES | NO | "NAO", "pendente -- run live com motor 'embedding'", 0.0 |
| manual | YES | NO | "NAO", "pendente -- run live com motor 'manual'", 0.0 |
Every branch -- offline OR not, any engine, with or without a credential -- currently returns an
honest NAO at 0.0 confidence. `matched_count` is always 0 by construction, so `match_confiavel`
cannot currently pass (gate formula: `(not offline) and (total>0) and (matched_count>=total)`).
The catalog-AUDIT side (`_audit_text_vs_photo`) is the only currently-functional analysis, and it
runs on local data with zero network calls.
## Patterns
- **Composite key, never a single field**: `_normalize_join_key` builds `key=value|key=value|...`
  from whichever of `match_join_keys` the item actually carries; a missing field is silently
  skipped (never padded with a placeholder)
- **Exclusion is structural, not accidental**: `match_exclude_keys` (default ean/gtin/barcode) is
  stripped from the join even if a caller's `match_join_keys` leaks one in -- defensive, logged as
  a note, never a silent drop
- **Audit runs regardless of match_engine**: `audit_enabled` is independent of `match_engine`;
  even `match_engine=none` still produces cadastral-divergence flags
- **Shared helpers, not a shared service**: `_normalize_join_key` + `_audit_text_vs_photo` are
  PURE functions (no I/O) importable by name -- `sourcing_opportunity.py` soft-imports both
  (product_match.py:314-330) rather than calling a shared microservice
| Pattern | When to use |
|---------|-------------|
| match_engine=none (default) | Every run today -- no live engine exists yet |
| audit_enabled=true (default) | Always, unless the caller only wants raw match rows |
| audit_min_photo_px tuned up (>200) | Stricter photo-quality catalogs (e.g. premium marketplaces) |
## Anti-Patterns
| Anti-Pattern | Why it fails |
|-------------|-------------|
| Describing `reverse_image`/`embedding`/`manual` as working today | product_match.py has NO implementation for any of the three (verified by reading build(), lines 396-406) -- they are closed-enum placeholders |
| Treating EAN/GTIN/barcode as a valid join key | Structurally excluded -- every reseller recodes them (ADR driver, real-world sourcing evidence) |
| Reordering the 4 output sections | `capability_contracts_v1.0.md` freezes order+layout; StructuredResultView is frozen to fields\|table\|list |
| Fabricating a SIM/PARCIAL match when offline | Degrade-never: offline ALWAYS returns NAO at 0.0, never invented (product_match.py:386-393) |
| Conflating with vision_tool | product_match is a two-record JOIN + audit; vision_tool analyzes ONE image with no join target |
| Conflating with opportunity_matrix | opportunity_matrix (P11/N06) ranks buy-side cost x demand; product_match (P04/N03) is record-linkage |
## Application
1. Identify the supplier-item x marketplace-listing join task and confirm EAN/GTIN/barcode are excluded
2. Enumerate `match_join_keys` (default photo/dimension/supplier_code) and any extra `match_exclude_keys`
3. Select `match_engine` from the closed enum, documenting current non-implementation honestly
4. Set `match_confidence_floor` (default 0.7) and `audit_min_photo_px` (default 200)
5. Declare the 4 output sections in frozen order and the `match_confiavel` gate + blockers

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[bld_schema_product_match]] | downstream | 0.48 |
| [[bld_knowledge_vision_tool]] | sibling | 0.44 |
| p08_adr_opportunity_matrix_kind | upstream | 0.43 |
| n01_sourcing_rigor | upstream | 0.40 |
| n03_schema | upstream | 0.36 |
