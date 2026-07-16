---
kind: collaboration
id: bld_collaboration_field_manifest
pillar: P12
llm_function: COLLABORATE
purpose: How field-manifest-builder works in crews with other builders
pattern: each builder must know its ROLE in a team, what it RECEIVES and PRODUCES
quality: null
title: "Collaboration Field Manifest"
version: "1.0.0"
author: n03_builder
tags: [field_manifest, builder, examples]
tldr: "Golden and anti-examples for field_manifest construction, demonstrating the schema-to-form derivation mold and its common drift pitfalls."
domain: "field manifest construction"
created: "2026-07-03"
updated: "2026-07-03"
8f: "F8_collaborate"
keywords: [field manifest construction, collaboration field manifest, field_manifest, builder, examples, "### crew: product editor stack", my role, crew compositions, contract stack, schema-to-form]
density_score: 0.87
---
# Collaboration: field-manifest-builder
## My Role in Crews
I am a SPECIALIST. I answer ONE question: "what sections and fields make up this
editor, and what schema/gate/form all derive from them?"
I do not define single unilateral input contracts (input_schema). I do not define
abstract reusable types with no render/gate semantics (type_def). I do not implement
app-logic behavior (that is the HandlerRegistry, a separate runtime seam I describe
the NEED for but never the implementation of).
## Crew Compositions
### Crew: "Product Editor Stack"
```
  1. type-def-builder -> "abstract reusable shapes the fields may reference"
  2. input-schema-builder -> "single-purpose entry contracts for narrower operations"
  3. field-manifest-builder -> "the full schema-to-form derivation: sections + fields + publish gate"
  4. supabase-data-layer-builder -> "where the derived, validated payload persists"
```
### Crew: "Contract Stack" (adjacent to input-schema-builder's own crew)
```
  1. field-manifest-builder -> "derivational editor contract (schema + gate + form, ONE source)"
  2. input-schema-builder -> "unilateral input contract (fields, types, defaults) for a narrower operation"
  3. interface-builder -> "bilateral integration contract"
```
## Handoff Protocol
### I Receive
- seeds: entity/editor name, the sections it should group fields under, per-field
  kind/required/min/max/default/helpText, which fields gate publish and how
- optional: tenantParam flags, handler-seam needs (upload/autoCalc/aiAssist), any
  existing sibling manifest to diff against
### I Produce
- field_manifest artifact (.md + YAML frontmatter)
- committed to: `cex/P06/examples/p06_fm_{{slug}}.md`
### I Signal
- signal: complete (with quality score from QUALITY_GATES)
- if quality < 8.0: signal retry with failure reasons
## Builders I Depend On
| Builder | Why |
|---------|-----|
| input-schema-builder | `input_schema` is field_manifest's own `depends_on` sibling-by-contrast (narrower, single-purpose entry contracts a field_manifest's individual operations may still need) |
| type-def-builder | `type_def` is field_manifest's own `depends_on` sibling-by-contrast (abstract shapes a field's value may reference) |
| supabase-data-layer-builder | `supabase_data_layer` is field_manifest's own `depends_on` -- where the derived, validated payload is persisted (`ApiClient.createEntity`) |
## Builders That Depend On Me
| Builder | Why |
|---------|-----|
| (none registered yet) | field_manifest is newly scaffolded (this cell); no other builder in the taxonomy currently lists `field_manifest` in its own `depends_on` -- future admin/editor-shaped kinds may adopt it |
