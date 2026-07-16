---
kind: schema
id: bld_schema_field_manifest
pillar: P06
llm_function: CONSTRAIN
purpose: Formal schema -- SINGLE SOURCE OF TRUTH for field_manifest
pattern: TEMPLATE derives from this. CONFIG restricts this.
quality: null
title: "Schema Field Manifest"
version: "1.0.0"
author: n03_builder
tags: [field_manifest, builder, examples]
tldr: "Golden and anti-examples for field_manifest construction, demonstrating the schema-to-form derivation mold and its common drift pitfalls."
domain: "field manifest construction"
created: "2026-07-03"
updated: "2026-07-03"
8f: "F1_constrain"
keywords: [formal schema, field manifest construction, schema field manifest, field_manifest, builder, examples, "id pattern", regex, sections and fields, publish gate rules, frontmatter fields]
density_score: 0.88
related:
  - bld_schema_input_schema
  - bld_schema_type_def
  - bld_schema_unit_eval
  - bld_schema_smoke_eval
  - bld_architecture_field_manifest
---

# Schema: field_manifest
## Frontmatter Fields
| Field | Type | Required | Default | Notes |
|-------|------|----------|---------|-------|
| id | string (p06_fm_{{slug}}) | YES | - | Namespace compliance |
| kind | literal "field_manifest" | YES | - | Type integrity |
| pillar | literal "P06" | YES | - | Pillar assignment |
| version | semver string | YES | "1.0.0" | Versioning |
| created | date YYYY-MM-DD | YES | - | Creation date |
| updated | date YYYY-MM-DD | YES | - | Last update |
| author | string | YES | - | Producer identity |
| scope | string | YES | - | Which entity/editor this manifest serves |
| sections | list[SectionDef] | YES | - | Ordered section groupings (min 1) |
| fields | list[FieldDef] | YES | - | Field definitions (min 1) |
| publish_gate | list[PublishRule bound to a field] | REC | [] | Publish-transition rules |
| depends_on | list[string] | YES | [input_schema, type_def, supabase_data_layer] | Fixed per kinds_meta.json |
| domain | string | YES | - | Manifest domain |
| quality | null | YES | null | Never self-score |
| tags | list[string], len >= 3 | YES | - | Must include "field-manifest" |
| tldr | string <= 160ch | YES | - | Dense summary |
| keywords | list[string] | REC | - | Brain search terms |
| density_score | float 0.80-1.00 | REC | - | Content density |
## SectionDef Object
```yaml
sections:
  - id: "identity"
    title: "Identidade"
```
Each section MUST have: `id` (stable, referenced by `FieldDef.section`), `title`
(human heading). Order in the list IS the render order (per the reference
`ManifestForm.tsx`, which groups `manifest.fields` by `manifest.sections` order).
## FieldDef Object
```yaml
fields:
  - name: "name"
    label: "Nome do Produto"
    kind: "text"
    section: "identity"
    required: true
    min: 3
    max: 100
    placeholder: "Ex: Cama Donut Premium"
    default: null
    helpText: null
    tenantParam: false
```
Each field MUST have: `name`, `label`, `kind`, `section`. Optional: `placeholder`,
`required`, `min`, `max`, `options` (for `kind: select`), `numbered` (render-only,
`orderedArray` only), `default`, `helpText`, `publish`, `tenantParam`.
`kind` MUST be one of the 14 closed values: `text`, `textarea`, `number`, `slug`,
`price`, `tags`, `stringArray`, `orderedArray`, `faq`, `images`, `mediaKit`, `select`,
`keyValue`, `boolean` (per the reference `FieldKind` union in `types.ts` -- an
unmapped kind is a defect, not a style choice: the reference `buildSchema.ts`
`coreTypeFor()` throws via an exhaustiveness guard on any kind outside this set).
## PublishRule Object (attached to a field via `field.publish`, or listed under `publish_gate`)
```yaml
publish:
  rule: "minCount"
  threshold: 3
  label: "benefícios funcionais"
  companions: []
```
`rule` MUST be one of: `minCount` (list/FAQ-pair count >= `threshold`), `minLength`
(trimmed string length >= `threshold`), `present` (any non-empty value, `threshold`
ignored), `positive` (numeric > 0 for this field AND every field named in
`companions`, `threshold` ignored). `label` is the short human string shown in a
"missing to publish" checklist; it is REQUIRED regardless of rule.
## ID Pattern
Regex: `^p06_fm_[a-z][a-z0-9_]+$`
Rule: id MUST equal filename stem.
## Body Structure (required sections)
1. `## Contract Definition` -- which entity/editor this manifest serves
2. `## Sections` -- table with id/title, in render order
3. `## Fields` -- table with name/kind/section/required/default/description
4. `## Publish Gate` -- table with field/rule/threshold/label/companions (may be empty if nothing gates publish)
5. `## Examples` -- at least one valid field object and one valid publish-rule object
## Constraints
- max_bytes: 8192 (body only) -- per `kinds_meta.json`
- naming: `p06_fm_{{slug}}.md`
- machine_format: yaml/json (compiled form)
- id == filename stem
- sections list MUST have at least 1 entry; fields list MUST have at least 1 entry
- each field MUST have name, kind (one of the 14 closed values), and section
- each field.section MUST reference an id present in sections
- multi-field publish rules (`positive` spanning >1 field) MUST declare `companions` explicitly
- quality: null always
- depends_on: input_schema, type_def, supabase_data_layer (fixed by kinds_meta.json -- do not add or remove without a kinds_meta.json edit, which is out of scope for a builder)
- field_manifest is DERIVATIONAL -- schema + publish-gate + rendered form all come from the SAME sections+fields list, never authored independently of each other

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[bld_schema_input_schema]] | sibling | 0.52 |
| [[bld_schema_type_def]] | sibling | 0.48 |
| [[bld_schema_unit_eval]] | sibling | 0.34 |
| [[bld_schema_smoke_eval]] | sibling | 0.33 |
| [[bld_architecture_field_manifest]] | downstream | 0.32 |
