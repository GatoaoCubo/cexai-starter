---
kind: output_template
id: bld_output_template_opportunity_matrix
pillar: P05
llm_function: PRODUCE
purpose: Modelo com variáveis para a produção de opportunity_matrix
quality: null
title: "Modelo de Saída -- Opportunity Matrix"
version: "1.0.0"
author: n03_builder
tags: [opportunity_matrix, builder, output_template]
tldr: "Modelo com variáveis para a produção de opportunity_matrix"
domain: "construção de opportunity_matrix"
created: "2026-07-02"
updated: "2026-07-02"
8f: "F6_produce"
keywords: [construção de opportunity_matrix, modelo de saída opportunity matrix, opportunity_matrix, builder, output_template, catalog_sources, opp_score, sourcing_confiavel, matriz de oportunidade]
density_score: 0.85
related:
  - bld_schema_opportunity_matrix
  - opportunity-matrix-builder
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

<!-- slug: identificador em minúsculas, ex.: ferramentas_q3 ou hardware_catalog_2026 -->
<!-- title: nome descritivo, ex.: "Sourcing Opportunity -- Ferragens Q3 2026" -->
<!-- domain: contexto de indústria/catálogo, ex.: "tools/hardware", "pet supplies" -->
<!-- region: recorte de mercado de demanda, ex.: "Brasil", "Global" (padrão Global) -->
<!-- cost_source_strategy: um de column|filename|fixed|formula|none (padrão column) -->
<!-- demand_signal_basis: um de reviews|price_scrape|sales_rank|spec_sheet|manual (padrão reviews) -->
<!-- verify_top_n: inteiro, contagem de re-checagem cética top-N (padrão 10) -->

## Contrato de Entrada

| Chave | Tipo | Obrigatório | Padrão | Nota |
|-----|------|----------|---------|------|
| catalog_sources | object[] | sim | -- | >=1; lado da oferta (PDF/CSV/XLSX/imagem), cada `{uri, format, supplier_name, rows}` |
| cost_source_strategy | enum | não | column | column\|filename\|fixed\|formula\|none |
| tax_pct | number | não | 0 | imposto sobre o custo (ex.: IPI) |
| region | string | não | Global | recorte de mercado de demanda |
| demand_signal_basis | enum | não | reviews | reviews\|price_scrape\|sales_rank\|spec_sheet\|manual |
| fee_model | enum | não | percent | percent\|fixed_plus_percent\|fixed_per_unit\|tiered |
| freight_model | enum | não | none | none\|flat\|weight\|cubic |
| verify_top_n | number | não | 10 | contagem de re-checagem cética (preço web = teto) |
| show_net_margin | boolean | não | false | opt-in; padrão mostra BRUTA |

## Seções de Saída (ordem congelada, de MOLD_SOURCING_OPPORTUNITY)

### 1. Resumo executivo (fields)
| Label | Value |
|-------|-------|
| Melhores apostas | `{{best_bets}}` |
| Volume play | `{{volume_play}}` |
| Margem bruta media | `{{avg_gross_margin}}` |
| Split por relevancia | `{{relevance_split}}` |
| Alerta de dado critico | `{{critical_data_alert}}` |

### 2. Matriz de oportunidade (table, 9 cols)
Colunas: `#, Produto, Fornecedor (desc%), Custo, Preco mercado, Margem, Demanda, Relevancia, Score`
Ranqueado por `opp_score` decrescente. Margem mostra LIQUIDA só quando `show_net_margin=true` (senão BRUTA).

### 3. Leitura por categoria (table, 5 cols)
Colunas: `Categoria, Itens, Custo, Preco verif., Veredito`
Agrupado por `product_type` normalizado, ordenado por tamanho de grupo decrescente.

### 4. Cobertura (fields)
| Label | Value |
|-------|-------|
| Tipos parseados | `{{n_parsed}} SKUs lidos de {{n_sources}} catalogos ({{n_types}} tipos)` |
| Tipos cruzados | `{{n_cross_referenced}} cruzados com preco+demanda de mercado` |
| Cauda-longa nao coberta | `{{n_uncovered}} SKUs sem match de demanda confiavel -- KEPT` |
| Itens sem preco verificado | `{{n_manual}} (bucket "manual / sem preco")` |

### 5. Verificacao (top-N) (table, 5 cols)
Colunas: `Produto, Preco estimado, Preco real (verif.), Fontes, Confianca`
Recorte = as `verify_top_n` linhas mais bem ranqueadas; preço web tratado como teto.

### 6. Match / auditoria (table, 4 cols)
Colunas: `Codigo, Match?, Confianca, Flag de auditoria`
Emitida SÓ para linhas que carregam `photo_uri` ou `dimension`; caso contrário, uma única linha de honest-skip (`--, NAO, 0.0, sem insumo visual`). Compartilha o motor `product_match`.

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
| Proximo passo encadeavel | `{{next_step}}` (alimenta `marketplace_listing` / TUDAO quando APROVADO) |

## Artefatos Relacionados
| Artefato | Relacionamento | Pontuação |
|----------|-------------|-------|
| [[bld_prompt_opportunity_matrix]] | upstream | 0.38 |
| [[bld_schema_opportunity_matrix]] | downstream | 0.36 |
| [[opportunity-matrix-builder]] | downstream | 0.35 |
| p08_adr_opportunity_matrix_kind | upstream | 0.32 |
