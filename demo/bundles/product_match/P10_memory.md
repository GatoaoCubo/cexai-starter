---
id: p10_lr_product_match_builder
kind: learning_record
pillar: P10
version: 1.0.0
created: 2026-07-02
updated: 2026-07-02
author: builder_agent
observation: "Static read of _tools/capability_generators/product_match.py (build(), lines 323-544) shows that ALL four match_engine enum values (reverse_image, embedding, manual, none) currently resolve to the SAME honest-NAO-at-0.0 row; only the reason text differs ('nao executado' vs 'pendente -- run live com motor X'). No live matcher exists yet. The catalog-audit side (_audit_text_vs_photo) is the only functional analysis path and runs entirely offline on local item fields."
pattern: "Ground every product_match spec in the generator's ACTUAL branch behavior, not the enum's aspirational vocabulary. Document match_engine as a closed enum with an honest 'implemented: no' column per value until a live engine ships. Mirror the 4 output sections BYTE-IDENTICAL to MOLD_PRODUCT_MATCH order+layout. Keep body under 5120 bytes."
evidence: "Direct source read (this build session, 2026-07-02): product_match.py lines 386-406 (offline vs non-offline branches both emit NAO), lines 476-524 (match_confiavel gate formula + score deductions), apps/dashboard_web/lib/molds.ts lines 3289-3391 (MOLD_PRODUCT_MATCH mock, contract_version 1.0)."
confidence: 0.9
outcome: OBSERVATION
domain: product_match
tags: [product-match, record-linkage, catalog-audit, match-engine-status, offline-honest-null, join-key]
tldr: "match_engine is a closed enum where only 'none' is behaviorally distinct today (forces offline); reverse_image/embedding/manual are unimplemented placeholders. The audit side is the only currently-real analysis. Stay under 5120 bytes."
impact_score: 7.5
decay_rate: 0.05
agent_group: n03_engineering
keywords: [product match, match engine status, join key exclusion, offline honest null, catalog audit, record linkage, match confiavel gate]
memory_scope: project
observation_types: [reference, project]
quality: null
title: "Memory Product Match"
8f: "F7_govern"
density_score: 0.90
llm_function: INJECT
related:
  - product-match-builder
  - bld_schema_product_match
---
## Summary
`product_match` is consumed by two callers today: the dashboard run path (N03, verb=analyze) and
`sourcing_opportunity.py` (N06), which soft-imports the two PURE helpers `_normalize_join_key` and
`_audit_text_vs_photo` for its own visual-audit stage. Because the match side is a scaffold (no
live reverse-image/embedding/manual engine exists), a spec that implies live matching capability
would mislead both callers. The difference between an honest product_match spec and a misleading
one comes down to one decision made at spec time: does the spec claim the enum's vocabulary is
implemented, or does it document the enum as closed-but-largely-unimplemented?
## Pattern
**Document match_engine as a closed enum with an explicit implementation-status column.**
Match engine status (grounded in product_match.py, not aspirational):
1. `none` (default): the ONLY value with distinct code behavior -- forces `offline=True`
   unconditionally, regardless of a supplied credential.
2. `reverse_image` / `embedding` / `manual`: valid enum members, zero implementation -- the
   generator emits the identical honest-NAO row with a "pendente -- run live com motor '{engine}'"
   reason string (product_match.py:396-406).
3. An unrecognized string falls back to `none` with a note, never a crash.
Join key rules:
1. Default `match_join_keys`: `[photo, dimension, supplier_code]` -- composite, never a single field.
2. `match_exclude_keys` (default `[ean, gtin, barcode]`) is an INTERNAL override -- present in
   `product_match.py`'s `inputs.get(...)` calls but ABSENT from `MOLD_PRODUCT_MATCH.input_contract`
   (the dashboard-exposed 6 fields). A spec documents it as an advanced/internal knob, not a
   dashboard field.
3. A join key that also appears in the exclude set is stripped defensively and logged
   (product_match.py:372-377) -- never silently honored.
Output section budget (5120 bytes max): Overview (300) + Input Contract (1200) + Output Sections
(2400) + Gate (600) = ~4500, leaving headroom for frontmatter-adjacent prose.
## Anti-Pattern
1. Describing `reverse_image` as "calls Google Lens" or similar -- no such call exists in the
   codebase as of this read; it is an enum placeholder.
2. Treating `match_confiavel` as achievable today -- `matched_count` is 0 by construction while
   offline, and there is no live branch that populates it either (product_match.py:396-406), so
   the gate cannot currently pass regardless of input.
3. Omitting the `match_exclude_keys` internal override because it is absent from the dashboard mold
   (a complete spec documents both the dashboard-exposed AND the internal-override surface).
4. Reordering the 4 output sections or changing a column set (the shape is frozen to
   `MOLD_PRODUCT_MATCH`; see `capability_contracts_v1.0.md` "How to build to this contract").
5. Using EAN/GTIN/barcode as a join key (structurally excluded -- every reseller recodes them).
6. Setting quality to a non-null value (self-scoring corrupts pool quality metrics).
## Context
Body limit 5120B. Budget: Overview (300) + Input Contract (1200) + Output Sections (2400) + Gate
(600). Link to `_tools/capability_generators/product_match.py` for the real implementation; don't
duplicate its code in the spec body (spec-only, per SCHEMA constraints).

## Metadata

```yaml
id: p10_lr_product_match_builder
pipeline: 8F
scoring: hybrid_3_layer
```

```bash
python _tools/cex_score.py --apply p10-lr-product-match-builder.md
```

## Properties

| Property | Value |
|----------|-------|
| Kind | `learning_record` |
| Pillar | P10 |
| Domain | product_match |
| Pipeline | 8F (F1-F8) |
| Scorer | cex_score.py |
| Compiler | cex_compile.py |
| Retriever | cex_retriever.py |
| Quality target | 9.0+ |
| Density target | 0.85+ |

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[bld_prompt_product_match]] | upstream | 0.43 |
| [[product-match-builder]] | upstream | 0.34 |
| [[bld_schema_product_match]] | upstream | 0.34 |
