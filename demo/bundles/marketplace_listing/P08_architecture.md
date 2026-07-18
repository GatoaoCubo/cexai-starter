---
id: bld_architecture_marketplace_listing
kind: pattern
pillar: P08
llm_function: CONSTRAIN
8f: F1_constrain
version: 1.0.0
created: "2026-07-02"
updated: "2026-07-02"
author: n03_builder
title: "Arquitetura: onde o marketplace_listing se encaixa"
domain: marketplace_listing
quality: null
tags: [marketplace_listing, builder, architecture, channel-adapter, P08]
tldr: "Como marketplace_listing se encaixa no CEXAI: kind definido por kinds_meta.json (upstream_source=cex_channel_adapter.py), computado em runtime pelo generator de capability_generators, dual-projetado por cex_dual_output, espelhado no dashboard por molds.ts."
density_score: 0.9
related:
  - bld_schema_marketplace_listing
  - bld_orchestration_marketplace_listing
  - bld_tools_marketplace_listing
  - output-validator-builder
---

# Arquitetura: onde o marketplace_listing se encaixa
## Posição no grafo de kinds
| Relação | Kind / Arquivo | Direção |
|----------|------|-----------|
| kind definido por | `.cex/kinds_meta.json` (entrada `marketplace_listing`: pillar P05, naming `p05_ml_{name}.md`, max_bytes 6144, depends_on canonical_product + output_validator) | contrato upstream |
| computado em runtime por | `_tools/capability_generators/marketplace_listing.py` (`@register("marketplace_listing")`, `build(inputs)`) | computação de referência upstream -- este builder a espelha 1:1 |
| dual-projetado por | `_tools/cex_dual_output.py` (`to_dual_output`) -> machine_md + human_html + media_slots | projeção downstream em runtime |
| despachado por | `_tools/cex_run_capability.py` (`capability_generators.get_generator("marketplace_listing")`) | orquestração em runtime |
| espelhado no dashboard por | `apps/dashboard_web/lib/molds.ts` (`MOLD_MARKETPLACE_LISTING`) -- o formulário de entrada + o mold em tela | sibling (frontend) |
| depends_on (kinds_meta) | canonical_product (P06, ainda não existe builder -- uma lacuna real), output_validator (P05, [[output-validator-builder]] existe) | upstream |
| NÃO É | partner_listing (um anúncio de diretório/vendas; conceito diferente) nem canonical_product (o superconjunto neutro por canal) | exclusão de fronteira |

## Dois vocabulários para a mesma ideia (leia antes de autorar)
O `boundary`/`description` de `.cex/kinds_meta.json` descrevem a camada de NÍVEL MAIS BAIXO
`_tools/cex_channel_adapter.py` (`MercadoLivreAdapter`, seu `upstream_source` declarado):
canonical_product -> um payload COM um bloco `_meta` + um relatório de prontidão
`PUBLISH-READY`/`NOT-READY` (`missing[]`/`warnings[]`, cada um `{field, severity, message}`).
Essa camada também filtra fotos para apenas `https://` e bloqueia de forma forçada quando
`available_quantity<=0` via uma verificação separada `buyability()`.

O capability generator EM PRODUÇÃO (`capability_generators/marketplace_listing.py` --
docstring: "capability slug = kind") lê os campos G1 do dashboard diretamente, NÃO tem
bloco `_meta`, NÃO filtra URLs de foto não-https, e NÃO bloqueia com estoque zero. Seu
veredito de prontidão é `score`/`passed`/`missing_required`/`notes` em vez de
`missing[]`/`warnings[]`/`PUBLISH-READY`. Mesma ideia de fundo (uma projeção por canal +
um gate), duas implementações diferentes, AINDA NÃO unificadas. Este builder autora no
formato do generator EM PRODUÇÃO porque é isso que o dashboard de um tenant de fato
despacha -- veja [[bld_knowledge_marketplace_listing]] para a lista completa de
divergências.

## Camadas
marketplace_listing é um ativo de OUTPUT do P05 (uma projeção declarativa autorada por
LLM/builder), distinto de:
- o GENERATOR DE RUNTIME (`capability_generators/marketplace_listing.py` -- Python
  determinístico, não um artefato de LLM; o contrato deste builder espelha sua saída,
  nunca a edita)
- a CAMADA DE NÍVEL MAIS BAIXO (`cex_channel_adapter.py` -- uma camada de nomenclatura de
  campos diferente, acima)
- o EMISSOR DUAL-OUTPUT (`cex_dual_output.py` -- projeta um StructuredOutput em
  machine_md + human_html; uma instância autorada por builder é upstream dessa projeção)

## Por que um kind, e não uma composição
Um anúncio por produto, por canal, precisa de uma unidade atômica, selecionável,
construível em swarm (um SKU x um canal = uma coordenada), da mesma forma que
bld_architecture_motion_scene justifica motion_scene: um pipeline_template + generator +
schema por anúncio fragmentaria o anúncio ML de um único produto em 3+ arquivos, sem um
único identificador de "este é o anúncio ML do SKU X".

## Artefatos Relacionados
| Artefato | Relação | Pontuação |
|----------|-------------|-------|
| [[bld_schema_marketplace_listing]] | sibling | 0.5 |
| [[bld_orchestration_marketplace_listing]] | sibling | 0.45 |
| [[bld_tools_marketplace_listing]] | sibling | 0.42 |
| [[output-validator-builder]] | related | 0.4 |
| spec_dual_output_contract | related | 0.38 |
