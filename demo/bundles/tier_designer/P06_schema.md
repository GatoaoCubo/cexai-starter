---
kind: schema
id: bld_schema_subscription_tier
pillar: P06
llm_function: CONSTRAIN
purpose: "Schema formal -- ÚNICA FONTE DE VERDADE para subscription_tier"
quality: null
title: "Schema Subscription Tier"
version: "1.0.0"
author: n03_builder
tags: [subscription_tier, builder, schema]
tldr: "Schema canônico de tier de assinatura SaaS, alinhado aos contratos de plano da Stripe Billing, Chargebee, Recurly e Paddle."
domain: "construção de subscription_tier"
created: "2026-04-14"
updated: "2026-04-14"
8f: "F1_constrain"
keywords: [construção de subscription_tier, schema subscription tier, contratos de plano da stripe chargebee recurly e paddle, subscription_tier, builder, schema, "{feature, included, quota, addon_price}", "{duration_days, payment_required, auto_convert}", "{metric, included_quota, overage_price}", interval=year]
density_score: 0.88
related:
  - bld_schema_reranker_config
  - bld_schema_integration_guide
  - bld_schema_benchmark_suite
  - bld_schema_sandbox_spec
  - bld_schema_eval_metric
---

## Campos do Frontmatter

### Obrigatórios
| Campo | Tipo | Obrigatório | Padrão | Notas |
|---|---|---|---|---|
| id | string | sim | null | Deve corresponder ao ID Pattern |
| kind | string | sim | "subscription_tier" | Valor fixo |
| pillar | string | sim | "P11" | Valor fixo |
| title | string | sim | null | Nome do tier legível por humanos (Starter, Pro, Business, Enterprise) |
| version | string | sim | "1.0.0" | Versionamento semântico |
| created | date | sim | null | ISO 8601 |
| updated | date | sim | null | ISO 8601 |
| author | string | sim | null | Responsável pelo produto/precificação |
| domain | string | sim | null | Linha de produto |
| quality | null | sim | null | Nunca autoavaliado; atribuído por revisão de pares |
| tags | list | sim | [] | Palavras-chave para busca |
| tldr | string | sim | null | Para quem é este tier + por quê, em uma linha |
| tier_name | string | sim | null | Nome de tier em texto livre (orientado a resultado: Starter/Growth/Scale; não Bronze/Silver/Gold) |
| monetization_unit | string | sim | null | "flat" \| "per_seat" \| "per_usage" \| "hybrid" |
| price | object | sim | {} | `{unit_amount: <int cents>, currency: <ISO 4217>, interval: <day\|week\|month\|year>, interval_count: <int>}` (canônico Stripe) |
| feature_matrix | list | sim | [] | Linhas: `{feature, included, quota, addon_price}` |

### Recomendados
| Campo | Tipo | Notas |
|---|---|---|
| trial_policy | object | `{duration_days, payment_required, auto_convert}` |
| grandfathering_policy | object | `{price_lock_months, feature_freeze, migration_offer}` -- obrigatório ao substituir um tier ativo |
| seat_limit | integer | Máximo de usuários (tiers per_seat / hybrid); null = ilimitado |
| usage_limits | object | `{metric, included_quota, overage_price}` por unidade medida |
| expansion_mrr | object | `{upgrade_to, add_on_catalog, seat_expansion_price}` |
| proration_behavior | string | "none" \| "create_prorations" \| "always_invoice" (valores do Stripe) |
| tax_behavior | string | "inclusive" \| "exclusive" \| "unspecified" |
| annual_discount_pct | number | Desconto quando `interval=year` vs. `interval=month`; norma da indústria de 15-25% |
| deprecation | object | `{status: active\|legacy\|sunset, sunset_date, successor_tier}` |

## ID Pattern
`^p11_st_[a-z][a-z0-9_]+\.yaml$`

## Estrutura do Corpo
1. **Público-Alvo** -- segmento de cliente-alvo e JTBD (job-to-be-done).
2. **Precificação** -- objeto de preço canônico do Stripe + desconto anual.
3. **Unidade de Monetização** -- flat / per_seat / per_usage / hybrid + justificativa.
4. **Matriz de Funcionalidades** -- linhas explícitas, sem listas em prosa.
5. **Trial e Conversão** -- trial_policy, caminho de upgrade, rateio (proration).
6. **Grandfathering** -- proteção de clientes legados quando este tier substitui outro.
7. **Desenho de Expansão** -- como os clientes crescem dentro de um tier e entre tiers (expansão de MRR).

## Restrições
- Tamanho do arquivo <= 3072 bytes.
- `price.unit_amount` DEVE ser um número inteiro na menor unidade de moeda (centavos, nunca em valores fracionados). Rejeite `9.99`; aceite `999`.
- `price.currency` DEVE ser um código ISO 4217 de 3 letras.
- `price.interval` DEVE ser um de `{day, week, month, year}` (canônico Stripe -- nada de "quarterly").
- `monetization_unit` DEVE ser um de `{flat, per_seat, per_usage, hybrid}`.
- `feature_matrix` DEVE ser não vazio; toda linha precisa de, no mínimo, `{feature, included}`.
- `grandfathering_policy` OBRIGATÓRIO quando `deprecation.status` estiver em `{legacy, sunset}`.
- Nomes de tier NÃO DEVEM usar metáforas de medalha (Bronze/Silver/Gold/Platinum) -- use linguagem orientada a resultado.
- O campo quality DEVE ser null (atribuído por revisão de pares).

## Related Artifacts
| Artefato | Relacionamento | Pontuação |
|----------|-------------|-------|
| bld_schema_reranker_config | sibling | 0.57 |
| bld_schema_integration_guide | sibling | 0.56 |
| bld_schema_benchmark_suite | sibling | 0.56 |
| bld_schema_sandbox_spec | sibling | 0.55 |
| [[bld_schema_eval_metric]] | sibling | 0.53 |
