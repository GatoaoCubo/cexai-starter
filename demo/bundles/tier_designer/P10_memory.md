---
kind: memory
id: bld_memory_subscription_tier
pillar: P10
llm_function: INJECT
purpose: "Experiência de produção acumulada para a geração de artefatos subscription_tier"
memory_scope: project
observation_types: [user, feedback, project, reference]
quality: null
title: "Memory Subscription Tier"
version: "1.0.0"
author: n03_builder
tags: [subscription_tier, builder, memory]
tldr: "Padrões golden e antipadrões para a construção de subscription tier SaaS: intervalos de cobrança alinhados ao Stripe, linhas de feature matrix, grandfathering explícito, expansão de MRR desenhada desde o início."
domain: "construção de subscription_tier"
created: "2026-04-14"
updated: "2026-04-14"
8f: "F3_inject"
keywords: [construção de subscription_tier, memory subscription tier, intervalos de cobrança alinhados ao stripe, linhas de feature matrix, grandfathering explícito, expansão de mrr desenhada desde o início, subscription_tier, builder, memory, resumo, tiers]
density_score: 0.88
related:
  - subscription-tier-builder
  - bld_schema_subscription_tier
---
# Memória: subscription-tier-builder

## Resumo
Tiers falham quando espelham a página de preços em vez de modelar a realidade da cobrança. O defeito mais comum é o billing_interval ambíguo (silenciosamente mensal quando o cliente esperava anual -> chargebacks). O segundo é a ausência de grandfathering: uma mudança de preço quebra contratos legados e dispara churn em massa. O terceiro é o acúmulo de funcionalidades (feature creep) entre tiers: Pro e Enterprise ficam indistinguíveis, colapsando o ARPU.

## Padrão
1. Use os campos canônicos do Stripe/Chargebee/Paddle: price.unit_amount (centavos), price.currency (ISO 4217), price.recurring.interval (day/week/month/year), price.recurring.interval_count, tax_behavior (inclusive/exclusive).
2. Modele billing_interval + interval_count juntos. "A cada 3 meses" = interval=month, interval_count=3 (semântica do Stripe), não uma string customizada "quarterly".
3. Feature_matrix é uma tabela: linhas = funcionalidades, colunas = tiers, células = {included, quota, addon_price}. Nada de listas de funcionalidades em prosa.
4. Modele a unidade de monetização: per_seat (Slack, Linear), per_usage (Stripe, OpenAI), hybrid (Zendesk), flat (Basecamp). O campo tier_type é obrigatório.
5. A grandfathering_policy é OBRIGATÓRIA: especifique price_lock (meses), feature_freeze (sim/não), migration_offer. Salesforce e HubSpot têm playbooks de grandfathering documentados.
6. Desenhe os ganchos de expansion_mrr: upgrade_path_to (id do próximo tier), add_on_catalog, seat_expansion_price. 30-40% da receita de SaaS vem de expansão -- trate isso como prioridade de primeira classe.
7. Inclua trial_policy (duration_days, payment_required, auto_convert) e proration_behavior (none/create_prorations/always_invoice, conforme o Stripe).

## Evidência
O schema da API Stripe Billing e a documentação de planos da Chargebee são o contrato de fato da indústria para modelos de assinatura. O relatório "10 Laws of Cloud" da Bessemer e o SaaS Benchmarks da OpenView confirmam: (a) teto de 3-4 tiers, (b) desconto anual sobre mensal de 15-25%, (c) net revenue retention >= 110% é a meta de expansão de MRR. O Gartner (Magic Quadrant: Subscription Management) cita Zuora, Chargebee, Recurly, Stripe Billing e Paddle como sistemas canônicos.

## Armadilhas
- **Tier gratuito fixo no código (estilo H06)**: nem todo SaaS é freemium (Salesforce, HubSpot Enterprise, Notion Business) -- o tier gratuito é uma escolha de GTM, não uma restrição do schema.
- **Nomenclatura Bronze/Silver/Gold**: tiers baseados em metáfora perdem para os orientados a resultado (Starter/Growth/Scale, Solo/Team/Business) porque os clientes se auto-selecionam pelo papel que exercem, não pelo metal.
- **Colapso de sobreposição de funcionalidades**: Pro e Enterprise diferem só no "SLA de suporte" -> compradores negociam para baixo, indo para o Pro.
- **Moeda como string**: "USD$9.99" em vez de {amount: 999, currency: "USD"} quebra a cobrança multirregional.
- **Opacidade fiscal**: ignorar tax_behavior causa falhas de conformidade com o VAT da UE.
- **Mudança de plano sem política de rateio (proration)**: upgrades no meio do ciclo cobram a mais ou perdem receita -- escolha create_prorations e documente.
- **Sem caminho de depreciação**: um tier legado com 300 clientes acumula dívida técnica -- todo tier precisa de um plano de encerramento (sunset).

## Related Artifacts
| Artefato | Relacionamento | Pontuação |
|----------|-------------|-------|
| [[bld_knowledge_subscription_tier]] | upstream | 0.60 |
| [[subscription-tier-builder]] | downstream | 0.56 |
| [[bld_schema_subscription_tier]] | upstream | 0.49 |
| p08_pat_pricing_framework | upstream | 0.33 |
