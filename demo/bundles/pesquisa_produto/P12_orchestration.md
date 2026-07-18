---
kind: collaboration
id: bld_collaboration_knowledge_card
pillar: P12
llm_function: COLLABORATE
purpose: Como o knowledge-card-builder trabalha em crews (equipes) com outros builders
pattern: todo builder precisa conhecer seu PAPEL em uma equipe, o que ele RECEBE e o que PRODUZ
quality: null
title: "Colaboração: Knowledge Card"
version: "1.0.0"
author: n03_builder
tags: [knowledge_card, builder, examples]
tldr: "Exemplos ideais e contraexemplos para a construção de knowledge cards, demonstrando estrutura ideal e erros comuns."
domain: "construção de knowledge_card"
created: "2026-04-07"
updated: "2026-04-07"
8f: "F8_collaborate"
keywords: [construção de knowledge_card, colaboração knowledge card, knowledge_card, builder, examples, "### crew: agente novo ponta-a-ponta", "### crew: configuração de pipeline rag", meu papel, composições de equipe, fundação de conteúdo]
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
  - bld_collaboration_knowledge_index
  - bld_collaboration_knowledge_graph
---
# Colaboração: knowledge-card-builder
## Meu Papel em Equipes
Eu sou um ESPECIALISTA. Eu respondo UMA pergunta: "qual é o fato essencial e pesquisável sobre este tópico?"
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
### Equipe: "Agent Novo Ponta a Ponta"
```
  1. knowledge-card-builder -> "conhecimento de domínio para a expertise do agent"
  2. agent-builder -> "definição de agent moldada pelo conhecimento"
  3. instruction-builder -> "passos de execução embasados em fatos"
  4. boot-config-builder -> "configuração do provider"
  5. agent-package-builder -> "pacote implantável"
```
### Equipe: "Configuração do Pipeline RAG"
```
  1. knowledge-card-builder -> "conteúdo para embeddar e indexar"
  2. embedding-config-builder -> "parâmetros do modelo de embedding"
  3. knowledge-index-builder -> "configuração do índice de busca"
```
## Protocolo de Handoff
### Eu Recebo
- seeds: nome do tópico, domain, material de origem ou briefing de pesquisa
- opcional: meta de densidade, classificação (domain_kc ou meta_kc), cards relacionados
### Eu Produzo
- artifact knowledge_card (.md + frontmatter .yaml, máximo 5KB, densidade > 0.8)
- commitado em: `cex/P01/examples/p01_kc_{topic}.md`
### Eu Sinalizo
- signal: complete (com a nota de qualidade do QUALITY_GATES)
- se quality < 8.0: signal retry com os motivos da falha
## Builders dos Quais Dependo
Nenhum -- builder independente (layer 0). Knowledge cards são destilados a partir de material de origem.
## Builders Que Dependem de Mim
| Builder | Por quê |
|---------|-----|
| agent-builder | A expertise do agent é embasada em knowledge cards |
| axiom-builder | Axiomas são formalizados a partir de fatos destilados |
| context-doc-builder | Documentos de domínio referenciam fatos de knowledge card |
| knowledge-index-builder | Knowledge cards são o conteúdo primário para indexação |
| instruction-builder | Roteiros referenciam conhecimento factual para precisão |


## Related Artifacts

| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[bld_collaboration_agent]] | sibling | 0.40 |
| [[bld_collaboration_system_prompt]] | sibling | 0.36 |
| [[bld_architecture_kind]] | upstream | 0.34 |
| [[bld_collaboration_builder]] | sibling | 0.33 |
| [[bld_collaboration_boot_config]] | sibling | 0.33 |
| [[bld_collaboration_instruction]] | sibling | 0.31 |
| [[bld_collaboration_agent_package]] | sibling | 0.30 |
| [[bld_collaboration_model_card]] | sibling | 0.30 |
| [[bld_collaboration_knowledge_index]] | sibling | 0.30 |
| [[bld_collaboration_knowledge_graph]] | sibling | 0.29 |
