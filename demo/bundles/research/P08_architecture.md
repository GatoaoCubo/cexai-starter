---
kind: architecture
id: bld_architecture_knowledge_card
pillar: P08
llm_function: CONSTRAIN
purpose: Component map of knowledge_card — inventory, dependencies, and architectural position
quality: null
title: "Architecture Knowledge Card"
version: "1.0.0"
author: n03_builder
tags: [knowledge_card, builder, examples]
tldr: "Golden and anti-examples for knowledge card construction, demonstrating ideal structure and common pitfalls."
domain: "knowledge card construction"
created: "2026-04-07"
updated: "2026-04-07"
8f: "F1_constrain"
keywords: [component map of knowledge_card, and architectural position, knowledge card construction, architecture knowledge card, knowledge_card, builder, examples, component inventory, dependency graph, boundary table]
density_score: 0.90
related:
  - bld_architecture_knowledge_index
  - knowledge-card-builder
  - bld_architecture_rag_source
---
## Inventário de Componentes
| Nome | Papel | Dono | Status |
|------|------|-------|--------|
| title | Rótulo curto e pesquisável que identifica o fato | author | obrigatório |
| body | Conteúdo do fato atômico destilado, alta densidade de informação >= 0.8 | author | obrigatório |
| domain_tags | Rótulos de tópico que habilitam o roteamento de recuperação | author | obrigatório |
| card_type | Classificação: domain_kc ou meta_kc | author | obrigatório |
| sources | Referências de origem do fato destilado | author | obrigatório |
| confidence_score | Nota de confiabilidade do fato (0.0–1.0) | author | obrigatório |
| version | Contador de revisão para atualizações do fato | author | obrigatório |
| linked_artifacts | Outros cards ou artefatos aos quais este fato se conecta | author | opcional |
| expiry_hint | Sinal de que o fato pode ficar desatualizado após uma data | author | opcional |
## Grafo de Dependências
```
rag_source     --produces--> knowledge_card
knowledge_card --queried_by--> knowledge_index
knowledge_index    --injects_into--> system_prompt
knowledge_card --informs--> few_shot_example
knowledge_card --referenced_by--> context_doc
knowledge_card --referenced_by--> agent
```
| De | Para | Tipo | Dado |
|------|----|------|------|
| rag_source | knowledge_card | data_flow | texto-fonte bruto a ser destilado |
| knowledge_card | knowledge_index | data_flow | title, body, tags para indexação BM25 e vetorial |
| knowledge_index | system_prompt | data_flow | fatos recuperados injetados no contexto do prompt |
| knowledge_card | few_shot_example | data_flow | embasamento factual para pares de entrada/saída |
| knowledge_card | context_doc | data_flow | referenciado como evidência de apoio |
| knowledge_card | agent | data_flow | conhecimento de domínio vinculado na definição do agent |
## Tabela de Fronteiras
| knowledge_card É | knowledge_card NÃO É |
|-------------------|----------------------|
| Fato atômico e pesquisável com densidade >= 0.8 | Documento de referência amplo, sem gate de densidade |
| Versionado e com atribuição de fonte | Spec de um modelo de LLM ou seus parâmetros |
| Classificado como domain_kc ou meta_kc | Entrada de definição curta (3 linhas no máximo) |
| Injetado em prompts via índice de recuperação | Ponteiro de URL externa sem conteúdo destilado |
| Corpo máximo de 5KB (alta relação sinal-ruído) | Par de demonstração de entrada/saída |
| Pode expirar quando os fatos ficam desatualizados | Identidade do agent ou definição comportamental |
## Mapa de Camadas
| Camada | Componentes | Propósito |
|-------|------------|---------|
| Identidade | title, card_type, version | Nomear, classificar e versionar o fato |
| Conteúdo | body, confidence_score, expiry_hint | Carregar o fato destilado com sinal de confiabilidade |
| Descobribilidade | domain_tags, linked_artifacts | Habilitar roteamento de recuperação e referência cruzada |
| Proveniência | sources | Rastrear o fato até sua origem |
| Consumo | knowledge_index, system_prompt | Recuperar e injetar fatos no contexto do agent em runtime |

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[bld_architecture_knowledge_index]] | sibling | 0.32 |
| [[knowledge-card-builder]] | upstream | 0.32 |
| [[kc_knowledge_card]] | upstream | 0.31 |
| [[bld_architecture_rag_source]] | sibling | 0.29 |
| p01_kc_cex_lp01_knowledge | upstream | 0.29 |
