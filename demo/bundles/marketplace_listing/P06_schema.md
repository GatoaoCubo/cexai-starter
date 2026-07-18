---
id: bld_schema_marketplace_listing
kind: schema
pillar: P06
llm_function: CONSTRAIN
8f: F1_constrain
version: 1.0.0
created: "2026-07-02"
updated: "2026-07-02"
author: n03_builder
title: "Schema: marketplace_listing"
domain: marketplace_listing
quality: null
tags: [marketplace_listing, builder, schema, channel-projection, P06]
tldr: "Fonte única da verdade para um marketplace_listing: frontmatter + as 6 seções CONGELADAS + o payload ml_listing embutido + os campos do gate de prontidão, espelhados 1:1 a partir do capability generator em produção."
density_score: 0.92
related:
  - marketplace-listing-builder
  - bld_output_marketplace_listing
  - bld_eval_marketplace_listing
  - bld_prompt_marketplace_listing
  - output-validator-builder
---

# Schema: marketplace_listing
Hierarquia de derivação: **SCHEMA (este) > TEMPLATE (bld_output) > CONFIG (bld_config)**.
Fundamentado no generator EM PRODUÇÃO `_tools/capability_generators/marketplace_listing.py`
(slug de capability registrado `marketplace_listing`) + seu espelho de frontend
`apps/dashboard_web/lib/molds.ts` (`MOLD_MARKETPLACE_LISTING`). `.cex/kinds_meta.json`
fornece naming/max_bytes/pillar; seu `upstream_source` declarado é uma camada de nível
mais baixo, com formato diferente (`_tools/cex_channel_adapter.py`) -- veja
[[bld_architecture_marketplace_listing]] para a reconciliação de vocabulário.

## Campos de Frontmatter (obrigatórios)
| Campo | Tipo | Notas |
|-------|------|-------|
| id | string `p05_ml_{name}` | igual ao nome do arquivo (sem extensão) |
| kind | literal `marketplace_listing` | integridade de tipo |
| pillar | literal `P05` | atribuição de pilar |
| title | string | "Nome -- descrição em uma linha" |
| version | semver | começa em 1.0.0 |
| marketplace | enum, padrão `mercado_livre` | único canal conectado em `CHANNEL_ADAPTERS` hoje |
| sku | string | o SKU do vendedor (G1) que este anúncio projeta |
| quality | null | nunca autoavaliar (a meta-qualidade do CEX -- distinta do `score` de prontidão abaixo) |
| tags | lista >=3 | inclui `marketplace-listing` |

## Campos do gate de prontidão (frontmatter -- espelha o próprio StructuredOutput do generator)
| Campo | Tipo | Notas |
|-------|------|-------|
| score | float 0.0-1.0 | começa em 1.0, deduzido por campo ausente/fraco, com piso em 0.0 |
| passed | bool | zero missing_required E score >= 0.70 |
| missing_required | lista | subconjunto apenas de `titulo_ml->title`, `categoria_ml->category_id`, `preco->price` |
| notes | list[str] | prefixadas com `[FAIL]`/`[WARN]`; nunca descartadas silenciosamente |
| real | bool | sempre `true` para uma instância autorada por builder (nunca o chip mock/simulado) |

## Seis seções CONGELADAS (todas obrigatórias, títulos + layout + ordem exatos)
| # | Título | Layout | Linhas/Colunas |
|---|-------|--------|--------------|
| 1 | Listagem ML | fields | Titulo, Marketplace, Categoria ID, Condicao ML, Tipo de anuncio, Moeda |
| 2 | Preco e Estoque | fields | Preco (R$), Estoque, SKU do vendedor, Marca |
| 3 | Fotos | list | um item por URL de foto (ou a string honesta de estado vazio) |
| 4 | Atributos | table | colunas [Atributo (id), Valor] |
| 5 | Descricao | fields | Descricao completa |
| 6 | Payload ML (pronto para publicar) | fields | Produto interno, Fotos mapeadas, Atributos mapeados, JSON do anuncio |

## Payload `ml_listing` embutido (espelha o corpo da API de Items do ML)
`title, category_id, price, currency_id (sempre BRL), available_quantity, condition
(new|used|refurbished), listing_type_id, description.plain_text, pictures[].url,
attributes[]{id,value_name} (BRAND + SELLER_SKU auto-injetados quando ausentes),
seller_custom_field`. Serializado (ASCII, truncado em 900 caracteres + `...`) no campo
`JSON do anuncio` da seção 6; os mesmos 4-6 desses campos são TAMBÉM restabelecidos de
forma legível nas seções 1-2 -- mantenha as duas representações consistentes. Sem bloco
`_meta` (isso pertence à OUTRA camada -- veja [[bld_architecture_marketplace_listing]]).

## Restrições
- max_bytes: 6144 (corpo); naming `p05_ml_{name}.md` (`.cex/kinds_meta.json`); machine_format md.
- id == nome do arquivo (sem extensão); quality: null sempre; clean-room (nenhuma URL/preço/atributo fabricado).
- Título <=60 caracteres preferencial (apenas aviso suave, ML_TITLE_MAX); currency_id sempre BRL.

## Artefatos Relacionados
| Artefato | Relação | Pontuação |
|----------|-------------|-------|
| [[marketplace-listing-builder]] | sibling | 0.5 |
| [[bld_output_marketplace_listing]] | downstream | 0.5 |
| [[bld_eval_marketplace_listing]] | downstream | 0.48 |
| [[bld_prompt_marketplace_listing]] | downstream | 0.45 |
| [[output-validator-builder]] | related | 0.38 |
