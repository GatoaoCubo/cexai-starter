---
kind: config
id: bld_config_subscription_tier
pillar: P09
llm_function: CONSTRAIN
purpose: "Nomenclatura, caminhos e limites para a produção de subscription_tier"
quality: null
title: "Config Subscription Tier"
version: "1.0.0"
author: wave1_builder_gen_v2
tags: [subscription_tier, builder, config]
tldr: "Restrições de produção para subscription tier: nomenclatura (p11_st_{{name}}.yaml), caminhos de saída (P11/), limite de tamanho 3072B. Tier de precificação."
domain: "construção de subscription_tier"
created: "2026-04-14"
updated: "2026-04-14"
8f: "F1_constrain"
keywords: [limites para produção de subscription_tier, construção de subscription_tier, config subscription tier, caminhos de saída, limite de tamanho, tier de precificação, subscription_tier, builder, config, "p11_st_{{name}}.yaml"]
density_score: 0.85
related:
  - bld_config_ab_test_config
  - bld_config_api_reference
  - bld_config_customer_segment
  - bld_config_collaboration_pattern
  - bld_config_pricing_page
---

## Convenção de Nomenclatura
Padrão: `p11_st_{{name}}.yaml`
Exemplos: `p11_st_bronze.yaml`, `p11_st_premium.yaml`

## Caminhos
Artefatos: `/artifacts/subscription_tiers/p11_st_{{name}}.yaml`
Logs: `/logs/build/p11_st_{{name}}`

## Limites
max_bytes: 3072
max_turns: 150
effort_level: high

## Hooks
pre_build: null
post_build: null
on_error: null
on_quality_fail: null

## Restrições Específicas do Domínio

| Restrição | Valor |
|-----------|-------|
| Fronteira | Tier de precificação |
| Dependências | customer_segment |
| Função 8F primária | F1_constrain |
| Tamanho máximo do artefato | 3072 bytes |

## Casos de Borda

| Cenário | Tratamento |
|----------|---------|
| Campo obrigatório do frontmatter ausente | Falha no gate H01; retornar a F6 |
| Colisão de ID com artefato existente | Acrescentar sufixo de versão (_v2) |
| Corpo excede 3072 bytes | Reduzir seções em prosa; preservar tabelas |
| Dependência customer_segment não encontrada | Avisar; prosseguir com os padrões |

## Propriedades

| Propriedade | Valor |
|----------|-------|
| Kind | `config` |
| Pillar | P09 |
| Domain | construção de subscription_tier |
| Pipeline | 8F (F1-F8) |
| Scorer | cex_score.py |
| Compiler | cex_compile.py |
| Retriever | cex_retriever.py |
| Meta de qualidade | 9.0+ |
| Meta de densidade | 0.85+ |

## Related Artifacts
| Artefato | Relacionamento | Pontuação |
|----------|-------------|-------|
| bld_config_ab_test_config | sibling | 0.52 |
| bld_config_api_reference | sibling | 0.49 |
| [[bld_config_customer_segment]] | sibling | 0.48 |
| bld_config_collaboration_pattern | sibling | 0.48 |
| bld_config_pricing_page | sibling | 0.47 |
