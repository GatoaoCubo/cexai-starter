---
kind: collaboration
id: bld_collaboration_research_pipeline
pillar: P12
llm_function: COLLABORATE
purpose: Como o research-pipeline-builder atua em crews com outros builders
pattern: cada builder precisa saber seu PAPEL, o que RECEBE e o que PRODUZ
quality: null
title: "Colaboração: Pipeline de Pesquisa"
version: "1.0.0"
author: n03_builder
tags: [research_pipeline, builder, examples]
tldr: "Exemplos-modelo e anti-exemplos para a construção de pipelines de pesquisa, demonstrando a estrutura ideal e as armadilhas mais comuns."
domain: "construção de pipeline de pesquisa"
created: "2026-04-07"
updated: "2026-04-07"
8f: "F8_collaborate"
keywords: [research pipeline construction, collaboration research pipeline, research_pipeline, builder, examples, "### crew: research → content → publish", my role, crew compositions, market intelligence end, handoff protocol]
density_score: 0.90
related:
  - research-pipeline-builder
---
# Colaboração: research-pipeline-builder

## Meu Papel em Crews
Eu sou um ESPECIALISTA. Eu respondo a UMA pergunta: "como coletamos, pontuamos, sintetizamos e verificamos inteligência de mercado de múltiplas fontes de ponta a ponta?"
Eu não escrevo clientes de API. Eu não gero conteúdo. Eu não faço deploy de serviços.
Eu produzo a arquitetura do pipeline + o schema de config para que os builders posteriores implementem e façam o deploy.

## Composições de Crew

### Crew: "Inteligência de Mercado de Ponta a Ponta"
```
1. research-pipeline-builder → "7-stage pipeline architecture + config + quality gates"
2. knowledge-card-builder    → "domain knowledge cards from research output"
3. api-client-builder        → "Python clients for each data source"
4. cli-tool-builder          → "orchestrator CLI that runs the pipeline"
5. formatter-builder         → "HTML/PPTX report templates"
6. spawn-config-builder      → "cron deployment for scheduled research"
```

### Crew: "Pesquisa → Conteúdo → Publicação"
```
1. research-pipeline-builder → "collect market intelligence"
2. prompt-template-builder   → "turn research into content briefs"
3. social-publisher-builder  → "publish content to social platforms"
```

## Protocolo de Handoff
| Eu recebo de | Dados | Formato |
|---------------|------|--------|
| Usuário / N07 | Query de pesquisa + requisitos do nicho | Handoff de missão .md |
| knowledge-card-builder | Contexto de domínio para as perspectivas STORM | Artefato KC |

| Eu envio para | Dados | Formato |
|----------|------|--------|
| N02_marketing | Resultados da pesquisa para a estratégia de conteúdo | JSON + signal |
| N06_commercial | Inteligência de precificação, dados de concorrentes | JSON + signal |
| N01_intelligence | Relatório de mercado verificado | HTML/PPTX/JSON |
| cli-tool-builder | Spec do pipeline para implementação | Architecture .md |
| api-client-builder | Specs de API das fontes para o código do cliente | Tools .md |

## Roteamento de Nucleus
| Fase | Nucleus | Por que |
|-------|---------|-----|
| Design do pipeline | N03 (engenharia) | Trabalho de arquitetura + schema |
| Execução da pesquisa | N01 (intelligence) | Expertise de domínio, conhecimento de fontes |
| Conteúdo a partir da pesquisa | N02 (marketing) | Transforma insights em conteúdo |
| Precificação a partir da pesquisa | N06 (comercial) | Estratégia de precificação de mercado |
| Deploy do pipeline | N05 (operações) | Cron + monitoramento |

## Relação com o Social Publisher
```
Research Pipeline (INPUT)        Social Publisher (OUTPUT)
  collect → score → verify  →→→    generate → schedule → publish
  N01_intelligence               N02_marketing
  STORM+CRAG+CRITIC              Calendar + API + Rotation
```
Juntos, eles formam o ciclo: PESQUISA → DECISÃO → CONTEÚDO → PUBLICAÇÃO.

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| bld_collaboration_social_publisher | sibling | 0.40 |
| [[research-pipeline-builder]] | upstream | 0.34 |
| n01_dr_research_pipeline | related | 0.34 |
| p04_cli_research_pipeline_n01 | upstream | 0.31 |
| [[bld_orchestration_content_monetization]] | sibling | 0.30 |
