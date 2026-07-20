---
id: kc_field_manifest
kind: knowledge_card
8f: F3_inject
primary_8f: F1_constrain
type: kind
pillar: P06
title: "Field Manifest -- Deep Knowledge for field_manifest"
version: 1.0.0
created: 2026-07-03
updated: 2026-07-03
author: n03_engineering
domain: field_manifest
quality: null
tags: [field_manifest, P06, CONSTRAIN, kind-kc]
tldr: "Declarative product-editor description (sections + typed fields) from which the zod schema, publish-gate, and rendered form are ALL derived -- no drift, app-logic pluggable via a handler registry."
when_to_use: "Building, reviewing, or reasoning about field_manifest artifacts -- or any admin/editor surface where validation, a publish gate, and a rendered form risk drifting apart."
keywords: [field-manifest, schema-to-form, publish-gate, sections, fields, handler-registry, product-editor]
feeds_kinds: [field_manifest]
density_score: null
related:
  - p01_kc_input_schema
  - p01_kc_type_def
  - kc_fabrication_manifest
  - input-schema-builder
  - field-manifest-builder
---

# Field Manifest

## Spec
```yaml
kind: field_manifest
pillar: P06
llm_function: CONSTRAIN
max_bytes: 8192
naming: p06_fm_{{slug}}.md
core: false
depends_on: [input_schema, type_def, supabase_data_layer]
```

## What It Is
A declarative product-editor description -- ordered sections + ordered typed fields
-- from which THREE things derive with zero drift: a zod validation schema, a
publish-transition gate, and a rendered form. ISO = `FieldDef`/`SectionDef`/
`ProductManifest` (per `kinds_meta.json`'s boundary text, mirroring the real
`apps/dashboard_web/lib/field-manifest/types.ts` interfaces). NOT `input_schema`
(single unilateral data-validation schema, no UI/gate derivation). NOT `interface`
(bilateral integration contract). NOT `type_def` (single abstract, unrendered type).

Upstream source: "the reference commerce app's field-manifest (proving ground)" per
`kinds_meta.json`. FIRST instance in this repo: `.../field-manifest/productManifest.ts`
(564 lines, 14 sections, ~50 fields) -- self-declares this identity in its own header.

## Cross-Framework Map
| Framework | Concept | Notes |
|---|---|---|
| Zod | `.superRefine()` on `z.object()` | The publish gate: cross-field checks over the base shape |
| React Hook Form | `Controller` + typed defaults | Every field seeded typed-empty from first render |
| Django | `ModelForm` | One model drives validation AND widget rendering |
| Retool / Forest Admin | Schema-driven admin UI | Section+field list literally IS the admin surface |
| GoF Strategy/Plugin | Behavior injected by key | `HandlerRegistry`: `(field_kind, tenant) -> FieldHandlers \| undefined` |

## Real Implementation (this Central repo)
| Module | Role |
|--------|------|
| `lib/field-manifest/types.ts` | `FieldKind` (14-member closed union), `PublishRule`, `FieldDef`, `SectionDef`, `ProductManifest` |
| `lib/field-manifest/buildSchema.ts` | `buildSchema(manifest)` -> `{baseSchema, schema, updateSchema, publishRequirements}` -- the derivation keystone |
| `lib/field-manifest/renderers.tsx` + `ManifestForm.tsx` | `FieldKind -> Renderer` registry; layout groups fields by section |
| `lib/field-manifest/handlers.ts` | `HandlerRegistry`, `inertHandlerRegistry` (safe default: inert no-ops), `AI_FORBIDDEN_CHANNEL_FIELDS` |
| `lib/field-manifest/productManifest.ts` | The FIRST field_manifest instance |
| `components/ManifestEntityForm.tsx` | Live mount: manifest -> RHF -> hand-resolved zod -> `ApiClient.createEntity` |
| `app/dashboard/data/[entity]/new/page.tsx` | Route mounting `<ManifestEntityForm>` with `productManifest` |
| `__tests__/manifest-mount.test.tsx` | Vitest/RTL suite (read, NOT executed this session -- no Node invoked) |

## Key Parameters
| Field | Type | Default | Note |
|---|---|---|---|
| `sections` | `SectionDef[]` | required, min 1 | Order = render order |
| `fields` | `FieldDef[]` | required, min 1 | name/label/kind/section + optional required/min/max/options/default/helpText/publish/tenantParam |
| `kind` (per field) | 1 of 14 closed `FieldKind` | required | Exhaustiveness-guarded: unmapped kind throws, never silently degrades |
| `publish` (per field) | `PublishRule \| undefined` | ungated | `minCount`/`minLength`/`present`/`positive`, optional `companions` |
| `tenantParam` | boolean | false | Doc-only flag for a future distiller; never changes behavior |

## Patterns
| Pattern | When | Example |
|---|---|---|
| Multi-field gate via `companions` | Gate spans >1 field, 1 error location | `dim_length_cm` (`positive`) lists `companions: [dim_width_cm, dim_height_cm]` |
| `tenantParam: true` | Field VALUE is tenant-specific content | `why_it_works`, `benefits_emotional`, `margem_b2c/b2b` |
| Inert-by-default registry | Mount with zero tenant behavior bound | `inertHandlerRegistry = () => undefined` -- degrades safely, never crashes |
| Base-vs-refined zod split | Gate-free partial update alongside gated create | `updateSchema` derives from `baseSchema`, NEVER from the gated `schema` |

## Anti-Patterns
| Anti-Pattern | Why It Fails | Fix |
|---|---|---|
| Tenant literals in the generic core | Breaks "swap only the manifest" minting model | Tenant data lives only in the instance file (e.g. `productManifest.ts`) |
| `.superRefine()` before `.partial()` | Resulting `ZodEffects` has no `.partial()`/`.extend()` | Derive `updateSchema` from `baseSchema`, never the gated `schema` |
| Multi-field gate, no `companions` | Error maps to 1 field; others fail invisibly | Name every co-dependent field in `companions` |
| Hardcoded behavior inline | Couples app-logic to the declarative layer | Route through `HandlerRegistry`, keyed by `(field_kind, tenant)` |

## Integration Graph
```
[input_schema] --sibling_contrast--> [field_manifest] <--sibling_contrast-- [type_def]
[field_manifest.sections+fields] --derives--> {schema, publishRequirements, rendered form}
[field_manifest.fields[].kind]   --keys-->    HandlerRegistry -> FieldHandlers
[supabase_data_layer] <--persists-- [field_manifest] (via ApiClient.createEntity)
```

## Decision Tree
- IF one source must derive schema + publish-gate + form together THEN `field_manifest`
- IF only a single unilateral validation schema, no UI/gate derivation THEN `input_schema`
- IF a bilateral integration contract THEN `interface`
- IF only a single abstract, unrendered type THEN `type_def`
- DEFAULT: `field_manifest` for admin/editor surfaces where validation/gate/UI drift is the risk

## Quality Criteria
- GOOD: sections+fields ordered, non-empty; every field has name/label/kind/section
- GREAT: publish rules companion-aware; tenantParam complete; handler-seam needs documented per field
- FAIL: tenant literals in core files; `kind` outside the closed set; a gate that silently passes on an omitted companion

## Honesty Note
`types.ts`/`handlers.ts` cite `docs/specs/02_products_admin/` (FR-001/002/011) as their
spec -- that path does not exist in this repo (only `04_bootstrap_orchestrator`
through `10_multitenant_100` do). The cited spec lives in the reference commerce app,
not here -- same dangling pattern the parent triage flagged for `01_ads_catalog`
(Sec 3.3). Harmless to this kind's realness (established by code + the live test).

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[p01_kc_input_schema]] | sibling | 0.44 |
| [[p01_kc_type_def]] | sibling | 0.40 |
| [[input-schema-builder]] | related | 0.30 |
| [[field-manifest-builder]] | downstream | 0.30 |
