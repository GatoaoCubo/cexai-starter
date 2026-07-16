---
id: bld_schema_brandbook
kind: input_schema
pillar: P06
builder: brandbook-builder
version: 1.0.0
quality: null
title: Schema -- brandbook
author: n06_commercial
tags: [input_schema, brandbook, P06]
llm_function: CONSTRAIN
created: 2026-06-22
updated: 2026-06-22
related:
  - bld_architecture_document_loader
---

## Input Schema (MoldField[])

```yaml
input_contract:
  - key: brand_name
    type: text
    label: "Nome da marca"
    required: true
    placeholder: "ex. Nome da Marca, Loja Boutique, EmpresaX"

  - key: brand_essence
    type: text
    label: "Essencia da marca (1 frase)"
    required: false
    placeholder: "ex. Conforto premium para pets urbanos"

  - key: brand_materials
    type: file|url|text
    label: "Materiais da marca (PDF / logo / site / descricao)"
    required: false
    placeholder: "Envie PDF do brandbook existente, logo PNG, URL do site, ou descricao livre"
    note: >
      Cell A pre-processes:
        brand_materials_palette -> hex list extracted from logo/image
        brand_materials_text    -> text extracted from PDF/URL
        brand_materials_data_uri -> uploaded image as data-uri
```

## Field Mapping (generator internals)

| Input key | Generator field | Fallback |
|-----------|----------------|---------|
| brand_name | brand_name | [fornecer: nome da marca] |
| brand_essence | brand_essence | [fornecer: essencia] |
| brand_materials | materials_text (raw) | "" |
| brand_materials_text | materials_text (Cell A extracted) | "" |
| brand_materials_palette | colors list | [] |
| brand_materials_data_uri | produced_media["logo_primary"] | upload-fallback slot |

## Related Artifacts

| Artifact | Relationship | Score |
|----------|-------------|-------|
| p04_ct_distill | upstream | 0.16 |
| [[bld_architecture_document_loader]] | upstream | 0.16 |
| p06_is_env_contract_n05 | sibling | 0.16 |
