---
id: bld_tools_canonical_product
kind: knowledge_card
pillar: P06
title: "Canonical Product Builder -- Tools"
version: 1.0.0
llm_function: CALL
tags: [builder, canonical_product, tools]
author: builder
quality: null
tldr: "Canonical Product schema: tool integrations, CLI commands, and external capabilities"
8f: "F3_inject"
keywords: [canonical product schema, tool integrations, cli commands, and external capabilities, builder, canonical_product, tools, cex_canonical_product.py, cex_catalog_merge.py, cex_channel_adapter.py]
density_score: 0.88
created: "2026-07-03"
updated: "2026-07-03"
related:
  - bld_tools_data_contract
  - bld_tools_validation_schema
  - kc_canonical_product
  - canonical-product-builder
  - bld_schema_canonical_product
---
# Canonical Product Builder -- Tools

Builder domain: catalog / golden-record. Primary nucleus: N04 (merge) / N05 (adapter) / N03 (this builder).

## Runtime Tools

| Tool | Function | Stage |
|------|----------|-------|
| `python _tools/cex_canonical_product.py --demo` | Proof: merge Bling+ML+own_site -> typed canonical; shows the 900g-vs-450g weight conflict + provenance | F6 PRODUCE |
| `python _tools/cex_canonical_product.py --self-test` | DB-free correctness checks (dims parser, bridge, schema, structural law, coverage) | F7 GOVERN |
| `cex_canonical_product.canonical_from_merged(golden, product_id=)` | Bridge one golden record -> typed CanonicalProduct | F6 PRODUCE |
| `cex_canonical_product.merge_to_canonical(by_source, policy=)` | Full pipeline: merge N source records -> typed CanonicalProduct | F5 CALL |
| `cex_canonical_product.validate_against_schema(canonical)` | Structural + structural-law check, returns (ok, errors[]) | F7 GOVERN |
| `cex_canonical_product.field_union_coverage(canonical)` | SC-001 completeness metric | F7 GOVERN |
| `cex_canonical_product.provenance_coverage(canonical)` | SC-001 provenance-coverage metric | F7 GOVERN |
| `python _tools/cex_catalog_merge.py` | Upstream: multi-source merge engine this kind bridges (N04) | F3 INJECT |
| `python _tools/cex_product_catalog_adapter.py` | Upstream: raw-data normalize/validate adapter (N05) | F3 INJECT |
| `python _tools/cex_channel_adapter.py` | Downstream: `ChannelAdapter.map()+.validate()` -> `marketplace_listing` | F5 CALL |
| `python _tools/cex_grounded_copy.py` | Downstream: treats canonical_product as "fact ground-truth" for ad copy | F5 CALL |
| `python _tools/cex_content_factory.py` | Downstream: content-fabric consumer | F5 CALL |
| `python _tools/cex_ads_dryrun.py` | Offline demo/self-test harness for the merge+bridge (P1+P2) | F7 GOVERN |
| `python -m pytest tests/test_ads_canonical.py -q` | SC-001 acceptance suite -- 17 passed (re-run 2026-07-03) | F7 GOVERN |
| `python _tools/cex_compile.py {path}` | Compile artifact to YAML | F8 COLLABORATE |
| `python _tools/cex_doctor.py` | Validate builder integrity (12 ISOs present) | F7 GOVERN |

## Context Sources

| Source | Content | Stage |
|--------|---------|-------|
| `N00_genesis/P01_knowledge/library/kind/kc_canonical_product.md` | Primary domain KC | F3 INJECT |
| `.cex/kinds_meta.json` (key: `canonical_product`) | Boundary, pillar, naming, depends_on | F1 CONSTRAIN |
| `docs/schema/contracts/canonical_product.schema.json` | JSON Schema contract (26 required of 42 fields) | F2 BECOME |
| `archetypes/builders/canonical-product-builder/bld_schema_canonical_product.md` | Output schema | F2 BECOME |

## Discovery

```bash
# Find existing canonical_product artifacts
python _tools/cex_retriever.py --query "channel-neutral product golden record provenance conflicts"

# Re-run the real acceptance suite
python -m pytest tests/test_ads_canonical.py -q

# Validate a new artifact
python _tools/cex_hooks.py validate path/to/artifact.md
```

## Tool Integration Checklist

- Verify tool name follows snake_case convention
- Validate input/output matches `canonical_product.schema.json`
- Cross-reference with `cex_channel_adapter.py` for downstream discoverability
- Test with `--self-test` before any production use

## Invocation Pattern

```yaml
name: cex_canonical_product
input_schema: golden_record (dict)
output_schema: canonical_product.schema.json
error_handling: degrade-never (empty golden -> valid empty shape)
timeout: n/a (pure, stdlib-only, no I/O)
```
```bash
python _tools/cex_compile.py {FILE}
python _tools/cex_doctor.py --scope canonical-product-builder
```

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[bld_tools_data_contract]] | sibling | 0.55 |
| [[bld_tools_validation_schema]] | sibling | 0.54 |
| [[kc_canonical_product]] | upstream | 0.50 |
| [[canonical-product-builder]] | upstream | 0.45 |
| [[bld_schema_canonical_product]] | downstream | 0.40 |
