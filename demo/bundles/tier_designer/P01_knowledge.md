---
kind: knowledge_card
id: bld_knowledge_card_subscription_tier
pillar: P01
llm_function: INJECT
purpose: "Conhecimento de domínio para a produção de artefatos subscription_tier"
quality: null
title: "Knowledge Card Subscription Tier"
version: "1.0.0"
author: n03_builder
tags: [subscription_tier, builder, knowledge_card]
tldr: "Conhecimento de domínio sobre tiers de assinatura SaaS: contratos de cobrança Stripe/Chargebee, unidades de monetização, matrizes de funcionalidades, NRR / expansão de MRR e disciplina de grandfathering."
domain: "construção de subscription_tier"
created: "2026-04-14"
updated: "2026-04-14"
8f: "F3_inject"
keywords: [construção de subscription_tier, knowledge card subscription tier, contratos de cobrança chargebee, unidades de monetização, matrizes de funcionalidades, expansão de mrr, disciplina de grandfathering]
density_score: 0.88
related:
  - bld_memory_subscription_tier
  - subscription-tier-builder
  - bld_schema_subscription_tier
---
## Visão Geral do Domínio
Tiers de assinatura são a unidade estrutural da monetização em SaaS: cada tier é um pacote de funcionalidades com preço definido e uma cadência de cobrança recorrente. Um bom desenho de tiers equilibra simplicidade (no máximo 3-4 tiers, para evitar fadiga de decisão) com discriminação de preço entre segmentos de clientes. Os sistemas de registro da indústria -- Stripe Billing, Chargebee, Recurly, Paddle, Zuora -- impõem um contrato canônico: um `unit_amount` inteiro na menor unidade da moeda, uma `currency` no padrão ISO 4217, um `recurring.interval` em {day, week, month, year} e um `interval_count`. Artefatos de tier que se desviam dessa semântica quebram a cobrança multirregional, o cálculo de impostos e o rateio proporcional (proration).

Além da mecânica, o desenho de tiers governa duas métricas de SaaS que determinam o valor de uma empresa: Net Revenue Retention (NRR, meta >= 110%) e Gross Revenue Retention (GRR, meta >= 90%). Os tiers impulsionam o NRR através de ganchos de expansão: crescimento de seats (modelos per_seat), crescimento de uso (per_usage) e caminhos de upgrade (tier -> tier). O relatório "State of the Cloud" da Bessemer e o SaaS Benchmarks da OpenView publicam esses limiares todo ano.

## Conceitos-Chave
| Conceito | Definição | Fonte |
|---|---|---|
| Monetization Unit | O eixo de captura de valor: flat, per_seat, per_usage ou hybrid. | OpenView SaaS Pricing Benchmarks (anual) |
| Feature Matrix | Tabela que mapeia funcionalidades para tiers com células `{included, quota, addon_price}`. | Documentação de produto do Stripe Billing |
| Price Object (Stripe) | Formato canônico `{unit_amount, currency, recurring.interval, interval_count}`. | Referência da API Stripe (`/v1/prices`) |
| Net Revenue Retention (NRR) | MRR retido e expandido de uma coorte ao longo de 12 meses. Meta >= 110%. | Bessemer "State of the Cloud" |
| Expansion MRR | MRR incremental vindo de clientes existentes via crescimento de seats, uso ou upgrade. | OpenView SaaS Benchmarks |
| Grandfathering | Manter clientes legados no preço/funcionalidades antigos após uma mudança de tier. | Documentação de produto da Stripe e da Chargebee |
| Proration Behavior | Como mudanças de plano no meio do ciclo são cobradas. Valores Stripe: none, create_prorations, always_invoice. | API Stripe (`proration_behavior`) |
| ARPU / ARPA | Receita Média por Usuário / por Conta. | Métrica padrão de SaaS (SaaStr, KeyBanc) |
| Churn Rate | Percentual de clientes que cancelam por período. Churn de logo e churn de receita são distintos. | KeyBanc SaaS Survey |
| Seat Expansion | Crescimento dentro de um tier via usuários licenciados adicionais (impulsiona o NRR em modelos per_seat). | Manuais (playbooks) da Salesforce, Slack, Linear |
| Annual Discount | Incentivo para pagamento antecipado; norma da indústria de 15-25% vs. mensal. | Dados da OpenView e da ProfitWell |
| Sample Ratio in Pricing Tests | Guardrail ao testar preços em A/B -- SRM invalida as conclusões. | Kohavi et al. (2020) "Trustworthy Online Controlled Experiments" |

## Padrões da Indústria
- Stripe Billing API (`/v1/prices`, `/v1/products`, `/v1/subscriptions`) -- contrato de fato do objeto de preço.
- Chargebee Plans API -- modelo de plano, addon, cupom e entitlement.
- Recurly Plans & Add-ons -- decomposição em tier + add-on + cupom.
- Paddle Billing -- semântica de Merchant of Record (tax_behavior, preço por geolocalização).
- Zuora Billing -- modelo enterprise de rate plan + charge.
- ISO 4217 -- códigos de moeda (obrigatório para price.currency).
- Gartner Magic Quadrant: Subscription Management -- panorama de fornecedores.
- OpenView SaaS Benchmarks -- normas de NRR, GRR e CAC payback.

## Padrões Comuns
1. **Teto de 3-4 tiers** -- Starter, Growth/Pro, Business, Enterprise. Mais que 4 gera fadiga de decisão (dado: ProfitWell).
2. **Baseado em seats para ferramentas de colaboração** (Slack, Linear, Notion) -- a contagem de seats impulsiona o MRR de expansão naturalmente.
3. **Baseado em uso para APIs/infraestrutura** (OpenAI, Stripe, AWS) -- medidor + cota incluída + preço de excedente.
4. **Híbrido (plataforma + uso)** (Zendesk, Intercom) -- taxa fixa de plataforma + valor por seat ou por conversa.
5. **Desconto anual de 15-25%** -- antecipa caixa, aumenta a retenção.
6. **Enterprise = customizado** -- preço "fale conosco" com contrato negociado; o tier é apenas uma casca (shell).

## Armadilhas
- **Nomenclatura de medalha** (Bronze/Silver/Gold): compradores se auto-selecionam pelo resultado desejado ("sou um time", "administro um negócio"), não por metal.
- **Preços em ponto flutuante** (9.99): quebra o Stripe, arredonda errado em multi-moeda e falha na contabilidade exata de centavos.
- **Grandfathering ausente**: risco jurídico + churn em massa quando um tier ativo é reprecificado sem trava de preço.
- **Colapso de sobreposição**: Pro e Enterprise diferem só no "SLA de suporte" -> compradores negociam para baixo, indo para o Pro.
- **Sem ganchos de expansão**: tier fixo sem caminho de seat/uso/upgrade limita o NRR abaixo de 100%.
- **Ignorar o rateio (proration)**: upgrades no meio do ciclo cobram a mais ou perdem receita -- escolha `create_prorations` e documente.
- **Opacidade fiscal**: omitir `tax_behavior` quebra a conformidade com o VAT da UE / imposto sobre vendas dos EUA.
- **Sem plano de encerramento (sunset)**: todo tier acumula dívida técnica -- desenhe a depreciação desde o primeiro dia.

## Related Artifacts
| Artefato | Relacionamento | Pontuação |
|----------|-------------|-------|
| [[bld_memory_subscription_tier]] | downstream | 0.58 |
| [[subscription-tier-builder]] | downstream | 0.49 |
| [[bld_schema_subscription_tier]] | downstream | 0.40 |
| p08_pat_pricing_framework | downstream | 0.34 |
