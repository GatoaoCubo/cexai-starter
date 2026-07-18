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
  - bld_architecture_kind
  - bld_collaboration_system_prompt
  - bld_collaboration_builder
  - bld_collaboration_boot_config
  - bld_collaboration_instruction
  - bld_collaboration_agent_package
  - bld_collaboration_model_card
  - bld_collaboration_kind
  - bld_collaboration_retriever
---
# Colaboracao: knowledge-card-builder
## Meu Papel nas Crews
Eu sou um ESPECIALISTA. Eu respondo a UMA pergunta: "qual e o fato essencial e pesquisavel sobre este topico?"
Eu nao defino personas de agent. Eu nao configuro parametros de boot.
Eu destilo conhecimento em fatos atomicos para que agents e builders tenham contexto factual para decisoes.
## Composicoes de Crew
### Crew: "Fundacao de Conteudo"
```
  1. context-doc-builder -> "escopo e contexto de dominio"
  2. knowledge-card-builder -> "fatos atomicos pesquisaveis (densidade > 0.8)"
  3. glossary-entry-builder -> "definicoes de termos"
  4. few-shot-example-builder -> "exemplos de formato fundamentados em conhecimento"
```
### Crew: "Novo Agent Ponta a Ponta"
```
  1. knowledge-card-builder -> "conhecimento de dominio para a expertise do agent"
  2. agent-builder -> "definicao de agent moldada pelo conhecimento"
  3. instruction-builder -> "passos de execucao fundamentados em fatos"
  4. boot-config-builder -> "configuracao do provedor"
  5. agent-package-builder -> "pacote implantavel"
```
### Crew: "Configuracao do Pipeline de RAG"
```
  1. knowledge-card-builder -> "conteudo para embutir (embed) e indexar"
  2. embedding-config-builder -> "parametros do modelo de embedding"
  3. knowledge-index-builder -> "configuracao do indice de busca"
```
## Protocolo de Handoff
### Eu Recebo
- seeds: nome do topico, dominio, material-fonte ou briefing de pesquisa
- opcional: meta de densidade, classificacao (domain_kc ou meta_kc), cards relacionados
### Eu Produzo
- artefato knowledge_card (.md + frontmatter .yaml, maximo 5KB, densidade > 0.8)
- commitado em: `cex/P01/examples/p01_kc_{topic}.md`
### Eu Sinalizo
- sinal: complete (com a pontuacao de qualidade do QUALITY_GATES)
- se quality < 8.0: sinaliza retry com os motivos da falha
## Builders dos Quais Dependo
Nenhum -- builder independente (layer 0). Artefatos knowledge_card sao destilados a partir de material-fonte.
## Builders Que Dependem de Mim
| Builder | Por que |
|---------|-----|
| agent-builder | A expertise do agent e fundamentada em artefatos knowledge_card |
| axiom-builder | Axiomas sao formalizados a partir de fatos destilados |
| context-doc-builder | Docs de dominio referenciam fatos de artefatos knowledge_card |
| knowledge-index-builder | Artefatos knowledge_card sao o conteudo primario para indexacao |
| instruction-builder | Receitas referenciam conhecimento factual para precisao |

## Artefatos Relacionados
| Artefato | Relacionamento | Pontuacao |
|----------|-------------|-------|
| [[bld_collaboration_agent]] | irmao | 0.39 |
| [[bld_architecture_kind]] | a montante | 0.34 |
| [[bld_collaboration_system_prompt]] | irmao | 0.34 |
| [[bld_collaboration_builder]] | irmao | 0.33 |
| [[bld_collaboration_boot_config]] | irmao | 0.32 |
| [[bld_collaboration_instruction]] | irmao | 0.31 |
| [[bld_collaboration_agent_package]] | irmao | 0.30 |
| [[bld_collaboration_model_card]] | irmao | 0.30 |
| [[bld_collaboration_kind]] | irmao | 0.29 |
| [[bld_collaboration_retriever]] | irmao | 0.28 |
