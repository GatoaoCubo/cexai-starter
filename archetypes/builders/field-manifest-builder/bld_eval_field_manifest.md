---
kind: quality_gate
id: p11_qg_field_manifest
pillar: P11
llm_function: GOVERN
purpose: Golden and anti-examples of field_manifest artifacts
pattern: few-shot learning -- LLM reads these before producing
quality: null
title: "Gate: Field Manifest"
version: "1.0.0"
author: "builder_agent"
tags: [quality-gate, field-manifest, schema-to-form, publish-gate, sections, fields]
tldr: "Gates ensuring field_manifest artifacts declare complete, typed sections+fields from which a schema, a publish gate, and a rendered form derive without drift."
domain: "field_manifest -- declarative schema-to-form derivation mold"
created: "2026-07-03"
updated: "2026-07-03"
8f: "F7_govern"
keywords: [publish gate, field manifest, schema-to-form, quality-gate, field-manifest, sections, fields]
density_score: 0.87
related:
  - bld_instruction_field_manifest
  - bld_schema_field_manifest
  - bld_knowledge_card_field_manifest
  - p11_qg_input_schema
  - p10_lr_field_manifest_builder
---
## Quality Gate

# Gate: Field Manifest
## Definition
| Field     | Value |
|-----------|-------|
| metric    | weighted soft score + all hard gates pass |
| threshold | 7.0 to publish; 8.0 for pool; 9.5 for golden |
| operator  | AND (all hard) + weighted average (soft) |
| scope     | any artifact with `kind: field_manifest` |
## HARD Gates
All must pass. Any failure = immediate reject.
| ID  | Check | Fail Condition |
|-----|-------|----------------|
| H01 | Frontmatter parses as valid YAML | Parse error on any field |
| H02 | ID matches `^p06_fm_[a-z][a-z0-9_]+$` | Uppercase, spaces, leading digit, or wrong prefix |
| H03 | ID equals filename stem | `id: p06_fm_products` in file `p06_fm_catalog.md` |
| H04 | Kind equals literal `field_manifest` | Any other kind value |
| H05 | Quality field is `null` | Any non-null value |
| H06 | sections list and fields list each have >= 1 entry | Either list empty or missing |
| H07 | Every field has name, kind (one of the 14 closed FieldKind values), and section; every field.section resolves to a declared section id | Missing key, unknown kind value, or dangling section reference |
## SOFT Scoring
Total weights sum to 100%.
| ID  | Dimension | Weight | 10 pts | 5 pts | 0 pts |
|-----|-----------|--------|--------|-------|-------|
| S01 | FieldKind precision | 1.0 | Every field uses one of the 14 closed kinds; none use a freeform/unlisted kind | Mostly closed-set, 1-2 ambiguous | Freeform kinds or `any` used |
| S02 | Publish-gate completeness | 1.0 | Every publish-critical field carries an explicit `publish` rule with `label` | Some publish-critical fields ungated | No publish gate documented at all |
| S03 | Multi-field gate honesty | 1.0 | Multi-field `positive` gates declare `companions` explicitly, mapping one error to one field | Companions implied but not listed | Multi-field gate collapsed into one field silently, others fail invisibly |
| S04 | tenantParam hygiene | 0.5 | Every tenant-specific-VALUE field flagged `tenantParam: true` | Some flagged, some missed | No tenant/generic distinction made |
| S05 | Handler-seam documentation | 1.0 | Every field needing upload/autoCalc/aiAssist names the handler and tenant-bound status | Handler needs mentioned but not per-field | No handler-seam section at all |
| S06 | Examples | 1.0 | At least 2 complete examples (one field object, one publish-rule object) | One example present | No examples |
**Score = sum(pts * weight) / sum(max_pts * weight) * 10**
## Actions
| Score | Tier | Action |
|-------|------|--------|
| >= 9.5 | Golden | Publish to pool as golden field-manifest contract |
| >= 8.0 | Skilled | Publish to pool + log pattern |
| >= 7.0 | Learning | Use but flag for improvement |
| < 7.0 | Rejected | Return to author with gate report |
## Bypass
| Field | Value |
|-------|-------|
| Conditions | Editor is mid-design and the field set is not yet stable; manifest explicitly marked `draft` |
| Approver | Owner agent lead |
| Audit trail | `bypass_reason` + `draft: true` both required in frontmatter |
| Expiry | Draft status expires after 14 days; must reach H-gate compliance or be deprecated |

## Examples

# Examples: field-manifest-builder
## Golden Example
INPUT: "Descreva o field_manifest do editor de produtos -- identidade, midia e o gate de publicacao"
OUTPUT:
```yaml
id: p06_fm_products
kind: field_manifest
pillar: P06
version: "1.0.0"
created: "2026-07-03"
updated: "2026-07-03"
author: "builder_agent"
scope: "products entity editor"
sections:
  - id: "identity"
    title: "Identidade"
  - id: "media"
    title: "Mídia"
fields:
  - name: "name"
    label: "Nome do Produto"
    kind: "text"
    section: "identity"
    required: true
    min: 3
    max: 100
    tenantParam: false
  - name: "images"
    label: "Imagens e Vídeos"
    kind: "images"
    section: "media"
    required: true
    max: 9
    tenantParam: false
publish_gate:
  - field: "dim_length_cm"
    rule: "positive"
    label: "as dimensões numéricas (comprimento, largura e altura em cm, cada uma maior que zero)"
    companions: ["dim_width_cm", "dim_height_cm"]
depends_on: [input_schema, type_def, supabase_data_layer]
domain: "product-editor"
quality: null
tags: [field-manifest, products, P06]
tldr: "Product editor field manifest: identity + media sections, dims publish gate spans 3 fields."
density_score: 0.88
```
## Contract Definition
The `products` entity editor. Fields group under 14 sections in the reference
instance (`productManifest.ts`); this excerpt shows 2. The dims publish gate is a
3-field `positive` check (length/width/height) mapped to a single error on
`dim_length_cm` via `companions`.
## Sections
| # | ID | Title |
|---|----|----|
| 1 | identity | Identidade |
| 2 | media | Mídia |
## Fields
| # | Name | Kind | Section | Required | Description |
|---|------|------|---------|----------|-------------|
| 1 | name | text | identity | YES | Product name, 3-100 chars |
| 2 | images | images | media | YES | Cover + up to 9 media files |
## Publish Gate
| Field | Rule | Companions |
|-------|------|------------|
| dim_length_cm | positive | dim_width_cm, dim_height_cm |
WHY THIS IS GOLDEN:
- quality: null (H05 pass)
- id matches p06_fm_ pattern (H02 pass)
- kind: field_manifest (H04 pass)
- sections + fields non-empty, every field has name/kind/section (H06/H07 pass)
- multi-field gate names companions explicitly (S03 = 10pts)

### S_RELATED: Cross-Reference Check (SOFT)
- [ ] `related:` frontmatter field populated (3-15 entries)
- [ ] `## Related Artifacts` section present in artifact body
- [ ] At least 1 upstream and 1 downstream reference
- Penalty: -0.3 if empty (does not block, encourages wiring)

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[bld_instruction_field_manifest]] | sibling | 0.44 |
| [[bld_schema_field_manifest]] | sibling | 0.42 |
| [[bld_knowledge_card_field_manifest]] | sibling | 0.40 |
| [[p11_qg_input_schema]] | related | 0.36 |
| [[p10_lr_field_manifest_builder]] | downstream | 0.33 |
