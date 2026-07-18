---
kind: tools
id: bld_tools_knowledge_card
pillar: P04
llm_function: CALL
purpose: Tools and APIs available for knowledge_card production
quality: null
title: "Tools Knowledge Card"
version: "1.0.0"
author: n03_builder
tags: [knowledge_card, builder, examples]
tldr: "Golden and anti-examples for knowledge card construction, demonstrating ideal structure and common pitfalls."
domain: "knowledge card construction"
created: "2026-04-07"
updated: "2026-04-07"
8f: "F5_call"
keywords: [knowledge card construction, tools knowledge card, knowledge_card, builder, examples, production tools, data sources, tool permissions, interim validation, related artifacts]
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
| validate_kc.py | Valida a KC: gates 10 HARD + 20 SOFT | Fase 3 | CONDICIONAL |
| brain_query [MCP] | Busca KCs existentes no pool | Fase 1 | CONDICIONAL |
| validate_artifact.py | Validador genérico de artefato | -- | [PLANEJADO] |
| cex_forge.py | Gera artefato a partir de seeds | Composição alternativa | [PLANEJADO] |
## Uso do validate_kc.py
```bash
# Arquivo único
python _tools/validate_kc.py path/to/p01_kc_topic.md
# Diretório (em lote)
python _tools/validate_kc.py P01_knowledge/examples/ --summary
# Saída JSON (legível por máquina)
python _tools/validate_kc.py path/to/file.md --json
```
Saída: passa/falha HARD + score SOFT de 0 a 10 + veredito.
Sugestões de correção fornecidas para os gates que falharem.
## Uso do brain_query
```python
brain_query("knowledge card about {topic}")
# Retorna: KCs existentes que correspondem ao tópico
# Propósito: evitar duplicatas, encontrar linked_artifacts
```
## Fontes de Dados
| Fonte | Caminho | Dado |
|--------|------|------|
| CEX Schema | P01_knowledge/_schema.yaml | Definições de campo da KC |
| CEX Examples | P01_knowledge/examples/ | 63+ KCs reais |
| CEX Template | P01_knowledge/templates/tpl_knowledge_card.md | Template preenchível |
| CEX Pool | artifacts/ (repositório de origem) | 1957+ artefatos publicados |
## Permissões de Ferramenta

| Categoria | Ferramentas | Status |
|----------|-------|--------|
| PERMITIDO | Read, Write, Edit, Bash, Glob, Grep | Explicitamente permitido |
| NEGADO | (nenhuma) | Explicitamente bloqueado |
| EFETIVO | Bash, Edit, Glob, Grep, Read, Write | PERMITIDO menos NEGADO |

## Validação Provisória
O validate_kc.py está ATIVO -- sempre rode antes de commitar.
Não é necessária checagem manual de gate (diferente do model-card-builder).

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[bld_tools_validation_schema]] | sibling | 0.50 |
| bld_tools_quality_gate | sibling | 0.46 |
| [[bld_tools_scoring_rubric]] | sibling | 0.45 |
| [[bld_tools_retriever_config]] | sibling | 0.44 |
| [[bld_tools_golden_test]] | sibling | 0.43 |
