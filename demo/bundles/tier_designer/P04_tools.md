---
kind: tools
id: bld_tools_subscription_tier
pillar: P04
llm_function: CALL
purpose: "Ferramentas disponíveis para a produção de subscription_tier"
quality: null
title: "Tools Subscription Tier"
version: "1.0.0"
author: wave1_builder_gen_v2
tags: [subscription_tier, builder, tools]
tldr: "Ferramentas disponíveis para a produção de subscription_tier"
domain: "construção de subscription_tier"
created: "2026-04-14"
updated: "2026-04-14"
8f: "F5_call"
keywords: [construção de subscription_tier, tools subscription tier, subscription_tier, builder, tools, ferramentas de produção, ferramentas de validação, referências externas, related artifacts]
density_score: 0.85
related:
  - kc_subscription_tier
  - bld_tools_edit_format
  - bld_tools_vad_config
---
## Ferramentas de Produção
| Ferramenta | Propósito | Quando |
|---|---|---|
| tier_compile.py | Compila as configurações do tier de assinatura | Durante a criação do tier |
| tier_score.py | Pontua os tiers com base em métricas de engajamento do usuário | Durante a avaliação do tier |
| tier_retriever.py | Recupera dados de tier de sistemas externos | Ao sincronizar com plataformas de pagamento |
| tier_doctor.py | Diagnostica problemas na configuração do tier | Durante a fase de validação |
| tier_optimizer.py | Otimiza precificação e benefícios do tier | Durante o refinamento do tier |
| tier_validator.py | Valida a conformidade do tier com as políticas | Antes do deploy |

## Ferramentas de Validação
| Ferramenta | Propósito | Quando |
|---|---|---|
| tier_linter.py | Verifica a sintaxe e a estrutura do tier | Durante o desenvolvimento |
| tier_comparator.py | Compara tiers entre si para checar consistência | Durante auditorias |
| tier_stress_tester.py | Simula cenários de alta carga para o tier | Antes do deploy |

## Referências Externas
- Stripe API (processamento de pagamento)
- TieredAccess framework (gestão de assinaturas)
- SchemaValidator (checagem do schema de configuração)

## Related Artifacts
| Artefato | Relacionamento | Pontuação |
|----------|-------------|-------|
| [[bld_prompt_subscription_tier]] | upstream | 0.33 |
| [[kc_subscription_tier]] | upstream | 0.32 |
| bld_tools_edit_format | sibling | 0.30 |
| bld_tools_vad_config | sibling | 0.30 |
| [[bld_orchestration_subscription_tier]] | downstream | 0.30 |
