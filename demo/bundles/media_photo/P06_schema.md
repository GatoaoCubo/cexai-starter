---
kind: schema
id: bld_schema_multimodal_prompt
pillar: P06
llm_function: CONSTRAIN
purpose: Schema formal -- FONTE ÚNICA DA VERDADE para multimodal_prompt
quality: null
title: "Schema Multimodal Prompt"
version: "1.0.0"
author: wave1_builder_gen_v2
tags: [multimodal_prompt, builder, schema]
tldr: "Schema formal -- FONTE ÚNICA DA VERDADE para multimodal_prompt"
domain: "construção de multimodal_prompt"
created: "2026-04-14"
updated: "2026-04-14"
8f: "F1_constrain"
keywords: [construção de multimodal_prompt, schema multimodal prompt, multimodal_prompt, builder, schema, campos de frontmatter, estrutura do corpo, estrutura do prompt, exemplo de uso, artefatos relacionados]
density_score: 0.85
related:
  - bld_schema_benchmark_suite
  - bld_schema_reranker_config
  - bld_schema_integration_guide
  - bld_schema_app_directory_entry
  - bld_schema_eval_metric
---

## Campos de Frontmatter
### Obrigatórios
| Campo     | Tipo             | Obrigatório | Padrão | Notas                              |
|-----------|------------------|----------|---------|------------------------------------|
| id        | string           | sim      | null    | Identificador único                  |
| kind      | string           | sim      | null    | Deve ser "multimodal_prompt"        |
| pillar    | string           | sim      | null    | P03                                |
| title     | string           | sim      | null    | Título descritivo                  |
| version   | string           | sim      | "1.0"   | Controle de versão                    |
| created   | datetime         | sim      | null    | ISO 8601                           |
| updated   | datetime         | sim      | null    | ISO 8601                           |
| author    | string           | sim      | null    | Nome do autor                         |
| domain    | string           | sim      | null    | Domínio de aplicação                 |
| quality   | null             | sim      | null    | Nunca autoavaliado; peer review atribui |
| tags      | array<string>    | sim      | []      | Palavras-chave                           |
| tldr      | string           | sim      | null    | Resumo em uma frase               |
| modalities | array<string>   | sim      | null    | Modalidades suportadas (ex.: text, image) |
| prompt_type | string        | sim      | null    | Tipo (ex.: instruction, query)    |

### Recomendados
| Campo           | Tipo             | Notas                          |
|------------------|------------------|--------------------------------|
| license          | string           | Licença open-source            |
| source           | string           | Fonte original                 |
| related_works    | array<string>    | Trabalhos citados                    |
| validation_metrics | array<string> | Critérios de avaliação            |

## Padrão de ID
^p03_mmp_[a-z][a-z0-9_]+.md$

## Estrutura do Corpo
1. **Introdução**: propósito e escopo do prompt.
2. **Modalidades**: descrição detalhada dos tipos de entrada/saída suportados.
3. **Estrutura do Prompt**: sintaxe, regras de formatação e exemplos.
4. **Exemplo de Uso**: cenários de aplicação do mundo real.
5. **Validação**: métricas e processo de peer review.

## Restrições
- O ID deve corresponder a ^p03_mmp_[a-z][a-z0-9_]+.md$
- Tamanho total <= 4096 bytes
- Todos os campos obrigatórios devem estar presentes
- O campo quality é somente peer-reviewed
- Caracteres somente ASCII são obrigatórios
- <= 80 linhas no total

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| bld_schema_benchmark_suite | sibling | 0.67 |
| bld_schema_reranker_config | sibling | 0.66 |
| bld_schema_integration_guide | sibling | 0.66 |
| bld_schema_app_directory_entry | sibling | 0.64 |
| [[bld_schema_eval_metric]] | sibling | 0.64 |
