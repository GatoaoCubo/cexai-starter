---
id: bld_output_marketplace_listing
kind: response_format
pillar: P05
llm_function: PRODUCE
8f: F6_produce
version: 1.0.0
created: "2026-07-02"
updated: "2026-07-02"
author: n03_builder
title: "Template: marketplace_listing instance"
domain: marketplace_listing
quality: null
tags: [marketplace_listing, builder, template, output, P05]
tldr: "The exact shape a marketplace_listing instance fills: frontmatter + the 6 FROZEN sections + the embedded ml_listing JSON, byte-identical in structure to the runtime capability generator's output."
density_score: 0.88
related:
  - bld_schema_marketplace_listing
  - bld_prompt_marketplace_listing
  - bld_eval_marketplace_listing
  - bld_config_marketplace_listing
  - output-validator-builder
---

# Template: marketplace_listing instance
Fill every placeholder; keep body <= 6144 bytes. Mirror the runtime sample
`_output/g2_sample_listing.md` (a live capability-generator run, not a builder-authored
instance -- same section shape, different provenance).

## Frontmatter
```yaml
id: p05_ml_{{name}}
kind: marketplace_listing
pillar: P05
title: "{{Name}} -- {{one-line description}}"
version: 1.0.0
created: "{{date}}"
author: n03_builder
domain: marketplace-listing
marketplace: mercado_livre
sku: "{{seller_sku}}"
score: {{0.0-1.0}}
passed: {{true|false}}
missing_required: [{{...}}]
notes: [{{...}}]
real: true
quality: null
tags: [marketplace-listing, mercado-livre, {{category}}, P05]
tldr: "{{dense one-line summary}}"
related: [bld_schema_marketplace_listing, output-validator-builder]
```

## Body sections (in order, EXACT titles -- 1:1 with the generator's 6 output_sections)
1. `# {{Name}}` + one paragraph (product + marketplace + intent).
2. `## Listagem ML` (fields) -- Titulo, Marketplace, Categoria ID, Condicao ML, Tipo de
   anuncio, Moeda.
3. `## Preco e Estoque` (fields) -- Preco (R$), Estoque, SKU do vendedor, Marca.
4. `## Fotos` (list) -- one item per photo URL, or the honest empty-state line.
5. `## Atributos` (table) -- columns `Atributo (id) | Valor`; when injected, BRAND is
   prepended (listed first) and SELLER_SKU is appended (listed last), matching generator order.
6. `## Descricao` (fields) -- Descricao completa.
7. `## Payload ML (pronto para publicar)` (fields) -- Produto interno, Fotos mapeadas,
   Atributos mapeados, JSON do anuncio (the serialized ml_listing, truncated at 900 chars
   with "..." past that length).

Note: the DUAL-OUTPUT projection (`cex_dual_output.to_dual_output`, runtime-only) appends
an 8th `## Media` section from the live media_slots ledger -- a builder-authored instance
does NOT fabricate that section; media slots are populated only by a real tenant
upload/pipeline run.

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[bld_schema_marketplace_listing]] | upstream | 0.55 |
| [[bld_prompt_marketplace_listing]] | sibling | 0.48 |
| [[bld_eval_marketplace_listing]] | downstream | 0.45 |
| [[bld_config_marketplace_listing]] | related | 0.4 |
| [[output-validator-builder]] | related | 0.36 |
