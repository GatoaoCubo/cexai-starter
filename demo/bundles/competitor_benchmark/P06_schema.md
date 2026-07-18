---
kind: schema
id: bld_schema_competitive_matrix
pillar: P06
llm_function: CONSTRAIN
purpose: Schema formal -- FONTE ÚNICA DA VERDADE para competitive_matrix
quality: null
title: "Schema Competitive Matrix"
version: "1.1.0"
author: wave1_builder_gen_v2
tags: [competitive_matrix, builder, schema]
tldr: "Schema formal -- feature-parity grid + battle card + posicionamento Gartner MQ para competitive_matrix."
domain: "construção de competitive_matrix"
created: "2026-04-14"
updated: "2026-04-14"
8f: "F1_constrain"
keywords: [competitive_matrix construction, schema competitive matrix, battle card, competitive_matrix, builder, schema, frontmatter fields, market segment, competitive matrix, body structure]
density_score: 0.85
related:
  - bld_schema_usage_report
  - bld_schema_pitch_deck
  - bld_schema_quickstart_guide
  - bld_schema_reranker_config
  - bld_schema_integration_guide
---

## Campos do Frontmatter
### Obrigatórios
| Campo | Tipo | Obrigatório | Padrão | Notas |
|-------|------|----------|---------|-------|
| id | string | sim | | Deve corresponder ao Padrão de ID |
| kind | string | sim | | Sempre "competitive_matrix" |
| pillar | string | sim | | P01 |
| title | string | sim | | "Matriz Competitiva de {Segmento de Mercado}" |
| version | string | sim | | Versão do artefato (ex.: "1.0.0") |
| created | string | sim | | ISO 8601 AAAA-MM-DD |
| updated | string | sim | | ISO 8601 AAAA-MM-DD |
| author | string | sim | | Usuário do analista |
| domain | string | sim | | Domínio de mercado |
| quality | null | sim | null | Nunca se autoavalia; peer review atribui |
| tags | list | sim | | Segmento de mercado, competitive_matrix |
| tldr | string | sim | | "Nosso produto vs N concorrentes em M dimensões" |
| competitors | list | sim | | Fornecedores nomeados (mínimo 3) |
| metrics | list | sim | | Dimensões de capacidade comparadas |
| analysis_date | string | sim | | ISO 8601 AAAA-MM-DD da coleta de dados |
| key_insights | string | sim | | Principal diferencial em uma frase |

### Recomendados
| Campo | Tipo | Notas |
|-------|------|-------|
| primary_competitor | string | Concorrente mais frequente nos negócios avaliados |
| data_sources | list | Nomes das fontes com datas de acesso |
| reviewers | list | Usuários dos revisores pares |

## Padrão de ID
^p01_cm_[a-z][a-z0-9_]+\\.md$

## Estrutura do Corpo
1. **Contexto de Mercado** -- Segmento, data da análise, fontes de dados, analista
2. **Feature Parity Grid** -- Linhas = capacidades, colunas = nos + concorrentes; Sim/Não/Parcial/Roadmap Q# AAAA
3. **Posicionamento Gartner MQ** -- Capacidade de Execução (1-5) x Completude de Visão (1-5) por fornecedor
4. **Battle Card** -- Nos vs concorrente primário: capacidade, nossa força, fraqueza deles, razão de vitória
5. **Comparação de Preços** -- Camadas entrada/intermediária/enterprise + modelo de precificação por fornecedor
6. **Insights Estratégicos** -- Top 3 diferenciais, 2 lacunas, guia anti-FUD

## Restrições
- O ID deve corresponder exatamente a ^p01_cm_[a-z][a-z0-9_]+\\.md$.
- analysis_date deve estar no formato ISO 8601.
- A lista competitors deve nomear pelo menos 3 fornecedores (sem nomes placeholder).
- O tamanho do arquivo não deve exceder 5120 bytes.
- O campo quality deve ser null (somente peer review).
- Todos os valores de capacidade devem usar: Sim / Não / Parcial / Roadmap Q# AAAA (nunca adjetivos vagos).
- Toda alegação deve citar uma fonte primária com data de acesso.
- Itens de roadmap devem incluir trimestre-alvo e ano.

## Artefatos Relacionados
| Artefato | Relacionamento | Pontuação |
|----------|-------------|-------|
| bld_schema_usage_report | sibling | 0.64 |
| bld_schema_pitch_deck | sibling | 0.63 |
| bld_schema_quickstart_guide | sibling | 0.62 |
| bld_schema_reranker_config | sibling | 0.61 |
| bld_schema_integration_guide | sibling | 0.60 |
