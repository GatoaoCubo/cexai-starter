---
kind: collaboration
id: bld_collaboration_opportunity_matrix
pillar: P12
llm_function: COLLABORATE
purpose: Como o opportunity-matrix-builder trabalha em equipes (crews) com outros builders
quality: null
title: "Colaboração -- Opportunity Matrix"
version: "1.0.0"
author: n03_builder
tags: [opportunity_matrix, builder, collaboration]
tldr: "Como o opportunity-matrix-builder trabalha em equipes (crews) com outros builders"
domain: "construção de opportunity_matrix"
created: "2026-07-02"
updated: "2026-07-02"
8f: "F8_collaborate"
keywords: [construção de opportunity_matrix, colaboração opportunity matrix, opportunity_matrix, builder, collaboration, papel na equipe, recebe de, produz para, fronteira, canonical_product]
density_score: 0.85
related:
  - opportunity-matrix-builder
  - bld_config_opportunity_matrix
  - roi-calculator-builder
---
## Papel na Equipe
Autora o artefato de oportunidade ranqueado de custo x demanda a partir de linhas de custo de catálogo de fornecedor parseadas e sinais de demanda de mercado. Traduz dado bruto de catálogo + demanda numa classificação acionável e com gate de compra/não-compra.

## Recebe De
| Builder | O Quê | Formato |
|---------|------|--------|
| research-pipeline-builder | Sinal de preço/demanda de mercado por product_type (rigor S1-S5) | mapa estruturado de data_sources |
| roi-calculator-builder | Primitivo de margem por item (custo -> referência de matemática de ROI) | artefato roi_calculator |
| scoring-rubric-builder | Critérios de ranking/ponderação para opp_score | artefato scoring_rubric |

## Produz Para
| Builder | O Quê | Formato |
|---------|------|--------|
| mold marketplace_listing (TUDAO) | Itens GO quando o gate sourcing_confiavel passa | lista chaveada por canonical_product |
| pipeline_template (receita p11_om_sourcing_opportunity) | A seção tipada final do pipeline de sourcing composto | artefato opportunity_matrix |
| Dashboard N06 (card de capability sourcing_opportunity) | O structured_output de 8 seções renderizado no dashboard | JSON de StructuredOutput |

## Fronteira
NÃO roda o pipeline de sourcing em si (parse + pesquisa + join/pontuação é trabalho do `pipeline_template` composto, conforme o driver a do ADR -- "compor, não inventar"). NÃO realiza casamento visual de produtos ou record-linkage (isso é `product_match`, P04/N03 -- a Seção 6 só expõe o resultado desse motor, compartilhando o contrato de chave de join via `match_join_keys`/`match_exclude_keys`).

## Composições de Equipe

### Crew: "Pipeline de Sourcing"
```
  1. research-pipeline-builder   -> "sinal de preço/demanda de mercado por product_type (rigor S1-S5)"
  2. roi-calculator-builder      -> "primitivo de margem por item (referência de matemática de ROI)"
  3. scoring-rubric-builder      -> "critérios de ranking/ponderação para o opp_score"
  4. opportunity-matrix-builder  -> "join ranqueado de custo x demanda, gate sourcing_confiavel"
```
Um `pipeline_template` (receita `p11_om_sourcing_opportunity`) compõe os 3 primeiros papéis ao
redor da saída deste kind -- eu sou sempre a etapa final e tipada da composição, nunca quem
orquestra o pipeline.

### Crew: "Auditoria de Sourcing" (com product_match)
```
  1. product-match-builder      -> "spec de casamento fornecedor x anúncio + auditoria de catálogo"
  2. opportunity-matrix-builder -> "join de custo x demanda no buy-side que consome as sinalizações da auditoria"
```
A Seção 6 ("Match / auditoria") do meu artefato só existe quando uma linha carrega insumo visual
(`photo_uri` ou `dimension`) -- nesse caso, ela expõe o resultado do motor de `product_match`,
nunca o reimplementa.

## Builders dos Quais Dependo
`roi_calculator` (primitivo de margem por item que meu cálculo de margem bruta/líquida referencia,
mas não duplica); `research_pipeline` (fonte do sinal de preço/demanda de mercado, sob o rigor
S1-S5); `scoring_rubric` (critérios de ranking/ponderação para o `opp_score`); `product_match`
(P04/N03, motor de match/auditoria compartilhado da Seção 6, soft-imported, nunca reimplementado
por mim). Os três primeiros são dependências DECLARADAS de composição (`depends_on` em
`.cex/kinds_meta.json`), não imports Python -- quem de fato une os dados é o `pipeline_template`
composto, não este builder.

## Builders Que Dependem de Mim
| Builder | Por quê |
|---------|-------|
| marketplace-listing-builder (TUDAO) | Consome os itens GO do meu artefato quando o gate `sourcing_confiavel` passa, chaveados por `canonical_product` |
| pipeline_template (`p11_om_sourcing_opportunity`) | Consome meu artefato como a seção tipada final da composição de sourcing |
| Dashboard N06 (card de capability `sourcing_opportunity`) | Renderiza minhas 8 seções como `structured_output` na interface |

## Artefatos Relacionados
| Artefato | Relacionamento | Pontuação |
|----------|-------------|-------|
| [[opportunity-matrix-builder]] | upstream | 0.35 |
| [[bld_config_opportunity_matrix]] | upstream | 0.30 |
| p08_adr_opportunity_matrix_kind | upstream | 0.28 |
| [[bld_prompt_opportunity_matrix]] | upstream | 0.26 |
| [[roi-calculator-builder]] | related | 0.24 |
