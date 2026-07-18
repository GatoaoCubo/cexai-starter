---
kind: architecture
id: bld_architecture_knowledge_card
pillar: P08
llm_function: CONSTRAIN
purpose: Mapa de componentes do knowledge_card -- inventário, dependências, e posição arquitetural
quality: null
title: "Arquitetura: Knowledge Card"
version: "1.0.0"
author: n03_builder
tags: [knowledge_card, builder, examples]
tldr: "Exemplos ideais e contraexemplos para a construção de knowledge cards, demonstrando estrutura ideal e erros comuns."
domain: "construção de knowledge_card"
created: "2026-04-07"
updated: "2026-04-07"
8f: "F1_constrain"
keywords: [mapa de componentes do knowledge_card, posição arquitetural, construção de knowledge_card, arquitetura knowledge card, knowledge_card, builder, examples, inventário de componentes, grafo de dependências, tabela de fronteiras]
density_score: 0.90
related:
  - bld_architecture_knowledge_index
  - knowledge-card-builder
  - bld_architecture_rag_source
---
## Inventário de Componentes
| Nome | Papel | Responsável | Status |
|------|------|-------|--------|
| title | Rótulo curto e pesquisável que identifica o fato | autor | obrigatório |
| body | Conteúdo do fato destilado, alta densidade de informação >= 0.8 | autor | obrigatório |
| domain_tags | Rótulos de tópico que habilitam o roteamento de retrieval | autor | obrigatório |
| card_type | Classificação: domain_kc ou meta_kc | autor | obrigatório |
| sources | Referências de origem do fato destilado | autor | obrigatório |
| confidence_score | Nota de confiabilidade do fato (0.0-1.0) | autor | obrigatório |
| version | Contador de revisão para atualizações do fato | autor | obrigatório |
| linked_artifacts | Outros cards ou artifacts aos quais este fato se conecta | autor | opcional |
| expiry_hint | Sinal de que o fato pode ficar desatualizado após uma data | autor | opcional |
## Grafo de Dependências
```
rag_source     --produz--> knowledge_card
knowledge_card --consultado_por--> knowledge_index
knowledge_index    --injeta_em--> system_prompt
knowledge_card --informa--> few_shot_example
knowledge_card --referenciado_por--> context_doc
knowledge_card --referenciado_por--> agent
```
| De | Para | Tipo | Dado |
|------|----|------|------|
| rag_source | knowledge_card | data_flow | texto de origem bruto para destilar |
| knowledge_card | knowledge_index | data_flow | title, body, tags para indexação BM25 e vetorial |
| knowledge_index | system_prompt | data_flow | fatos recuperados injetados no contexto do prompt |
| knowledge_card | few_shot_example | data_flow | embasamento factual para pares de input/output |
| knowledge_card | context_doc | data_flow | referenciado como evidência de suporte |
| knowledge_card | agent | data_flow | conhecimento de domínio vinculado na definição do agent |
## Tabela de Fronteiras
| knowledge_card É | knowledge_card NÃO É |
|-------------------|----------------------|
| Fato atômico pesquisável com densidade >= 0.8 | Documento de referência amplo, sem gate de densidade |
| Versionado e com atribuição de fonte | Spec de um modelo de LLM ou de seus parâmetros |
| Classificado como domain_kc ou meta_kc | Entrada de definição curta (3 linhas no máximo) |
| Injetado em prompts via índice de retrieval | Ponteiro de URL externa sem conteúdo destilado |
| Corpo com no máximo 5KB (alta relação sinal-ruído) | Par de demonstração de input/output |
| Pode expirar quando os fatos ficam desatualizados | Identidade ou definição comportamental de agent |
## Mapa de Camadas
| Camada | Componentes | Propósito |
|-------|------------|---------|
| Identidade | title, card_type, version | Nomear, classificar, e versionar o fato |
| Conteúdo | body, confidence_score, expiry_hint | Carregar o fato destilado com sinal de confiabilidade |
| Descoberta | domain_tags, linked_artifacts | Habilitar roteamento de retrieval e referências cruzadas |
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
