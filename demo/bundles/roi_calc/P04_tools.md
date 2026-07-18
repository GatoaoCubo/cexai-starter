---
kind: tools
id: bld_tools_roi_calculator
pillar: P04
llm_function: CALL
purpose: Ferramentas disponíveis para produção de roi_calculator
quality: null
title: "Ferramentas -- ROI Calculator"
version: "1.0.0"
author: wave1_builder_gen_v2
tags: [roi_calculator, builder, tools]
tldr: "Registro de ferramentas do roi_calculator-builder: ferramentas do pipeline CEX (compilar, pontuar, recuperar), operações de sistema de arquivos (Read/Write/Edit/Glob/Grep) e automação específica de domínio para a especificação do roi calculator com entradas, fórmulas e comparação de TCO para compradores econômicos."
domain: "construção de roi_calculator"
created: "2026-04-14"
updated: "2026-04-14"
8f: "F5_call"
keywords: [construção de roi_calculator, ferramentas roi calculator, ferramentas do pipeline cex, operações de sistema de arquivos, roi_calculator, builder, tools, ferramentas de produção, ferramentas de validação, referências externas]
density_score: 0.85
related:
  - bld_tools_compliance_checklist
  - bld_tools_audit_log
  - bld_tools_data_residency
  - bld_tools_synthetic_data_config
  - bld_tools_skill
---

## Ferramentas de Produção
| Ferramenta | Finalidade | Quando |
|------|---------|------|
| cex_compile.py | Compilar o artefato após a produção | F8 COLLABORATE |
| cex_score.py | Pontuar a qualidade do artefato (dimensões 5D) | F7 GOVERN |
| cex_retriever.py | Recuperar artefatos similares de ROI calculator para reuso | F3 INJECT |
| cex_doctor.py | Validar a saúde do builder, checar completude dos ISOs | F7 GOVERN |

## Ferramentas de Validação
| Ferramenta | Finalidade | Quando |
|------|---------|------|
| cex_wave_validator.py | Validação estrutural de YAML + frontmatter | Pós-produção |
| cex_hooks.py | Checagens de ASCII e schema no pre-commit | Pre-commit |

## Referências Externas
- Metodologia Forrester TEI (Total Economic Impact)
- Framework de TCO do Gartner
- Padrões de cálculo de NPV IFRS/GAAP

## Ferramentas do Pipeline CEX

| Ferramenta | Finalidade | Quando |
|------|---------|------|
| cex_compile.py | Compilar o artefato .md para .yaml | Após o Write (F8) |
| cex_score.py | Pontuação de qualidade por revisão de pares | Após a produção (F7) |
| cex_retriever.py | Descobrir artefatos similares via TF-IDF | Durante F3 INJECT |
| cex_doctor.py | Checagem de saúde dos ISOs do builder | Antes do dispatch |

## Fontes de Dados

| Fonte | Conteúdo | Quando usar |
|--------|---------|-------------|
| SCHEMA.md | Definições de campo, padrão de ID, restrições | Toda execução de produção |
| OUTPUT_TEMPLATE.md | Estrutura exata de frontmatter + corpo | Toda execução de produção |
| QUALITY_GATES.md | Gates HARD H01-H08 | Toda execução de validação |
| KNOWLEDGE.md | Conceitos de domínio para o roi calculator | Ao desenhar a estrutura |
| MEMORY.md | Erros comuns, antipadrões | Quando travado ou produzindo uma variante |

## Permissões de Ferramentas

| Categoria | Ferramentas | Status |
|----------|-------|--------|
| PERMITIDO | Read, Write, Edit, Bash, Glob, Grep | Explicitamente permitido |
| NEGADO | (nenhuma) | Explicitamente bloqueado |
| EFETIVO | Bash, Edit, Glob, Grep, Read, Write | PERMITIDO menos NEGADO |

## Propriedades

| Propriedade | Valor |
|----------|-------|
| Kind | `tools` |
| Pillar | P04 |
| Domínio | construção de roi calculator |
| Pipeline | 8F (F1-F8) |
| Avaliador (Scorer) | cex_score.py |
| Compilador | cex_compile.py |
| Recuperador (Retriever) | cex_retriever.py |
| Meta de qualidade | 9.0+ |
| Meta de densidade | 0.85+ |

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| bld_tools_compliance_checklist | sibling | 0.52 |
| bld_tools_audit_log | sibling | 0.49 |
| bld_tools_data_residency | sibling | 0.43 |
| bld_tools_synthetic_data_config | sibling | 0.40 |
| bld_tools_skill | sibling | 0.39 |
