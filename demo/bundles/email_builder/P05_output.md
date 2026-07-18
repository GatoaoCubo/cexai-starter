---
kind: output_template
id: bld_output_template_prompt_template
pillar: P00
quality: null
title: "Output Template Prompt Template"
version: "1.0.0"
author: n03_builder
tags: [prompt_template, builder, examples]
tldr: "Exemplos-modelo e antiexemplos para a construção de prompt template, demonstrando a estrutura ideal e as armadilhas mais comuns."
domain: "construção de prompt template"
created: "2026-04-07"
updated: "2026-04-07"
density_score: 0.90
llm_function: PRODUCE
related:
  - p03_ins_prompt_template
  - p11_qg_prompt_template
  - bld_output_template_reverse_prompt
  - bld_output_template_kind
  - bld_output_template_input_schema
  - bld_output_template_dataset_card
  - bld_output_template_visual_workflow
  - p11_qg_quality_gate
  - bld_eval_default
  - schema_prompt_template_builder
---

> Este é o esqueleto estrutural que todo artefato `prompt_template` produzido DEVE seguir.
> Os nomes de seção abaixo (Purpose, Variables Table, Template Body, Quality Gates, Examples)
> são o contrato de schema do kind `prompt_template` -- mantidos em inglês porque são a
> estrutura oficial que o gate de qualidade valida, não texto livre. Os placeholders
> `{{...}}` são preenchidos pelo builder no momento da produção do artefato real.

id: p03_pt_`{{topic_slug}}`
kind: prompt_template
pillar: P03
title: "`{{title}}`"
version: "`{{version}}`"
created: "`{{created}}`"
updated: "`{{updated}}`"
author: "`{{author}}`"
variables:
  - name: "`{{var_name_1}}`"
    type: "`{{var_type_1}}`"
    required: `{{var_required_1}}`
    default: "`{{var_default_1}}`"
    description: "`{{var_description_1}}`"
  - name: "`{{var_name_2}}`"
    type: "`{{var_type_2}}`"
    required: `{{var_required_2}}`
    default: "`{{var_default_2}}`"
    description: "`{{var_description_2}}`"
variable_syntax: "`{{variable_syntax}}`"
composable: `{{composable}}`
domain: "`{{domain}}`"
quality: `{{quality}}`
tags: [`{{tags}}`]
tldr: "`{{tldr}}`"
keywords: [`{{keywords}}`]
density_score: `{{density_score}}`
---

# `{{title}}`
## Purpose
`{{purpose_paragraph}}`
## Variables Table
| Name | Type | Required | Default | Description |
|---|---|---|---|---|
| `{{var_name_1}}` | `{{var_type_1}}` | `{{var_required_1}}` | `{{var_default_1}}` | `{{var_description_1}}` |
| `{{var_name_2}}` | `{{var_type_2}}` | `{{var_required_2}}` | `{{var_default_2}}` | `{{var_description_2}}` |
## Template Body
```
{{template_body}}
```
## Quality Gates
| Gate | Status | Notes |
|---|---|---|
| H01 id pattern | `{{h01_status}}` | `{{h01_notes}}` |
| H02 required fields | `{{h02_status}}` | `{{h02_notes}}` |
| H03 no undeclared vars | `{{h03_status}}` | `{{h03_notes}}` |
| H04 no unused vars | `{{h04_status}}` | `{{h04_notes}}` |
| H05 size <= 8192 bytes | `{{h05_status}}` | `{{h05_notes}}` |
| H06 valid syntax tier | `{{h06_status}}` | `{{h06_notes}}` |
| H07 var fields complete | `{{h07_status}}` | `{{h07_notes}}` |
| H08 body non-empty | `{{h08_status}}` | `{{h08_notes}}` |
## Examples
### Filled Example
**Variables:**
```yaml
{{example_variables}}
```
**Rendered Output:**
```
{{example_rendered_output}}
```


## Related Artifacts

| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[p03_ins_prompt_template]] | related | 0.32 |
| [[p11_qg_prompt_template]] | related | 0.30 |
| [[bld_output_template_reverse_prompt]] | sibling | 0.28 |
| [[bld_output_template_kind]] | sibling | 0.25 |
| [[bld_output_template_input_schema]] | sibling | 0.24 |
| [[bld_output_template_dataset_card]] | sibling | 0.24 |
| [[bld_output_template_visual_workflow]] | sibling | 0.24 |
| [[p11_qg_quality_gate]] | related | 0.22 |
| [[bld_eval_default]] | related | 0.21 |
| [[schema_prompt_template_builder]] | related | 0.21 |
