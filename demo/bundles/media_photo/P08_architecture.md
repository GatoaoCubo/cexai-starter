---
kind: architecture
id: bld_architecture_multimodal_prompt
pillar: P08
llm_function: CONSTRAIN
purpose: Mapa de componentes de multimodal_prompt -- inventário, dependências
quality: null
title: "Architecture Multimodal Prompt"
version: "1.0.0"
author: wave1_builder_gen_v2
tags: [multimodal_prompt, builder, architecture]
tldr: "Mapa de componentes de multimodal_prompt -- inventário, dependências"
domain: "construção de multimodal_prompt"
created: "2026-04-14"
updated: "2026-04-14"
8f: "F1_constrain"
keywords: [construção de multimodal_prompt, architecture multimodal prompt, multimodal_prompt, builder, architecture, inventário de componentes, posição arquitetural, artefatos relacionados, active, sibling]
density_score: 0.85
related:
  - bld_architecture_prompt_optimizer
  - bld_architecture_prompt_technique
  - bld_architecture_discovery_questions
  - bld_architecture_sales_playbook
  - bld_architecture_api_reference
---

## Inventário de Componentes
| Nome do ISO             | Papel                                      | Pilar | Status  |
|----------------------|-------------------------------------------|--------|---------|
| bld_manifest         | Define estrutura e metadados            | P03    | Ativo  |
| bld_instruction      | Codifica diretivas específicas da tarefa            | P03    | Ativo  |
| bld_system_prompt    | Define as diretrizes gerais de comportamento      | P03    | Ativo  |
| bld_schema           | Reforça a consistência do formato de dados            | P03    | Ativo  |
| bld_quality_gate     | Valida a conformidade da saída               | P03    | Ativo  |
| bld_output_template  | Estrutura o formato final da resposta              | P03    | Ativo  |
| bld_examples         | Fornece saídas de referência                | P03    | Ativo  |
| bld_knowledge_card   | Incorpora conhecimento específico do domínio          | P03    | Ativo  |
| bld_architecture     | Mapeia as interações entre componentes              | P03    | Ativo  |
| bld_collaboration    | Coordena fluxos de trabalho multiagente         | P03    | Ativo  |
| bld_config           | Gerencia parâmetros de runtime                | P03    | Ativo  |
| bld_memory           | Armazena dados de estado de sessão                 | P03    | Ativo  |
| bld_tools            | Integra APIs/funcionalidades externas  | P03    | Ativo  |

## Dependências
| De         | Para              | Tipo       |
|--------------|-----------------|------------|
| bld_manifest | bld_schema      | Definição |
| bld_instruction | bld_system_prompt | Herança |
| bld_quality_gate | bld_output_template | Validação |
| bld_knowledge_card | bld_examples | Referência |
| bld_tools    | llm_engine      | Integração |

## Posição Arquitetural
O multimodal_prompt atua como o orquestrador central no P03, sintetizando modalidades heterogêneas (texto, dado, lógica) em prompts coerentes. Funciona como o elo central de garantia de qualidade, colaboração e reforço de schema, permitindo que os sistemas CEX gerem saídas robustas e sensíveis ao contexto, respeitando restrições específicas de domínio e padrões de interoperabilidade.

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| bld_architecture_prompt_optimizer | sibling | 0.79 |
| bld_architecture_prompt_technique | sibling | 0.74 |
| bld_architecture_discovery_questions | sibling | 0.60 |
| bld_architecture_sales_playbook | sibling | 0.59 |
| bld_architecture_api_reference | sibling | 0.58 |
