---
kind: collaboration
id: bld_collaboration_roi_calculator
pillar: P12
llm_function: COLLABORATE
purpose: Como o roi_calculator-builder atua em equipes com outros builders
quality: null
title: "Colaboração -- ROI Calculator"
version: "1.0.0"
author: wave1_builder_gen_v2
tags: [roi_calculator, builder, collaboration]
tldr: "Como o roi_calculator-builder atua em equipes com outros builders"
domain: "construção de roi_calculator"
created: "2026-04-14"
updated: "2026-04-14"
8f: "F8_collaborate"
keywords: [construção de roi_calculator, colaboração roi calculator, roi_calculator, builder, collaboration, papel na equipe, calcula, recebe de, produz para, limite, related artifacts]
density_score: 0.85
related:
  - roi-calculator-builder
  - bld_config_roi_calculator
  - kc_roi_calculator
---
## Papel na Equipe
Calcula métricas de ROI usando entradas de investimento, receita e prazo. Traduz dados brutos em insights acionáveis de ROI para a tomada de decisão.

## Recebe De
| Builder       | O que                  | Formato     |
|---------------|-----------------------|------------|
| data_collector| Dados de investimento       | JSON       |
| revenue_tracker| Números de receita      | CSV        |
| time_frame_provider| Período de tempo       | Chamada de API   |

## Produz Para
| Builder       | O que                  | Formato     |
|---------------|-----------------------|------------|
| reporting     | Relatório-resumo de ROI    | PDF        |
| dashboard     | Métricas visuais de ROI    | Chamada de API   |
| analytics     | Dataset de ROI           | JSON       |

## Limite
Não trata do orçamento de custos (equipe de operações) nem do rastreamento real de uso (módulo usage_report).

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[roi-calculator-builder]] | upstream | 0.29 |
| [[bld_config_roi_calculator]] | upstream | 0.29 |
| n00_roi_calculator_manifest | upstream | 0.26 |
| [[bld_prompt_roi_calculator]] | upstream | 0.25 |
| [[kc_roi_calculator]] | upstream | 0.25 |
