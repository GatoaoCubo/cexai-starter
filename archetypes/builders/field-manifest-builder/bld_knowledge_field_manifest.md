---
kind: knowledge_card
id: bld_knowledge_card_field_manifest
pillar: P01
llm_function: INJECT
purpose: Domain knowledge for field_manifest production -- the schema-to-form derivation mold
sources: React Hook Form + Zod (buildSchema.ts / superRefine), Django ModelForm, Rails ActiveAdmin, Retool/Forest Admin schema-driven admin generators, JSON Schema Form (react-jsonschema-form)
quality: null
title: "Knowledge Card Field Manifest"
version: "1.0.0"
author: n03_builder
tags: [field_manifest, builder, examples]
tldr: "Golden and anti-examples for field_manifest construction, demonstrating the schema-to-form derivation mold and its common drift pitfalls."
domain: "field manifest construction"
created: "2026-07-03"
updated: "2026-07-03"
8f: "F3_inject"
keywords: [schema-to-form derivation, field manifest construction, knowledge card field manifest, field_manifest, builder, examples, domain knowledge, executive summary, publish gate, handler registry, related artifacts]
density_score: 0.88
related:
  - bld_instruction_field_manifest
  - p10_lr_field_manifest_builder
  - field-manifest-builder
  - p11_qg_field_manifest
  - bld_schema_field_manifest
---
# Domain Knowledge: field_manifest
## Executive Summary
A field_manifest is a declarative product-editor description -- ordered sections plus
typed fields -- from which a validation schema, a publish-transition gate, and a
rendered form are ALL derived, so the three cannot drift apart. Rooted in the same
idea as Django's ModelForm (one model definition drives both validation and widget
rendering) and schema-driven admin generators (Retool, Forest Admin, react-jsonschema-form),
but adds a THIRD derived artifact most of those frameworks keep separate: an explicit
publish/transition gate, expressed as per-field rules rather than a hand-written
validator function. field_manifest differs from input_schema (a single unilateral
data-validation contract with no UI or gate derivation), interface (a bilateral
integration contract), and type_def (an abstract, unrendered structural type).
## Spec Table
| Property | Value |
|----------|-------|
| Pillar | P06 (contracts/schema) |
| Naming | `p06_fm_{{slug}}.md` |
| max_bytes | 8192 |
| depends_on | input_schema, type_def, supabase_data_layer |
| core | false |
| Derives | zod baseSchema + schema (gated) + updateSchema (partial) + publishRequirements + rendered form |
| Reference implementation | `apps/dashboard_web/lib/field-manifest/` (types.ts, buildSchema.ts, renderers.tsx, ManifestForm.tsx, handlers.ts, productManifest.ts) |
## Patterns
- **Closed FieldKind vocabulary (14 members)**: text, textarea, number, slug, price, tags, stringArray, orderedArray, faq, images, mediaKit, select, keyValue, boolean -- each maps to exactly one zod type AND exactly one renderer; an unmapped kind must THROW (exhaustiveness guard), never silently drop
| Source | Concept | Application |
|--------|---------|-------------|
| Zod | `.superRefine()` on a base object | The publish gate: extra cross-field validation layered on top of the base shape |
| React Hook Form | Controller + typed defaults | Every field seeded to a typed empty value, never `undefined`, from first render |
| Django ModelForm | One model -> form + validation | field_manifest adds a THIRD derived artifact: the publish gate |
| Retool / Forest Admin | Schema-driven admin UI | The section+field list IS the admin surface description |
| Strategy / Plugin pattern | Behavior injected by key, not hardcoded | HandlerRegistry: `(field_kind, tenant) -> FieldHandlers | undefined` |
- **Base-vs-refined split (the superRefine landmine)**: `baseSchema = z.object(...)` (a ZodObject, supports `.partial()`/`.extend()`); `schema = baseSchema.superRefine(gate)` (a ZodEffects, the publish-gated schema the live form uses); `updateSchema = baseSchema.partial().extend(...)` (gate-free partial). `.superRefine()` must NEVER be applied before `.partial()` is derived -- a ZodEffects loses `.partial()`/`.extend()`.
- **Publish-gate rule taxonomy (4 kinds)**: `minCount` (list/FAQ-pair count >= threshold), `minLength` (trimmed string length >= threshold), `present` (any non-empty value), `positive` (numeric > 0, optionally spanning `companions` fields so one error maps to one field for a multi-field gate, e.g. length+width+height all positive mapped to the length field)
- **tenantParam is documentation-only**: marking a field `tenantParam: true` (e.g. `why_it_works`, `benefits_emotional`, `margem_b2c`/`margem_b2b`, `indicacao_porte`) tells a future distiller which fields are tenant-specific FILL vs generic base -- it does NOT alter schema or render behavior
- **The one non-declarative seam**: `HandlerRegistry` resolves `FieldHandlers` (`upload`, `cleanupOrphans`, `autoCalc`, `aiAssist`) per `(field_kind, tenant)`. The default `inertHandlerRegistry` returns `undefined` for every pair -- so a generated editor renders and validates correctly with ZERO tenant behavior bound; controls degrade to inert no-ops rather than crashing
- **Grounding contract on AI-assist**: an `aiAssist` handler stages a diff for human review (HITL), and MUST NOT propose values for channel-link fields (`purchase_link`, `whatsapp_link`, `mercadolivre_link`) -- a hardcoded forbidden-field list enforces this at the seam, not inside the manifest
## Anti-Patterns
| Anti-Pattern | Why it fails |
|-------------|-------------|
| Tenant literals inside the generic core (types/buildSchema/renderers/ManifestForm) | Breaks the "swap only the manifest instance" minting model -- every tenant would need a core fork |
| `superRefine()` applied before `.partial()` | The resulting ZodEffects has no `.partial()`/`.extend()` -- the update schema cannot be derived |
| A multi-field publish gate with no `companions` | The error maps to only one field; the other required fields fail silently with no visible reason |
| Hardcoding upload/price-calc/AI behavior into the manifest | Couples app-logic to the declarative layer -- no per-tenant behavior swap without editing the manifest itself |
| A new FieldKind added without extending every consuming switch | Exhaustiveness guard should catch this at build/type-check time -- an anti-pattern is disabling or removing that guard |
| Treating field_manifest as an output validation layer (post-generation) | That is validation_schema's job, not field_manifest's -- field_manifest is input-editor-shaped, not output-shaped |
## Application
1. Identify scope: which entity/editor does this manifest serve? (reference: `products`)
2. Define sections: ordered groupings the form renders under
3. Define fields: name, kind (from the 14-member set), section, required/min/max/default
4. Attach publish rules: which fields gate the draft->published transition, and how
5. Flag tenant fields: `tenantParam: true` wherever the VALUE (not just config) is tenant-specific
6. Document handler-seam needs: which fields require upload, auto-calc, or AI-assist behavior (implementation lives elsewhere)
## References
- Zod: `.superRefine()`, `.partial()`, `.extend()` (zod docs)
- React Hook Form: Controller-based typed forms (react-hook-form docs)
- Django: ModelForm (docs.djangoproject.com)
- JSON Schema Form: react-jsonschema-form (rjsf-team)
- Reference implementation: `apps/dashboard_web/lib/field-manifest/{types,buildSchema,renderers,ManifestForm,handlers,productManifest}.ts`

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[bld_instruction_field_manifest]] | downstream | 0.48 |
| [[p10_lr_field_manifest_builder]] | downstream | 0.42 |
| [[field-manifest-builder]] | downstream | 0.40 |
| [[p11_qg_field_manifest]] | downstream | 0.36 |
| [[bld_schema_field_manifest]] | downstream | 0.34 |
