---
kind: tools
id: bld_tools_competitive_matrix
pillar: P04
llm_function: CALL
purpose: Ferramentas disponíveis para produção de competitive_matrix
quality: null
title: "Tools Competitive Matrix"
version: "1.1.0"
author: wave1_builder_gen_v2
tags: [competitive_matrix, builder, tools]
tldr: "Ferramentas CEX disponíveis para produção e validação de competitive_matrix"
domain: "construção de competitive_matrix"
created: "2026-04-14"
updated: "2026-04-14"
8f: "F5_call"
keywords: [competitive_matrix construction, tools competitive matrix, competitive_matrix, builder, tools, production tools, validation tools, external references, gartner magic quadrant, forrester wave]
density_score: 0.85
related:
  - bld_tools_changelog
  - bld_tools_case_study
  - bld_tools_api_reference
  - bld_tools_rbac_policy
  - bld_tools_nps_survey
---

## Ferramentas de Produção
| Ferramenta | Propósito | Quando |
|------|---------|------|
| cex_compile.py | Compila o artefato .md para o sidecar .yaml | Após a escrita |
| cex_score.py | Pontua a matriz contra as dimensões do gate de qualidade | Antes da publicação |
| cex_retriever.py | Encontra matrizes existentes para referência cruzada | Durante a pesquisa |
| cex_doctor.py | Valida frontmatter, padrão de ID e conformidade de kind | Antes da publicação |

## Ferramentas de Validação
| Ferramenta | Propósito | Quando |
|------|---------|------|
| cex_wave_validator.py | Verifica todos os ISOs do builder quanto a conformidade de schema | Após a construção |
| cex_hooks.py | Validação de YAML e enforcement do gate de qualidade no pre-commit | No git commit |

## Referências Externas
- Metodologia Gartner Magic Quadrant (dimensões de capacidade de execução x visão)
- Metodologia de pontuação Forrester Wave (ponderação de funcionalidades e benchmarking)
- G2 Grid (dados de avaliação verificada de usuários para comparação de funcionalidades)
- Battlecard.io / Klue / Crayon (referências de estrutura de battle card)

## Artefatos Relacionados
| Artefato | Relacionamento | Pontuação |
|----------|-------------|-------|
| bld_tools_changelog | sibling | 0.43 |
| bld_tools_case_study | sibling | 0.43 |
| bld_tools_api_reference | sibling | 0.36 |
| [[bld_tools_rbac_policy]] | sibling | 0.35 |
| bld_tools_nps_survey | sibling | 0.35 |
