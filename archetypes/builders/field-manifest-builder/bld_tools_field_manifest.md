---
kind: tools
id: bld_tools_field_manifest
pillar: P04
llm_function: CALL
purpose: Tools and APIs available for field_manifest production
quality: null
title: "Tools Field Manifest"
version: "1.0.0"
author: n03_builder
tags: [field_manifest, builder, examples]
tldr: "Golden and anti-examples for field_manifest construction, demonstrating the schema-to-form derivation mold and its common drift pitfalls."
domain: "field manifest construction"
created: "2026-07-03"
updated: "2026-07-03"
8f: "F5_call"
keywords: [field manifest construction, tools field manifest, field_manifest, builder, examples, production tools, data sources, tool permissions, interim validation, related artifacts]
density_score: 0.87
related:
  - bld_tools_input_schema
  - bld_tools_type_def
  - bld_tools_supabase_data_layer
  - bld_tools_interface
  - bld_tools_validation_schema
---

# Tools: field-manifest-builder
## Production Tools
| Tool | Purpose | When | Status |
|------|---------|------|--------|
| brain_query [MCP] | Search existing field_manifests in pool | Phase 1 (check duplicates) | CONDITIONAL |
| Grep / Glob | Search `apps/dashboard_web/lib/field-manifest/` + sibling entity editors for prior art | Phase 1 | ACTIVE |
| cex_hooks.py | Pre-commit / pipeline hook enforcement on saved artifact | Phase 3 | REGISTERED (`.cex/kind_tool_supplement.json` bucket) |
| cex_schema_hydrate.py | Schema hydration pass over the artifact's frontmatter | Phase 3 | REGISTERED (same bucket) |
| cex_compile.py | .md -> .yaml/.json compilation of the produced artifact | F8 COLLABORATE | REGISTERED (same bucket) |
| cex_hooks_native.py | Native-runtime hook variant | Phase 3 | REGISTERED (same bucket) |
| validate_artifact.py | Generic artifact validator | Phase 3 | [PLANNED] |
## Real Implementation Touchpoints (grounding, not production tools)
These are the REAL code modules a field_manifest artifact describes -- read them to
verify field/gate/handler claims before producing, but do not treat them as CLI tools
this builder invokes:
| Module | Role |
|--------|------|
| `apps/dashboard_web/lib/field-manifest/types.ts` | FieldKind union (14), PublishRule, FieldDef, SectionDef, ProductManifest -- the ISO this kind's schema mirrors |
| `apps/dashboard_web/lib/field-manifest/buildSchema.ts` | Derives `{baseSchema, schema, updateSchema, publishRequirements}` from a manifest; the derivation keystone |
| `apps/dashboard_web/lib/field-manifest/renderers.tsx` | `FieldKind -> Renderer` registry (`FIELD_KIND_RENDERERS`) |
| `apps/dashboard_web/lib/field-manifest/ManifestForm.tsx` | Pure layout: groups fields by section, renders via the registry |
| `apps/dashboard_web/lib/field-manifest/handlers.ts` | `HandlerRegistry`, `inertHandlerRegistry`, `AI_FORBIDDEN_CHANNEL_FIELDS`, `filterChannelLinkDiffs` |
| `apps/dashboard_web/lib/field-manifest/productManifest.ts` | The FIRST field_manifest kind instance (14 sections, ~50 fields) -- the proof input |
| `apps/dashboard_web/components/ManifestEntityForm.tsx` | Live mount: wires a manifest to react-hook-form + hand-resolved zod validation + `ApiClient.createEntity` |
| `apps/dashboard_web/app/dashboard/data/[entity]/new/page.tsx` | The route mounting `<ManifestEntityForm>` with `productManifest` |
| `apps/dashboard_web/__tests__/manifest-mount.test.tsx` | Vitest/RTL suite exercising the live mount (render / block-on-empty / submit) -- file read, NOT executed this session (no Node invoked) |
## Data Sources
| Source | Path/URL | Data |
|--------|----------|------|
| CEX Schema | P06_schema/_schema.yaml | Field definitions for field_manifest |
| kinds_meta.json | `.cex/kinds_meta.json` (field_manifest entry) | boundary, naming, max_bytes, depends_on |
| kind_tool_supplement.json | `.cex/kind_tool_supplement.json` | `kind_to_tools["field_manifest"]` = [cex_hooks.py, cex_schema_hydrate.py, cex_compile.py, cex_hooks_native.py] (a shared generic bucket, not field_manifest-specific tooling) |
| Reference implementation | `apps/dashboard_web/lib/field-manifest/` | Real FieldKind/PublishRule/buildSchema/handlers mechanics |
| Zod docs | https://zod.dev/ | `.superRefine()` / `.partial()` / `.extend()` semantics |
## Tool Permissions

| Category | Tools | Status |
|----------|-------|--------|
| ALLOWED | Read, Write, Edit, Bash, Glob, Grep | Explicitly permitted |
| DENIED | (none) | Explicitly blocked |
| EFFECTIVE | Bash, Edit, Glob, Grep, Read, Write | ALLOWED minus DENIED |

## Interim Validation
No dedicated automated validator exists yet for field_manifests (same status as its
`input_schema` sibling). Manually check each QUALITY_GATES.md gate against the
produced artifact:
1. [ ] YAML parses without error
2. [ ] id matches `p06_fm_` prefix
3. [ ] sections list and fields list are both non-empty
4. [ ] each field has name, kind (one of the 14 closed values), and section
5. [ ] quality is null
6. [ ] every `publish` rule names a `label`; multi-field rules name `companions`

## Honesty Note
The reference source files (`types.ts`, `handlers.ts`) cite `docs/specs/02_products_admin/{spec,plan}.md`
(FR-001/FR-002/FR-011) as their originating spec. That path does NOT exist in this
Central repo (`docs/specs/` here contains only `04_bootstrap_orchestrator` through
`10_multitenant_100` plus `compiled/`) -- confirmed via directory listing. This mirrors
the dangling `spec_version` pattern the parent triage flagged for other kinds
(`canonical_product`/`tenant_voice_profile`'s `01_ads_catalog`): the cited spec lives
in the separate reference commerce app / an earlier project phase, not here. Harmless
to this kind's realness (established independently by the code + the live test file),
but worth knowing before citing that path as if it resolves in this repo.

## Metadata

```yaml
id: bld_tools_field_manifest
pipeline: 8F
scoring: hybrid_3_layer
```

```bash
python _tools/cex_score.py --apply bld-tools-field-manifest.md
```

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[bld_tools_input_schema]] | sibling | 0.58 |
| [[bld_tools_type_def]] | sibling | 0.54 |
| [[bld_tools_supabase_data_layer]] | sibling | 0.50 |
| [[bld_tools_interface]] | sibling | 0.42 |
| [[bld_tools_validation_schema]] | sibling | 0.40 |
