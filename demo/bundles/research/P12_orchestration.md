---
kind: collaboration
id: bld_collaboration_knowledge_card
pillar: P12
llm_function: COLLABORATE
purpose: How knowledge-card-builder works in crews with other builders
pattern: each builder must know its ROLE in a team, what it RECEIVES and PRODUCES
quality: null
title: "Collaboration Knowledge Card"
version: "1.0.0"
author: n03_builder
tags: [knowledge_card, builder, examples]
tldr: "Golden and anti-examples for knowledge card construction, demonstrating ideal structure and common pitfalls."
domain: "knowledge card construction"
created: "2026-04-07"
updated: "2026-04-07"
8f: "F8_collaborate"
keywords: [knowledge card construction, collaboration knowledge card, knowledge_card, builder, examples, "### crew: new agent end-to-end", "### crew: rag pipeline setup", my role, crew compositions, content foundation]
density_score: 0.90
related:
  - bld_collaboration_agent
  - bld_collaboration_system_prompt
  - bld_collaboration_builder
  - bld_collaboration_boot_config
  - bld_architecture_kind
  - bld_collaboration_instruction
  - bld_collaboration_knowledge_index
  - bld_collaboration_agent_package
  - bld_collaboration_model_card
  - bld_collaboration_knowledge_graph
---
# Colaboração: knowledge-card-builder
## Meu Papel em Crews
Eu sou um ESPECIALISTA. Eu respondo UMA pergunta: "qual é o fato essencial e pesquisável sobre este tópico?"
Eu não defino personas de agent. Eu não configuro parâmetros de boot.
Eu destilo conhecimento em fatos atômicos para que agents e builders tenham contexto factual para decisões.
## Composições de Crew
### Crew: "Fundação de Conteúdo"
```
  1. context-doc-builder -> "escopo e contexto de domínio"
  2. knowledge-card-builder -> "fatos atômicos e pesquisáveis (densidade > 0.8)"
  3. glossary-entry-builder -> "definições de termo"
  4. few-shot-example-builder -> "exemplos de formato embasados no conhecimento"
```
### Crew: "Agent Novo de Ponta a Ponta"
```
  1. knowledge-card-builder -> "conhecimento de domínio para a expertise do agent"
  2. agent-builder -> "definição de agent moldada pelo conhecimento"
  3. instruction-builder -> "passos de execução embasados em fatos"
  4. boot-config-builder -> "configuração do provider"
  5. agent-package-builder -> "pacote implantável"
```
### Crew: "Setup de Pipeline RAG"
```
  1. knowledge-card-builder -> "conteúdo para embedding e indexação"
  2. embedding-config-builder -> "parâmetros do modelo de embedding"
  3. knowledge-index-builder -> "configuração do índice de busca"
```
## Protocolo de Handoff
### Eu Recebo
- seeds: nome do tópico, domínio, material-fonte ou brief de pesquisa
- opcional: meta de densidade, classificação (domain_kc ou meta_kc), cards relacionados
### Eu Produzo
- artefato knowledge_card (.md + frontmatter .yaml, máx. 5KB, densidade > 0.8)
- commitado em: `cex/P01/examples/p01_kc_{topic}.md`
### Eu Sinalizo
- signal: complete (com a nota de qualidade do QUALITY_GATES)
- se quality < 8.0: signal retry com os motivos da falha
## Builders dos Quais Eu Dependo
Nenhum -- builder independente (camada 0). Knowledge cards são destilados a partir de material-fonte.
## Builders Que Dependem de Mim
| Builder | Por quê |
|---------|-----|
| agent-builder | A expertise do agent é embasada em knowledge cards |
| axiom-builder | Axiomas são formalizados a partir de fatos destilados |
| context-doc-builder | Docs de domínio referenciam fatos de knowledge card |
| knowledge-index-builder | Knowledge cards são o conteúdo primário para indexação |
| instruction-builder | Receitas referenciam conhecimento factual para precisão |


## Related Artifacts

| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[bld_collaboration_agent]] | sibling | 0.41 |
| [[bld_collaboration_system_prompt]] | sibling | 0.37 |
| [[bld_collaboration_builder]] | sibling | 0.34 |
| [[bld_collaboration_boot_config]] | sibling | 0.33 |
| [[bld_architecture_kind]] | upstream | 0.33 |
| [[bld_collaboration_instruction]] | sibling | 0.32 |
| [[bld_collaboration_knowledge_index]] | sibling | 0.32 |
| [[bld_collaboration_agent_package]] | sibling | 0.31 |
| [[bld_collaboration_model_card]] | sibling | 0.31 |
| [[bld_collaboration_knowledge_graph]] | sibling | 0.30 |
