---
kind: schema
id: bld_schema_roi_calculator
pillar: P06
llm_function: CONSTRAIN
purpose: Schema formal -- FONTE ÚNICA DA VERDADE para roi_calculator
quality: null
title: "Schema -- ROI Calculator"
version: "1.0.0"
author: wave1_builder_gen_v2
tags: [roi_calculator, builder, schema]
tldr: "Schema formal -- FONTE ÚNICA DA VERDADE para roi_calculator"
domain: "construção de roi_calculator"
created: "2026-04-14"
updated: "2026-04-14"
8f: "F1_constrain"
keywords: [construção de roi_calculator, schema roi calculator, roi_calculator, builder, schema, campos de frontmatter, estrutura do corpo, metodologia de cálculo, parâmetros de entrada, métricas de saída]
density_score: 0.85
related:
  - bld_schema_reranker_config
  - bld_schema_benchmark_suite
  - bld_schema_integration_guide
  - bld_schema_prompt_technique
  - bld_schema_pitch_deck
---

## Campos de Frontmatter
### Obrigatórios
| Campo | Tipo | Obrigatório | Padrão | Notas |
|------|------|----------|---------|-------|
| id | string | sim | null | Deve corresponder ao Padrão de ID |
| kind | string | sim | "roi_calculator" | Identificador de kind do CEX |
| pillar | string | sim | "P11" | Classificação de pilar |
| title | string | sim | null | Título descritivo |
| version | string | sim | "1.0.0" | Versionamento semântico |
| created | datetime | sim | null | Formato ISO 8601 |
| updated | datetime | sim | null | Formato ISO 8601 |
| author | string | sim | null | Parte responsável |
| domain | string | sim | "roi" | Contexto de domínio |
| quality | null | sim | null | Nunca autoavaliar; a revisão por pares atribui |
| tags | list | sim | [] | Metadados de palavras-chave |
| tldr | string | sim | null | Resumo da finalidade |
| calculation_method | string | sim | null | Fórmula/algoritmo de ROI |
| input_parameters | list | sim | [] | Variáveis obrigatórias |
| output_metrics | list | sim | [] | Valores resultantes |

### Recomendados
| Campo | Tipo | Notas |
|------|------|-------|
| last_reviewed | datetime | Timestamp da revisão por pares |
| reviewers | list | Identificadores dos revisores |
| validation_status | string | "pending"/"approved" |
| example_use_case | string | Exemplo de aplicação |

## Padrão de ID
^p11_roi_[a-z][a-z0-9_]+$

## Estrutura do Corpo
1. **Metodologia de Cálculo**
   Descrição detalhada da fórmula e da lógica de ROI

2. **Parâmetros de Entrada**
   Lista das variáveis obrigatórias com tipos de dado e faixas

3. **Métricas de Saída**
   Definição dos valores calculados e suas unidades

4. **Premissas**
   Condições e limitações do modelo

5. **Procedimentos de Validação**
   Passos para verificar a precisão e os casos-limite

6. **Exemplo de Caso de Uso**
   Cenário prático com entrada/saída de exemplo

## Restrições
- O ID deve corresponder exatamente ao padrão regex
- Todos os campos obrigatórios devem estar presentes
- O YAML deve ser válido e ter menos de 4096 bytes
- Os campos específicos de domínio devem seguir o schema
- O campo quality deve passar por revisão de pares
- O versionamento deve seguir o formato semântico

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| bld_schema_reranker_config | sibling | 0.72 |
| bld_schema_benchmark_suite | sibling | 0.67 |
| bld_schema_integration_guide | sibling | 0.67 |
| bld_schema_prompt_technique | sibling | 0.64 |
| bld_schema_pitch_deck | sibling | 0.63 |
