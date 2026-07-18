---
id: bld_config_marketplace_listing
kind: env_config
pillar: P09
llm_function: CONSTRAIN
8f: F1_constrain
version: 1.0.0
created: "2026-07-02"
updated: "2026-07-02"
author: n03_builder
title: "Config: parâmetros de construção do marketplace_listing"
domain: marketplace_listing
quality: null
tags: [marketplace_listing, builder, config, P09]
tldr: "Parâmetros em tempo de construção para um marketplace_listing: canal de marketplace, padrão de listing_type_id, padrão de condição, moeda, e o limiar de aprovação do gate de prontidão."
density_score: 0.88
related:
  - bld_schema_marketplace_listing
  - bld_prompt_marketplace_listing
  - bld_eval_marketplace_listing
  - bld_architecture_marketplace_listing
  - bld_tools_marketplace_listing
---

# Config: parâmetros de construção do marketplace_listing
CONFIG restringe o SCHEMA; nunca adiciona campos que o schema não conhece.
## Parâmetros
| Parâmetro | Padrão | Faixa | Efeito |
|------|---------|-------|--------|
| marketplace | mercado_livre | mercado_livre (único canal que `CHANNEL_ADAPTERS` conecta hoje) | canal-alvo; o formato do OUTPUT permanece específico do ML independentemente do valor |
| listing_type_id | gold_special | gold_special, gold_pro, gold_premium, silver, bronze, free | nível de anúncio no ML |
| condition | novo | novo\|usado\|recondicionado (-> new\|used\|refurbished; desconhecido assume new por padrão) | condição do produto |
| currency_id | BRL | BRL (fixo) | constante do ML Brasil, nunca sobrescrita |
| title_max_len | 60 | fixo (ML_TITLE_MAX) | apenas aviso suave acima deste tamanho, nunca truncamento forçado por este builder |
| pass_threshold | 0.70 | fixo | piso de score para `passed=true` (também exige zero missing_required) |

## Invariantes (não podem ser sobrescritas)
- quality permanece null (a meta-qualidade do CEX; distinta do campo `score` embutido).
- currency_id é sempre BRL; não há caminho multi-moeda no generator em produção.
- A auto-injeção de BRAND/SELLER_SKU nunca sobrescreve um atributo que a linha já declara.
- missing_required só pode conter `titulo_ml->title`, `categoria_ml->category_id`,
  `preco->price` -- nenhum outro campo pode aparecer ali (estoque/condicao/marca/fotos
  recebem apenas aviso suave, nunca gate forçado, no generator em produção).

## Artefatos Relacionados
| Artefato | Relação | Pontuação |
|----------|-------------|-------|
| [[bld_schema_marketplace_listing]] | upstream | 0.5 |
| [[bld_prompt_marketplace_listing]] | sibling | 0.42 |
| [[bld_eval_marketplace_listing]] | downstream | 0.4 |
| [[bld_architecture_marketplace_listing]] | related | 0.38 |
| [[bld_tools_marketplace_listing]] | related | 0.36 |
