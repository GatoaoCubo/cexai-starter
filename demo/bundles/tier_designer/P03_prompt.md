---
kind: instruction
id: bld_instruction_subscription_tier
pillar: P03
llm_function: REASON
purpose: "Processo de produção passo a passo para subscription_tier"
quality: null
title: "Instruction Subscription Tier"
version: "1.0.0"
author: wave1_builder_gen_v2
tags: [subscription_tier, builder, instruction]
tldr: "Processo de produção passo a passo para subscription_tier"
domain: "construção de subscription_tier"
created: "2026-04-14"
updated: "2026-04-14"
8f: "F6_produce"
keywords: [construção de subscription_tier, instruction subscription tier, subscription_tier, builder, instruction, price_id, currency, recurring_interval, feature_matrix, constraints]
density_score: 0.85
related:
  - kc_subscription_tier
  - bld_tools_subscription_tier
---
## Fase 1: PESQUISA
1. Analisar tendências de mercado para modelos de precificação SaaS (ex.: freemium, em tiers).
2. Fazer benchmark dos tiers de assinatura de concorrentes quanto a paridade de funcionalidades e preço.
3. Identificar as funcionalidades essenciais a incluir em cada tier (ex.: chamadas de API, limites de armazenamento).
4. Priorizar funcionalidades com base no valor para o cliente e na viabilidade técnica.
5. Segmentar os usuários-alvo por padrão de uso (leve, médio, enterprise).
6. Revisar requisitos legais de precificação (ex.: conformidade fiscal, políticas de reembolso).

## Fase 2: COMPOSIÇÃO
1. Definir o nome do tier usando o campo `name` do SCHEMA.md (ex.: "Basic", "Pro").
2. Definir a estrutura de preço com `price_id`, `currency` e `recurring_interval`.
3. Mapear funcionalidades para tiers em `feature_matrix` (ex.: "usuários ilimitados" -> "Pro").
4. Especificar restrições via `constraints` (ex.: "máximo de 100 chamadas de API/mês").
5. Vincular às configurações do gateway de pagamento em `external_ids`.
6. Adicionar a descrição do tier usando a seção `summary` do OUTPUT_TEMPLATE.md.
7. Validar dependências entre funcionalidades (ex.: "Pro" requer as funcionalidades do "Basic").
8. Documentar os fluxos de onboarding de cada tier em `user_journey`.
9. Finalizar o artefato com os metadados `created_at` e `updated_at` do SCHEMA.md.

## Fase 3: VALIDAÇÃO
- [ ] Checar a conformidade com o schema via validador de JSON schema.
- [ ] Confirmar a consistência de preço entre todos os tiers e moedas.
- [ ] Garantir que a feature_matrix esteja alinhada com a implementação técnica.
- [ ] Verificar a lógica de aplicação das restrições nos sistemas de backend.
- [ ] Conduzir testes com usuários reais usando configurações de tier de exemplo.

## Related Artifacts
| Artefato | Relacionamento | Pontuação |
|----------|-------------|-------|
| bld_instruction_pricing_page | sibling | 0.42 |
| [[kc_subscription_tier]] | upstream | 0.38 |
| [[bld_tools_subscription_tier]] | downstream | 0.34 |
| n00_pricing_page_manifest | downstream | 0.34 |
