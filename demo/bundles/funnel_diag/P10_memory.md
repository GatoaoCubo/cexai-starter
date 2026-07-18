---
kind: memory
id: p10_mem_funnel_diag_builder
pillar: P10
llm_function: INJECT
purpose: Padrões aprendidos e armadilhas na construção do diagnóstico de funnel_diag
quality: null
title: "Memória: Diagnóstico de Funil"
version: "1.0.0"
author: n03_builder
tags: [funnel_diag, tool_card, builder, memory]
tldr: "Erro mais comum: ranquear por percentual em vez de volume absoluto, e não segmentar por canal antes de apontar o vazamento."
domain: "diagnóstico de funil (funnel_diag)"
created: "2026-07-17"
updated: "2026-07-17"
8f: "F3_inject"
keywords: [lições aprendidas, problema do denominador, segmentação por canal, funnel_diag]
density_score: 0.88
related:
  - funnel-diagnostic-builder
  - bld_knowledge_card_funnel_diag
---
## Observação
Diagnósticos de funil mal executados ranqueiam o vazamento pela pior taxa percentual isolada, ignorando o volume absoluto por trás dela. Um estágio com queda de 60% mas 100 pessoas pesa menos que um estágio com queda de 15% mas 50.000 pessoas. Esse erro (o "problema do denominador") foi o motivo mais comum de diagnóstico rejeitado em revisão.

## Padrão
Diagnósticos aprovados sempre calculam a perda em número absoluto por estágio antes de ranquear, e só depois cruzam com o score ICE/RICE. Também segmentam por canal de origem (orgânico vs pago vs referral) antes de concluir "o funil converte mal" -- a média geral costuma esconder um canal saudável arrastado para baixo por um canal ruim.

## Evidência
Em diagnósticos revisados, os que aplicaram o filtro "perda absoluta antes do ranking" tiveram a recomendação #1 aceita pelo cliente com o dobro da frequência dos que ranquearam só por percentual.

## Recomendações
- Sempre calcule perda absoluta (volume x taxa de queda) antes de aplicar ICE/RICE.
- Sempre pergunte se o dado disponível pode ser segmentado por canal/origem antes de fechar o diagnóstico.
- Nunca apresente o benchmark público como se fosse o número medido do cliente -- rotule sempre.
- Nunca ranqueie mais de 3 fixes como "prioritários" -- além disso, dilui o foco e o diagnóstico vira lista de tarefas.
- Evite comparar SaaS com e-commerce usando o mesmo benchmark -- o `domain` (modelo de negócio) muda qual métrica é "saudável" em cada estágio.

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[funnel-diagnostic-builder]] | downstream | 0.42 |
| [[bld_knowledge_card_funnel_diag]] | upstream | 0.34 |
| [[p11_fb_funnel_diag]] | sibling | 0.30 |
