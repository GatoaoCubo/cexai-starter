---
kind: tools
id: bld_tools_opportunity_matrix
pillar: P04
llm_function: CALL
purpose: Ferramentas disponíveis para a produção de opportunity_matrix
quality: null
title: "Ferramentas -- Opportunity Matrix"
version: "1.0.0"
author: n03_builder
tags: [opportunity_matrix, builder, tools]
tldr: "Registro de ferramentas do builder de opportunity matrix: ferramentas do pipeline CEX (compile, score, retrieve), operações de sistema de arquivos (Read/Write/Edit/Glob/Grep), e o gerador real + fiação de capability para decisões de compra/sourcing pontuadas de custo-de-fornecedor x demanda-de-mercado."
domain: "construção de opportunity_matrix"
created: "2026-07-02"
updated: "2026-07-02"
8f: "F5_call"
keywords: [construção de opportunity_matrix, ferramentas opportunity matrix, ferramentas do pipeline cex, operações de sistema de arquivos, opportunity_matrix, builder, tools, gerador sourcing_opportunity, fiação de capability, ferramentas de produção]
density_score: 0.85
related:
  - bld_tools_roi_calculator
  - opportunity-matrix-builder
---
## Ferramentas de Produção
| Ferramenta | Propósito | Quando |
|------|---------|------|
| cex_compile.py | Compila o artefato após a produção | F8 COLLABORATE |
| cex_score.py | Pontua a qualidade do artefato (dimensões 5D) | F7 GOVERN |
| cex_retriever.py | Recupera artefatos opportunity_matrix similares para reuso | F3 INJECT |
| cex_doctor.py | Valida a saúde do builder, checa completude dos ISOs | F7 GOVERN |

## Referência de Runtime (o gerador real que este builder documenta)
| Componente | Caminho | Nota |
|-----------|------|------|
| Gerador | `_tools/capability_generators/sourcing_opportunity.py` | `@register("opportunity_matrix")`; offline-determinístico, nunca lança exceção |
| Fiação de capability | `_tools/cex_run_capability.py` | slug `sourcing_opportunity` -> (N06, opportunity_matrix, P11, analyze) |
| Forma de I/O congelada | `apps/dashboard_web/lib/molds.ts` | MOLD_SOURCING_OPPORTUNITY (9 entradas, 8 seções) |
| Resumo do contrato | `apps/dashboard_web/lib/capability_contracts_v1.0.md` | Seção 15 |
| Entrada de CLI | `.claude/commands/sourcing.md` | `/sourcing <catalog_dir\|sources> [params]` |
| Pytest offline | `_tools/tests/test_capgen_sourcing.py` | checagens de forma + honestidade (referência somente-leitura; não editar) |

## Ferramentas de Validação
| Ferramenta | Propósito | Quando |
|------|---------|------|
| cex_wave_validator.py | Validação estrutural de YAML + frontmatter | Pós-produção |
| cex_hooks.py | Checagens de ASCII e schema no pre-commit | Pre-commit |

## Referências de Rigor de Domínio
- `_docs/specs/contract/n01_sourcing_rigor.md` -- invariantes S1-S5 (triangulação, proveniência, frescor, gate, honest-null)
- `_docs/specs/contract/n06_unit_econ.md` -- citado pela disciplina geral custo->preço->take-rate->margem (o próprio pacote de seção LTV/CAC desse documento é voltado a outros kinds, não a este)
- `_docs/specs/contract/n06_benchmark.md` -- citado pelo princípio de superfície de ranking ponderado (opp_score); o próprio pacote de seção desse documento é voltado a competitor_benchmark
- `_docs/specs/contract/n03_schema.md` -- vocabulário de tipo fechado para o input_contract

## Ferramentas do Pipeline CEX
| Ferramenta | Propósito | Quando |
|------|---------|------|
| cex_compile.py | Compila o artefato .md para .yaml | Após o Write (F8) |
| cex_score.py | Pontuação de qualidade por peer-review | Após a produção (F7) |
| cex_retriever.py | Descobre artefatos similares por TF-IDF | Durante F3 INJECT |
| cex_doctor.py | Checagem de saúde dos ISOs do builder | Antes do dispatch |

## Fontes de Dados
| Fonte | Conteúdo | Quando usar |
|--------|---------|-------------|
| SCHEMA.md | Definições de campo, padrão de ID, restrições | Toda execução de produção |
| OUTPUT_TEMPLATE.md | Frontmatter + estrutura de corpo exatos | Toda execução de produção |
| QUALITY_GATES.md | Gates HARD H01-H08 | Toda execução de validação |
| KNOWLEDGE.md | Conceitos de domínio para opportunity matrix | Ao desenhar a estrutura |
| MEMORY.md | Erros comuns, antipadrões | Ao travar ou produzir uma variante |

## Permissões de Ferramentas
| Categoria | Ferramentas | Status |
|----------|-------|--------|
| PERMITIDAS | Read, Write, Edit, Bash, Glob, Grep | Explicitamente permitidas |
| NEGADAS | (nenhuma) | Explicitamente bloqueadas |
| EFETIVAS | Bash, Edit, Glob, Grep, Read, Write | PERMITIDAS menos NEGADAS |

## Propriedades
| Propriedade | Valor |
|----------|-------|
| Kind | `tools` |
| Pillar | P04 |
| Domain | construção de opportunity matrix |
| Pipeline | 8F (F1-F8) |
| Scorer | cex_score.py |
| Compiler | cex_compile.py |
| Retriever | cex_retriever.py |
| Meta de qualidade | 9.0+ |
| Meta de densidade | 0.85+ |

## Artefatos Relacionados
| Artefato | Relacionamento | Pontuação |
|----------|-------------|-------|
| [[bld_tools_roi_calculator]] | sibling | 0.52 |
| [[opportunity-matrix-builder]] | related | 0.45 |
| sourcing | related | 0.40 |
| p08_adr_opportunity_matrix_kind | upstream | 0.38 |
| [[bld_prompt_opportunity_matrix]] | related | 0.35 |
