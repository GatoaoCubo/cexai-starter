---
kind: collaboration
id: bld_collaboration_knowledge_card
pillar: P12
llm_function: COLLABORATE
purpose: Como o knowledge-card-builder trabalha em equipes (crews) com outros builders
pattern: todo builder deve saber seu PAPEL numa equipe, o que RECEBE e o que PRODUZ
quality: null
title: "Collaboration Knowledge Card"
version: "1.0.0"
author: n03_builder
tags: [knowledge_card, builder, examples]
tldr: "Golden and anti-examples for knowledge card construction, demonstrating ideal structure and common pitfalls."
domain: "construção de knowledge_card"
created: "2026-04-07"
updated: "2026-04-07"
8f: "F8_collaborate"
keywords: [knowledge card construction, collaboration knowledge card, knowledge_card, builder, examples, "### crew: new agent end-to-end", "### crew: rag pipeline setup", my role, crew compositions, content foundation]
density_score: 0.90
related:
  - bld_collaboration_agent
  - bld_collaboration_system_prompt
  - bld_architecture_kind
  - bld_collaboration_builder
  - bld_collaboration_boot_config
  - bld_collaboration_instruction
  - bld_collaboration_agent_package
  - bld_collaboration_model_card
  - bld_collaboration_kind
  - bld_collaboration_retriever
---
# Collaboration: knowledge-card-builder
## Meu Papel nas Equipes
Eu sou um ESPECIALISTA. Eu respondo a UMA pergunta: "qual é o fato essencial e pesquisável sobre este tópico?"
Eu não defino personas de agent. Eu não configuro parâmetros de boot.
Eu destilo conhecimento em fatos atômicos para que agents e builders tenham contexto factual para decisões.
## Composições de Equipe
### Equipe: "Fundação de Conteúdo"
```
  1. context-doc-builder -> "escopo e contexto de domínio"
  2. knowledge-card-builder -> "fatos atômicos pesquisáveis (densidade > 0.8)"
  3. glossary-entry-builder -> "definições de termos"
  4. few-shot-example-builder -> "exemplos de formato baseados em conhecimento"
```
### Equipe: "Novo Agent de Ponta a Ponta"
```
  1. knowledge-card-builder -> "conhecimento de domínio para a expertise do agent"
  2. agent-builder -> "definição de agent moldada pelo conhecimento"
  3. instruction-builder -> "passos de execução baseados em fatos"
  4. boot-config-builder -> "configuração de provider"
  5. agent-package-builder -> "pacote implantável"
```
### Equipe: "Configuração do Pipeline RAG"
```
  1. knowledge-card-builder -> "conteúdo para embedding e indexação"
  2. embedding-config-builder -> "parâmetros do modelo de embedding"
  3. knowledge-index-builder -> "configuração do índice de busca"
```
## Protocolo de Handoff
### Eu Recebo
- seeds: nome do tópico, domínio, material de origem ou brief de pesquisa
- opcional: meta de densidade, classificação (domain_kc ou meta_kc), cards relacionados
### Eu Produzo
- artefato knowledge_card (.md + frontmatter .yaml, max 5KB, densidade > 0.8)
- commitado em: `cex/P01/examples/p01_kc_{topic}.md`
### Eu Sinalizo
- signal: complete (com a pontuação de qualidade do QUALITY_GATES)
- se quality < 8.0: signal retry com os motivos da falha
## Builders dos Quais Dependo
Nenhum -- builder independente (layer 0). Knowledge_cards são destilados a partir de material de origem.
## Builders Que Dependem de Mim
| Builder | Por Quê |
|---------|-----|
| agent-builder | A expertise do agent é embasada em knowledge_cards |
| axiom-builder | Axiomas são formalizados a partir de fatos destilados |
| context-doc-builder | Docs de domínio referenciam fatos de knowledge_card |
| knowledge-index-builder | Knowledge_cards são o conteúdo primário para indexação |
| instruction-builder | Recipes referenciam conhecimento factual para precisão |

## Artefatos Relacionados

| Artefato | Relacionamento | Pontuação |
|----------|-------------|-------|
| [[bld_collaboration_agent]] | irmão | 0.39 |
| [[bld_collaboration_system_prompt]] | irmão | 0.35 |
| [[bld_architecture_kind]] | a montante | 0.34 |
| [[bld_collaboration_builder]] | irmão | 0.33 |
| [[bld_collaboration_boot_config]] | irmão | 0.32 |
| [[bld_collaboration_instruction]] | irmão | 0.31 |
| [[bld_collaboration_agent_package]] | irmão | 0.30 |
| [[bld_collaboration_model_card]] | irmão | 0.30 |
| [[bld_collaboration_kind]] | irmão | 0.29 |
| [[bld_collaboration_retriever]] | irmão | 0.29 |
