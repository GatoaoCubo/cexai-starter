---
kind: tools
id: bld_tools_knowledge_card
pillar: P04
llm_function: CALL
purpose: "Ferramentas e APIs disponiveis para a producao de knowledge_card"
quality: null
title: "Ferramentas: knowledge_card"
version: "1.0.0"
author: n03_builder
tags: [knowledge_card, builder, examples]
tldr: "Exemplos-modelo e anti-exemplos de construcao de knowledge_card, demonstrando estrutura ideal e armadilhas comuns."
domain: "construcao de knowledge_card"
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
| validate_kc.py | Valida o KC: 10 portoes HARD + 20 SOFT | Fase 3 | CONDICIONAL |
| brain_query [MCP] | Busca KCs existentes no pool | Fase 1 | CONDICIONAL |
| validate_artifact.py | Validador generico de artefato | -- | [PLANEJADO] |
| cex_forge.py | Gera artefato a partir de seeds | Composicao alternativa | [PLANEJADO] |
## Uso do validate_kc.py
```bash
# Arquivo unico
python _tools/validate_kc.py path/to/p01_kc_topic.md
# Diretorio (lote)
python _tools/validate_kc.py P01_knowledge/examples/ --summary
# Saida JSON (legivel por maquina)
python _tools/validate_kc.py path/to/file.md --json
```
Saida: pass/fail dos HARD + pontuacao SOFT de 0 a 10 + veredito.
Sugestoes de correcao sao fornecidas para os portoes que falharem.
## Uso do brain_query
```python
brain_query("knowledge card about {topic}")
# Retorna: KCs existentes que casam com o topico
# Proposito: evitar duplicatas, encontrar linked_artifacts
```
## Fontes de Dado
| Fonte | Caminho | Dado |
|--------|------|------|
| CEX Schema | P01_knowledge/_schema.yaml | Definicoes de campo do KC |
| CEX Examples | P01_knowledge/examples/ | 63+ KCs reais |
| CEX Template | P01_knowledge/templates/tpl_knowledge_card.md | Template preenchivel |
| CEX Pool | artifacts/ (repositorio de origem) | 1957+ artefatos publicados |
## Permissoes de Ferramenta

| Categoria | Ferramentas | Status |
|----------|-------|--------|
| PERMITIDO | Read, Write, Edit, Bash, Glob, Grep | Explicitamente autorizado |
| NEGADO | (nenhuma) | Explicitamente bloqueado |
| EFETIVO | Bash, Edit, Glob, Grep, Read, Write | PERMITIDO menos NEGADO |

## Validacao Intermediaria
validate_kc.py esta ATIVO -- sempre rode antes de commitar.
Nenhuma checagem manual de portao e necessaria (diferente do model-card-builder).

## Related Artifacts
| Artefato | Relacao | Pontuacao |
|----------|-------------|-------|
| [[bld_tools_validation_schema]] | sibling | 0.50 |
| bld_tools_quality_gate | sibling | 0.46 |
| [[bld_tools_scoring_rubric]] | sibling | 0.45 |
| [[bld_tools_retriever_config]] | sibling | 0.44 |
| [[bld_tools_golden_test]] | sibling | 0.43 |
