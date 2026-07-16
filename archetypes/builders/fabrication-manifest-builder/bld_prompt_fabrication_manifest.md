---
kind: instruction
id: bld_instruction_fabrication_manifest
pillar: P03
llm_function: REASON
purpose: Step-by-step production process for fabrication_manifest
quality: null
title: "Instruction Fabrication Manifest"
version: "1.0.0"
author: n03_engineering
tags: [fabrication_manifest, builder, instruction, orchestration]
tldr: "Step-by-step production process for fabrication_manifest"
domain: "fabrication_manifest construction"
created: "2026-07-03"
updated: "2026-07-03"
8f: "F6_produce"
keywords: [fabrication_manifest construction, instruction fabrication manifest, fabrication_manifest, builder, instruction, orchestration, tenant_id, brand_config_ref, chosen_capabilities, stage_status]
density_score: 0.85
related:
  - bld_schema_fabrication_manifest
  - fabrication-manifest-builder
  - p12_qg_fabrication_manifest
  - bld_knowledge_card_fabrication_manifest
  - bld_output_template_fabrication_manifest
---
## Phase 1: RESEARCH
1. Read `.cex/kinds_meta.json`'s `fabrication_manifest` entry (boundary, naming, max_bytes,
   depends_on: `white_label_config`, `capability_registry`).
2. Check whether a manifest ALREADY exists for the target tenant at
   `.cex/tenants/<tid>/runtime/fabrication_manifest.yaml` (mirrors `load_manifest`). If it exists,
   the task is RESUME/EXPLAIN, not a fresh draft -- constitution 4 (idempotent, resumable).
3. Read `_tools/cex_bootstrap_orchestrator.py`'s module docstring for the CURRENT pipeline shape
   (A INGEST -> B PROVISION -> C FABRICATE x3 -> D WIRE) and its deprecation banner (top of file,
   points to `_tools/cex_distill.py` as of 2026-07-02).
4. Identify the referenced `brand_config_ref` (a moldgen `.ts` overlay path or a brand-spec
   YAML/JSON) -- a REFERENCE only, never resolved brand values.
5. Identify `chosen_capabilities` from the tenant's actual decision (GDP manifest or explicit
   user list) -- never invent capability slugs; they must exist in `capability_registry`.

## Phase 2: COMPOSE (preview / explain only -- never a live mutation)
1. Reference SCHEMA.md for the exact top-level keys `new_manifest()` returns.
2. Set `schema: cex.fabrication_manifest/1` and `kind: fabrication_manifest` -- the ONLY two
   self-describing fields this artifact carries (there is NO `id:`/`title:`/`version:` frontmatter
   the way a normal CEX `.md` artifact has; this is a bare state YAML).
3. Set `tenant_id` to the sanitized tenant slug (mirrors `_safe_tenant_id`: `[a-z0-9_-]`, 1-64
   chars, no traversal).
4. Set `brand_config_ref` to the reference path/id if known, else `null`.
5. Set `brandbook` to the raw Stage-A input dict if one was supplied verbatim, else `null`.
6. Set `chosen_capabilities` to the tenant's chosen list (deduplicated, ordered).
7. Set `targets: {brain: null, site: null, admin: null}` -- these are ONLY filled by Stage C.
8. Set `hosting_target` to `cex_managed` unless the tenant explicitly requested `sovereign` (which
   is a DEFERRED stub -- flag this, do not silently accept it as workable).
9. Set `status: draft` and `stage_status` -- ALL 7 keys (`A,B,C,D,C_admin,C_site,C_brain`) at
   `pending` for a genuinely fresh manifest.
10. Leave `provision`, `fabricate`, `ingest`, `wire` ABSENT/null in any preview -- these blocks are
    populated exclusively by running the real pipeline functions (`provision_tenant`,
    `fabricate_layers`, `ingest_brandbook`, `wire_flywheel`).

## Phase 3: VALIDATE
- [ ] No frontmatter/`id:` field invented -- this kind self-stamps only `schema:` + `kind:`.
- [ ] `tenant_id` passes the sanitize contract (no traversal, no empty string).
- [ ] `brand_config_ref` is a path/id string or `null` -- never inline brand values.
- [ ] `chosen_capabilities` entries are real, declared capability slugs (no invented names).
- [ ] `hosting_target` is one of the registered `HostingTarget` ids (`cex_managed`, `sovereign`).
- [ ] `stage_status` values are all in `pending|done|skipped|error` -- no free text.
- [ ] `C` is only marked `done` when every `C_*` key is terminal AND at least one is `done`
      (`_roll_up_stage_c` semantics) -- never hand-set without checking the sub-keys.
- [ ] Any `provision`/`fabricate`/`ingest`/`wire` block present in an EXISTING file is treated as
      READ-ONLY evidence of a real run -- never edited or extended by hand.
- [ ] The module's deprecation status is disclosed if the output recommends running the CLI for
      a brand-new tenant.

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[bld_schema_fabrication_manifest]] | downstream | 0.45 |
| [[fabrication-manifest-builder]] | downstream | 0.40 |
| [[p12_qg_fabrication_manifest]] | downstream | 0.36 |
| [[bld_knowledge_card_fabrication_manifest]] | upstream | 0.35 |
| [[bld_output_template_fabrication_manifest]] | downstream | 0.34 |
