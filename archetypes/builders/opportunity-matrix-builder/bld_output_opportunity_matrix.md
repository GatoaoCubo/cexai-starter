---
kind: output_template
id: bld_output_template_opportunity_matrix
pillar: P05
llm_function: PRODUCE
purpose: Template with vars for opportunity_matrix production
quality: null
title: "Output Template Opportunity Matrix"
version: "1.0.0"
author: n03_builder
tags: [opportunity_matrix, builder, output_template]
tldr: "Template with vars for opportunity_matrix production"
domain: "opportunity_matrix construction"
created: "2026-07-02"
updated: "2026-07-02"
8f: "F6_produce"
keywords: [opportunity_matrix construction, output template opportunity matrix, opportunity_matrix, builder, output_template, catalog_sources, opp_score, sourcing_confiavel, matriz de oportunidade]
density_score: 0.85
related:
  - bld_instruction_opportunity_matrix
  - bld_schema_opportunity_matrix
  - opportunity-matrix-builder
  - p11_qg_opportunity_matrix
  - p08_adr_opportunity_matrix_kind
---
```yaml
---
id: p11_om_{{slug}}
kind: opportunity_matrix
pillar: P11
title: "{{title}}"
version: "1.0.0"
author: "{{author}}"
created: "{{created}}"
updated: "{{updated}}"
domain: "{{domain}}"
quality: null
tags: [{{tags}}]
tldr: "{{tldr}}"
region: "{{region}}"
cost_source_strategy: "{{cost_source_strategy}}"
demand_signal_basis: "{{demand_signal_basis}}"
verify_top_n: {{verify_top_n}}
---
```

<!-- slug: lowercase identifier, e.g. ferramentas_q3 or hardware_catalog_2026 -->
<!-- title: Descriptive name, e.g. "Sourcing Opportunity -- Ferragens Q3 2026" -->
<!-- domain: Industry/catalog context, e.g. "tools/hardware", "pet supplies" -->
<!-- region: demand market cut, e.g. "Brasil", "Global" (default Global) -->
<!-- cost_source_strategy: one of column|filename|fixed|formula|none (default column) -->
<!-- demand_signal_basis: one of reviews|price_scrape|sales_rank|spec_sheet|manual (default reviews) -->
<!-- verify_top_n: int, top-N skeptical re-check count (default 10) -->

## Input Contract

| Key | Type | Required | Default | Note |
|-----|------|----------|---------|------|
| catalog_sources | object[] | yes | -- | >=1; supply side (PDF/CSV/XLSX/image), each `{uri, format, supplier_name, rows}` |
| cost_source_strategy | enum | no | column | column\|filename\|fixed\|formula\|none |
| tax_pct | number | no | 0 | tax on cost (e.g. IPI) |
| region | string | no | Global | demand market cut |
| demand_signal_basis | enum | no | reviews | reviews\|price_scrape\|sales_rank\|spec_sheet\|manual |
| fee_model | enum | no | percent | percent\|fixed_plus_percent\|fixed_per_unit\|tiered |
| freight_model | enum | no | none | none\|flat\|weight\|cubic |
| verify_top_n | number | no | 10 | skeptical re-check count (web price = ceiling) |
| show_net_margin | boolean | no | false | opt-in; default shows BRUTA |

## Output Sections (frozen order, from MOLD_SOURCING_OPPORTUNITY)

### 1. Resumo executivo (fields)
| Label | Value |
|-------|-------|
| Melhores apostas | `{{best_bets}}` |
| Volume play | `{{volume_play}}` |
| Margem bruta media | `{{avg_gross_margin}}` |
| Split por relevancia | `{{relevance_split}}` |
| Alerta de dado critico | `{{critical_data_alert}}` |

### 2. Matriz de oportunidade (table, 9 cols)
Columns: `#, Produto, Fornecedor (desc%), Custo, Preco mercado, Margem, Demanda, Relevancia, Score`
Ranked by `opp_score` desc. Margem shows LIQUIDA only when `show_net_margin=true` (else BRUTA).

### 3. Leitura por categoria (table, 5 cols)
Columns: `Categoria, Itens, Custo, Preco verif., Veredito`
Grouped by normalized `product_type`, sorted by group size desc.

### 4. Cobertura (fields)
| Label | Value |
|-------|-------|
| Tipos parseados | `{{n_parsed}} SKUs lidos de {{n_sources}} catalogos ({{n_types}} tipos)` |
| Tipos cruzados | `{{n_cross_referenced}} cruzados com preco+demanda de mercado` |
| Cauda-longa nao coberta | `{{n_uncovered}} SKUs sem match de demanda confiavel -- KEPT` |
| Itens sem preco verificado | `{{n_manual}} (bucket "manual / sem preco")` |

### 5. Verificacao (top-N) (table, 5 cols)
Columns: `Produto, Preco estimado, Preco real (verif.), Fontes, Confianca`
Slice = top `verify_top_n` ranked rows; web price treated as ceiling.

### 6. Match / auditoria (table, 4 cols)
Columns: `Codigo, Match?, Confianca, Flag de auditoria`
Emitted ONLY for rows carrying `photo_uri` or `dimension`; else one honest-skip row (`--, NAO, 0.0, sem insumo visual`). Shares the `product_match` engine.

### 7. Proveniencia (fields)
| Label | Value |
|-------|-------|
| Fontes consultadas | `{{sources_consulted}}` |
| Fontes sem dado | `{{sources_no_data}}` |
| Status por fonte | `{{per_source_status}}` (ok\|blocked\|skipped\|failed) |
| Banda de frescor | `{{freshness_band}}` (GREEN <90d \| AMBER 90-365d \| RED >365d) |
| Take-rate usado | `{{take_rate_label}}` |

### 8. Veredito + proximos passos (fields)
| Label | Value |
|-------|-------|
| sourcing_confiavel | `{{gate_bool}}` |
| Condicoes do gate | margem_bruta_top >= 25% AND top-N verificado AND nenhum item critico sem preco AND frescor != RED |
| Avaliacao das condicoes | `{{gate_evaluation}}` |
| Acoes ranqueadas | `{{ranked_actions}}` |
| Proximo passo encadeavel | `{{next_step}}` (feeds `marketplace_listing` / TUDAO on APROVADO) |

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[bld_prompt_opportunity_matrix]] | upstream | 0.38 |
| [[bld_schema_opportunity_matrix]] | downstream | 0.36 |
| [[opportunity-matrix-builder]] | downstream | 0.35 |
| [[p11_qg_opportunity_matrix]] | downstream | 0.34 |
| p08_adr_opportunity_matrix_kind | upstream | 0.32 |
