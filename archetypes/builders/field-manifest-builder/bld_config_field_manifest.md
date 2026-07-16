---
kind: config
id: bld_config_field_manifest
pillar: P09
llm_function: CONSTRAIN
purpose: Naming conventions, file paths, size limits, operational constraints
pattern: CONFIG restricts SCHEMA, never contradicts it
effort: medium
max_turns: 25
disallowed_tools: []
fork_context: null
hooks:
  pre_build: null
  post_build: null
  on_error: null
  on_quality_fail: null
permission_scope: nucleus
quality: null
title: "Config Field Manifest"
version: "1.0.0"
author: n03_builder
tags: [field_manifest, builder, examples]
tldr: "Golden and anti-examples for field_manifest construction, demonstrating the schema-to-form derivation mold and its common drift pitfalls."
domain: "field manifest construction"
created: "2026-07-03"
updated: "2026-07-03"
8f: "F1_constrain"
keywords: [naming conventions, file paths, size limits, operational constraints, field manifest construction, config field manifest, field_manifest, builder, examples, "p06_fm_{{slug}}.md"]
density_score: 0.87
related:
  - bld_schema_field_manifest
  - bld_config_input_schema
  - bld_config_type_def
  - bld_config_supabase_data_layer
---
# Config: field_manifest Production Rules
## Naming Convention
| Scope | Convention | Example |
|-------|-----------|---------|
| Artifact files | `p06_fm_{{slug}}.md` | `p06_fm_products.md` |
| Builder directory | kebab-case | `field-manifest-builder/` |
| Frontmatter fields | snake_case | `tenant_param`, `publish_gate` |
| Scope slugs | snake_case, lowercase | `products`, `catalog_entry` |
Rule: id MUST equal filename stem.
## File Paths
1. Output: `cex/P06_schema/examples/p06_fm_{{slug}}.md`
2. Compiled: `cex/P06_schema/compiled/p06_fm_{{slug}}.json`
3. Reference implementation this kind describes (read-only grounding, not an
   output path): `apps/dashboard_web/lib/field-manifest/`
## Size Limits (aligned with SCHEMA -- per kinds_meta.json)
1. Body: max 8192 bytes
2. Total: ~9000 bytes including frontmatter
3. Density: >= 0.80
## FieldKind Type Enum (14 closed values, per reference `types.ts`)
| Kind | Zod atom (buildSchema.ts) | Renderer family |
|------|---------------------------|-----------------|
| text | `z.string().trim()` (+min/max) | Input |
| textarea | `z.string().trim()` (+min/max) | Textarea |
| number | `z.coerce.number()` (+min/max) | number Input |
| slug | `slugSchema` (product.atoms.ts) | Input |
| price | `priceSchema` (product.atoms.ts) | number Input |
| tags | `textArraySchema` (+max) | TagInput |
| stringArray | `textArraySchema` (+max) | TagInput |
| orderedArray | `textArraySchema` (+max) | ArrayFieldEditor |
| faq | `faqSchema` | FAQEditor |
| images | `z.array(z.string().trim().min(1))` (+min/max) | ImageUploader |
| mediaKit | `z.array(mediaKitImageSchema)` (+max) | MediaKitUploader |
| select | `z.enum([...])` or `z.string()` if no options | Select |
| keyValue | `z.record(z.string(), z.unknown())` | AttributesEditor |
| boolean | `z.boolean()` (+default) | Switch/checkbox |
Adding a 15th kind requires extending BOTH the zod mapping and the renderer
registry -- the reference `coreTypeFor()` throws on an unmapped kind
(exhaustiveness guard); this builder must never describe a kind outside the 14
without flagging the extension as a two-sided change.
## Required vs Optional Policy
1. Required fields: MUST be provided by caller (or form), never carry a `default`
2. Optional fields: SHOULD carry a `default` appropriate to their kind (arrays
   default to `[]`, booleans to `false`, selects with a default use it, else
   `.optional()`)
3. No field can be both required AND carry a default (required means caller provides)
## Publish-Gate Config (fixed rule vocabulary, per reference `buildSchema.ts`)
| Rule | threshold used? | companions used? |
|------|-------------------|-------------------|
| minCount | YES (count >= threshold) | rarely |
| minLength | YES (trimmed length >= threshold) | rarely |
| present | NO (ignored) | rarely |
| positive | NO (ignored) | YES for multi-field numeric gates |
## depends_on (fixed by kinds_meta.json -- do not vary per-instance)
`input_schema`, `type_def`, `supabase_data_layer`

## Metadata

```yaml
id: bld_config_field_manifest
pipeline: 8F
scoring: hybrid_3_layer
```

```bash
python _tools/cex_score.py --apply bld-config-field-manifest.md
```

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[bld_schema_field_manifest]] | upstream | 0.42 |
| [[bld_config_input_schema]] | sibling | 0.38 |
| [[bld_config_type_def]] | sibling | 0.36 |
| [[bld_config_supabase_data_layer]] | sibling | 0.30 |
