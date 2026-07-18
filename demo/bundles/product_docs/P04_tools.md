---
kind: tools
id: bld_tools_knowledge_card
pillar: P04
llm_function: CALL
purpose: Ferramentas e APIs disponíveis para a produção de knowledge_card
quality: null
title: "Tools Knowledge Card"
version: "1.0.0"
author: n03_builder
tags: [knowledge_card, builder, examples]
tldr: "Exemplos ideais e anti-exemplos para a construção de knowledge_card, demonstrando a estrutura ideal e as armadilhas mais comuns."
domain: "construção de knowledge_card"
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
| validate_kc.py | Validar o KC: gates 10 HARD + 20 SOFT | Fase 3 | CONDITIONAL |
| brain_query [MCP] | Buscar KCs existentes no pool | Fase 1 | CONDITIONAL |
| validate_artifact.py | Validador genérico de artefatos | -- | [PLANNED] |
| cex_forge.py | Gerar artefato a partir de seeds | Composição alternativa | [PLANNED] |
## Uso do validate_kc.py
```bash
# Single file
python _tools/validate_kc.py path/to/p01_kc_topic.md
# Directory (batch)
python _tools/validate_kc.py P01_knowledge/examples/ --summary
# JSON output (machine-readable)
python _tools/validate_kc.py path/to/file.md --json
```
Saída: HARD pass/fail + pontuação SOFT 0-10 + veredito.
Sugestões de correção são fornecidas para os gates que falharem.
## Uso do brain_query
```python
brain_query("knowledge card about {topic}")
# Returns: existing KCs matching topic
# Purpose: avoid duplicates, find linked_artifacts
```
## Fontes de Dados
| Fonte | Caminho | Dados |
|--------|------|------|
| CEX Schema | P01_knowledge/_schema.yaml | Definições de campos do KC |
| CEX Examples | P01_knowledge/examples/ | 63+ KCs reais |
| CEX Template | P01_knowledge/templates/tpl_knowledge_card.md | Template preenchível |
| CEX Pool | artifacts/ (repositório fonte) | 1957+ artefatos publicados |
## Permissões de Ferramentas

| Categoria | Ferramentas | Status |
|----------|-------|--------|
| ALLOWED | Read, Write, Edit, Bash, Glob, Grep | Explicitamente permitido |
| DENIED | (nenhuma) | Explicitamente bloqueado |
| EFFECTIVE | Bash, Edit, Glob, Grep, Read, Write | ALLOWED menos DENIED |

## Validação Intermediária
validate_kc.py está ATIVO -- rode sempre antes de commitar.
Não precisa checar gates manualmente (diferente do model-card-builder).

## Artefatos Relacionados
| Artefato | Relacionamento | Pontuação |
|----------|-------------|-------|
| [[bld_tools_validation_schema]] | irmão | 0.50 |
| bld_tools_quality_gate | irmão | 0.46 |
| [[bld_tools_scoring_rubric]] | irmão | 0.45 |
| [[bld_tools_retriever_config]] | irmão | 0.44 |
| [[bld_tools_golden_test]] | irmão | 0.43 |
