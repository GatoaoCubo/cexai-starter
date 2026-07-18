---
kind: quality_gate
id: p11_qg_subscription_tier
pillar: P11
llm_function: GOVERN
purpose: "Gate de qualidade com pontuação HARD e SOFT para subscription_tier"
quality: null
title: "Quality Gate Subscription Tier"
version: "1.0.0"
author: n03_builder
tags: [subscription_tier, builder, quality_gate]
tldr: "Gate de qualidade em nível de artefato: valida a estrutura YAML de subscription_tier, a conformidade de campos Stripe/Chargebee e a integridade de precificação (não métricas de cobrança em tempo de execução)."
domain: "construção de subscription_tier"
created: "2026-04-14"
updated: "2026-04-14"
8f: "F7_govern"
keywords: [construção de subscription_tier, quality gate subscription tier, gate de qualidade em nível de artefato, valida a estrutura yaml de subscription_tier, conformidade de campos chargebee, integridade de precificação, não métricas de cobrança em tempo de execução]
density_score: 0.87
related:
  - bld_schema_subscription_tier
  - subscription-tier-builder
  - bld_memory_subscription_tier
---
## Gate de Qualidade

## Definição
| métrica | limiar | operador | escopo |
|---|---|---|---|
| schema_fields_present | 100% | == | frontmatter |
| price_integrity | valid | == | objeto de preço |
| score_minimum | 8.0 | >= | artefato |

## HARD Gates
| ID | Verificação | Condição de Falha |
|---|---|---|
| H01 | Frontmatter YAML válido | YAML ausente ou malformado |
| H02 | ID corresponde a `^p11_st_[a-z][a-z0-9_]+\.yaml$` | ID não está conforme |
| H03 | Campo `kind` == `subscription_tier` | kind errado ou ausente |
| H04 | `tier_name` presente e NÃO em `{bronze, silver, gold, platinum, diamond}` | Nomenclatura de metáfora de medalha |
| H05 | `monetization_unit` em `{flat, per_seat, per_usage, hybrid}` | Inválido ou ausente |
| H06 | `price.unit_amount` é inteiro >= 0 (menor unidade de moeda, centavos) | Decimal ou negativo |
| H07 | `price.currency` é código ISO 4217 de 3 letras | Moeda inválida |
| H08 | `price.interval` em `{day, week, month, year}` E `interval_count` é inteiro positivo | Interval não canônico |
| H09 | `feature_matrix` não vazio E toda linha tem, no mínimo, `{feature, included}` | Vazio ou malformado |
| H10 | `grandfathering_policy` presente quando `deprecation.status` está em `{legacy, sunset}` | Grandfathering ausente em tier depreciado |
| H11 | `quality: null` no frontmatter | Autoavaliado (deve ser null) |

## SOFT Scoring
| Dim | Dimensão | Peso | Guia de Pontuação |
|---|---|---|---|
| D1 | Especificidade de público | 0.12 | 1.0: JTBD + segmento + porte; 0.5: apenas segmento; 0.0: "genérico" |
| D2 | Canonicidade de precificação | 0.12 | 1.0: objeto de preço no formato Stripe + tax_behavior; 0.5: parecido com Stripe; 0.0: formato livre |
| D3 | Clareza da matriz de funcionalidades | 0.12 | 1.0: linhas com quota+addon_price; 0.5: apenas included; 0.0: lista em prosa |
| D4 | Adequação da unidade de monetização | 0.10 | 1.0: unidade condizente com o produto (per_seat para colaboração, per_usage para API); 0.0: incompatível |
| D5 | Diferenciação entre tiers | 0.10 | 1.0: cada tier adiciona 2+ capacidades diferenciadas; 0.5: adiciona 1; 0.0: sobreposição |
| D6 | Desenho de trial e conversão | 0.08 | 1.0: trial_policy + auto_convert + proration; 0.5: parcial; 0.0: ausente |
| D7 | Disciplina de grandfathering | 0.08 | 1.0: price_lock + feature_freeze + oferta de migração; 0.0: ignorado |
| D8 | Ganchos de expansão de MRR | 0.10 | 1.0: upgrade_to + add_ons + expansão de seats precificada; 0.5: apenas caminho de upgrade; 0.0: nenhum |
| D9 | Economia do desconto anual/mensal | 0.08 | 1.0: desconto anual de 15-25% justificado; 0.5: desconto sem justificativa; 0.0: sem opção anual |
| D10 | Planejamento de depreciação | 0.10 | 1.0: sunset_date + successor_tier documentados; 0.0: tier desenhado sem ciclo de vida |

Soma dos pesos = 1.00.

## Ações
| Pontuação | Ação |
|---|---|
| >= 9.5 | GOLDEN: publicar no sistema de cobrança |
| >= 8.0 | PUBLISH: enviar para Stripe/Chargebee |
| >= 7.0 | REVIEW: devolver ao responsável por precificação/produto |
| < 7.0 | REJECT: reconstruir -- canonicidade de preço ou feature matrix incompletos |

## Bypass
| condição | aprovador | trilha de auditoria |
|---|---|---|
| Contrato enterprise customizado (termos não padrão) | CRO + CFO | Contrato + registro de decisão |
| Exceção de precificação em mercado regulado | Diretoria Jurídica | Memorando de conformidade anexado |

## Exemplos

## Exemplo Golden
---
kind: subscription_tier
name: Notion Team Plan
provider: Notion
pricing: "$15/user/month"
features:
  - Páginas ilimitadas
  - Edição colaborativa
  - Suporte prioritário
  - 5GB de armazenamento
billing_cycle: monthly
limitations:
  - Sem analytics avançado
  - Integrações limitadas

O Team Plan da Notion oferece ferramentas de colaboração escaláveis para times pequenos. A precificação é transparente, com ciclo de cobrança mensal. As funcionalidades incluem edição em tempo real e armazenamento, mas falta analytics avançado para times orientados a dados.

## Antiexemplo 1: Precificação Ausente
---
kind: subscription_tier
name: Slack Premium
provider: Slack
features:
  - Mensagens ilimitadas
  - Emojis customizados
  - Segurança avançada
billing_cycle: annual

## Por que falha: A ausência de detalhes de preço torna a definição do tier incompleta. Os usuários não conseguem avaliar o custo-benefício sem saber o preço.

## Antiexemplo 2: Mistura com Content Monetization
---
kind: subscription_tier
name: Substack Creator Tier
provider: Substack
pricing: "$10/reader/month"
features:
  - Domínio customizado
  - Analytics de e-mail
  - Acesso a programa de afiliados
billing_cycle: yearly

## Por que falha: Foca em monetização de conteúdo (programas de afiliados) em vez de funcionalidades de assinatura SaaS. Viola as condições de fronteira ao confundir modelos de precificação.

### H_RELATED: Checagem de Referência Cruzada (HARD)
- [ ] Campo `related:` do frontmatter preenchido (mínimo 3 entradas)
- [ ] Seção `## Related Artifacts` presente no corpo do artefato
- [ ] Ao menos 1 referência upstream e 1 downstream ou sibling
- Gate: REJECT se < 3 entradas (auto-preenchido por cex_wikilink.py em F6.5)

### S_RELATED: Checagem de Referência Cruzada (SOFT)
- [ ] Campo `related:` do frontmatter preenchido (3-15 entradas)
- [ ] Seção `## Related Artifacts` presente no corpo do artefato
- [ ] Ao menos 1 referência upstream e 1 downstream
- Penalidade: -0.3 se vazio (não bloqueia, incentiva a referenciação cruzada)
