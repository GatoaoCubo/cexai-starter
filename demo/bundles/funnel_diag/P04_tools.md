---
kind: tools
id: bld_tools_funnel_diag
pillar: P04
llm_function: CALL
purpose: Ferramentas e fontes de dados disponíveis para a produção do tool_card de funnel_diag
quality: null
title: "Ferramentas: Diagnóstico de Funil"
version: "1.0.0"
author: n03_builder
tags: [funnel_diag, tool_card, builder, tools]
tldr: "Fontes de dados de analytics/CRM (GA4, Mixpanel, RD Station, HubSpot, Stripe) + ferramentas de pipeline CEXAI (compile/score/retriever/doctor)."
domain: "diagnóstico de funil (funnel_diag)"
created: "2026-07-17"
updated: "2026-07-17"
8f: "F5_call"
keywords: [fontes de dados de funil, google analytics, RD Station, ferramentas de produção, funnel_diag]
density_score: 0.88
related:
  - bld_knowledge_card_funnel_diag
  - bld_output_template_funnel_diag
---
# Ferramentas: funnel_diag

## Fontes de Dados (o usuário traz; o agente não tem acesso live a nenhuma)
| Fonte | Estágio(s) que informa | Dado típico |
|---|---|---|
| Google Analytics 4 (GA4) | Atrair, Engajar | Sessões, origem de tráfego, taxa de engajamento |
| Mixpanel / Amplitude | Engajar, Converter | Funis de produto, ativação, retenção por cohort |
| RD Station / HubSpot | Atrair, Converter | Leads, MQL/SQL, taxa de conversão por campanha |
| Stripe / ChartMogul | Converter, Reter, Expandir | MRR, churn, upsell, LTV |
| Hotjar / FullStory | Engajar, Converter | Gravações de sessão, heatmap, taxa de abandono |

Este agente **não chama nenhuma dessas ferramentas diretamente** -- ele opera 100% sobre o que o usuário cola no `intent` ou anexa à conversa. Não há Action/plugin de coleta live nesta capacidade (diferente de bundles com tiers de scraping).

## Ferramentas de Produção (pipeline CEXAI)
| Ferramenta | Propósito | Quando |
|---|---|---|
| cex_compile.py | Compila o artefato .md produzido para .yaml | F8 COLLABORATE |
| cex_score.py | Score de qualidade do artefato (5 dimensões) | F7 GOVERN |
| cex_retriever.py | Recupera diagnósticos de funil similares para reuso | F3 INJECT |
| cex_doctor.py | Checa a saúde/completude dos 12 ISOs do builder | F7 GOVERN |

## Permissões de Ferramenta
| Categoria | Ferramentas | Status |
|---|---|---|
| PERMITIDO | Read, Write, Edit, Bash, Glob, Grep | Explicitamente permitido |
| NEGADO | Chamada de API live (analytics/CRM) | Fora do escopo desta capacidade |
| EFETIVO | Leitura/escrita de artefato local | PERMITIDO menos NEGADO |

## Propriedades
| Propriedade | Valor |
|---|---|
| Kind | `tools` |
| Pilar | P04 |
| Domínio | diagnóstico de funil (funnel_diag) |
| Pipeline | 8F (F1-F8) |
| Scorer | cex_score.py |
| Compilador | cex_compile.py |
| Meta de qualidade | 9.0+ |
| Meta de densidade | 0.85+ |

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[bld_knowledge_card_funnel_diag]] | sibling | 0.40 |
| [[bld_output_template_funnel_diag]] | sibling | 0.38 |
| [[bld_config_funnel_diag]] | sibling | 0.32 |
