---
kind: knowledge_card
id: bld_knowledge_card_funnel_diag
pillar: P01
llm_function: INJECT
purpose: Conhecimento de domínio para a produção do tool_card da capacidade funnel_diag
sources: framework AARRR (Dave McClure, 500 Startups, 2007), funil bowtie SaaS (Winning by Design), ICE/RICE scoring, SaaS Metrics 2.0 (David Skok)
quality: null
title: "Conhecimento de Domínio: Diagnóstico de Funil"
version: "1.0.0"
author: n03_builder
tags: [funnel_diag, tool_card, builder, knowledge_card]
tldr: "Framework de 5 estágios (atrair-engajar-converter-reter-expandir), métricas por estágio e métodos de priorização ICE/RICE para achar o vazamento de maior ROI no funil."
domain: "diagnóstico de funil (funnel_diag)"
created: "2026-07-17"
updated: "2026-07-17"
8f: "F3_inject"
keywords: [funil de vendas, diagnóstico de funil, taxa de conversão, priorização ICE, churn, retenção de receita, funnel_diag, tool_card]
density_score: 0.90
related:
  - funnel-diagnostic-builder
  - bld_schema_funnel_diag
---
# Conhecimento de Domínio: funnel_diag

## Visão Geral do Domínio
Diagnóstico de funil é a disciplina de growth que localiza, entre todos os estágios da jornada do cliente, qual estágio concentra a maior perda de receita potencial -- e depois ordena os consertos possíveis por impacto dividido por esforço, nunca pela facilidade isolada de implementar. Um diagnóstico correto não entrega "10 ideias de otimização"; ele aponta 1 a 3 vazamentos de maior alavancagem e justifica a ordem com números, não com intuição.

## Estágios do Funil (framework funnel_diag)
| Estágio | Nome EN (referência) | Pergunta que o estágio responde | Métrica típica |
|---|---|---|---|
| Atrair | Attract | Como as pessoas certas chegam até você? | Tráfego qualificado, CAC, CTR, custo por lead |
| Engajar | Engage | Elas entendem o valor rápido o suficiente? | Taxa de ativação, tempo-até-valor, PQL |
| Converter | Convert | Elas viram cliente pagante? | Taxa de conversão trial->pago, ticket médio, ciclo de venda |
| Reter | Retain | Elas continuam pagando? | Churn mensal, NPS, taxa de renovação |
| Expandir | Expand | Elas gastam mais com o tempo? | NRR (Net Revenue Retention), upsell rate, LTV |

Este é um recorte do framework AARRR ("Pirate Metrics", Dave McClure / 500 Startups, 2007) adaptado ao formato bowtie usado por consultorias de growth para SaaS B2B (Winning by Design): o funil não termina na venda -- ele dobra sobre si mesmo em Reter/Expandir, porque para a maioria dos modelos de assinatura o LTV pós-venda pesa mais que o CAC de aquisição.

## Métodos de Priorização (achar o "maior ROI")
| Método | Fórmula / lógica | Quando usar | Origem |
|---|---|---|---|
| ICE | (Impacto + Confiança + Facilidade) / 3, cada eixo 1-10 | Priorização rápida, poucos dados | Sean Ellis, GrowthHackers |
| RICE | (Alcance x Impacto x Confiança) / Esforço | Quando há volume/alcance para diferenciar fixes | Intercom |
| PIE | (Potencial + Importância + Facilidade) / 3 | CRO (conversion rate optimization) clássico | Widerfunnel |

`funnel_diag` usa ICE como padrão (mais simples de explicar ao usuário final) e aceita RICE quando o usuário fornece dado de alcance (reach) por estágio.

## Métricas de Referência (benchmarks públicos, só para contexto -- nunca usados como dado real do cliente)
| Métrica | Faixa típica citada na indústria | Fonte |
|---|---|---|
| Churn mensal SaaS B2B saudável | 1-2%/mês | SaaS Metrics 2.0, David Skok (Matrix Partners) |
| NRR (Net Revenue Retention) de referência | >=100% (best-in-class >110%) | Benchmarks públicos de empresas SaaS de capital aberto |
| Taxa de conversão trial->pago (self-serve) | 15-25% | Benchmarks de mercado amplamente citados |
| Taxa de abandono de carrinho e-commerce | 60-80% | Benchmarks de mercado amplamente citados |

Benchmarks são ponto de partida para comparação, nunca substituem o dado real do cliente -- se o usuário não fornecer o número, o card marca `[A CONFIRMAR]`, nunca preenche com o benchmark disfarçado de medição.

## Padrões Comuns
- O vazamento de maior ROI raramente está no estágio mais visível (Converter); geralmente está em Reter ou Expandir, porque o efeito composto ao longo dos meses supera o ganho pontual de uma conversão a mais.
- Corrigir o estágio com o maior volume absoluto de perda costuma valer mais que corrigir o estágio com a pior taxa percentual isolada (o "problema do denominador").
- Métricas médias escondem variância por canal/segmento -- sempre que possível, o diagnóstico segmenta por origem de tráfego ou tipo de cliente antes de concluir onde está o vazamento.

## Armadilhas (Pitfalls)
- Vanity metrics (visitas, downloads) sem taxa de conversão associada não localizam vazamento nenhum.
- Comparar a média do cliente contra o benchmark da indústria sem ajustar por segmento/ICP produz falso positivo.
- Ranquear fixes só por facilidade de implementar (ignorando impacto) produz uma lista de tarefas fáceis, não um diagnóstico de ROI.

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[funnel-diagnostic-builder]] | downstream | 0.44 |
| [[bld_schema_funnel_diag]] | downstream | 0.40 |
| [[bld_output_template_funnel_diag]] | downstream | 0.36 |
| [[roi-calculator-builder]] | sibling | 0.30 |
