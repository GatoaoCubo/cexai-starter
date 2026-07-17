---
kind: output_template
id: bld_output_template_fabrication_manifest
pillar: P05
llm_function: PRODUCE
purpose: Template with vars for fabrication_manifest production
quality: null
title: "Output Template Fabrication Manifest"
version: "1.0.0"
author: n03_engineering
tags: [fabrication_manifest, builder, output_template, orchestration]
tldr: "Template with vars for fabrication_manifest production"
domain: "fabrication_manifest construction"
created: "2026-07-03"
updated: "2026-07-03"
8f: "F6_produce"
keywords: [fabrication_manifest construction, output template fabrication manifest, fabrication_manifest, builder, output_template, tenant_id, stage_status, hosting_target, chosen_capabilities]
density_score: 0.85
related:
  - fabrication-manifest-builder
  - bld_schema_fabrication_manifest
---
## IMPORTANT -- this is NOT a normal CEX `.md` artifact
`fabrication_manifest` is a bare YAML file with NO sidecar frontmatter (no `id`/`title`/`version`
fields). It self-stamps only `schema:` and `kind:`. This template shows the STARTER shape
(`new_manifest()`'s pure fields) plus the shape of the blocks that ONLY the real pipeline may
fill (`provision`/`fabricate`/`ingest`/`wire`). A builder producing a PREVIEW fills section A only
and leaves section B `null`; section B is shown for recognition/validation, never for hand-authoring.

## A. Starter shape (safe to draft as a preview)
```yaml
schema: cex.fabrication_manifest/1
kind: fabrication_manifest
tenant_id: "{{tenant_id}}"                 # sanitized: [a-z0-9_-], 1-64 chars, no traversal
brand_config_ref: "{{brand_config_ref}}"   # a REFERENCE (path/id) or null -- never inline values
brandbook: null                            # the raw Stage-A input dict, or null until supplied
chosen_capabilities: []                    # {{chosen_capabilities_list}} -- real registry slugs only
targets:
  brain: null
  site: null
  admin: null
hosting_target: "{{hosting_target}}"       # cex_managed (default) | sovereign (deferred stub)
status: draft                              # draft -> ingested|provisioned|fabricated
stage_status:
  A: pending
  B: pending
  C: pending
  D: pending
  C_admin: pending
  C_site: pending
  C_brain: pending
provision: null
fabricate: null
```

## B. Pipeline-only blocks (READ, never hand-write -- shown for recognition)
```yaml
# Present ONLY after the real CLI has run the corresponding stage. A real example
# (.cex/tenants/acme_demo/runtime/fabrication_manifest.yaml, read this build):
ingest:
  brand_name: Acme
  mechanism: "brandbook cap (build) -> cex_brand_writeback.write_brand_overlay (B2)"
  ok: true
provision:
  data_plane: {isolation_asserted: true, live_db_applied: false, rls_surfaces: [tenant_data, tenant_memory, tenant_runtime]}
  hosting: {binding: {target: cex_managed, provisioned: false}, readiness: {ready: true}}
fabricate:
  admin: {final_enabled: [ads, landing], declared_count: 17}
  brain: {scaffold_kind: pointer, deployed: false, pushed: false}
  site:  {page_count: 2, pages: [landing, catalog], deployed: false}
wire:
  closed: true
  mechanism: "the EXISTING flywheel (wave-0.5 B), asserted DB-free over the audited adapter seam"
  run_to_readback: {rows_written: 1, rows_read_back: 1, artifact_matched: true}
```

## Notes on Section B
- `targets.{brain,site,admin}` mirror the SAME data once Stage C runs -- do not duplicate by hand.
- `hosting.binding` fields prefixed `__CEX_MANAGED_*__` are PLACEHOLDERS (constitution 3+5) --
  never a real secret or live endpoint even in a genuine run.
- If asked to produce this section, the correct answer is "run `fabricate <tid>`" (or its
  successor `cex_distill.py`), not a hand-typed guess.

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[fabrication-manifest-builder]] | downstream | 0.36 |
| [[bld_schema_fabrication_manifest]] | downstream | 0.36 |
