---
kind: knowledge_card
id: bld_knowledge_card_opportunity_matrix
pillar: P01
llm_function: INJECT
purpose: Conhecimento de domínio para a produção de opportunity_matrix
quality: null
title: "Ficha de Conhecimento -- Opportunity Matrix"
version: "1.0.0"
author: n03_builder
tags: [opportunity_matrix, builder, knowledge_card]
tldr: "Conhecimento de domínio para a produção de opportunity_matrix"
domain: "construção de opportunity_matrix"
created: "2026-07-02"
updated: "2026-07-02"
8f: "F3_inject"
keywords: [construção de opportunity_matrix, ficha de conhecimento opportunity matrix, opportunity_matrix, builder, knowledge_card, visão geral do domínio, conceitos-chave, sourcing buy-side, take-rate, opp_score]
density_score: 0.85
related:
  - roi-calculator-builder
  - opportunity-matrix-builder
---
## Visão Geral do Domínio
`opportunity_matrix` (P11, N06, verbo `analyze`) quantifica decisões de sourcing buy-side cruzando o custo do fornecedor (o lado da OFERTA, extraído dos catálogos do tenant) contra preço de mercado e demanda por tipo de produto. É o gêmeo inbound do `marketplace_listing` (o mold de projeção de canal outbound/TUDAO): os dois compartilham exatamente um seam, o registro `canonical_product`, e ambos reusam o mesmo casador visual (`product_match`) para resolução de identidade. O gerador real (`_tools/capability_generators/sourcing_opportunity.py`, slug de capability `sourcing_opportunity`) é offline-determinístico: nunca chama rede ou LLM, e degrada para células honest-null em vez de fabricar dado de mercado quando nenhuma credencial/`demand_sources` é fornecida.

## Conceitos-Chave
| Conceito | Definição | Fonte |
|---------|-----------|--------|
| Estratégia de fonte de custo | Como unit_cost é derivado de uma linha de catálogo: column\|filename\|fixed\|formula\|none | sourcing_opportunity.py::_row_cost |
| Bucket manual | Linhas sem custo derivável -- MANTIDAS (nunca descartadas), expostas em Cobertura como "manual / sem preco" | sourcing_opportunity.py |
| Take-rate | fee_model x freight_model combinados; net_margin = venda - custo - taxa - frete | sourcing_opportunity.py::_fee_amount/_freight_amount |
| opp_score | Ranking ponderado: 0.4 margem + 0.3 demanda + 0.2 estoque + 0.1 confiança (padrões, sobrescrevível via score_weights) | sourcing_opportunity.py::_DEFAULT_SCORE_WEIGHTS |
| sourcing_confiavel | Gate nomeado de go/no-go: margem_bruta_top >= 25% AND top-N verificado AND nenhum item critico sem preco AND frescor != RED | sourcing_opportunity.py Seção 8 |
| Rigor de sourcing S1-S5 | Triangulação+confiança, proveniência-como-seção, banda de frescor, gate nomeado, honest-null | _docs/specs/contract/n01_sourcing_rigor.md |
| Chave de join | product_type normalizado (minúsculas, espaços colapsados); EAN/GTIN/código de barras explicitamente EXCLUÍDOS | sourcing_opportunity.py::_DEFAULT_MATCH_EXCLUDE_KEYS |

## Padrões da Indústria
- Análise de sourcing de procurement/arbitragem buy-side (ranking de custo-vs-demanda em varejo + atacado)
- Padrão de banda de frescor compartilhado com `competitor_benchmark` (GREEN/AMBER/RED)
- Padrão de encadeamento de gate nomeado compartilhado com `ready_for_ads` (verticais de pesquisa N01)

## Padrões Comuns
1. Manter toda linha parseada em algum lugar (bucket priced / manual / cauda-longa) -- nunca descartar silenciosamente (S5)
2. Tratar o preço web verificado como um TETO na re-checagem cética do top-N, nunca como piso
3. Exibir margem BRUTA por padrão; LIQUIDA só quando `show_net_margin=true` (opt-in)
4. Encadear um gate aprovado (`sourcing_confiavel: true`) para `marketplace_listing` (TUDAO) como próximo passo
5. Emitir a Seção 6 (Match/auditoria) só quando existe insumo visual (foto/dimensão) numa linha

## Armadilhas
- Fabricar um preço de venda ou nível de demanda quando offline (sem credencial / sem demand_sources) -- deve renderizar "nao pesquisado"
- Usar EAN/GTIN/código de barras como chave de join entre marketplaces (todo revendedor recodifica produtos white-label)
- Truncar SKUs de cauda-longa silenciosamente em vez de reportá-los em Cobertura (type_cap padrão é 0 = sem truncamento)
- Confundir este kind com `roi_calculator` (matemática de margem de uma única linha) ou `competitive_matrix` (battlecard de features de concorrentes) -- `opportunity_matrix` é o JOIN ranqueado multi-linha de custo x demanda

## Artefatos Relacionados
| Artefato | Relacionamento | Pontuação |
|----------|-------------|-------|
| p08_adr_opportunity_matrix_kind | upstream | 0.55 |
| [[roi-calculator-builder]] | sibling | 0.45 |
| [[opportunity-matrix-builder]] | downstream | 0.42 |
| [[bld_prompt_opportunity_matrix]] | downstream | 0.38 |
