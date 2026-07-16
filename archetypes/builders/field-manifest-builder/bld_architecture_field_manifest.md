---
kind: architecture
id: bld_architecture_field_manifest
pillar: P08
llm_function: CONSTRAIN
purpose: Component map of field_manifest -- inventory, dependencies, and architectural position
quality: null
title: "Architecture Field Manifest"
version: "1.0.0"
author: n03_builder
tags: [field_manifest, builder, examples]
tldr: "Golden and anti-examples for field_manifest construction, demonstrating the schema-to-form derivation mold and its common drift pitfalls."
domain: "field manifest construction"
created: "2026-07-03"
updated: "2026-07-03"
8f: "F1_constrain"
keywords: [component map of field_manifest, and architectural position, field manifest construction, architecture field manifest, field_manifest, builder, examples, component inventory, dependency graph, boundary table]
density_score: 0.88
related:
  - bld_knowledge_card_field_manifest
  - bld_architecture_input_schema
  - bld_architecture_type_def
  - field-manifest-builder
  - bld_instruction_field_manifest
---
## Component Inventory
| Name | Role | Owner | Status |
|------|------|-------|--------|
| sections | Ordered groupings the rendered form displays under | author | required |
| fields | Typed entries with kind/section/required/publish/tenantParam | author | required |
| field_kind | One of 14 closed widget/validation archetypes per field | author | required |
| publish_gate | Per-field rule (minCount/minLength/present/positive) gating draft->published | author | recommended |
| companions | Extra field names that must ALSO satisfy a shared multi-field gate | author | optional |
| tenant_param_flags | Documentation-only marker for tenant-specific VALUE fields | author | optional |
| handler_seam | Documented need for upload/cleanupOrphans/autoCalc/aiAssist per field | author | optional |
| depends_on | Fixed reference to input_schema, type_def, supabase_data_layer | kinds_meta.json | required |
## Dependency Graph
```
input_schema        --sibling_contrast--> field_manifest
type_def             --sibling_contrast--> field_manifest
supabase_data_layer  --persists--> field_manifest (fields map to DB columns via ApiClient.createEntity)
field_manifest.{sections,fields} --derives--> zod baseSchema/schema/updateSchema (buildSchema)
field_manifest.fields[].publish   --derives--> publishRequirements[] (buildSchema)
field_manifest.fields[].kind      --derives--> rendered form (FIELD_KIND_RENDERERS registry + ManifestForm)
field_manifest.fields[].kind      --keys--> HandlerRegistry (field_kind, tenant) -> FieldHandlers
```
| From | To | Type | Data |
|------|----|------|------|
| input_schema | field_manifest | sibling_contrast | field_manifest's own boundary text names input_schema as the "single data-validation schema, no UI/gate derivation" contrast |
| type_def | field_manifest | sibling_contrast | field_manifest's own boundary text names type_def as the "single type" contrast |
| supabase_data_layer | field_manifest | data_flow | `ApiClient.createEntity(entity, values)` persists the manifest-derived, zod-validated payload |
| field_manifest | zod schema (schema/baseSchema/updateSchema) | derivation | `buildSchema(manifest)` -- ONE call, ONE source, three derived schema shapes |
| field_manifest | publishRequirements | derivation | Built from every field carrying a `publish` rule; drives BOTH the zod `superRefine` gate AND the live UI checklist |
| field_manifest | rendered form | derivation | `ManifestForm` groups `fields` by `sections` order, dispatching each to `FIELD_KIND_RENDERERS[field.kind]` |
| field_manifest | HandlerRegistry | seam | App-logic behavior resolved by `(field.kind, tenant)`, NOT stored in the manifest itself |
## Boundary Table
| field_manifest IS | field_manifest IS NOT |
|-----------------|---------------------|
| A DERIVATIONAL contract: schema + gate + form ALL come from ONE field list | Three independently-authored artifacts that happen to agree today |
| A product/entity-EDITOR-shaped description (sections group fields for a UI) | A single unilateral data-validation contract with no UI/gate concern (that is input_schema) |
| Unidirectional-render + bidirectional-validate (renders AND validates from the same source) | A bilateral integration contract between two agents/services (that is interface) |
| Concrete, with 14 closed FieldKind archetypes each mapped to a real zod type + renderer | An abstract, unrendered structural type definition (that is type_def) |
| Declarative for WHAT a field is; app-logic (HOW it behaves) lives in a separate HandlerRegistry seam | A place to hardcode upload/pricing/AI behavior |
## Layer Map
| Layer | Components | Purpose |
|-------|------------|---------|
| Contract declaration | sections, fields, field_kind | Define the shape of the editor and its typed fields |
| Derivation | buildSchema (baseSchema/schema/updateSchema), publishRequirements | Turn ONE field list into validation + publish-gate, with no second source |
| Render | FIELD_KIND_RENDERERS registry, ManifestForm | Turn the SAME field list into a laid-out, section-grouped form |
| Behavior seam | HandlerRegistry, inertHandlerRegistry, AI_FORBIDDEN_CHANNEL_FIELDS | Pluggable, per-(field_kind, tenant) app-logic; safe-by-default when unbound |
| Consumers | ManifestEntityForm (live mount), ApiClient.createEntity, supabase_data_layer | Wire the derived schema + rendered form to a real submit path |

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[bld_knowledge_card_field_manifest]] | upstream | 0.40 |
| [[bld_architecture_input_schema]] | sibling | 0.39 |
| [[bld_architecture_type_def]] | sibling | 0.37 |
| [[field-manifest-builder]] | upstream | 0.36 |
| [[bld_instruction_field_manifest]] | upstream | 0.34 |
