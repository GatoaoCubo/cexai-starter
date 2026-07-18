---
kind: schema
id: bld_schema_opportunity_matrix
pillar: P06
llm_function: CONSTRAIN
purpose: Schema formal -- FONTE ÚNICA DA VERDADE para opportunity_matrix
quality: null
title: "Schema -- Opportunity Matrix"
version: "1.0.0"
author: n03_builder
tags: [opportunity_matrix, builder, schema]
tldr: "Schema formal -- FONTE ÚNICA DA VERDADE para opportunity_matrix"
domain: "construção de opportunity_matrix"
created: "2026-07-02"
updated: "2026-07-02"
8f: "F1_constrain"
keywords: [construção de opportunity_matrix, schema opportunity matrix, opportunity_matrix, builder, schema, campos de frontmatter, estrutura do corpo, contrato de entrada, seções de saída, sourcing_confiavel]
density_score: 0.85
related:
  - roi-calculator-builder
  - research-pipeline-builder
  - scoring-rubric-builder
---
## Campos do Frontmatter
### Obrigatórios
| Campo | Tipo | Obrigatório | Padrão | Notas |
|------|------|----------|---------|-------|
| id | string | sim | null | Deve casar com o Padrão de ID |
| kind | string | sim | "opportunity_matrix" | Identificador de kind do CEX |
| pillar | string | sim | "P11" | Classificação de pillar |
| title | string | sim | null | Título descritivo |
| version | string | sim | "1.0.0" | Versionamento semântico |
| created | datetime | sim | null | Formato ISO 8601 |
| updated | datetime | sim | null | Formato ISO 8601 |
| author | string | sim | null | Parte responsável |
| domain | string | sim | "sourcing" | Contexto de domínio |
| quality | null | sim | null | Nunca se autoavalie; peer review atribui |
| tags | list | sim | [] | Metadado de palavras-chave |
| tldr | string | sim | null | Resumo do propósito |
| region | string | sim | "Global" | Recorte de mercado de demanda |
| cost_source_strategy | string | sim | "column" | Um de column\|filename\|fixed\|formula\|none |
| demand_signal_basis | string | sim | "reviews" | Um de reviews\|price_scrape\|sales_rank\|spec_sheet\|manual |

### Recomendados
| Campo | Tipo | Notas |
|------|------|-------|
| verify_top_n | int | Contagem de re-checagem cética (padrão 10) |
| show_net_margin | boolean | Exibição LIQUIDA opt-in (padrão false) |
| fee_model | string | percent\|fixed_plus_percent\|fixed_per_unit\|tiered (padrão percent) |
| freight_model | string | none\|flat\|weight\|cubic (padrão none) |
| last_reviewed | datetime | Timestamp do peer review |
| reviewers | list | Identificadores dos revisores |

## Padrão de ID
^p11_om_[a-z][a-z0-9_]+$

## Estrutura do Corpo (8 seções, ordem + layout congelados -- MOLD_SOURCING_OPPORTUNITY)
1. **Resumo executivo** (fields) -- melhores apostas, volume play, margem bruta media, split por relevancia, alerta de dado critico
2. **Matriz de oportunidade** (table, 9 cols) -- `#, Produto, Fornecedor (desc%), Custo, Preco mercado, Margem, Demanda, Relevancia, Score`
3. **Leitura por categoria** (table, 5 cols) -- `Categoria, Itens, Custo, Preco verif., Veredito`
4. **Cobertura** (fields) -- tipos parseados/cruzados, cauda-longa nao coberta, itens sem preco verificado
5. **Verificacao (top-N)** (table, 5 cols) -- `Produto, Preco estimado, Preco real (verif.), Fontes, Confianca`
6. **Match / auditoria** (table, 4 cols) -- `Codigo, Match?, Confianca, Flag de auditoria`
7. **Proveniencia** (fields) -- fontes consultadas/sem dado, status por fonte, banda de frescor, take-rate usado
8. **Veredito + proximos passos** (fields) -- gate `sourcing_confiavel`, condicoes, avaliacao, acoes ranqueadas, proximo passo

## Restrições
- O ID deve casar exatamente com o padrão regex; nomenclatura `p11_om_{{name}}.md` (conforme `.cex/kinds_meta.json`)
- Todos os campos obrigatórios devem estar presentes; corpo abaixo de 5120 bytes (`max_bytes`)
- A contagem de células de uma linha de tabela DEVE ser igual à contagem de colunas da sua seção (regra de não-drift, `_base.py table_section`)
- `depends_on`: roi_calculator (primitivo de margem por item), research_pipeline (pesquisa de demanda), scoring_rubric (critérios de ranking) -- conforme `.cex/kinds_meta.json`
- `requires_external_context: true` (pesquisa de demanda web); `requires_live_tools: false`; `primary_8f: F4_reason`
- A chave de join é o `product_type` normalizado; EAN/GTIN/código de barras NUNCA são uma chave de join (fonte: `_DEFAULT_MATCH_EXCLUDE_KEYS` do gerador)
- O campo quality deve passar por peer review; o versionamento deve seguir o formato semântico

## Artefatos Relacionados
| Artefato | Relacionamento | Pontuação |
|----------|-------------|-------|
| [[bld_prompt_opportunity_matrix]] | sibling | 0.50 |
| [[roi-calculator-builder]] | related | 0.40 |
| [[research-pipeline-builder]] | related | 0.38 |
| [[scoring-rubric-builder]] | related | 0.36 |
