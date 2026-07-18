---
kind: tools
id: bld_tools_knowledge_card
pillar: P04
llm_function: CALL
purpose: Ferramentas e APIs disponíveis para a produção de knowledge_card
quality: null
title: "Ferramentas: Knowledge Card"
version: "1.0.0"
author: n03_builder
tags: [knowledge_card, builder, examples]
tldr: "Exemplos ideais e contraexemplos para a construção de knowledge cards, demonstrando estrutura ideal e erros comuns."
domain: "construção de knowledge_card"
created: "2026-04-07"
updated: "2026-04-07"
8f: "F5_call"
keywords: [construção de knowledge_card, ferramentas knowledge card, knowledge_card, builder, examples, ferramentas de produção, fontes de dados, permissões de ferramentas, validação intermediária, related artifacts]
density_score: 0.90
related:
  - bld_tools_validation_schema
  - bld_tools_quality_gate
  - bld_tools_scoring_rubric
  - bld_tools_retriever_config
  - bld_tools_golden_test
---

# Ferramentas: knowledge-card-builder
## Ferramentas de Produção
| Ferramenta | Propósito | Quando | Status |
|------|---------|------|--------|
| validate_kc.py | Validar o KC: 10 gates HARD + 20 SOFT | Fase 3 | CONDITIONAL |
| brain_query [MCP] | Buscar KCs existentes no pool | Fase 1 | CONDITIONAL |
| validate_artifact.py | Validador genérico de artifact | -- | [PLANNED] |
| cex_forge.py | Gerar artifact a partir de seeds | Composição alternativa | [PLANNED] |
## Uso do validate_kc.py
```bash
# Single file
python _tools/validate_kc.py path/to/p01_kc_topic.md
# Directory (batch)
python _tools/validate_kc.py P01_knowledge/examples/ --summary
# JSON output (machine-readable)
python _tools/validate_kc.py path/to/file.md --json
```
Saída: HARD pass/fail + nota SOFT 0-10 + veredito.
Sugestões de correção são fornecidas para os gates que falharem.
## Uso do brain_query
```python
brain_query("knowledge card about {topic}")
# Returns: existing KCs matching topic
# Purpose: avoid duplicates, find linked_artifacts
```
## Fontes de Dados
| Fonte | Caminho | Dado |
|--------|------|------|
| CEX Schema | P01_knowledge/_schema.yaml | Definições de campo do KC |
| CEX Examples | P01_knowledge/examples/ | 63+ KCs reais |
| CEX Template | P01_knowledge/templates/tpl_knowledge_card.md | Template preenchível |
| CEX Pool | artifacts/ (repositório de origem) | 1957+ artifacts publicados |
## Permissões de Ferramentas

| Categoria | Ferramentas | Status |
|----------|-------|--------|
| ALLOWED | Read, Write, Edit, Bash, Glob, Grep | Explicitamente permitido |
| DENIED | (nenhuma) | Explicitamente bloqueado |
| EFFECTIVE | Bash, Edit, Glob, Grep, Read, Write | ALLOWED menos DENIED |

## Validação Intermediária
O validate_kc.py está ATIVO -- sempre rode antes de commitar.
Não é necessário checar gates manualmente (diferente do model-card-builder).

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[bld_tools_validation_schema]] | sibling | 0.50 |
| bld_tools_quality_gate | sibling | 0.46 |
| [[bld_tools_scoring_rubric]] | sibling | 0.45 |
| [[bld_tools_retriever_config]] | sibling | 0.44 |
| [[bld_tools_golden_test]] | sibling | 0.43 |
