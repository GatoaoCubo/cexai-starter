---
kind: architecture
id: bld_architecture_competitive_matrix
pillar: P08
llm_function: CONSTRAIN
purpose: Mapa de componentes de competitive_matrix -- inventário, dependências
quality: null
title: "Architecture Competitive Matrix"
version: "1.0.0"
author: wave1_builder_gen_v2
tags: [competitive_matrix, builder, architecture]
tldr: "Mapa de componentes de competitive_matrix -- inventário, dependências"
domain: "construção de competitive_matrix"
created: "2026-04-14"
updated: "2026-04-14"
8f: "F1_constrain"
keywords: [competitive_matrix construction, architecture competitive matrix, competitive_matrix, builder, architecture, component inventory, architectural position, related artifacts, active, sibling]
density_score: 0.85
related:
  - bld_architecture_graph_rag_config
  - bld_architecture_faq_entry
  - bld_architecture_reranker_config
  - bld_architecture_changelog
  - bld_architecture_ecommerce_vertical
---

## Inventário de Componentes
| Nome do ISO             | Papel                                      | Pilar | Status  |
|----------------------|-------------------------------------------|--------|---------|
| bld_manifest         | Define a estrutura da matriz                  | P01    | Ativo  |
| bld_instruction      | Especifica as regras de geração                | P01    | Ativo  |
| bld_system_prompt    | Define o comportamento do LLM na construção da matriz     | P01    | Ativo  |
| bld_schema           | Garante a consistência do formato de dados          | P01    | Ativo  |
| bld_quality_gate     | Valida a precisão da saída                 | P01    | Ativo  |
| bld_output_template  | Estrutura a exibição final da matriz             | P01    | Ativo  |
| bld_examples         | Fornece matrizes de referência               | P01    | Ativo  |
| bld_knowledge_card   | Incorpora insights específicos de domínio           | P01    | Ativo  |
| bld_architecture     | Mapeia as interações entre componentes             | P01    | Ativo  |
| bld_collaboration    | Habilita a coordenação entre builders        | P01    | Ativo  |
| bld_config           | Centraliza os parâmetros de configuração    | P01    | Ativo  |
| bld_memory           | Armazena o histórico de dados da matriz             | P01    | Ativo  |
| bld_tools            | Integra utilitários externos de análise    | P01    | Ativo  |

## Dependências
| De              | Para                  | Tipo         |
|-------------------|---------------------|--------------|
| bld_manifest      | bld_config          | Configuração|
| bld_instruction   | bld_system_prompt   | Definição   |
| bld_output_template | bld_schema        | Estrutura    |
| bld_quality_gate  | bld_memory          | Validação    |
| bld_tools         | API Externa        | Integração   |

## Posição Arquitetural
competitive_matrix atua como orquestrador central no CEX P01, sintetizando os ISOs do builder para automatizar a análise do panorama competitivo. Garante a geração estruturada e de alta qualidade da matriz por meio de enforcement de schema, gates de qualidade e mecanismos de colaboração, ao mesmo tempo em que aproveita memória e ferramentas para profundidade e precisão dos dados.

## Artefatos Relacionados
| Artefato | Relacionamento | Pontuação |
|----------|-------------|-------|
| bld_architecture_graph_rag_config | sibling | 0.76 |
| bld_architecture_faq_entry | sibling | 0.75 |
| bld_architecture_reranker_config | sibling | 0.75 |
| bld_architecture_changelog | sibling | 0.75 |
| bld_architecture_ecommerce_vertical | sibling | 0.73 |
