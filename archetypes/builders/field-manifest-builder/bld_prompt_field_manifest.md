---
kind: instruction
id: bld_instruction_field_manifest
pillar: P03
llm_function: REASON
purpose: Step-by-step production process for field_manifest
pattern: 3-phase pipeline (research -> compose -> validate)
quality: null
title: "Instruction Field Manifest"
version: "1.0.0"
author: n03_builder
tags:
  - "field_manifest"
  - "builder"
  - "examples"
tldr: "Golden and anti-examples for field_manifest construction, demonstrating the schema-to-form derivation mold and its common drift pitfalls."
domain: "field manifest construction"
created: "2026-07-03"
updated: "2026-07-03"
8f: "F4_reason"
keywords:
  - "field manifest construction"
  - "instruction field manifest"
  - "field_manifest"
  - "builder"
  - "examples"
  - "p06_fm_[a-z][a-z0-9_]+"
  - "publish gate rules"
  - "handler registry"
  - "field kind"
  - "related artifacts"
density_score: 0.88
related:
  - bld_knowledge_card_field_manifest
  - bld_schema_field_manifest
  - p10_lr_field_manifest_builder
  - bld_instruction_input_schema
  - p11_qg_field_manifest
---
# Instructions: How to Produce a field_manifest
## Phase 1: RESEARCH
1. Identify the entity/editor this manifest serves -- name it explicitly (e.g. "products", the reference instance in `productManifest.ts`)
2. List every SECTION the editor groups fields under, in display order (the reference instance has 14: identity, media, short_description, detailed_content, benefits, specs, usage_care, faq, links, pricing, media_kit, stock_status, seo, marketplace_codes)
3. For each field: assign a stable `name` (matches the schema key + DB column + form name), a human `label`, and exactly one `kind` from the closed 14-member set (text, textarea, number, slug, price, tags, stringArray, orderedArray, faq, images, mediaKit, select, keyValue, boolean)
4. Classify each field as `required` or not; a required field never carries a `default`
5. For list-shaped fields (tags/stringArray/orderedArray/faq/images/mediaKit) decide a `max` item cap; for text/textarea/number decide `min`/`max` bounds
6. Identify which fields gate the PUBLISH transition (draft -> published) and assign each a `publish` rule: `minCount` (list length), `minLength` (trimmed string length), `present` (any non-empty value), or `positive` (numeric > 0); multi-field numeric gates (e.g. all of length/width/height positive) map to ONE field via `companions`
7. Flag any field whose VALUE is tenant-specific content (not just tenant-configured) with `tenantParam: true` -- documentation-only, read by a future distiller, never changes schema/render behavior
8. Identify which fields need app-logic behavior beyond declarative validation (image upload + orphan cleanup, price auto-calc from cost x margin, AI-assisted fill) -- these route through the HandlerRegistry seam, keyed by `(field_kind, tenant)`, NEVER hardcoded into the manifest
9. Check existing field_manifests via brain_query [IF MCP] or `Grep` for the same entity -- avoid duplicating an existing manifest
## Phase 2: COMPOSE
1. Read SCHEMA.md (`bld_schema_field_manifest.md`) -- source of truth for all frontmatter fields and the FieldDef/SectionDef/ProductManifest shapes
2. Read OUTPUT_TEMPLATE.md (`bld_output_field_manifest.md`) -- fill the template following SCHEMA constraints exactly
3. Fill frontmatter: id (`p06_fm_{{slug}}`), kind, pillar, version, created/updated, quality: null
4. Write the Sections list: ordered `{id, title}` pairs, matching what fields reference
5. Write the Fields section: one row per field with columns name / kind / section / required / min-max / default / publish-rule
6. Write the Publish Gate section: one row per field carrying a `publish` rule, its threshold/label, and any `companions`
7. Write the Handler Seam section: which fields need `upload`, `cleanupOrphans`, `autoCalc`, or `aiAssist` behavior, and which tenant context each needs (documentation of the NEED, not the implementation)
8. Write the Tenant Fields section: list every `tenantParam: true` field for the future distiller
9. Write the Examples section: at least one complete, valid field object and one complete, valid publish-rule object
10. Verify body is within 8192 bytes (per `kinds_meta.json` `max_bytes`)
## Phase 3: VALIDATE
1. Check QUALITY_GATES.md (`bld_eval_field_manifest.md`) -- apply each gate manually
2. HARD gates (all must pass):
   - YAML frontmatter parses without errors
   - id matches pattern `p06_fm_[a-z][a-z0-9_]+`
   - kind == field_manifest
   - sections list has at least one entry, fields list has at least one entry
   - every field entry has name, kind, and section; `kind` is one of the 14 closed values
   - quality == null
3. SOFT gates (score each against QUALITY_GATES.md):
   - every publish-gated field's rule is unambiguous (rule + threshold/label present)
   - multi-field gates declare `companions` explicitly (no silent multi-field coupling)
   - tenantParam fields are flagged, not left implicit
   - handler-seam needs are documented per field, not assumed
   - at least one complete field example and one complete publish-rule example present
4. Cross-check scope boundaries:
   - is this a DERIVATIONAL schema-to-form contract (schema + gate + render from ONE source), not a single data-validation schema (input_schema)?
   - not a bilateral integration contract (interface)?
   - not an abstract, unrendered type definition (type_def)?
   - does app-logic stay OUT of the manifest and live in the HandlerRegistry seam instead?
5. If score < 8.0: revise in the same pass before outputting

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[bld_knowledge_card_field_manifest]] | upstream | 0.40 |
| [[bld_schema_field_manifest]] | downstream | 0.36 |
| [[p10_lr_field_manifest_builder]] | downstream | 0.34 |
| [[bld_instruction_input_schema]] | sibling | 0.33 |
| [[p11_qg_field_manifest]] | downstream | 0.33 |
