---
kind: schema
id: bld_schema_product_match
pillar: P06
llm_function: CONSTRAIN
purpose: Schema formal -- FONTE ÚNICA DA VERDADE para product_match
pattern: o TEMPLATE deriva deste. o CONFIG restringe este.
quality: null
title: "Schema -- Product Match"
version: "1.0.0"
author: n03_builder
tags:
  - "product_match"
  - "builder"
  - "examples"
tldr: "Exemplos ideais (golden) e anti-exemplos para a construção de product_match, demonstrando a estrutura ideal e as armadilhas comuns."
domain: "construção de product_match"
created: "2026-07-02"
updated: "2026-07-02"
8f: "F1_constrain"
keywords:
  - "schema formal"
  - "construção de product_match"
  - "schema product match"
  - "product_match"
  - "builder"
  - "examples"
  - "^p04_pm_[a-z][a-z0-9_]+$"
  - "## overview"
  - "## input contract"
  - "## output sections"
density_score: 0.90
related:
  - bld_schema_vision_tool
  - bld_schema_data_contract
  - bld_schema_output_validator
  - bld_config_product_match
---

# Schema: product_match
## Campos do Frontmatter
| Campo | Tipo | Obrigatório | Padrão | Notas |
|-------|------|----------|---------|-------|
| id | string (p04_pm_{name}) | SIM | - | Conformidade de namespace |
| kind | literal "product_match" | SIM | - | Integridade de tipo |
| pillar | literal "P04" | SIM | - | Atribuição de pillar (kinds_meta.json) |
| version | string semver | SIM | "1.0.0" | Versionamento do artefato |
| created | data YYYY-MM-DD | SIM | - | Data de criação |
| updated | data YYYY-MM-DD | SIM | - | Última atualização |
| author | string | SIM | - | Identidade de quem produziu |
| name | string | SIM | - | Nome legível da spec |
| contract_version | string | SIM | "1.0" | Espelha `MOLD_PRODUCT_MATCH.contract_version` (molds.ts) |
| match_join_keys | list[string] | RECOMENDADO | [photo, dimension, supplier_code] | Campos de join por não-chave composta |
| match_exclude_keys | list[string] | RECOMENDADO | [ean, gtin, barcode] | Nunca entram no join (todo revendedor os recodifica) |
| match_engine | enum: reverse_image, embedding, manual, none | RECOMENDADO | none | Vocabulário fechado -- `_MATCH_ENGINE_ENUM` em product_match.py |
| match_confidence_floor | float 0.0-1.0 | RECOMENDADO | 0.7 | Piso que um match precisa ultrapassar para contar como SIM |
| audit_enabled | boolean | RECOMENDADO | true | Ativa/desativa o efeito colateral de auditoria de catálogo |
| audit_min_photo_px | integer | RECOMENDADO | 200 | Abaixo disso, uma foto é sinalizada como baixa resolução |
| quality | null | SIM | null | Nunca se autoavalie |
| tags | list[string], len >= 3 | SIM | - | Deve incluir "product_match" |
| tldr | string <= 160ch | SIM | - | Resumo denso |
| description | string <= 200ch | RECOMENDADO | - | O que a spec casa/audita |
## Padrão de ID
Regex: `^p04_pm_[a-z][a-z0-9_]+$`
Regra: o id DEVE ser igual ao stem do nome do arquivo. Fonte: `.cex/kinds_meta.json` naming
`p04_pm_{{name}}.md`.
## Estrutura do Corpo (seções obrigatórias)
1. `## Overview` -- o que é casado/auditado, quem consome a saída, enquadramento offline-first
2. `## Input Contract` -- os 6 campos expostos no dashboard (items, match_join_keys, match_engine,
   match_confidence_floor, audit_enabled, audit_min_photo_px) + o override interno
   `match_exclude_keys` (lido pelo gerador, ausente de `MOLD_PRODUCT_MATCH`)
3. `## Output Sections` -- as 4 seções congeladas, em ordem: Resultado do match (table),
   Auditoria de catalogo (list), Proveniencia (fields), Veredito (fields)
4. `## Gate` -- o gate nomeado `match_confiavel` + seu vocabulário de bloqueadores
## Restrições
- max_bytes: 5120 (só o corpo -- max_bytes de product_match em `.cex/kinds_meta.json`)
- naming: p04_pm_{name}.md
- machine_format: yaml (artefato compilado via cex_compile.py)
- id == stem do nome do arquivo
- a ordem+layout das seções de saída são CONGELADOS em `MOLD_PRODUCT_MATCH`
  (apps/dashboard_web/lib/molds.ts) -- uma spec NÃO PODE reordenar, renomear ou relayoutar uma
  seção (StructuredResultView é fixo em fields|table|list; ver
  `capability_contracts_v1.0.md` "How to build to this contract")
- match_join_keys NUNCA PODE admitir silenciosamente uma chave excluída -- product_match.py:372-377
  remove defensivamente qualquer chave-de-exclusão vazada e registra uma nota; uma spec documenta
  a mesma exclusão, não um workaround
- quality: null sempre
- SEM código de implementação no corpo -- só spec (a implementação real vive em
  `_tools/capability_generators/product_match.py`, de propriedade da engenharia N03, não dos
  artefatos de spec deste kind)
- depends_on (kinds_meta.json, dependência DECLARADA de taxonomia, NÃO um import Python):
  `vision_tool`, `data_contract`, `output_validator` -- verificado via grep que
  `product_match.py` não importa NEM um módulo vision_tool (nenhum existe em
  `_tools/capability_generators/`) NEM nenhum módulo de schema/validador; a dependência é
  composicional (uma spec completa cita o primitivo visual que seu `match_engine` eventualmente
  chamaria, o contrato de dados para `items`, e o validador de saída para as 4 seções), não um
  `import` de runtime.

## Artefatos Relacionados
| Artefato | Relacionamento | Pontuação |
|----------|-------------|-------|
| [[bld_schema_vision_tool]] | sibling | 0.55 |
| [[bld_schema_data_contract]] | upstream | 0.40 |
| [[bld_schema_output_validator]] | upstream | 0.38 |
| [[bld_config_product_match]] | downstream | 0.35 |
