---
id: bld_memory_marketplace_listing
kind: learning_record
pillar: P10
llm_function: INJECT
8f: F3_inject
version: 1.0.0
created: "2026-07-02"
updated: "2026-07-02"
author: n03_builder
title: "Padrões: construções de marketplace_listing"
domain: marketplace_listing
quality: null
tags: [marketplace_listing, builder, memory, patterns, P10]
tldr: "Padrões aprendidos + modos de falha recorrentes nas construções de marketplace_listing: mapear primeiro, matemática do gate verificada com antecedência, placeholders honestos e as armadilhas de divergência."
density_score: 0.9
related:
  - bld_knowledge_marketplace_listing
  - bld_eval_marketplace_listing
  - bld_feedback_marketplace_listing
  - bld_config_marketplace_listing
  - output-validator-builder
---

# Padrões: construções de marketplace_listing
## O que pontuou alto
| Padrão | Por quê |
|---------|-----|
| Mapear primeiro | percorrer a tabela G1->G2 antes de escrever uma única seção -> nenhum campo fica sem mapear |
| Matemática do gate verificada com antecedência | computar score/passed/missing_required no F4 REASON, antes do F6 -> nenhuma surpresa do H06 no F7 |
| Placeholders honestos, ao pé da letra | usar as strings exatas do generator ("(sem sku)", "(sem marca -- obrigatorio pelo ML)") -> o artefato lê de forma idêntica a uma execução real de um tenant |
| Ordem de BRAND/SELLER_SKU preservada | BRAND prependido, SELLER_SKU anexado, seguindo a mesma ordem de construção de lista do generator -> a tabela de Atributos bate byte a byte |
| Prontidão no frontmatter, não em uma 7ª seção | score/passed/missing_required/notes vivem no frontmatter, espelhando o StructuredOutput do generator -- nunca inventados como uma seção do corpo |

## Falhas recorrentes
| Falha | Correção |
|---------|-----|
| Assumir um filtro https | o generator em produção não tem nenhum; somente a camada de nível mais baixo `cex_channel_adapter.py` filtra -- não adicione um filtro que o artefato não reflete |
| Assumir um bloqueio forçado de estoque (available_quantity<=0) | o generator em produção nunca faz gate sobre estoque; somente `buyability()` na OUTRA camada faz isso |
| Truncar o título | o generator em produção apenas avisa acima de 60 caracteres, nunca trunca -- truncar é comportamento do `clean_ml_title` da OUTRA camada |
| Seção renomeada "Payload ML" sem o sufixo | o título exato é `Payload ML (pronto para publicar)` -- remover o sufixo quebra o H05 |
| Confundir `quality` com `score` | `quality` é sempre `null` (meta do CEX); `score` é o float de prontidão embutido 0.0-1.0 -- dois campos de frontmatter diferentes |
| Inventar um bloco `_meta` | o `ml_listing` do generator em produção não tem nenhum; `_meta` pertence à saída de `map()` da outra camada |

## Formato da biblioteca
Uma instância por coordenada (SKU x marketplace); hoje `marketplace` está efetivamente
fixo em `mercado_livre` (a única entrada em `CHANNEL_ADAPTERS`), então o eixo de cobertura
é apenas o SKU até que um segundo canal seja conectado.

## Artefatos Relacionados
| Artefato | Relação | Pontuação |
|----------|-------------|-------|
| [[bld_knowledge_marketplace_listing]] | upstream | 0.45 |
| [[bld_eval_marketplace_listing]] | sibling | 0.42 |
| [[bld_feedback_marketplace_listing]] | sibling | 0.4 |
| [[bld_config_marketplace_listing]] | related | 0.38 |
| [[output-validator-builder]] | related | 0.36 |
