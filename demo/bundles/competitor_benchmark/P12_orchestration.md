---
kind: collaboration
id: bld_collaboration_competitive_matrix
pillar: P12
llm_function: COLLABORATE
purpose: Como o competitive_matrix-builder trabalha em crews com outros builders
quality: null
title: "Collaboration Competitive Matrix"
version: "1.0.0"
author: wave1_builder_gen_v2
tags: [competitive_matrix, builder, collaboration]
tldr: "Como o competitive_matrix-builder trabalha em crews com outros builders"
domain: "construção de competitive_matrix"
created: "2026-04-14"
updated: "2026-04-14"
8f: "F8_collaborate"
keywords: [competitive_matrix construction, collaboration competitive matrix, competitive_matrix, builder, collaboration, crew role  
analyzes, receives from, produces for, boundary  
does, related artifacts]
density_score: 0.85
related:
  - bld_collaboration_eval_metric
  - bld_collaboration_customer_segment
  - bld_collaboration_ecommerce_vertical
  - p02_agent_web_researcher
  - bld_collaboration_sales_playbook
  - bld_collaboration_integration_guide
  - bld_collaboration_subscription_tier
---
## Papel na Crew
Analisa dados de concorrentes, estrutura funcionalidades/benefícios e gera matrizes visuais de comparação para a tomada de decisão estratégica.

## Recebe De
| Builder         | O Que               | Formato     |
|----------------|--------------------|------------|
| market_research| Lista de concorrentes    | CSV        |
| product_specs  | Definições de funcionalidades| JSON       |
| sales_team     | Tendências de mercado     | API        |

## Produz Para
| Builder         | O Que                  | Formato     |
|----------------|-----------------------|------------|
| strategy_team  | Matriz competitiva    | Markdown   |
| product_team   | Relatório de análise de lacunas   | PDF        |
| sales_team     | Dados de benchmarking     | CSV        |

## Limite
NÃO trata análise de segmento de cliente (ICP) ou conteúdo narrativo (pitch_deck). Tratado pelo customer_segment_builder e pitch_deck_builder, respectivamente.

## Artefatos Relacionados
| Artefato | Relacionamento | Pontuação |
|----------|-------------|-------|
| [[bld_collaboration_eval_metric]] | sibling | 0.20 |
| [[bld_collaboration_customer_segment]] | sibling | 0.17 |
| [[bld_collaboration_ecommerce_vertical]] | sibling | 0.17 |
| [[p02_agent_web_researcher]] | upstream | 0.16 |
| [[bld_collaboration_sales_playbook]] | sibling | 0.15 |
| [[bld_collaboration_integration_guide]] | sibling | 0.15 |
| [[bld_collaboration_subscription_tier]] | sibling | 0.15 |
