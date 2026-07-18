---
kind: architecture
id: bld_architecture_research_pipeline
pillar: P08
llm_function: CONSTRAIN
purpose: Mapa de componentes do research pipeline -- 7 etapas, multi-modelo, fluxo de dados
quality: null
title: "Arquitetura: Pipeline de Pesquisa"
version: "1.0.0"
author: n03_builder
tags:
  - "research_pipeline"
  - "builder"
  - "examples"
tldr: "Exemplos-modelo e anti-exemplos para a construção de pipelines de pesquisa, demonstrando a estrutura ideal e as armadilhas mais comuns."
domain: "construção de pipeline de pesquisa"
created: "2026-04-07"
updated: "2026-04-07"
8f: "F1_constrain"
keywords:
  - "data flow"
  - "research pipeline construction"
  - "architecture research pipeline"
  - "research_pipeline"
  - "builder"
  - "examples"
  - "## data flow"
  - "stage pipeline"
  - "component inventory"
  - "related artifacts"
density_score: 0.90
related:
  - research-pipeline-builder
---
# Arquitetura: research_pipeline no CEX

## Pipeline de 7 Etapas
```
QUERY → S1 INTENT (classify) → S2 PLAN/STORM (5 perspectives × 5-7 sub-Qs)
  → S3 RETRIEVE/CRAG (30+ sources parallel, quality gate ≥0.7)
  → S4 RESOLVE (entity dedup cross-source)
  → S5 SCORE (Gartner 7-dim per result)
  → S6 SYNTHESIZE/GoT (domain models merge data)
  → S7 VERIFY/CRITIC (thinking model, max 3 iter)
  → REPORT [HTML + PPTX + JSON]
```

## Fluxo de Dados
```
config.yaml ──► intent_classifier ──► storm_planner
                                          │
                              5 perspectives × 5-7 Qs
                                          │
                            ┌─────────────┼─────────────┐
                            ▼             ▼             ▼
                     inbound_src    search_src    outbound_src
                     (marketplace)  (web search)  (social/review)
                            │             │             │
                            └──────┬──────┘─────────────┘
                                   ▼
                           crag_scorer (0.0-1.0)
                                   │ (≥0.7 pass)
                                   ▼
                          entity_resolver (dedup)
                                   │
                                   ▼
                         gartner_scorer (7-dim)
                                   │
                                   ▼
                        got_synthesizer (multi-model)
                                   │
                                   ▼
                         critic_verifier (max 3 iter)
                                   │
                            ┌──────┼──────┐
                            ▼      ▼      ▼
                          HTML   PPTX   JSON
```

## Inventário de Componentes
| Componente | Etapa | Modelo | Externo |
|-----------|-------|-------|----------|
| intent_classifier | S1 | regex+embed | nenhum |
| storm_planner | S2 | raciocínio | LLM API |
| parallel_retriever | S3 | APIs | 30+ fontes |
| crag_scorer | S3 | rápido | LLM API |
| entity_resolver | S4 | determinístico | Embedding API |
| gartner_scorer | S5 | rápido | LLM API |
| got_synthesizer | S6 | multi-modelo | Multi-LLM |
| critic_verifier | S7 | raciocínio | Modelo de raciocínio |
| report_renderer | Out | template | Jinja2 |

## Posição no CEX
| Camada | Localização |
|-------|----------|
| Template + Exemplos | P04_tools/{templates,examples}/ |
| Instância de nucleus | N01_intelligence/{tools,knowledge,orchestration}/ |
| Config da empresa | _instances/{co}/N01_intelligence/ |

## Limites
| Este builder | Outro builder |
|-------------|---------------|
| Arquitetura do pipeline | Runtime Python → cli-tool-builder |
| Catálogo de fontes | Código de cliente de API → api-client-builder |
| Schema de config | Schema de banco de dados → db-connector-builder |
| Estrutura do relatório | HTML/CSS → formatter-builder |

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| p04_cli_research_pipeline_n01 | upstream | 0.33 |
| [[bld_prompt_research_pipeline]] | upstream | 0.32 |
| [[research-pipeline-builder]] | upstream | 0.30 |
| [[bld_orchestration_research_pipeline]] | downstream | 0.30 |
| p02_agent_research_pipeline_intelligence | upstream | 0.26 |
