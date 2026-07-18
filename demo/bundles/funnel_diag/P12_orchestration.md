---
kind: collaboration
id: bld_collaboration_funnel_diag
pillar: P12
llm_function: COLLABORATE
purpose: Como o funnel-diagnostic-builder trabalha em crews com outros builders
pattern: cada builder conhece seu papel no time, o que recebe e o que produz
quality: null
title: "Colaboração: Diagnóstico de Funil"
version: "1.0.0"
author: n03_builder
tags: [funnel_diag, tool_card, builder, collaboration]
tldr: "Recebe dados brutos de analytics/CRM do usuário; produz o tool_card de diagnóstico; entrega para roi_calculator (valor financeiro) e sales_playbook/pricing (execução)."
domain: "diagnóstico de funil (funnel_diag)"
created: "2026-07-17"
updated: "2026-07-17"
8f: "F8_collaborate"
density_score: 0.88
related:
  - funnel-diagnostic-builder
  - roi-calculator-builder
---
## Meu Papel em Crews
Sou um ESPECIALISTA. Respondo UMA pergunta: "qual estágio do funil, corrigido primeiro, devolve o maior retorno por esforço?"
Não calculo valor financeiro detalhado (isso é `roi_calculator`). Não escrevo a copy da correção (isso é um `prompt_template`). Não defino preço (isso é `pricing_page`/`subscription_tier`).

## Composições de Crew
### Crew: "Diagnóstico de Crescimento Completo"
```
  1. funnel-diagnostic-builder -> "onde está o vazamento de maior ROI"
  2. roi-calculator-builder -> "quanto vale corrigir esse vazamento em R$"
  3. sales-playbook-builder -> "como a equipe executa o conserto"
```
### Crew: "Funil + Precificação"
```
  1. funnel-diagnostic-builder -> "vazamento no estágio Converter"
  2. pricing-page-builder -> "nova estrutura de oferta/preço para reduzir o vazamento"
```

## Protocolo de Handoff
### Eu Recebo
- seeds: intent em texto livre + (quando disponível) métricas por estágio coladas pelo usuário
- opcional: modelo de negócio, benchmarks próprios do cliente, método de priorização preferido (ICE ou RICE)

### Eu Produzo
- artefato tool_card (.md, máx. 5120 bytes de corpo, os 5 estágios cobertos)
- salvo em: `N06_commercial/P11_feedback/tool_cards/p11_tc_funnel_diag_{{slug}}.md`

### Eu Sinalizo
- signal: complete (com score do gate de qualidade)
- se score < 7.0: signal de retry com os gates que falharam

## Builders dos Quais Dependo
Nenhum -- builder independente (camada 0). O diagnóstico parte dos dados que o usuário traz.

## Builders Que Dependem de Mim
| Builder | Por quê |
|---|---|
| roi-calculator-builder | Usa o vazamento identificado como input para o cálculo financeiro detalhado |
| sales-playbook-builder | Usa o fix #1 ranqueado para desenhar o playbook de execução |
| pricing-page-builder | Usa o vazamento no estágio Converter como input de reestruturação de oferta |

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[funnel-diagnostic-builder]] | upstream | 0.40 |
| [[roi-calculator-builder]] | sibling | 0.36 |
| [[bld_architecture_funnel_diag]] | sibling | 0.30 |
