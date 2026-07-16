---
kind: config
id: bld_config_fabrication_manifest
pillar: P09
llm_function: CONSTRAIN
purpose: Naming, paths, limits for fabrication_manifest production
quality: null
title: "Config Fabrication Manifest"
version: "1.0.0"
author: n03_engineering
tags: [fabrication_manifest, builder, config, orchestration]
tldr: "Naming, paths, limits for fabrication_manifest production"
domain: "fabrication_manifest construction"
created: "2026-07-03"
updated: "2026-07-03"
8f: "F1_constrain"
keywords: [fabrication_manifest construction, config fabrication manifest, fabrication_manifest, builder, config, tenant runtime, gitignored, fabrication_manifest.yaml]
density_score: 0.85
related:
  - bld_config_deployment_manifest
  - bld_config_team_charter
  - fabrication-manifest-builder
  - bld_schema_fabrication_manifest
---
## Naming Convention -- TWO conflicting sources (documented, not resolved by this cell)
| Source | Pattern | Status |
|--------|---------|--------|
| `.cex/kinds_meta.json` | `p12_fm_{{tenant}}.yaml` | Nominal/declared naming |
| `_tools/cex_bootstrap_orchestrator.py` (`MANIFEST_FILENAME`) | `fabrication_manifest.yaml` (FIXED, tenant scoping via directory) | ACTUAL runtime behavior |

Both are real and verified this build (kinds_meta read directly; code read directly; the
`petlux_showcase` instance on disk is literally named `fabrication_manifest.yaml`, not
`p12_fm_petlux_showcase.yaml`). This builder surfaces the gap; reconciling `kinds_meta.json` is
out of this cell's mandate (edits to that file are explicitly forbidden this wave).

## Paths (real, verified)
Runtime instance: `.cex/tenants/`{{tenant_id}}`/runtime/fabrication_manifest.yaml`
Resolved via: `resolve_tenant_path(MANIFEST_FILENAME, surface="runtime", tenant_id=..., create=True)`
-- the fail-closed path guard (escape attempts raise `SystemExit`), never a hand-joined path.
Git status: **GITIGNORED** (`.gitignore:156`) -- a tenant's fabrication state never lands in the
framework tree. Never `git add -f` this file.

## Limits
| Field | Value | Source |
|-------|-------|--------|
| max_bytes (declared) | 4096 | `.cex/kinds_meta.json` |
| max_bytes (observed) | ~5,500B for a fully-fabricated instance | `kc_fabrication_manifest.md` (petlux_showcase fixture) -- OVER budget, already documented |
| ISO max_bytes (this builder's own files) | 8192 (10240 for bld_prompt) | `_tools/cex_doctor.py` MAX_BYTES/MAX_BYTES_PROMPT |

## Hooks (adapted -- this kind has NO compile step)
| Hook | Action |
|------|--------|
| pre_build | Run `load_manifest(tenant_id)` first -- never assume a fresh state (resumability). |
| post_build | NONE -- there is no `cex_compile.py` step; this is not a `.md`+frontmatter artifact. The real "post_build" is the CLI itself calling `save_manifest()`. |
| on_preview_only | If drafting a PREVIEW (not a real run), label it clearly as a preview and do not write it to the tenant runtime path. |
| on_error | Fail-closed: a bad `tenant_id` or unknown `hosting_target`/`stage` value raises `SystemExit` BEFORE any write (mirrors the module's own contract). |

## Version Policy
- `schema: cex.fabrication_manifest/1` is the only version marker on the artifact itself (no
  semver `version:` field the way `.md` artifacts carry one).
- Re-running the pipeline UPDATES the same single file in place (idempotent) -- never a v2/v3 copy.
- A schema bump (`cex.fabrication_manifest/2`) would be a code change to `MANIFEST_SCHEMA`, not
  something this builder introduces unilaterally.

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[bld_config_deployment_manifest]] | sibling | 0.30 |
| [[bld_config_team_charter]] | sibling | 0.28 |
| [[fabrication-manifest-builder]] | downstream | 0.30 |
| [[bld_schema_fabrication_manifest]] | related | 0.32 |
