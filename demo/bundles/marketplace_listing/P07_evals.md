---
id: bld_eval_marketplace_listing
kind: quality_gate
pillar: P11
llm_function: GOVERN
8f: F7_govern
version: 1.0.0
created: "2026-07-02"
updated: "2026-07-02"
author: n03_builder
title: "Gate: marketplace_listing"
domain: marketplace_listing
quality: null
tags: [marketplace_listing, builder, eval, quality_gate, P11]
tldr: "Gates HARD + SOFT para marketplace_listing: 6 seções CONGELADAS, payload ml_listing embutido com 7 chaves obrigatórias, vocabulário de condição, injeção de BRAND/SELLER_SKU, honestidade do gate de prontidão, corpo <= 6144B."
density_score: 0.9
related:
  - bld_schema_marketplace_listing
  - bld_output_marketplace_listing
  - marketplace-listing-builder
  - bld_feedback_marketplace_listing
  - output-validator-builder
---

# Gate: marketplace_listing
## Gates HARD (qualquer FAIL -> REJECT, sem score)
| ID | Verificação | Regra |
|----|-------|------|
| H01 | Frontmatter faz parse | YAML válido, completo |
| H02 | Padrão do id | `^p05_ml_[a-z][a-z0-9_]+$`, igual ao nome do arquivo (sem extensão) |
| H03 | Literal do kind | `kind` é exatamente `marketplace_listing` |
| H04 | quality nulo | `quality` é null |
| H05 | seis seções presentes | Listagem ML, Preco e Estoque, Fotos, Atributos, Descricao, Payload ML (pronto para publicar) -- títulos exatos, ordem exata |
| H06 | consistência do payload | as 7 chaves ML (title/category_id/price/currency_id/available_quantity/condition/listing_type_id) aparecem de forma consistente TANTO nas linhas de campo de Listagem ML + Preco e Estoque QUANTO na string JSON do anuncio da seção Payload ML |
| H07 | corpo dentro do limite | corpo <= 6144 bytes |

## Pontuação SOFT (0 ou 10 x peso)
| Dimensão | Peso | Condição de aprovação |
|-----------|--------|----------------|
| titulo_ml mapeado + <=60 caracteres | 1.0 | title não vazio; comprimento <=60 ou nota [WARN] presente |
| categoria_ml mapeado | 1.0 | category_id não vazio |
| preco mapeado | 1.0 | price > 0 |
| Injeção de BRAND + SELLER_SKU | 1.0 | attributes[] carrega BRAND (a partir de marca) e SELLER_SKU (a partir de sku) quando essas entradas foram informadas |
| Vocabulário de condição correto | 1.0 | novo/usado/recondicionado mapeiam para new/used/refurbished (desconhecido assume new por padrão) |
| Padrões de currency + listing_type | 0.5 | currency_id==BRL; listing_type_id assume gold_special por padrão quando ausente |
| Honestidade do gate de prontidão | 1.0 | score/passed/missing_required/notes computados conforme a tabela de deduções, nunca estimados por cima |
| Clean-room | 1.0 | nenhuma URL de foto, preço ou valor de atributo fabricado |
| Fotos/Descricao/Marca com aviso suave | 0.5 | a ausência produz uma nota [WARN], nunca um descarte silencioso |
Soma dos pesos 8.0; `soft = sum(peso*score)/8.0*10`.

## Ações
| Score | Ação |
|-------|--------|
| >= 9.5 | GOLDEN -- entrada canônica da biblioteca |
| >= 8.0 | PUBLISH |
| >= 7.0 | REVISE -- a matemática do gate ou o formato das seções precisa de ajuste |
| < 7.0 | REJECT |

## Padrão-ouro vs Anti-padrão
- Padrão GOLDEN: uma linha G1 completa (veja a amostra de runtime
  `_output/g2_sample_listing.md` -- Arranhador Torre Sisal 1.2m, 2 fotos, BRAND+SELLER_SKU
  auto-injetados, score de prontidão 1.0, passed=true) -- 6 seções, todas as 7 chaves do
  ml_listing preenchidas, zero missing_required.
- ANTI: uma seção retitulada ou reordenada; uma URL de foto fabricada; category_id deixado
  vazio sem nota [FAIL]; BRAND omitido quando marca foi informada; `quality` não-nulo; o
  `score` de prontidão escrito dentro de `quality` (são dois campos distintos).

## Artefatos Relacionados
| Artefato | Relação | Pontuação |
|----------|-------------|-------|
| [[bld_schema_marketplace_listing]] | upstream | 0.55 |
| [[bld_output_marketplace_listing]] | sibling | 0.45 |
| [[marketplace-listing-builder]] | sibling | 0.42 |
| [[bld_feedback_marketplace_listing]] | downstream | 0.4 |
| [[output-validator-builder]] | related | 0.38 |
