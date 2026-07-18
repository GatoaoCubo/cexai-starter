---
kind: architecture
id: bld_architecture_knowledge_card
pillar: P08
llm_function: CONSTRAIN
purpose: "Mapa de componentes do knowledge_card -- inventario, dependencias e posicao arquitetural"
quality: null
title: "Arquitetura: knowledge_card"
version: "1.0.0"
author: n03_builder
tags: [knowledge_card, builder, examples]
tldr: "Exemplos-modelo e anti-exemplos de construcao de knowledge_card, demonstrando estrutura ideal e armadilhas comuns."
domain: "construcao de knowledge_card"
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

## Inventario de Componentes
| Nome | Papel | Dono | Status |
|------|------|-------|--------|
| title | Rotulo curto e pesquisavel que identifica o fato | author | obrigatorio |
| body | Conteudo do fato atomico destilado, densidade de informacao alta (>= 0.8) | author | obrigatorio |
| domain_tags | Rotulos de topico que habilitam o roteamento de recuperacao | author | obrigatorio |
| card_type | Classificacao: domain_kc ou meta_kc | author | obrigatorio |
| sources | Referencias de origem do fato destilado | author | obrigatorio |
| confidence_score | Nota de confiabilidade do fato (0.0-1.0) | author | obrigatorio |
| version | Contador de revisao para atualizacoes do fato | author | obrigatorio |
| linked_artifacts | Outros cards ou artefatos aos quais este fato se conecta | author | opcional |
| expiry_hint | Sinaliza que o fato pode ficar desatualizado apos uma data | author | opcional |
## Grafo de Dependencias
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
| rag_source | knowledge_card | data_flow | texto de origem bruto para destilar |
| knowledge_card | knowledge_index | data_flow | title, body, tags para indexacao BM25 e vetorial |
| knowledge_index | system_prompt | data_flow | fatos recuperados injetados no contexto do prompt |
| knowledge_card | few_shot_example | data_flow | embasamento factual para os pares de input/output |
| knowledge_card | context_doc | data_flow | referenciado como evidencia de apoio |
| knowledge_card | agent | data_flow | conhecimento de dominio vinculado na definicao do agent |
## Tabela de Fronteira
| knowledge_card E | knowledge_card NAO E |
|-------------------|----------------------|
| Fato atomico e pesquisavel com densidade >= 0.8 | Documento de referencia amplo, sem portao de densidade |
| Versionado e com fonte atribuida | Especificacao de um modelo de LLM ou de seus parametros |
| Classificado como domain_kc ou meta_kc | Entrada de definicao curta (maximo 3 linhas) |
| Injetado em prompts via indice de recuperacao | Ponteiro de URL externa sem conteudo destilado |
| Corpo de no maximo 5KB (alta relacao sinal-ruido) | Par de demonstracao de input/output |
| Pode expirar quando os fatos ficam desatualizados | Identidade do agent ou definicao comportamental |
## Mapa de Camadas
| Camada | Componentes | Proposito |
|-------|------------|---------|
| Identidade | title, card_type, version | Nomear, classificar e versionar o fato |
| Conteudo | body, confidence_score, expiry_hint | Carregar o fato destilado com sinal de confiabilidade |
| Descobribilidade | domain_tags, linked_artifacts | Habilitar o roteamento de recuperacao e o cross-reference |
| Procedencia | sources | Rastrear o fato ate sua origem |
| Consumo | knowledge_index, system_prompt | Recuperar e injetar fatos no contexto do agent em tempo de execucao |

## Related Artifacts
| Artefato | Relacao | Pontuacao |
|----------|-------------|-------|
| [[bld_architecture_knowledge_index]] | sibling | 0.32 |
| [[knowledge-card-builder]] | upstream | 0.32 |
| [[kc_knowledge_card]] | upstream | 0.31 |
| [[bld_architecture_rag_source]] | sibling | 0.29 |
| p01_kc_cex_lp01_knowledge | upstream | 0.29 |
