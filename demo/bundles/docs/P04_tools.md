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
## Ferramentas de Producao
| Ferramenta | Proposito | Quando | Status |
|------|---------|------|--------|
| validate_kc.py | Valida o KC: gates 10 HARD + 20 SOFT | Fase 3 | CONDICIONAL |
| brain_query [MCP] | Busca KCs existentes no pool | Fase 1 | CONDICIONAL |
| validate_artifact.py | Validador generico de artefatos | -- | [PLANEJADO] |
| cex_forge.py | Gera artefato a partir de seeds | Composicao alternativa | [PLANEJADO] |
## Uso do validate_kc.py
```bash
# Single file
python _tools/validate_kc.py path/to/p01_kc_topic.md
# Directory (batch)
python _tools/validate_kc.py P01_knowledge/examples/ --summary
# JSON output (machine-readable)
python _tools/validate_kc.py path/to/file.md --json
```
Saida: aprovacao/reprovacao HARD + pontuacao SOFT 0-10 + veredito.
Sugestoes de correcao fornecidas para os gates que falharem.
## Uso do brain_query
```python
brain_query("knowledge card about {topic}")
# Returns: existing KCs matching topic
# Purpose: avoid duplicates, find linked_artifacts
```
## Fontes de Dados
| Fonte | Caminho | Dado |
|--------|------|------|
| CEX Schema | P01_knowledge/_schema.yaml | Definicoes de campos do KC |
| CEX Examples | P01_knowledge/examples/ | 63+ KCs reais |
| CEX Template | P01_knowledge/templates/tpl_knowledge_card.md | Template preenchivel |
| CEX Pool | artifacts/ (repositorio de origem) | 1957+ artefatos publicados |
## Permissoes de Ferramentas

| Categoria | Ferramentas | Status |
|----------|-------|--------|
| PERMITIDO | Read, Write, Edit, Bash, Glob, Grep | Explicitamente permitido |
| NEGADO | (nenhuma) | Explicitamente bloqueado |
| EFETIVO | Bash, Edit, Glob, Grep, Read, Write | PERMITIDO menos NEGADO |

## Validacao Interina
validate_kc.py esta ATIVO -- sempre execute antes de commitar.
Nenhuma checagem manual de gate e necessaria (diferente do model-card-builder).

## Artefatos Relacionados
| Artefato | Relacionamento | Pontuacao |
|----------|-------------|-------|
| [[bld_tools_validation_schema]] | irmao | 0.50 |
| bld_tools_quality_gate | irmao | 0.46 |
| [[bld_tools_scoring_rubric]] | irmao | 0.45 |
| [[bld_tools_retriever_config]] | irmao | 0.44 |
| [[bld_tools_golden_test]] | irmao | 0.43 |
