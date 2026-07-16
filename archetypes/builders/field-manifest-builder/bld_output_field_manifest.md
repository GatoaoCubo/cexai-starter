---
kind: output_template
id: bld_output_template_field_manifest
pillar: P05
llm_function: PRODUCE
purpose: Template with {{vars}} that the LLM fills to produce a field_manifest
pattern: every field here exists in SCHEMA.md -- template derives, never invents
quality: null
title: "Output Template Field Manifest"
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
8f: "F6_produce"
keywords:
  - "template with"
  - "field manifest construction"
  - "output template field manifest"
  - "field_manifest"
  - "builder"
  - "examples"
  - "## sections"
  - "## fields"
  - "## publish gate"
  - "{{slug}}"
density_score: 0.88
related:
  - bld_schema_field_manifest
  - bld_output_template_input_schema
  - p10_lr_field_manifest_builder
  - bld_instruction_field_manifest
  - bld_schema_input_schema
---
# Output Template: field_manifest
```yaml
id: p06_fm_{{slug}}
kind: field_manifest
pillar: P06
version: "1.0.0"
created: "{{YYYY-MM-DD}}"
updated: "{{YYYY-MM-DD}}"
author: "{{who_produced}}"
scope: "{{what_entity_or_editor_this_serves}}"
sections:
  - id: "{{section_id_1}}"
    title: "{{section_title_1}}"
  - id: "{{section_id_2}}"
    title: "{{section_title_2}}"
fields:
  - name: "{{field_name}}"
    label: "{{human_label}}"
    kind: "{{text|textarea|number|slug|price|tags|stringArray|orderedArray|faq|images|mediaKit|select|keyValue|boolean}}"
    section: "{{section_id}}"
    required: {{true|false}}
    min: {{min_or_null}}
    max: {{max_or_null}}
    default: {{default_or_null}}
    helpText: "{{helper_text_or_null}}"
    tenantParam: {{true|false}}
  - name: "{{field_name_2}}"
    label: "{{human_label_2}}"
    kind: "{{kind}}"
    section: "{{section_id}}"
    required: {{true|false}}
publish_gate:
  - field: "{{gated_field_name}}"
    rule: "{{minCount|minLength|present|positive}}"
    threshold: {{threshold_or_null}}
    label: "{{checklist_label}}"
    companions: [{{other_field_names_or_empty}}]
depends_on: [input_schema, type_def, supabase_data_layer]
domain: "{{manifest_domain}}"
quality: null
tags: [field-manifest, {{scope_tag}}, {{domain_tag}}]
tldr: "{{dense_summary_max_160ch}}"
density_score: {{0.80_to_1.00}}
```
## Contract Definition
`{{what_entity_this_editor_serves_and_which_fields_gate_publish}}`
## Sections
| # | ID | Title |
|---|----|----|
| 1 | {{section_id}} | {{section_title}} |
| 2 | {{section_id}} | {{section_title}} |
## Fields
| # | Name | Kind | Section | Required | Default | Description |
|---|------|------|---------|----------|---------|-------------|
| 1 | {{name}} | `{{kind}}` | {{section}} | {{Y/N}} | `{{default}}` | `{{helpText}}` |
| 2 | {{name}} | `{{kind}}` | {{section}} | {{Y/N}} | `{{default}}` | `{{helpText}}` |
## Publish Gate
| Field | Rule | Threshold | Label | Companions |
|-------|------|-----------|-------|------------|
| {{field}} | `{{rule}}` | {{threshold}} | {{label}} | {{companions_or_none}} |
## Handler Seam (documented need, not implementation)
| Field | Handler Needed | Tenant-bound? |
|-------|----------------|----------------|
| {{field}} | `{{upload\|cleanupOrphans\|autoCalc\|aiAssist}}` | {{Y/N}} |
## Tenant Fields (tenantParam: true)
| Field | Why tenant-specific |
|-------|---------------------|
| {{field}} | {{reason}} |
## Examples
```json
{{one_valid_field_object}}
```
```json
{{one_valid_publish_rule_object}}
```
## References
1. `{{reference_1}}`
2. `{{reference_2}}`

## Template Standards

1. Define all required sections for this output kind
2. Include frontmatter schema with mandatory fields
3. Provide structural markers for post-validation
4. Specify format constraints for markdown YAML JSON
5. Reference the input_schema/type_def/supabase_data_layer dependencies explicitly

## Properties

| Property | Value |
|----------|-------|
| Kind | `output_template` |
| Pillar | P05 |
| Domain | field manifest construction |
| Pipeline | 8F (F1-F8) |
| Scorer | cex_score.py |
| Compiler | cex_compile.py |
| Retriever | cex_retriever.py |
| Quality target | 9.0+ |
| Density target | 0.85+ |

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[bld_schema_field_manifest]] | downstream | 0.39 |
| [[bld_output_template_input_schema]] | sibling | 0.37 |
| [[p10_lr_field_manifest_builder]] | downstream | 0.33 |
| [[bld_instruction_field_manifest]] | upstream | 0.30 |
| [[bld_schema_input_schema]] | sibling | 0.28 |
