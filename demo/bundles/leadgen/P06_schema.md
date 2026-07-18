---
kind: schema
id: bld_schema_research_pipeline
pillar: P06
llm_function: CONSTRAIN
purpose: Schema formal -- FONTE ÚNICA DA VERDADE para a config do research_pipeline
pattern: CONFIG deriva disto. TEMPLATE renderiza isto.
quality: null
title: "Schema: Pipeline de Pesquisa"
version: "1.0.0"
author: n03_builder
tags: [research_pipeline, builder, examples]
tldr: "Exemplos-modelo e anti-exemplos para a construção de pipelines de pesquisa, demonstrando a estrutura ideal e as armadilhas mais comuns."
domain: "construção de pipeline de pesquisa"
created: "2026-04-07"
updated: "2026-04-07"
8f: "F1_constrain"
keywords: [formal schema, research pipeline construction, schema research pipeline, research_pipeline, builder, examples, config schema, validation rules, related artifacts, least categories]
density_score: 0.90
related:
  - bld_schema_usage_report
  - bld_schema_pitch_deck
  - bld_schema_quickstart_guide
  - bld_schema_reranker_config
---

# Schema: research_pipeline

## Schema de Config (o YAML que toda empresa preenche)

### identity (obrigatório)
| Campo | Tipo | Obrigatório | Exemplo |
|-------|------|----------|---------|
| empresa | string | SIM | "ACME" |
| nicho | string | SIM | "pet_ecommerce" |
| idioma | enum(pt-BR,en,es,fr,de) | SIM | "pt-BR" |
| pais | enum(BR,US,EU,UK,LATAM,APAC,custom) | SIM | "BR" |

### sources (obrigatório -- pelo menos 2 categorias)
| Categoria | Tipo | Obrigatório | Exemplo |
|----------|------|----------|---------|
| inbound | list[string] | SIM | [mercadolivre, shopee, amazon_br] |
| outbound | list[string] | NÃO | [youtube, reddit, reclameaqui] |
| search | list[string] | SIM | [serper, exa, gemini_search] |
| trends | list[string] | NÃO | [pytrends, keepa] |
| rag | list[string] | NÃO | [local_docs, supabase_embeddings] |

### storm_perspectives (obrigatório, mínimo 3)
| Campo | Tipo | Obrigatório | Exemplo |
|-------|------|----------|---------|
| role | string | SIM | "buyer" |
| focus | string | SIM | "preço frete reviews confiança" |

### multi_model (obrigatório)
| Campo | Tipo | Obrigatório | Padrão |
|-------|------|----------|---------|
| extraction | string (model ID) | SIM | "gemini-2.5-flash" |
| reasoning | string (model ID) | SIM | "gpt-5-mini" |
| social | string (model ID) | NÃO | mesmo valor de extraction |
| critic | string (model ID) | SIM | "o4-mini" |

### budget (obrigatório)
| Campo | Tipo | Obrigatório | Padrão |
|-------|------|----------|---------|
| firecrawl_monthly | int | NÃO | 3000 |
| firecrawl_per_research | int | NÃO | 10 |
| serper_daily | int | NÃO | 100 |

### output (obrigatório)
| Campo | Tipo | Obrigatório | Padrão |
|-------|------|----------|---------|
| formats | list[enum(html,pptx,json,md)] | SIM | [html, json] |
| idioma | string | SIM | mesmo valor de identity.idioma |
| template | enum(consulting,academic,brief,raw) | NÃO | "consulting" |

### quality (obrigatório)
| Campo | Tipo | Obrigatório | Padrão |
|-------|------|----------|---------|
| crag_min_score | float(0.0-1.0) | SIM | 0.7 |
| critic_max_iterations | int(1-5) | SIM | 3 |
| final_min_score | float(1.0-10.0) | SIM | 8.0 |

### marketplace_schemas (opcional -- para fontes inbound)
| Campo | Tipo | Obrigatório | Exemplo |
|-------|------|----------|---------|
| {source_name} | object | NÃO | {fields: [title, price, rating, sold_qty]} |
| {source}.fields | list[string] | SIM | campos de dados extraídos por marketplace |

## Regras de Validação
1. sources deve ter pelo menos 2 categorias preenchidas (mínimo: inbound + search)
2. storm_perspectives deve ter pelo menos 3 entradas
3. Todos os campos de chave de API *_env DEVEM estar em SCREAMING_SNAKE_CASE
4. Nenhum segredo em texto plano em qualquer parte da config
5. os valores de budget devem ser inteiros positivos
6. crag_min_score deve estar entre 0.0 e 1.0
7. critic_max_iterations deve estar entre 1 e 5
8. multi_model.critic deve ser um modelo de raciocínio

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| bld_schema_usage_report | sibling | 0.54 |
| bld_schema_pitch_deck | sibling | 0.53 |
| bld_schema_quickstart_guide | sibling | 0.53 |
| bld_schema_reranker_config | sibling | 0.53 |
| bld_schema_social_publisher | sibling | 0.52 |
