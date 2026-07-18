---
kind: collaboration
id: bld_collaboration_research_universe
pillar: P12
llm_function: COLLABORATE
purpose: Como o research-universe-builder trabalha em crews com outros builders
quality: null
title: "Collaboration Research Universe"
version: "1.0.0"
author: n03_builder
tags: [research_universe, builder, collaboration]
tldr: "Como o research-universe-builder trabalha em crews com outros builders"
domain: "construção de research_universe"
created: "2026-07-17"
updated: "2026-07-17"
8f: "F8_collaborate"
keywords: [collaboration research universe, papel na crew, recebe de, produz para, research_universe, builder, collaboration, boundary, handoff]
density_score: 0.88
related:
  - bld_collaboration_competitive_matrix
  - bld_collaboration_knowledge_card
  - p02_agent_web_researcher
---
## Papel na Crew
Recebe uma semente (produto, marca, CNPJ, empresa, palavra-chave ou `store:id`), roda as 6 trilhas independentes e devolve um relatório unificado com status honesto por trilha. É tipicamente o PRIMEIRO builder a tocar uma semente nova -- outros builders de decisão consomem o relatório dele como contexto, não o contrário.

## Recebo De
| Builder/Fonte | O Que | Formato |
|----------------|--------------------|------------|
| usuário (intake direto) | Semente + tipo + trilhas priorizadas (opcional) | Texto livre |
| knowledge_card | Contexto de domínio/setor previamente destilado, se existir | Markdown |
| dado colado pelo usuário | Print de app store, texto do Reclame Aqui, resultado de consulta de CNPJ | Texto/imagem colada na conversa |

## Produzo Para
| Builder | O Que | Formato |
|----------------|-----------------------|------------|
| competitive_matrix (bundle `competitor_benchmark`) | Contexto de firmografia + reputação + sinal social de um concorrente | Markdown (research_universe) |
| opportunity_matrix (bundle `sourcing_opportunity`) | Sinal de reputação + firmografia de um fornecedor/oportunidade | Markdown (research_universe) |
| sales_playbook / equipe comercial | Perguntas multi-perspectiva + sentimento em PT para qualificação | Markdown (research_universe) |
| research_pipeline (bundle `leadgen`) | Firmografia + sinal social de uma lista de leads, um por vez | Markdown (research_universe) |

## Crew Compositions
### Crew: "Due Diligence de Fornecedor"
```
  1. research-universe-builder -> "firmografia + reputação + sinal social do fornecedor"
  2. opportunity_matrix-builder -> "avaliação de oportunidade usando o relatório acima como insumo"
```
### Crew: "Preparação de Venda Competitiva"
```
  1. research-universe-builder -> "sinal social + reputação + perguntas multi-perspectiva do concorrente"
  2. competitive_matrix-builder -> "battle card usando o relatório acima como contexto de partida"
```

## Limite (Boundary)
NÃO produz matriz competitiva formal (feature parity, battle card) -- isso é escopo do `competitive_matrix`-builder. NÃO decide se uma oportunidade é boa ou ruim -- isso é escopo do `opportunity_matrix`-builder. NÃO gera copy de vendas ou de marketing -- apenas fornece o contexto factual multi-fonte que esses outros builders consomem.

## Handoff Protocol
### Recebo
- Semente (obrigatório) + tipo de semente (ou o próprio agente classifica)
- Opcional: trilhas priorizadas, dado já coletado pelo usuário

### Produzo
- Artefato `research_universe` (.md, max 6144 bytes, 6 trilhas + tabela de status + procedência)
- Salvo como: `p01_ru_{{slug}}.md`

### Sinalizo
- Sinal: completo (com `coverage_score` e pontuação do gate de qualidade P07)
- Se `coverage_score` < 0.5: sinal inclui aviso explícito de cobertura baixa

## Builders Que Dependem de Mim
| Builder | Por que |
|---------|---------|
| competitive_matrix-builder | Usa firmografia/reputação/sinal social como ponto de partida do battle card |
| opportunity_matrix-builder | Usa firmografia/reputação para avaliar risco de um fornecedor/oportunidade |
| research_pipeline (leadgen) | Usa o relatório como enriquecimento de um lead individual |

## Artefatos Relacionados
| Artefato | Relacionamento | Pontuação |
|----------|-------------|-------|
| [[bld_collaboration_competitive_matrix]] | sibling | 0.36 |
| [[bld_collaboration_knowledge_card]] | sibling | 0.30 |
| [[p02_agent_web_researcher]] | upstream | 0.24 |
| [[research-universe-builder]] | upstream | 0.22 |
