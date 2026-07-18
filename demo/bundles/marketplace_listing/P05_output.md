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
title: "Template: instância de marketplace_listing"
domain: marketplace_listing
quality: null
tags: [marketplace_listing, builder, template, output, P05]
tldr: "O formato exato que uma instância de marketplace_listing preenche: frontmatter + as 6 seções CONGELADAS + o JSON do ml_listing embutido, idêntico em estrutura à saída do capability generator em runtime."
density_score: 0.88
related:
  - bld_schema_marketplace_listing
  - bld_prompt_marketplace_listing
  - bld_eval_marketplace_listing
  - bld_config_marketplace_listing
  - output-validator-builder
---

# Template: instância de marketplace_listing
Preencha cada placeholder; mantenha o corpo <= 6144 bytes. Espelhe a amostra de runtime
`_output/g2_sample_listing.md` (uma execução real do capability generator, não uma
instância autorada por builder -- mesmo formato de seção, proveniência diferente).

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

## Seções do corpo (em ordem, TÍTULOS EXATOS -- 1:1 com as 6 output_sections do generator)
1. `# {{Name}}` + um parágrafo (produto + marketplace + intenção).
2. `## Listagem ML` (fields) -- Titulo, Marketplace, Categoria ID, Condicao ML, Tipo de
   anuncio, Moeda.
3. `## Preco e Estoque` (fields) -- Preco (R$), Estoque, SKU do vendedor, Marca.
4. `## Fotos` (list) -- um item por URL de foto, ou a linha honesta de estado vazio.
5. `## Atributos` (table) -- colunas `Atributo (id) | Valor`; quando injetado, BRAND é
   prependido (listado primeiro) e SELLER_SKU é anexado (listado por último), seguindo a
   mesma ordem do generator.
6. `## Descricao` (fields) -- Descricao completa.
7. `## Payload ML (pronto para publicar)` (fields) -- Produto interno, Fotos mapeadas,
   Atributos mapeados, JSON do anuncio (o ml_listing serializado, truncado em 900
   caracteres com "..." a partir desse tamanho).

Nota: a projeção DUAL-OUTPUT (`cex_dual_output.to_dual_output`, somente em runtime) anexa
uma 8ª seção `## Media` a partir do ledger de media_slots ao vivo -- uma instância autorada
por builder NÃO fabrica essa seção; os slots de mídia só são populados por uma execução
real de upload/pipeline de um tenant.

## Artefatos Relacionados
| Artefato | Relação | Pontuação |
|----------|-------------|-------|
| [[bld_schema_marketplace_listing]] | upstream | 0.55 |
| [[bld_prompt_marketplace_listing]] | sibling | 0.48 |
| [[bld_eval_marketplace_listing]] | downstream | 0.45 |
| [[bld_config_marketplace_listing]] | related | 0.4 |
| [[output-validator-builder]] | related | 0.36 |
