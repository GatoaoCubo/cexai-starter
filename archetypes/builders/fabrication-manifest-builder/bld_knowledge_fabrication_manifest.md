---
kind: knowledge_card
id: bld_knowledge_card_fabrication_manifest
pillar: P01
llm_function: INJECT
purpose: Domain knowledge for fabrication_manifest production
quality: null
title: "Knowledge Card Fabrication Manifest"
version: "1.0.0"
author: n03_engineering
tags: [fabrication_manifest, builder, knowledge_card, orchestration, bootstrap]
tldr: "Domain knowledge for fabrication_manifest production"
domain: "fabrication_manifest construction"
created: "2026-07-03"
updated: "2026-07-03"
8f: "F3_inject"
keywords: [fabrication_manifest construction, knowledge card fabrication manifest, fabrication_manifest, builder, knowledge_card, bootstrap_orchestrator, tenant_id, stage_status, domain overview]
density_score: 0.85
related:
  - fabrication-manifest-builder
  - bld_collaboration_fabrication_manifest
  - bld_tools_fabrication_manifest
  - kc_fabrication_manifest
  - bld_schema_fabrication_manifest
---
## Domain Overview
A `fabrication_manifest` is the per-tenant recipe + resume-anchor for ONE run of the bootstrap
orchestrator (`_tools/cex_bootstrap_orchestrator.py`, 2,745 lines): one BrandBook fabricates a
complete per-tenant fused stack (L0 brain + L2 site + L3 admin) through 4 stages -- A INGEST
(BrandBook -> brand config), B PROVISION (mint the per-tenant surface), C FABRICATE (C3 admin +
C0 brain + C2 site, each independently resumable), D WIRE (assert the flywheel closes). It is
NOT hand-authored: the module composes EXISTING proven pieces (`cex_tenant_onboard.onboard()`,
the compose/module-manager attach gate, the dual-output human-faces) end to end and is itself the
FIRST engine organized *around* this kind as a first-class concept (`MANIFEST_KIND =
"fabrication_manifest"`, `MANIFEST_SCHEMA = "cex.fabrication_manifest/1"`).

**Current status (grounded, not assumed):** the module carries a 2026-07-02 deprecation banner
(`docs/SPEC_TENANT_BRAIN_RUNNABLE.md` P4) pointing new tenant-fabrication work at
`_tools/cex_distill.py`. It still runs (warns on stderr, does not block) and its test suite still
passes (24/24, `_tools/tests/test_bootstrap_orchestrator.py`). `cex_distill.py` does NOT reference
this kind at all -- it is a separate pipeline. This builder exists so intent resolution has
something real to load (F2 BECOME), not to relaunch the deprecated engine as the recommended path.

## Key Concepts
| Concept | Definition | Source |
|---------|------------|--------|
| fabrication_manifest | Per-tenant recipe + resume-anchor for one bootstrap-orchestrator run | `.cex/kinds_meta.json` |
| Stage (A/B/C/D) | The 4 pipeline phases; each has a `stage_status` key in `pending\|done\|skipped\|error` | `cex_bootstrap_orchestrator.py:140-160` |
| C_admin/C_site/C_brain | The 3 granular Stage-C sub-contracts, independently resumable | `cex_bootstrap_orchestrator.py:153-158` |
| HostingTarget | Pluggable hosting seam (mirrors `ChannelAdapter`); `cex_managed` (v1) vs `sovereign` (deferred stub) | `cex_bootstrap_orchestrator.py:170-265` |
| brand_config_ref | A REFERENCE to the tenant's brand config -- never duplicated brand values | spec decision 8.4 |
| Idempotent resume | `fabricate_all` re-runs only stages not already `done` | constitution 4 |
| Data-plane binding | RLS surfaces (`tenant_data`,`tenant_memory`,`tenant_runtime`) the manifest records | `cex_bootstrap_orchestrator.py:275` |

## Real Evidence (grounded, not invented)
- Central implementation: `_tools/cex_bootstrap_orchestrator.py` (`MANIFEST_KIND`, `MANIFEST_SCHEMA`,
  `MANIFEST_FILENAME` at lines 136-138; new/load/save/mutate lifecycle lines 269-410ish;
  `_cmd_status` CLI subcommand at lines 1978-1989).
- A real, live tenant instance verified by direct read: `.cex/tenants/petlux_showcase/runtime/
  fabrication_manifest.yaml` (`brand_name: PetLux`, 2 chosen capabilities, all 7 stage_status keys
  `done`, a real `wire.edit_to_reflect` readback proof).
- Passing tests re-run this build: `python -m pytest _tools/tests/test_bootstrap_orchestrator.py -q`
  -> 24 passed.
- Spec: `docs/specs/04_bootstrap_orchestrator/spec.md` (status: Draft, names this kind explicitly).

## Common Patterns
1. Always `load_manifest(tenant_id)` before assuming a fresh state -- resumability is the point.
2. `stage_status.C` reaches `done` when `C_admin` + `C_brain` are `done` and `C_site` is either
   `done` or `skipped` (a SKIPPED site does not block the umbrella C from completing).
3. `hosting_target` binding is recorded as PLACEHOLDER fields (`__CEX_MANAGED_REPO__/...`) --
   never a real secret or live endpoint (constitution 3+5).
4. A dangling/wrong-suffix `brand_config_ref` degrades to `None` at provision time -- never
   aborts the run (degrade-never).

## Pitfalls
- Treating this kind like `team_charter`/`deployment_manifest` (hand-authored `.md` + frontmatter
  + `cex_compile.py`) -- it is a bare `.yaml`, no sidecar frontmatter, no compile step.
- Hand-writing `stage_status: done` for a stage that never actually ran -- corrupts the resume
  anchor and can cause `fabricate_all` to silently skip real work.
- Duplicating brand values inline instead of a `brand_config_ref` pointer (violates constitution 3).
- Assuming `_tools/cex_bootstrap_orchestrator.py` is the CURRENT recommended path for new tenant
  work without checking its own deprecation banner first.

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[fabrication-manifest-builder]] | downstream | 0.61 |
| [[bld_collaboration_fabrication_manifest]] | downstream | 0.44 |
| [[bld_tools_fabrication_manifest]] | downstream | 0.43 |
| [[kc_fabrication_manifest]] | sibling | 0.42 |
| [[bld_schema_fabrication_manifest]] | downstream | 0.41 |
