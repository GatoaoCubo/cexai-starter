---
id: bld_memory_canonical_product
kind: entity_memory
pillar: P10
llm_function: INJECT
version: 1.0.0
quality: null
tags: [canonical_product, memory, patterns]
title: "Memory Patterns: canonical_product"
author: builder
tldr: "Canonical Product memory: context persistence, recall triggers, and honesty flags"
8f: "F3_inject"
keywords: [memory patterns, canonical product memory, context persistence, recall triggers, canonical_product, memory, patterns, common mistakes, dangling spec_version]
density_score: 0.88
created: "2026-07-03"
updated: "2026-07-03"
related:
  - canonical-product-builder
  - kc_canonical_product
  - bld_rules_canonical_product
  - bld_architecture_canonical_product
  - bld_context_sources_canonical_product
---
# Memory Patterns: canonical_product
## What to Remember
- THE STRUCTURAL LAW is non-negotiable: structured attrs stay OUT of prose, always
- Provenance and conflicts are CARRIED from the merge, never invented, never silently resolved
- `condition` defaults to "new" ONLY when no source supplied one -- do not claim provenance for a default
- `currency` defaults BRL and `id` is synthetic -- both are EXCLUDED from the provenance denominator (claiming a source for a system default would be fabrication)
- canonical_product boundary: the channel-neutral UNION, NOT a per-channel projection (`marketplace_listing`) and NOT the rendered page (`product_ad`)

## Known Gap (honesty flag, from evidence-gathering)
- `.cex/kinds_meta.json`'s `spec_version: "docs/specs/01_ads_catalog"` does NOT exist
  in this repo (`docs/specs/` holds only `04_bootstrap_orchestrator`..`10_multitenant_100`
  + `compiled`). Reading `_tools/cex_canonical_product.py:9` alongside
  `docs/archive/SPEC_central_backlog_2026_06_23.md` suggests this path belongs to
  **the reference commerce app / an earlier project phase**, not this Central repo.
  Not fabricated -- just stale/external. Do NOT chase it as a citable Central path.

## Common Mistakes
| Mistake | Correction |
|---------|-----------|
| Conflating with `marketplace_listing` | canonical_product = channel-neutral union; marketplace_listing = per-channel projection |
| Conflating with `product_ad` | canonical_product = golden record; product_ad = rendered buyer page (capability layer, unregistered kind) |
| Averaging a numeric conflict (e.g. weight 900g vs 450g) | Flag in `_conflicts`; a human resolves it |
| Inventing a value for an absent field | `None`/`[]`/`{}` -- never-fabricate |
| Burying `key_features`/`benefits_*` inside `description`/`long_description` | Structural law violation -- keep separate |

## Cross-Kind Memory
- `data_contract` / `validation_schema`: both are `depends_on` PREREQUISITES, not downstream of this kind
- `marketplace_listing`: DOWNSTREAM, and its own `depends_on` names `canonical_product` -- `cex_distill.py`'s `kind_closure` pulls this kind into EVERY `vertical==retail`/`has_store` tenant distillation (structural, not incidental)
- `product_ad`: downstream, via `cex_grounded_copy.py` (treats canonical_product as "the fact ground-truth"; voice shapes the sentence, never the facts)

## Reuse Signals
- Check existing instances: grep P06 for `cp_` / `p06_cp_` prefix files
- Check `tests/fixtures/corpus_50.json` (the real 50-product, >=2-source corpus) before hand-building a new example
- Run `python _tools/cex_canonical_product.py --demo` to see the reference merge+bridge before authoring a new one

## Memory Persistence Checklist
- Verify memory type matches taxonomy (entity, episodic, procedural, working)
- Validate retention aligns with the tenant catalog's refresh cadence
- Cross-reference `memory_scope` for boundary correctness
- Check for stale entries (e.g. the dangling `spec_version` above) that need a hygiene pass

## Memory Pattern
```yaml
type: classified
retention: defined
scope: bounded
decay: configured
```
```bash
python _tools/cex_compile.py {FILE}
python _tools/cex_memory_update.py --check
```

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[canonical-product-builder]] | upstream | 0.43 |
| [[kc_canonical_product]] | upstream | 0.41 |
| [[bld_rules_canonical_product]] | downstream | 0.38 |
| [[bld_architecture_canonical_product]] | upstream | 0.36 |
| [[bld_context_sources_canonical_product]] | related | 0.35 |
