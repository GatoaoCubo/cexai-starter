---
kind: tools
id: bld_tools_product_match
pillar: P04
llm_function: CALL
purpose: Ferramentas e APIs disponíveis para a produção de product_match
quality: null
title: "Ferramentas -- Product Match"
version: "1.0.0"
author: n03_builder
tags: [product_match, builder, examples]
tldr: "Exemplos ideais (golden) e anti-exemplos para a construção de product_match, demonstrando a estrutura ideal e as armadilhas comuns."
domain: "construção de product_match"
created: "2026-07-02"
updated: "2026-07-02"
8f: "F5_call"
keywords: [construção de product_match, ferramentas product match, product_match, builder, examples, ferramentas de produção, fontes de dados, referência do motor de match, chaves de join, implementação real]
density_score: 0.90
related:
  - bld_tools_vision_tool
  - bld_tools_output_validator
  - bld_schema_product_match
  - bld_config_product_match
---
# Ferramentas: product-match-builder
## Ferramentas de Produção
| Ferramenta | Propósito | Quando | Status |
|------|---------|------|--------|
| brain_query [MCP] | Busca artefatos product_match existentes no pool | Fase 1 (checar duplicatas) | CONDICIONAL |
| validate_artifact.py | Validador genérico de artefatos | Fase 3 | [PLANEJADO] |
| cex_run_capability.py --capability product_match | Exercita o gerador REAL contra itens de exemplo (checagem de ground-truth) | Fase 1/3 | DISPONÍVEL |
## Fontes de Dados
| Fonte | Caminho/URL | Dados |
|--------|----------|------|
| Registro de kinds do CEX | `.cex/kinds_meta.json` (chave `product_match`) | pillar, max_bytes, naming, depends_on, primary_8f |
| Gerador real (ground truth) | `_tools/capability_generators/product_match.py` | comportamento real de `build()` -- campos, seções, gate, fórmula de pontuação |
| Espelho do contrato | `apps/dashboard_web/lib/capability_contracts_v1.0.md` seção 16 | tabela de contrato de entrada/saída voltada ao dashboard |
| Mold (forma congelada) | `apps/dashboard_web/lib/molds.ts` (`MOLD_PRODUCT_MATCH`) | linhas mock de exemplo, `contract_version` |
| Fiação de runtime | `_tools/cex_run_capability.py` `_BASE_CAPABILITIES["product_match"]` | nucleus=N03, pillar=P04, verbo=analyze |
| ADR de origem | `N06_commercial/P08_architecture/p08_adr_opportunity_matrix_kind.md` | por que o kind existe, racional das chaves de join |
| Rigor de domínio | `_docs/specs/contract/n01_sourcing_rigor.md`, `n03_schema.md`, `n03_validation.md` | rigor de sourcing S1-S5 + doutrina de tipo/validação |
## Referência do Motor de Match (status conforme implementado -- ver bld_knowledge_product_match.md para a matriz completa)
| Motor | Tipo | Implementado? | Notas |
|--------|------|:---:|-------|
| none | padrão | N/A (força offline) | Toda linha é honest-NAO com confiança 0.0 |
| reverse_image | valor do enum | NÃO | Eventualmente encapsularia um primitivo `vision_tool` (intenção do ADR); nenhum caminho de código existe |
| embedding | valor do enum | NÃO | Nenhuma chamada de similaridade vetorial existe |
| manual | valor do enum | NÃO | Nenhuma integração com fila de revisão manual existe |
## Auxiliares Puros Compartilhados (importáveis pelo nome -- product_match.py `__all__`)
| Auxiliar | Assinatura | Consumidor |
|--------|-----------|----------|
| `_normalize_join_key` | `(item, join_keys, exclude_keys) -> str` | `sourcing_opportunity.py` (soft-import, product_match.py:314-330) |
| `_audit_text_vs_photo` | `(item, min_photo_px=200) -> Optional[str]` | `sourcing_opportunity.py` (mesmo bloco de soft-import) |
Ambas são PURAS (sem I/O), TOTAIS (nunca lançam exceção -- degrade-never), e ASCII-safe conforme a
regra de código.
## Permissões de Ferramentas

| Categoria | Ferramentas | Status |
|----------|-------|--------|
| PERMITIDAS | Read, Write, Edit, Bash, Glob, Grep | Explicitamente permitidas |
| NEGADAS | (nenhuma) | Explicitamente bloqueadas |
| EFETIVAS | Bash, Edit, Glob, Grep, Read, Write | PERMITIDAS menos NEGADAS |

## Validação Interina
Ainda não existe validador automatizado para artefatos de spec product_match. Verifique
manualmente cada gate de `p11_qg_product_match.md` contra o artefato produzido. Checagens-chave:
YAML parseia, o padrão de id casa com `p04_pm_`, as seções de saída casam com a ordem+layout de
`MOLD_PRODUCT_MATCH`, corpo <= 5120 bytes, quality == null, match_engine é um dos 4 valores do
enum fechado, EAN/GTIN/código de barras nunca listados como chave de join ativa.

## Artefatos Relacionados
| Artefato | Relacionamento | Pontuação |
|----------|-------------|-------|
| [[bld_tools_vision_tool]] | sibling | 0.49 |
| [[bld_tools_output_validator]] | sibling | 0.46 |
| [[bld_schema_product_match]] | upstream | 0.40 |
| [[bld_config_product_match]] | sibling | 0.38 |
| n01_sourcing_rigor | related | 0.33 |
