---
kind: knowledge_card
id: bld_knowledge_card_research_pipeline
pillar: P01
llm_function: INJECT
purpose: Conhecimento de domínio para o design de pipelines de pesquisa -- padrões STORM, CRAG, CRITIC
sources: Artigo STORM (Stanford), artigo CRAG (Yan et al 2024), artigo CRITIC (Gou et al 2024), sistema de produção ACME (13,908 linhas)
quality: null
title: "Cartão de Conhecimento: Pipeline de Pesquisa"
version: "1.0.0"
author: n03_builder
tags: [research_pipeline, builder, examples]
tldr: "Exemplos-modelo e anti-exemplos para a construção de pipelines de pesquisa, demonstrando a estrutura ideal e as armadilhas mais comuns."
domain: "construção de pipeline de pesquisa"
created: "2026-04-07"
updated: "2026-04-07"
8f: "F3_inject"
keywords: [critic patterns, research pipeline construction, knowledge card research pipeline, research_pipeline, builder, examples, domain knowledge, executive summary, core patterns, corrective retrieval]
density_score: 0.90
related:
  - research-pipeline-builder
---
# Conhecimento de Domínio: research_pipeline

## Resumo Executivo
Um research pipeline é um sistema orientado por configuração que coleta, pontua, sintetiza e verifica inteligência de mercado a partir de 30+ fontes. Construído sobre três padrões acadêmicos: **STORM** (planejamento de queries multi-perspectiva, de Stanford), **CRAG** (RAG corretivo com gates de qualidade por fonte) e **CRITIC** (auto-verificação iterativa com modelos de raciocínio). O research-pipeline-builder do CEX destila um sistema de produção de 13,908 linhas em um padrão reutilizável de 7 etapas.

## Os 3 Padrões Centrais

### STORM (Survey of Topic via Retrieval and Organization of Multi-perspective)
- **Artigo**: Stanford/UW 2024 -- gera artigos com qualidade de Wikipedia a partir do zero
- **Adaptação CEX**: gera 5 perspectivas de especialista por query de pesquisa, cada uma decomposta em 5-7 subperguntas atômicas. Isso multiplica a cobertura de retrieval em 25-35x em relação a uma query única.
- **Por que funciona**: pesquisa de ângulo único perde pontos cegos da concorrência, dores do comprador e tendências de mercado. A abordagem multi-perspectiva do STORM cobre todos os ângulos sistematicamente.

### CRAG (Corrective Retrieval-Augmented Generation)
- **Artigo**: Yan et al 2024 -- avalia a qualidade do retrieval antes de usa-lo
- **Adaptação CEX**: todo resultado recuperado recebe uma nota de qualidade (0.0-1.0). Abaixo do limiar (padrão 0.7) → aciona uma fonte alternativa ou descarta. Evita que dados de baixa qualidade poluam a síntese.
- **Dimensões de qualidade**: relevância, atualidade, completude, confiabilidade.

### CRITIC (Self-Correcting with Tool-Interactive Critique)
- **Artigo**: Gou et al 2024 -- o LLM verifica a própria saída e corrige com ferramentas
- **Adaptação CEX**: a Etapa 7 usa um modelo de raciocínio (o4-mini) para verificar a síntese contra os dados-fonte. Captura alucinações, erros numéricos e contradições. Máximo de 3 iterações -- ganhos marginais depois disso.

## Pipeline de 7 Etapas
| Etapa | Nome | Modelo | Entrada | Saída |
|-------|------|--------|---------|-------|
| 1 | INTENT | Classificador rápido | Query do usuário | domínio, verbo, complexidade, rota |
| 2 | PLAN (STORM) | Modelo de raciocínio | Intent + perspectivas | 25-35 subperguntas |
| 3 | RETRIEVE (CRAG) | APIs + scraping | Subperguntas | Resultados pontuados (≥0.7) |
| 4 | RESOLVE | Determinístico | Resultados brutos | Entidades deduplicadas |
| 5 | SCORE | Modelo rápido | Entidades | Listagens pontuadas (7 dimensões Gartner) |
| 6 | SYNTHESIZE (GoT) | Modelos de domínio | Dados pontuados | Análise estruturada |
| 7 | VERIFY (CRITIC) | Modelo de raciocínio | Síntese + fontes | Relatório verificado |

## Antipadrões
| Antipadrão | Por Que Falha |
|-------------|-------------|
| Retrieval de query única | Perde 80% dos dados relevantes (sem diversidade de perspectiva) |
| Sem gate de qualidade no retrieval | Entra lixo, sai lixo; o CRAG evita isso |
| Síntese com modelo único | Domínios diferentes precisam de modelos diferentes; Flash para extração, GPT para raciocínio |
| Sem etapa de verificação | 15-20% da síntese de LLM contém alucinações; o CRITIC as captura |
| Orçamento de scraping ilimitado | Créditos de Firecrawl/Serper acabam rápido; tetos de orçamento são essenciais |
| Lista de fontes hardcoded | Cada nicho precisa de fontes diferentes; a config precisa ser flexível |

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[research-pipeline-builder]] | downstream | 0.49 |
| p02_agent_research_pipeline_intelligence | downstream | 0.46 |
| [[kc_research_pipeline]] | sibling | 0.44 |
| [[kc_research_methods]] | sibling | 0.43 |
| [[bld_prompt_research_pipeline]] | downstream | 0.41 |
