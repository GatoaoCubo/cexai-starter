---
id: bld_orchestration_marketplace_listing
kind: workflow
pillar: P12
llm_function: COLLABORATE
8f: F8_collaborate
version: 1.0.0
created: "2026-07-02"
updated: "2026-07-02"
author: n03_builder
title: "Orquestração: despachando + compondo marketplace_listing"
domain: marketplace_listing
quality: null
tags: [marketplace_listing, builder, orchestration, dual-output, P12]
tldr: "Como as construções de marketplace_listing são despachadas (um SKU por construção) e como o caminho de runtime SEPARADO (cex_run_capability + capability_generators + cex_dual_output) de fato atende um tenant ao vivo."
density_score: 0.88
related:
  - bld_architecture_marketplace_listing
  - bld_prompt_marketplace_listing
  - bld_tools_marketplace_listing
  - output-validator-builder
---

# Orquestração: marketplace_listing
## Construção única (o caminho deste builder)
`marketplace-listing-builder` executa F1-F8 sobre uma linha G1 -> uma instância
`p05_ml_{sku}.md`. 8F padrão: F1 restringe kind/pillar/naming, F2 carrega os ISOs, F3
injeta a linha G1 + [[bld_knowledge_marketplace_listing]], F4 planeja o mapeamento de
campos + a matemática do gate, F5 verifica as ferramentas, F6 autora as 6 seções, F7
valida os gates, F8 compila + comita.

## O caminho de runtime SEPARADO (o que um tenant ao vivo realmente dispara)
Um tenant clicando em "gerar" na capability marketplace_listing do dashboard NÃO executa
este builder. O que roda é: `cex_run_capability.py` resolve
`capability_generators.get_generator("marketplace_listing")` -> `build(inputs)` (Python
puro, determinístico) -> `cex_dual_output.to_dual_output("marketplace_listing", struct,
media_requests=listing_media_requests(inputs), produced_media=listing_produced_media(inputs))`
-> `{machine_md, human_html, media_slots}`, persistido por tenant (RLS). O trabalho deste
builder é manter o contrato ARQUETÍPICO `p05_ml_*` idêntico em formato/byte a esse caminho
de runtime -- não substituí-lo.

## Composição downstream
Uma instância autorada por builder é um exemplo de referência/fixture/padrão-ouro
(documentação, QA, onboarding antes de um tenant ter dados G1 ao vivo) -- consumida onde
quer que um exemplo governado de "como é um marketplace_listing" seja necessário. Ela se
compõe com [[output-validator-builder]] (o kind sibling do P05 do qual este `depends_on`,
conforme `.cex/kinds_meta.json`) para uma futura etapa de validação, e com
spec_dual_output_contract para o formato dual-output com o qual deve continuar
compatível.

## Convergência
Ainda não existe um laço de swarm/cobertura de biblioteca para este kind (diferente da
matriz design_system x primitive de `motion_scene`) -- o eixo de cobertura de hoje é uma
instância por SKU, construída sob demanda, não pré-populada.

## Artefatos Relacionados
| Artefato | Relação | Pontuação |
|----------|-------------|-------|
| [[bld_architecture_marketplace_listing]] | upstream | 0.5 |
| [[bld_prompt_marketplace_listing]] | sibling | 0.42 |
| [[bld_tools_marketplace_listing]] | related | 0.4 |
| spec_dual_output_contract | related | 0.4 |
| [[output-validator-builder]] | related | 0.38 |
