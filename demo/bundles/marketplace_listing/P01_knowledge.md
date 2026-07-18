---
id: bld_knowledge_marketplace_listing
kind: knowledge_card
pillar: P01
llm_function: INJECT
8f: F3_inject
version: 1.0.0
created: "2026-07-02"
updated: "2026-07-02"
author: n03_builder
title: "Conhecimento de Domínio: marketplace_listing"
domain: marketplace_listing
quality: null
tags: [marketplace_listing, builder, knowledge, mercado-livre, P01]
tldr: "Fatos atômicos para construir marketplace_listing: o mapeamento de campos G1->G2, o vocabulário de condição, a injeção de BRAND/SELLER_SKU, a regra de título do ML, a fiação de media-slot e a divergência entre as duas implementações."
density_score: 0.92
related:
  - bld_schema_marketplace_listing
  - bld_architecture_marketplace_listing
  - bld_memory_marketplace_listing
  - bld_config_marketplace_listing
  - output-validator-builder
---

# Conhecimento de Domínio: marketplace_listing
## Mapeamento de campos G1 -> G2 (a partir de `capability_generators/marketplace_listing.py`)
| Campo G1 (dashboard) | Campo G2 (payload ML) | Notas |
|---|---|---|
| titulo_ml | title | <=60 caracteres preferencial (ML_TITLE_MAX); sem truncamento forçado por este builder |
| descricao | description.plain_text | corpo do anúncio |
| categoria_ml | category_id | id de categoria oficial do ML, ex. `MLB1055` |
| marca | atributo BRAND | injetado em attributes[] somente se ainda não presente |
| condicao | condition | novo->new, usado->used, recondicionado->refurbished; desconhecido->new |
| preco | price | float, R$ |
| estoque | available_quantity | inteiro >= 0; NÃO verificado por gate no generator em produção |
| fotos | pictures[].url | string separada por vírgula OU array JSON; SEM filtro https (ver divergência abaixo) |
| atributos | attributes[]{id,value_name} | objeto JSON `{"key":"value"}` |
| sku | seller_custom_field + atributo SELLER_SKU | injetado em attributes[] somente se ainda não presente |

## Regra de título do ML
Máximo preferencial de 60 caracteres (`ML_TITLE_MAX`). O generator em produção NÃO trunca --
apenas anexa uma nota `[WARN]` e deduz 0,05 do score. (A camada de nível mais baixo
`cex_channel_adapter.py` TRUNCA sim, no limite de uma palavra, via `clean_ml_title` -- um
módulo diferente, que este builder não espelha.)

## Gate de prontidão (o contrato score/passed/missing_required/notes)
Começa em 1.0; deduz 0,20 (titulo_ml ausente), 0,05 (title >60 caracteres), 0,15 (categoria_ml
ausente), 0,15 (preco<=0), 0,05 (descricao ausente), 0,10 (sem fotos), 0,05 (marca ausente);
piso em 0,0. `passed` exige zero itens em `missing_required` (somente titulo_ml/categoria_ml/
preco podem popular essa lista) E `score>=0.70`.

## Fiação de media-slot (para a projeção dual-output, não autorada por este builder)
Um slot de imagem por URL de foto (`foto_N`), ou um único slot de fallback de upload `foto_0`
quando nenhuma foto é fornecida; um slot `video_demo` é SEMPRE declarado e NUNCA
auto-produzido (nunca-fabricar). Isso é computado por `listing_media_requests`/
`listing_produced_media` no mesmo módulo generator, descoberto por `_base.resolve_media`
via a convenção de prefixo `listing_`.

## A divergência entre as duas implementações (leia antes de citar "o" contrato)
Dois módulos computam uma forma relacionada-mas-diferente para "anúncio ML": o generator EM
PRODUÇÃO `capability_generators/marketplace_listing.py` (a fonte da verdade deste builder:
score/passed/missing_required/notes, sem `_meta`, sem filtro https, sem gate de estoque) e o
`MercadoLivreAdapter` de nível mais baixo em `cex_channel_adapter.py` (o `upstream_source`
declarado em `.cex/kinds_meta.json`: bloco `_meta`, `PUBLISH-READY`/`NOT-READY` +
`missing[]`/`warnings[]`, cada um `{field,severity,message}`, fotos somente https,
bloqueio forçado com estoque zero via `buyability()`). Nunca apresente o comportamento
de um módulo como se fosse do outro.

## Artefatos Relacionados
| Artefato | Relação | Pontuação |
|----------|-------------|-------|
| [[bld_schema_marketplace_listing]] | downstream | 0.5 |
| [[bld_architecture_marketplace_listing]] | upstream | 0.45 |
| [[bld_memory_marketplace_listing]] | sibling | 0.4 |
| [[bld_config_marketplace_listing]] | related | 0.38 |
| [[output-validator-builder]] | related | 0.36 |
