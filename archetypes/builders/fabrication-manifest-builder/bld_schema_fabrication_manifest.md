---
kind: schema
id: bld_schema_fabrication_manifest
pillar: P06
llm_function: CONSTRAIN
purpose: Formal schema -- SINGLE SOURCE OF TRUTH for fabrication_manifest
quality: null
title: "Schema Fabrication Manifest"
version: "1.0.0"
author: n03_engineering
tags: [fabrication_manifest, builder, schema, orchestration]
tldr: "Formal schema -- SINGLE SOURCE OF TRUTH for fabrication_manifest"
domain: "fabrication_manifest construction"
created: "2026-07-03"
updated: "2026-07-03"
8f: "F1_constrain"
keywords: [fabrication_manifest construction, schema fabrication manifest, fabrication_manifest, builder, schema, tenant_id, stage_status, hosting_target, p12_fm]
density_score: 0.85
related:
  - bld_schema_deployment_manifest
  - bld_schema_team_charter
  - fabrication-manifest-builder
---
## Top-Level Fields (real shape -- `new_manifest()`, `_tools/cex_bootstrap_orchestrator.py:278-315`)
### Required (present from creation)
| Field | Type | Required | Default | Notes |
|-------|------|----------|---------|-------|
| schema | string | yes | `cex.fabrication_manifest/1` | Self-stamped; NOT a `.md` frontmatter id |
| kind | string | yes | `fabrication_manifest` | Self-stamped; the ONLY taxonomy tag on the file |
| tenant_id | string | yes | | Via `_safe_tenant_id`: `[a-z0-9_-]`, 1-64 chars, rejects traversal/empty |
| brand_config_ref | string\|null | yes | null | A REFERENCE only (path/id) -- never resolved values |
| brandbook | dict\|null | yes | null | Raw Stage-A input, recorded verbatim, never resolved |
| chosen_capabilities | list | yes | [] | Union-merged on re-run, never dropped |
| targets | dict | yes | `{brain:null,site:null,admin:null}` | Filled per-layer as Stage C runs |
| hosting_target | string | yes | `cex_managed` | Must be a registered `HostingTarget` id |
| status | string | yes | `draft` | `draft -> ingested\|provisioned\|fabricated`; no `wired` state |
| stage_status | dict | yes | all `pending` | 7 keys: `A,B,C,D,C_admin,C_site,C_brain` |
| provision | dict\|null | yes | null | Filled ONLY by `provision_tenant()` (Stage B) |
| fabricate | dict\|null | yes | null | Filled ONLY by `fabricate_layers()` (Stage C) |

### Added later by the pipeline (NOT present on a fresh manifest)
| Field | Added by | Notes |
|-------|----------|-------|
| ingest | `ingest_brandbook()` | Stage A result: brand_name, overlay_path, mechanism |
| wire | `wire_flywheel()` | Stage D result: closed, run_to_readback, write_leg/return_leg |

## Naming -- a DOCUMENTED discrepancy (grounded, not invented)
`.cex/kinds_meta.json` declares `naming: "p12_fm_{{tenant}}.yaml"`. The REAL code
(`MANIFEST_FILENAME = "fabrication_manifest.yaml"`, `manifest_path()`) uses a FIXED filename --
tenant scoping comes from the DIRECTORY (`.cex/tenants/<tid>/runtime/`), not the filename. The
kind-KC (`kc_fabrication_manifest.md`) already documents this exact gap. Do not "fix" the naming
by hand -- surface the discrepancy if asked; changing it is a kinds_meta.json edit, out of this
cell's mandate.

## max_bytes -- a DOCUMENTED overage
`max_bytes: 4096` per kinds_meta. The real `acme_demo` instance observed this build is
larger (multi-stage manifests with `provision`/`fabricate`/`wire` populated commonly exceed 4 KiB
-- the kind-KC records ~5,500B for that fixture). This is an existing, already-documented gap,
not something this builder should silently paper over.

## Constraints (real, from the module)
- `tenant_id` MUST pass `_safe_tenant_id` BEFORE any write (fail-closed, `SystemExit` on failure).
- `hosting_target` MUST be a key in `HOSTING_TARGETS` (`cex_managed`, `sovereign`) -- an unknown
  id raises `SystemExit` (`get_hosting_target`).
- `sovereign` as a REAL target raises `SystemExit` at `provision_record()` time -- it is a
  declared stub only (`SovereignTarget`).
- Every `stage_status` value MUST be one of `pending|done|skipped|error` (`STAGE_VALUES`) --
  `_set_stage` raises `SystemExit` on an unknown stage key or value.
- `stage_status.C` derives from the 3 `C_*` keys via `_roll_up_stage_c` -- never set directly by
  a human/LLM without checking the sub-keys first.
- File is GITIGNORED (`.gitignore:156`) -- never committed to the framework tree.

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[bld_schema_deployment_manifest]] | sibling | 0.50 |
| [[bld_schema_team_charter]] | sibling | 0.48 |
| [[fabrication-manifest-builder]] | downstream | 0.40 |
