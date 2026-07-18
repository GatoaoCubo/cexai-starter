---
kind: quality_gate
id: p11_qg_product_match
pillar: P11
llm_function: GOVERN
purpose: Exemplos ideais (golden) e anti-exemplos de artefatos product_match
pattern: aprendizado few-shot -- o LLM lê estes antes de produzir
quality: null
title: "Gate -- product_match"
version: "1.0.0"
author: "builder_agent"
tags: [quality-gate, product-match, P04, record-linkage, catalog-audit, confidence-floor]
tldr: "Gate de aprovação/reprovação para artefatos product_match: cobertura do contrato de entrada, fidelidade das seções de saída ao MOLD_PRODUCT_MATCH, honestidade do motor de match, e o gate nomeado match_confiavel."
domain: "definição de spec de casamento visual de registros (record-linkage) / auditoria de catálogo -- um casador item-de-fornecedor x anúncio-de-marketplace com join por não-chave composta e uma auditoria de catálogo offline"
created: "2026-07-02"
updated: "2026-07-02"
8f: "F7_govern"
keywords: [casamento visual de registros, definição de spec de auditoria de catálogo, cobertura do contrato de entrada, fidelidade das seções de saída, honestidade do motor de match, gate nomeado match_confiavel]
density_score: 0.90
related:
  - bld_schema_product_match
---
## Gate de Qualidade

# Gate: product_match
## Definição
| Campo | Valor |
|---|---|
| métrica | pontuação de qualidade do artefato product_match |
| limiar | 7.0 (publicar >= 8.0, golden >= 9.5) |
| operador | soma ponderada |
| escopo | todos os artefatos com `kind: product_match` |
## Gates HARD
Todos precisam passar (lógica AND). Qualquer falha isolada = REJEITAR.
| ID | Verificação | Condição de Falha |
|---|---|---|
| H01 | Frontmatter parseia como YAML válido | Erro de parse no bloco de frontmatter |
| H02 | ID casa com `^p04_pm_[a-z][a-z0-9_]+$` | ID contém maiúsculas, hífens, prefixo ausente, ou espaços |
| H03 | ID é igual ao stem do nome do arquivo | `id: p04_pm_supplier_ml` mas o arquivo é `p04_pm_supplier_amz.md` |
| H04 | Kind é igual ao literal `product_match` | `kind: tool` ou `kind: catalog_audit` ou qualquer outro valor |
| H05 | Campo quality é null | `quality: 8.5` ou qualquer valor não-null |
| H06 | Todos os campos obrigatórios presentes | Falta algum de: match_join_keys, match_engine, match_confidence_floor |
| H07 | Seções de saída casam com a ordem+layout de `MOLD_PRODUCT_MATCH` | Seção ausente, reordenada, ou com layout alterado (deve ser table/list/fields/fields) |
| H08 | EAN/GTIN/código de barras nunca documentados como chave de join ativa | `match_join_keys` inclui `ean`/`gtin`/`barcode` sem uma nota de exclusão |
| H09 | match_engine é um dos 4 valores do enum fechado | Qualquer valor fora de {reverse_image, embedding, manual, none} |
| H10 | Seção Veredito carrega o gate nomeado `match_confiavel` | Nome do gate ausente, renomeado, ou lista de bloqueadores omitida |
## Pontuação SOFT
Os pesos somam 100%.
| Dimensão | Peso | Critérios |
|---|---|---|
| Cobertura do contrato de entrada | 1.5 | Os 6 campos do dashboard documentados com tipo/obrigatoriedade/padrão; override interno `match_exclude_keys` anotado |
| Fidelidade das seções de saída | 1.5 | Cada uma das 4 seções tem exatamente as colunas/chaves de `MOLD_PRODUCT_MATCH` |
| Honestidade do motor de match | 1.0 | Status de implementação por valor do enum declarado com precisão (none = único comportamento distinto hoje) |
| Piso de confiança declarado | 1.0 | `match_confidence_floor` presente e seu papel no split SIM/PARCIAL/NAO explicado |
| Exclusão de chave de join documentada | 1.0 | Padrão de `match_exclude_keys` + racional (recodificação pelo revendedor) declarado explicitamente |
| Completude do gate + bloqueadores | 1.0 | `match_confiavel` + Cobertura + Bloqueadores todos presentes e consistentes |
## Ações
| Pontuação | Nível | Ação |
|---|---|---|
| >= 9.5 | Golden | Publicar no pool como referência golden |
| >= 8.0 | Publicar | Publicar no pool, adicionar ao índice de roteamento |
| >= 7.0 | Revisar | Sinalizar para melhoria antes de publicar |
| < 7.0 | Rejeitar | Devolver ao autor com as falhas de gate específicas |
## Bypass
| Campo | Valor |
|---|---|
| condições | Protótipo interno usado apenas enquanto o motor de reverse-image ao vivo ainda não existe, nunca enviado a produção |
| aprovador | Autocertificação do autor com comentário explicando o escopo de protótipo apenas |
| trilha de auditoria | Nota de bypass em comentário do frontmatter com data de expiração |
| expiração | 14d -- protótipos precisam ser promovidos a >= 7.0 ou removidos do repositório |
| nunca_bypassar | H01 (YAML não-parseável quebra todo o tooling), H05 (gates autoavaliados corrompem as métricas de qualidade), H07 (uma seção reordenada quebra o StructuredResultView, que é fixo em fields|table|list) |

## Exemplos

# Exemplos: product-match-builder
## Exemplo Golden
ENTRADA: "Crie uma spec product_match para o casador de catálogo fornecedor-vs-MercadoLivre"
SAÍDA:
```yaml
id: p04_pm_visual_catalog_match
kind: product_match
pillar: P04
version: "1.0.0"
created: "2026-07-02"
updated: "2026-07-02"
author: "builder_agent"
name: "Supplier x Marketplace Visual Catalog Match"
contract_version: "1.0"
match_join_keys: [photo, dimension, supplier_code]
match_exclude_keys: [ean, gtin, barcode]
match_engine: none
match_confidence_floor: 0.7
audit_enabled: true
audit_min_photo_px: 200
quality: null
```
## Overview
Une um item de catálogo de fornecedor a um anúncio de marketplace por uma não-chave composta
(foto+dimensão+código do fornecedor); EAN/GTIN/código de barras são estruturalmente excluídos
porque todo revendedor os recodifica. Roda o efeito colateral de auditoria de catálogo
(divergência texto-vs-foto, foto de baixa resolução) sobre dados locais do item independente do
acesso à rede. Consumido pela execução no dashboard N03 (verbo=analyze) e por soft-import de
`sourcing_opportunity.py` (N06) para sua própria etapa de auditoria.
## Input Contract
| chave | tipo | obrigatório | padrão |
|-----|------|:---:|---------|
| items | object[] | sim | -- |
| match_join_keys | string[] | não | [photo, dimension, supplier_code] |
| match_engine | enum | não | none |
| match_confidence_floor | number | não | 0.7 |
| audit_enabled | boolean | não | true |
| audit_min_photo_px | number | não | 200 |
| match_exclude_keys (interno) | string[] | não | [ean, gtin, barcode] |
## Output Sections
A forma congelada abaixo espelha `MOLD_PRODUCT_MATCH` (apps/dashboard_web/lib/molds.ts) -- suas
próprias linhas ilustrativas de referência com "dados simulados". Uma execução REAL hoje
(match_engine=none, o padrão) retorna toda linha de match como NAO honesto com confiança 0.0
(product_match.py:386-393); a seção de auditoria é a única genuinamente ao vivo offline.
1. `Resultado do match` (table) -- colunas [Codigo, Match?, Fonte casada, Confianca]
2. `Auditoria de catalogo` (list) -- sinalizações de divergência cadastral/de foto
3. `Proveniencia` (fields) -- Motor de match, Chave de casamento, Fontes consultadas, Status por
   fonte, Honest-null offline
4. `Veredito` (fields) -- `match_confiavel`, Cobertura, Bloqueadores
POR QUE ISTO É GOLDEN:
- quality: null (H05 passa)
- id casa com o padrão p04_pm_ (H02 passa)
- kind: product_match (H04 passa)
- match_join_keys, match_engine, match_confidence_floor todos presentes (H06 passa)
- 4 seções na ordem/layout de `MOLD_PRODUCT_MATCH` (H07 passa)
- EAN/GTIN/código de barras documentados como excluídos, não como chave de join (H08 passa)
- match_engine=none é um valor válido do enum fechado (H09 passa)
- Veredito carrega `match_confiavel` + Cobertura + Bloqueadores (H10 passa)
## Anti-Exemplo
ENTRADA: "Crie um casador de produtos"
SAÍDA RUIM:
```yaml
id: product-matcher
kind: matcher
pillar: tools
name: Product Matcher
join_key: ean
capabilities: [match]
quality: 9.0
tags: [match]
```
Casa produtos por código de barras usando IA de visão.

### S_RELATED: Checagem de Referência Cruzada (SOFT)
- [ ] Campo `related:` do frontmatter preenchido (3-15 entradas)
- [ ] Seção `## Related Artifacts` presente no corpo do artefato
- [ ] Pelo menos 1 referência upstream e 1 downstream
- Penalidade: -0.3 se vazio (não bloqueia, apenas incentiva a fiação)

## Artefatos Relacionados
| Artefato | Relacionamento | Pontuação |
|----------|-------------|-------|
| p11_qg_quality_gate | sibling | 0.44 |
| [[bld_schema_product_match]] | upstream | 0.40 |
| p08_adr_opportunity_matrix_kind | upstream | 0.38 |
