---
kind: architecture
id: bld_architecture_roi_calculator
pillar: P08
llm_function: CONSTRAIN
purpose: Mapa de componentes do roi_calculator -- inventário, dependências
quality: null
title: "Arquitetura -- ROI Calculator"
version: "1.0.0"
author: wave1_builder_gen_v2
tags: [roi_calculator, builder, architecture]
tldr: "Mapa de componentes do roi_calculator -- inventário, dependências"
domain: "construção de roi_calculator"
created: "2026-04-14"
updated: "2026-04-14"
8f: "F1_constrain"
keywords: [construção de roi_calculator, arquitetura roi calculator, roi_calculator, builder, architecture, inventário de componentes, posição arquitetural, related artifacts, tarefa bld_instruction, execução de tarefa]
density_score: 0.85
related:
  - bld_architecture_api_reference
  - bld_architecture_quickstart_guide
  - bld_architecture_sales_playbook
  - bld_architecture_discovery_questions
  - bld_architecture_benchmark_suite
---

## Inventário de Componentes
| Nome do ISO            | Papel                          | Pilar | Status  |
|---------------------|-------------------------------|--------|---------|
| bld_manifest        | Configuração do builder         | P11    | Ativo  |
| bld_instruction     | Diretrizes de execução de tarefa     | P03    | Ativo  |
| bld_system_prompt   | Framework de interação com o LLM     | P03    | Ativo  |
| bld_schema          | Definição da estrutura de dados     | P06    | Ativo  |
| bld_quality_gate    | Regras de validação              | P11    | Ativo  |
| bld_output_template | Formatação do resultado              | P05    | Ativo  |
| bld_examples        | Exemplos de entrada/saída           | P07    | Ativo  |
| bld_knowledge_card  | Conhecimento específico de domínio     | P01    | Ativo  |
| bld_architecture    | Design do sistema do builder    | P08    | Ativo  |
| bld_collaboration   | Coordenação entre múltiplos builders    | P12    | Ativo  |
| bld_config          | Gestão de parâmetros de runtime  | P09    | Ativo  |
| bld_memory          | Mecanismo de retenção de estado        | P10    | Ativo  |
| bld_tools           | Funções utilitárias           | P04    | Ativo  |

## Dependências
| De              | Para                  | Tipo         |
|-------------------|---------------------|--------------|
| bld_config        | bld_manifest        | Configuração|
| bld_instruction   | bld_system_prompt   | Execução    |
| bld_quality_gate  | bld_schema          | Validação   |
| bld_output_template | bld_examples      | Referência    |
| bld_tools         | external_calculator | Integração  |

## Posição Arquitetural
O roi_calculator opera como uma ferramenta especializada dentro do Pilar P11 do CEX, focada em quantificar métricas de retorno sobre investimento por meio de ISOs de builder estruturados. Ele se integra com o bld_instruction para execução de tarefas, com o bld_schema para consistência de dados e com o bld_quality_gate para verificações de precisão, posicionando-se como um componente central de analytics no ecossistema do pilar.

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| bld_architecture_api_reference | sibling | 0.71 |
| bld_architecture_quickstart_guide | sibling | 0.69 |
| bld_architecture_sales_playbook | sibling | 0.68 |
| bld_architecture_discovery_questions | sibling | 0.67 |
| bld_architecture_benchmark_suite | sibling | 0.66 |
