---
kind: collaboration
id: bld_collaboration_knowledge_card
pillar: P12
llm_function: COLLABORATE
purpose: "Como o knowledge-card-builder trabalha em crews com outros builders"
pattern: "todo builder precisa saber seu PAPEL em uma equipe, o que ele RECEBE e o que ele PRODUZ"
quality: null
title: "Colaboracao: knowledge_card"
version: "1.0.0"
author: n03_builder
tags: [knowledge_card, builder, examples]
tldr: "Exemplos-modelo e anti-exemplos de construcao de knowledge_card, demonstrando estrutura ideal e armadilhas comuns."
domain: "construcao de knowledge_card"
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
  - bld_collaboration_agent_package
  - bld_collaboration_model_card
  - bld_collaboration_knowledge_index
  - bld_collaboration_knowledge_graph
---
# Colaboracao: knowledge-card-builder
## Meu Papel nas Crews
Eu sou um ESPECIALISTA. Eu respondo UMA pergunta: "qual e o fato essencial e pesquisavel sobre este topico?"
Eu nao defino personas de agent. Eu nao configuro parametros de boot.
Eu destilo conhecimento em fatos atomicos para que agents e builders tenham contexto factual para decisoes.
## Composicoes de Crew
### Crew: "Fundacao de Conteudo"
```
  1. context-doc-builder -> "escopo e contexto de dominio"
  2. knowledge-card-builder -> "fatos atomicos e pesquisaveis (densidade > 0.8)"
  3. glossary-entry-builder -> "definicoes de termo"
  4. few-shot-example-builder -> "exemplos de formato baseados no conhecimento"
```
### Crew: "Novo Agent de Ponta a Ponta"
```
  1. knowledge-card-builder -> "conhecimento de dominio para a expertise do agent"
  2. agent-builder -> "definicao de agent moldada pelo conhecimento"
  3. instruction-builder -> "passos de execucao baseados em fatos"
  4. boot-config-builder -> "configuracao de provider"
  5. agent-package-builder -> "pacote implantavel"
```
### Crew: "Configuracao de Pipeline RAG"
```
  1. knowledge-card-builder -> "conteudo para embutir (embed) e indexar"
  2. embedding-config-builder -> "parametros do modelo de embedding"
  3. knowledge-index-builder -> "configuracao do indice de busca"
```
## Protocolo de Handoff
### Eu Recebo
- seeds: nome do topico, dominio, material de origem ou brief de pesquisa
- opcional: meta de densidade, classificacao (domain_kc ou meta_kc), cards relacionados
### Eu Produzo
- artefato knowledge_card (.md + frontmatter .yaml, maximo 5KB, densidade > 0.8)
- commitado em: `cex/P01/examples/p01_kc_{topic}.md`
### Eu Sinalizo
- signal: complete (com a nota de qualidade do QUALITY_GATES)
- se quality < 8.0: signal retry com os motivos da falha
## Builders dos Quais Dependo
Nenhum -- builder independente (camada 0). Knowledge cards sao destilados a partir de material de origem.
## Builders Que Dependem de Mim
| Builder | Por que |
|---------|-----|
| agent-builder | A expertise do agent e embasada em knowledge cards |
| axiom-builder | Axiomas sao formalizados a partir de fatos destilados |
| context-doc-builder | Docs de dominio referenciam fatos de knowledge card |
| knowledge-index-builder | Knowledge cards sao o conteudo primario para indexacao |
| instruction-builder | As receitas referenciam conhecimento factual para precisao |


## Related Artifacts

| Artefato | Relacao | Pontuacao |
|----------|-------------|-------|
| [[bld_collaboration_agent]] | sibling | 0.42 |
| [[bld_collaboration_system_prompt]] | sibling | 0.37 |
| [[bld_collaboration_builder]] | sibling | 0.35 |
| [[bld_collaboration_boot_config]] | sibling | 0.34 |
| [[bld_architecture_kind]] | upstream | 0.34 |
| [[bld_collaboration_instruction]] | sibling | 0.33 |
| [[bld_collaboration_agent_package]] | sibling | 0.32 |
| [[bld_collaboration_model_card]] | sibling | 0.32 |
| [[bld_collaboration_knowledge_index]] | sibling | 0.32 |
| [[bld_collaboration_knowledge_graph]] | sibling | 0.30 |
