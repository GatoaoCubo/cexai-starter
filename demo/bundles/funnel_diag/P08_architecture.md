---
kind: architecture
id: bld_architecture_funnel_diag
pillar: P08
llm_function: CONSTRAIN
purpose: Mapa de componentes do funnel_diag -- inventário, dependências, posição arquitetural
quality: null
title: "Arquitetura: Diagnóstico de Funil"
version: "1.0.0"
author: n03_builder
tags: [funnel_diag, tool_card, builder, architecture]
tldr: "Inventário dos 12 ISOs, grafo de dependência com o schema/output_template, e limite claro entre funnel_diag e roi_calculator/pricing."
domain: "diagnóstico de funil (funnel_diag)"
created: "2026-07-17"
updated: "2026-07-17"
8f: "F1_constrain"
keywords: [inventário de componentes, grafo de dependência, limite de escopo, funnel_diag]
density_score: 0.88
related:
  - bld_knowledge_card_funnel_diag
  - roi-calculator-builder
---
## Inventário de Componentes
| Nome do ISO | Papel | Pilar | Status |
|---|---|---|---|
| bld_knowledge_card_funnel_diag | Conhecimento de domínio (estágios, benchmarks, ICE/RICE) | P01 | Ativo |
| funnel-diagnostic-builder | Identidade, persona, regras | P02 | Ativo |
| bld_instruction_funnel_diag | Processo de produção em 3 fases | P03 | Ativo |
| bld_tools_funnel_diag | Fontes de dados + ferramentas de pipeline | P04 | Ativo |
| bld_output_template_funnel_diag | Template de saída com {{vars}} | P05 | Ativo |
| bld_schema_funnel_diag | Schema formal -- fonte única da verdade | P06 | Ativo |
| p11_qg_funnel_diag | Gate de qualidade HARD + SOFT | P11 | Ativo |
| bld_architecture_funnel_diag | Este arquivo -- mapa de componentes | P08 | Ativo |
| bld_config_funnel_diag | Nomenclatura, caminhos, limites | P09 | Ativo |
| p10_mem_funnel_diag_builder | Padrões e armadilhas aprendidos | P10 | Ativo |
| p11_fb_funnel_diag | Anti-padrões e protocolo de correção | P11 | Ativo |
| bld_collaboration_funnel_diag | Papel em crews, handoffs | P12 | Ativo |

## Grafo de Dependência
```
bld_knowledge_card_funnel_diag --informa--> funnel-diagnostic-builder
funnel-diagnostic-builder      --segue-->    bld_instruction_funnel_diag
bld_instruction_funnel_diag    --usa-->      bld_schema_funnel_diag
bld_schema_funnel_diag         --deriva-->   bld_output_template_funnel_diag
bld_output_template_funnel_diag --validado_por--> p11_qg_funnel_diag
p11_qg_funnel_diag             --alimenta-->  p11_fb_funnel_diag
```
| De | Para | Tipo | Dado |
|---|---|---|---|
| bld_knowledge_card_funnel_diag | funnel-diagnostic-builder | fluxo_de_dado | estágios, benchmarks, métodos de scoring |
| bld_instruction_funnel_diag | bld_schema_funnel_diag | fluxo_de_dado | campos obrigatórios do artefato final |
| bld_schema_funnel_diag | bld_output_template_funnel_diag | fluxo_de_dado | estrutura de frontmatter + corpo |
| bld_output_template_funnel_diag | p11_qg_funnel_diag | fluxo_de_dado | artefato produzido -> validação |

## Tabela de Limite (Boundary)
| funnel_diag É | funnel_diag NÃO É |
|---|---|
| Diagnóstico -- aponta ONDE está o vazamento e QUAL corrigir primeiro | Cálculo financeiro detalhado (payback, NPV) -- isso é `roi_calculator` |
| Ranking por impacto/esforço (ICE/RICE) | Execução da correção (copy, landing page, automação) |
| Tool_card com 5 estágios fixos (atrair/engajar/converter/reter/expandir) | Análise de um único estágio isolado |
| Honesto sobre lacuna de dado (`[A CONFIRMAR]`) | Estimativa disfarçada de medição real |

## Mapa de Camadas
| Camada | Componentes | Propósito |
|---|---|---|
| Identidade | funnel-diagnostic-builder, bld_schema_funnel_diag | Nomear, classificar e restringir o artefato |
| Conteúdo | bld_knowledge_card_funnel_diag, bld_output_template_funnel_diag | Carregar o framework e a estrutura de saída |
| Validação | p11_qg_funnel_diag, p11_fb_funnel_diag | Garantir cobertura dos 5 estágios e zero fabricação |
| Colaboração | bld_collaboration_funnel_diag | Handoff para roi_calculator, pricing, sales_playbook |

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[bld_knowledge_card_funnel_diag]] | sibling | 0.36 |
| [[roi-calculator-builder]] | sibling | 0.32 |
| [[bld_collaboration_funnel_diag]] | sibling | 0.30 |
