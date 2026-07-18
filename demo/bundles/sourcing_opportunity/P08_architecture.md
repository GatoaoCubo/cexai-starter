---
kind: architecture
id: bld_architecture_opportunity_matrix
pillar: P08
llm_function: CONSTRAIN
purpose: Mapa de componentes do opportunity_matrix -- inventário, dependências
quality: null
title: "Arquitetura -- Opportunity Matrix"
version: "1.0.0"
author: n03_builder
tags: [opportunity_matrix, builder, architecture]
tldr: "Mapa de componentes do opportunity_matrix -- inventário, dependências"
domain: "construção de opportunity_matrix"
created: "2026-07-02"
updated: "2026-07-02"
8f: "F1_constrain"
keywords: [construção de opportunity_matrix, arquitetura opportunity matrix, opportunity_matrix, builder, architecture, inventário de componentes, posição arquitetural, gerador sourcing_opportunity, seam canonical_product]
density_score: 0.85
related:
  - bld_architecture_roi_calculator
  - roi-calculator-builder
  - research-pipeline-builder
  - scoring-rubric-builder
---
## Inventário de Componentes
| Nome do ISO | Papel | Pillar | Status |
|----------|------|--------|--------|
| bld_manifest (bld_model) | Configuração + identidade do builder | P11 | Ativo |
| bld_instruction (bld_prompt) | Diretrizes de execução de tarefa | P03 | Ativo |
| bld_schema | Definição da estrutura de dados | P06 | Ativo |
| bld_quality_gate (bld_eval) | Regras de validação | P11 | Ativo |
| bld_output_template (bld_output) | Formatação do resultado | P05 | Ativo |
| bld_knowledge_card (bld_knowledge) | Conhecimento específico de domínio | P01 | Ativo |
| bld_architecture | Design do sistema do builder | P08 | Ativo |
| bld_collaboration (bld_orchestration) | Coordenação multi-builder | P12 | Ativo |
| bld_config | Gestão de parâmetros de runtime | P09 | Ativo |
| bld_memory | Mecanismo de retenção de estado | P10 | Ativo |
| bld_tools | Funções utilitárias | P04 | Ativo |
| bld_feedback | Antipadrões + protocolo de correção | P11 | Ativo |

## Dependências
| De | Para | Tipo |
|------|-----|------|
| opportunity_matrix (este kind) | roi_calculator | Composição (primitivo de margem por item) |
| opportunity_matrix (este kind) | research_pipeline | Composição (pesquisa de demanda, S1-S5) |
| opportunity_matrix (este kind) | scoring_rubric | Composição (critérios de ranking) |
| opportunity_matrix (este kind) | product_match | Sibling (compartilha o motor de match/auditoria da Seção 6, soft-imported) |
| bld_instruction | bld_schema | Execução (campos alimentam o schema) |
| bld_quality_gate | bld_output_template | Validação (forma de seção checada contra o template) |

## Posição Arquitetural
`opportunity_matrix` opera dentro do Pillar P11 do CEX (feedback / economia de decisão) como o artefato de decisão de sourcing buy-side -- o gêmeo inbound de `marketplace_listing` (P05, outbound/TUDAO). Conforme `p08_adr_opportunity_matrix_kind` (ACEITO em 2026-06-25), é um kind folha que existe porque o framework de gerador-de-capability é 1-gerador-por-KIND: `competitive_matrix` já estava ocupado, forçando um slot registrável dedicado. O kind NÃO é dono do pipeline de sourcing (uma instância de `pipeline_template` compõe `research_pipeline` + `roi_calculator` + `scoring_rubric` ao seu redor); é só a SAÍDA tipada que o pipeline composto e o gerador real (`_tools/capability_generators/sourcing_opportunity.py`, slug de capability `sourcing_opportunity`, fiado N06/P11/analyze em `_tools/cex_run_capability.py`) têm como alvo. Os dois kinds de sourcing (`opportunity_matrix` + `product_match`) encontram o mold outbound `marketplace_listing` em exatamente um seam: o registro `canonical_product`.

## Artefatos Relacionados
| Artefato | Relacionamento | Pontuação |
|----------|-------------|-------|
| p08_adr_opportunity_matrix_kind | upstream | 0.60 |
| [[bld_architecture_roi_calculator]] | sibling | 0.55 |
| [[roi-calculator-builder]] | related | 0.45 |
| [[research-pipeline-builder]] | related | 0.40 |
| [[scoring-rubric-builder]] | related | 0.38 |
