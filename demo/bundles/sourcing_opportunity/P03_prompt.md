---
kind: instruction
id: bld_instruction_opportunity_matrix
pillar: P03
llm_function: REASON
purpose: Processo de produção passo a passo para opportunity_matrix
quality: null
title: "Instruções -- Opportunity Matrix"
version: "1.0.0"
author: n03_builder
tags: [opportunity_matrix, builder, instruction]
tldr: "Processo de produção passo a passo para opportunity_matrix"
domain: "construção de opportunity_matrix"
created: "2026-07-02"
updated: "2026-07-02"
8f: "F6_produce"
keywords: [construção de opportunity_matrix, instruções opportunity matrix, opportunity_matrix, builder, instruction, catalog_sources, opp_score, sourcing_confiavel, join de demanda, matemática de margem]
density_score: 0.85
related:
  - opportunity-matrix-builder
---
## Fase 1: PESQUISA
1. Leia as 9 entradas do `input_contract` congelado (`apps/dashboard_web/lib/molds.ts` `MOLD_SOURCING_OPPORTUNITY`): `catalog_sources` (obrigatório, object[]), `cost_source_strategy`, `tax_pct`, `region`, `demand_signal_basis`, `fee_model`, `freight_model`, `verify_top_n`, `show_net_margin`.
2. Leia o gerador que de fato produz este kind: `_tools/capability_generators/sourcing_opportunity.py` (`@register("opportunity_matrix")`) -- é a fonte única da verdade para nomes de campo, padrões e texto de seção.
3. Leia o contrato de rigor de sourcing (`_docs/specs/contract/n01_sourcing_rigor.md`): S1 triangulação+confiança, S2 proveniência-como-seção, S3 banda de frescor, S4 gate nomeado, S5 honest-null.
4. Leia a disciplina de margem/take-rate referenciada pelo contrato de capability (`_docs/specs/contract/n06_unit_econ.md`, citado genericamente para a matemática custo->preço->take-rate->margem -- note que o próprio pacote de seção LTV/CAC desse documento é voltado a `content_monetization`/`subscription_tier`, NÃO a este kind; opportunity_matrix implementa sua própria matemática de margem bruta/líquida diretamente no gerador).
5. Identifique a chave de join: `product_type` normalizado (minúsculas, espaços colapsados) cruza custo de fornecedor contra demanda de mercado -- NUNCA EAN/GTIN/código de barras (padrão de `match_exclude_keys`).
6. Observe os dois buckets de linha que o gerador mantém (nunca descarta): linhas `priced` (unit_cost derivável) e o bucket manual `"manual / sem preco"` (sem custo derivável -- mantido, exposto em Cobertura).

## Fase 2: COMPOSIÇÃO
1. Defina o schema em `bld_schema_opportunity_matrix.md`: campos de frontmatter, padrão de ID `^p11_om_[a-z][a-z0-9_]+$`, nomenclatura `p11_om_{{name}}.md`, max_bytes 5120.
2. Construa as 8 seções na ordem CONGELADA (título + layout + colunas byte-idênticos a `MOLD_SOURCING_OPPORTUNITY`): Resumo executivo (fields) -> Matriz de oportunidade (table, 9 cols) -> Leitura por categoria (table, 5 cols) -> Cobertura (fields) -> Verificacao top-N (table, 5 cols) -> Match / auditoria (table, 4 cols) -> Proveniencia (fields) -> Veredito + proximos passos (fields).
3. Calcule a margem: `gross_margin = venda - custo`; `net_margin = venda - custo - taxa - frete` (taxa via `fee_model`, frete via `freight_model`); a coluna de exibição mostra BRUTA a menos que `show_net_margin=true`.
4. Calcule `opp_score` como a soma ponderada dos fatores normalizados de margem/demanda/estoque/confiança (`score_weights`, padrão 0.4/0.3/0.2/0.1), depois ranqueie decrescente com a ordem de desempate.
5. Renderize toda célula de mercado/demanda ausente como honest-null (`"nao pesquisado"`) quando offline (sem credencial ou sem `demand_sources`) -- nunca invente um preço de venda.
6. Popule a Seção 6 (Match / auditoria) SÓ quando uma linha carrega insumo visual (`photo_uri` ou `dimension`); caso contrário emita a única linha de honest-skip.
7. Feche com a Seção 8: nomeie o gate `sourcing_confiavel`, explicite suas condições booleanas, e declare o próximo passo encadeável (alimenta `marketplace_listing` / TUDAO quando o gate passa).
8. Faça peer-review das formas de seção contra as expectativas de `_tools/tests/test_capgen_sourcing.py` (referência somente-leitura -- não edite esse arquivo).
9. Finalize o artefato com `quality: null` e controle de versão.

## Fase 3: VALIDAÇÃO
1. [ ] Verifique se os 8 títulos + layouts de seção casam exatamente com `MOLD_SOURCING_OPPORTUNITY`.
2. [ ] Verifique se toda linha de tabela tem exatamente `len(columns)` células (regra de não-drift).
3. [ ] Confirme que o gate `sourcing_confiavel` é nomeado com condições explícitas, não só um booleano.
4. [ ] Confirme que nenhum preço de venda/nível de demanda fabricado aparece onde a fonte está offline ou bloqueada.
5. [ ] Confirme que EAN/GTIN/código de barras nunca aparecem como a chave de join.

## Artefatos Relacionados
| Artefato | Relacionamento | Pontuação |
|----------|-------------|-------|
| [[opportunity-matrix-builder]] | downstream | 0.44 |
| [[bld_knowledge_opportunity_matrix]] | upstream | 0.40 |
| sourcing | related | 0.38 |

<!-- cex:domain_contract:start -->
## Domain Contract -- Enforced Rules (real law from the generator)

> Source: `_tools/capability_generators/sourcing_opportunity.py`'s `domain_contract()` -- read directly from the generator's own module constants (never re-typed by hand, never fabricated). Injected by `_tools/cex_bundle_deepen.py`; re-running regenerates this section idempotently.

**Contract Version**: 1.0.0

### Enums
- **cost_source_strategy**: column, filename, fixed, formula, none
- **demand_signal_basis**: reviews, price_scrape, sales_rank, spec_sheet, manual
- **fee_model**: percent, fixed_plus_percent, fixed_per_unit, tiered
- **freight_model**: none, flat, weight, cubic

### Cost Sourcing
- **default_strategy**: column
- **discount_filename_pattern**: (\d{1,2})
- **cost_column_aliases**: cost, unit_cost, custo, preco_custo, cost_price

### Demand Signal
- **default_basis**: reviews
- **level_labels**: high, medium, low, uncertain
- **level_weights**: 3, 2, 1, 0

### Take Rate
| Key | Value |
|-----|-------|
| default_fee_model | percent |
| default_freight_model | none |
| marketplace_fee_pct | 0.18 |
| marketplace_fee_fixed | 0.0 |
| tax_pct | 0.0 |
| show_net_margin_default | False |

### Score Weights
| Key | Value |
|-----|-------|
| margin | 0.4 |
| demand | 0.3 |
| stock | 0.2 |
| confidence | 0.1 |

### Ranking
- **tie_break_order**: has_market, demand, spread
- **type_cap**: 0

### Coverage And Rigor
| Key | Value |
|-----|-------|
| min_sources_per_type | 3 |
| data_window_days | 90 |
| treat_web_price_as_ceiling | True |
| coverage_report | True |
| verify_top_n | 10 |
| region | Global |

### Honest Null Tokens
- [UNAVAILABLE]
- [LOW]

### Relevance Taxonomy
- core
- adjacent
- both
- other

### Match And Audit
- **join_keys**: photo, dimension, supplier_code
- **exclude_keys**: ean, gtin, barcode
- **min_photo_px**: 200

### Honest Null Labels
| Key | Value |
|-----|-------|
| demand | nao pesquisado |
| price | nao pesquisado |
| manual_bucket | manual / sem preco |
| not_applicable | N/A |
<!-- cex:domain_contract:end -->
