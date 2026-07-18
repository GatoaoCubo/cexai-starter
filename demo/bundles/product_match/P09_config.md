---
kind: config
id: bld_config_product_match
pillar: P09
llm_function: CONSTRAIN
purpose: Convenções de nomenclatura, caminhos de arquivo, limites de tamanho, restrições operacionais
pattern: o CONFIG restringe o SCHEMA, nunca o contradiz
effort: medium
max_turns: 25
disallowed_tools: []
fork_context: null
hooks:
  pre_build: null
  post_build: null
  on_error: null
  on_quality_fail: null
permission_scope: nucleus
quality: null
title: "Configuração -- Product Match"
version: "1.0.0"
author: n03_builder
tags: [product_match, builder, examples]
tldr: "Exemplos ideais (golden) e anti-exemplos para a construção de product_match, demonstrando a estrutura ideal e as armadilhas comuns."
domain: "construção de product_match"
created: "2026-07-02"
updated: "2026-07-02"
8f: "F1_constrain"
keywords: [convenções de nomenclatura, caminhos de arquivo, limites de tamanho, restrições operacionais, construção de product_match, configuração product match, product_match, builder, examples, "p04_pm_{name}.md"]
density_score: 0.90
related:
  - bld_tools_product_match
  - bld_config_vision_tool
---
# Config: Regras de Produção do product_match
## Convenção de Nomenclatura
| Escopo | Convenção | Exemplo |
|-------|-----------|---------|
| Arquivos de artefato | `p04_pm_{name}.md` | `p04_pm_supplier_ml_catalog.md` |
| Diretório do builder | kebab-case | `product-match-builder/` |
| Campos do frontmatter | snake_case | `match_join_keys`, `match_engine`, `match_confidence_floor` |
| Slug do nome | snake_case, minúsculas, sem hifens | `supplier_ml_catalog`, `fornecedor_amazon_audit` |
| Valores de match engine | snake_case, minúsculas, enum fechado | `reverse_image`, `embedding`, `manual`, `none` |
| Nomes de chave de join | snake_case, minúsculas | `photo`, `dimension`, `supplier_code`, `code` |
Regra: o id DEVE ser igual ao stem do nome do arquivo. Hífens no id = FALHA DURA.
## Caminhos de Arquivo
- Saída: `N03_engineering/P04_tools/examples/p04_pm_{name}.md`
- Compilado: `N03_engineering/P04_tools/compiled/p04_pm_{name}.yaml`
- Implementação real (só referência, NUNCA editar a partir deste builder): `_tools/capability_generators/product_match.py`
- Espelho do contrato (só referência): `apps/dashboard_web/lib/molds.ts` (`MOLD_PRODUCT_MATCH`),
  `apps/dashboard_web/lib/capability_contracts_v1.0.md` seção 16
- Fiação de runtime (só referência): `_tools/cex_run_capability.py` `_BASE_CAPABILITIES["product_match"]`
## Limites de Tamanho (alinhados com o SCHEMA + kinds_meta.json)
- Corpo: máximo 5120 bytes (`.cex/kinds_meta.json` -> product_match.max_bytes)
- Densidade: >= 0.80 (sem enchimento)
## Enum do Motor de Match (vocabulário fechado -- product_match.py `_MATCH_ENGINE_ENUM`)
| Valor | Padrão | Implementado hoje? |
|-------|---------|---------------------|
| none | SIM (`_DEFAULT_MATCH_ENGINE`) | N/A -- força `offline=True` incondicionalmente |
| reverse_image | não | NÃO implementado -- mesma linha honest-NAO que offline, só o texto do motivo muda |
| embedding | não | NÃO implementado -- mesma linha honest-NAO |
| manual | não | NÃO implementado -- mesma linha honest-NAO |
Um valor não reconhecido cai de volta para `none` com uma nota; nunca um crash silencioso
(product_match.py:340-344).
## Enum de Chave de Join
| Valor | Alias de campo do item (o primeiro não-vazio vence) | Notas |
|-------|------------------------------------------|-------|
| photo | photo_uri, photo, image, image_uri | Membro padrão |
| dimension | dimension, dim, size | Membro padrão |
| supplier_code | code, supplier_code, sku | Membro padrão |
| code | code, supplier_code, sku | Mesmo conjunto de alias de supplier_code |
## Enum de Chave Excluída (nunca entram no join)
`ean` | `gtin` | `barcode` -- padrão `_DEFAULT_EXCLUDE_KEYS`. Uma chave de join que também aparece
em `match_exclude_keys` é removida defensivamente e registrada como nota
(product_match.py:372-377); uma spec documenta a exclusão como INTENCIONAL, nunca como workaround.
## Nomes das Seções de Saída (congelados, sensíveis à ordem)
1. `Resultado do match` (layout: table)
2. `Auditoria de catalogo` (layout: list)
3. `Proveniencia` (layout: fields)
4. `Veredito` (layout: fields)
Reordenar, renomear, ou relayoutar qualquer uma das quatro é uma FALHA DURA contra
`capability_contracts_v1.0.md` ("a FORMA é congelada; só os dados são reais").

## Artefatos Relacionados
| Artefato | Relacionamento | Pontuação |
|----------|-------------|-------|
| [[bld_tools_product_match]] | upstream | 0.33 |
| [[bld_prompt_product_match]] | upstream | 0.29 |
| [[bld_config_vision_tool]] | sibling | 0.28 |
