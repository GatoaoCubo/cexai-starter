---
id: bld_tools_marketplace_listing
kind: toolkit
pillar: P04
llm_function: CALL
8f: F5_call
version: 1.0.0
created: "2026-07-02"
updated: "2026-07-02"
author: n03_builder
title: "Ferramentas: construindo + validando um marketplace_listing"
domain: marketplace_listing
quality: null
tags: [marketplace_listing, builder, tools, P04]
tldr: "O inventário de ferramentas que uma construção de marketplace_listing usa: compile, doctor, score, index, além das referências de runtime às quais deve permanecer contratualmente idêntico (somente leitura)."
density_score: 0.88
related:
  - bld_prompt_marketplace_listing
  - bld_eval_marketplace_listing
  - bld_orchestration_marketplace_listing
  - bld_architecture_marketplace_listing
  - output-validator-builder
---

# Ferramentas: marketplace_listing
## Construir + governar
| Ferramenta | Uso |
|------|-----|
| `cex_compile.py` | compila a instância .md -> .yaml (obrigatório no F8) |
| `cex_doctor.py` | saúde do diretório do builder (este conjunto de ISOs passa 12/12) |
| `cex_score.py` | pontuação por pares (nunca autoavaliação) |
| `cex_index.py` | indexa frontmatter + wikilinks |

## Verificações de domínio
| Verificação | Como |
|-------|-----|
| Formato das seções | garanta que as 6 seções do corpo batem exatamente com títulos/ordem/layout de [[bld_schema_marketplace_listing]] |
| Chaves do ml_listing | garanta que as 7 chaves obrigatórias estão presentes (title/category_id/price/currency_id/available_quantity/condition/listing_type_id) |
| Matemática do gate | recompute o score a partir da tabela de deduções; garanta que bate com o `score` do frontmatter |
| Vocabulário de condição | garanta que condicao foi mapeada pela tabela de 3 vias, nunca um 4º valor |
| BRAND/SELLER_SKU | garanta que ambos estão presentes quando marca/sku foram informados, e ausentes (não fabricados) quando não foram |
| Tamanho do corpo | garanta que o corpo é <= 6144 bytes |

## Referências de runtime (SOMENTE LEITURA -- este builder espelha o contrato delas, nunca as edita)
| Caminho | Papel |
|------|------|
| `_tools/capability_generators/marketplace_listing.py` | o generator EM PRODUÇÃO que o contrato deste builder espelha 1:1 |
| `_tools/capability_generators/_base.py` | a interface StructuredOutput (`register`, `fields_section`/`table_section`/`list_section`, `structured_output`) |
| `_tools/cex_run_capability.py` | o despachante de runtime (`get_generator("marketplace_listing")`) |
| `_tools/cex_dual_output.py` | a projeção dual-output (`to_dual_output`) -> machine_md + human_html |
| `apps/dashboard_web/lib/molds.ts` | `MOLD_MARKETPLACE_LISTING` -- o formulário de entrada do frontend + o espelho do mold em tela |
| `_tools/tests/test_marketplace_listing.py` | a prova de testes do próprio generator (11 testes) -- outro stream é dono deste arquivo |
| `_tools/cex_channel_adapter.py` | a camada de nível mais baixo, com formato diferente (`upstream_source` de `.cex/kinds_meta.json`) |

## Disciplina
Ferramentas VALIDAM; elas nunca inventam o valor de um campo. O preço, as fotos e os
atributos de um marketplace_listing são autorados a partir da linha G1 real, depois
verificados contra o gate -- nunca adivinhados só para o gate passar.

## Artefatos Relacionados
| Artefato | Relação | Pontuação |
|----------|-------------|-------|
| [[bld_eval_marketplace_listing]] | upstream | 0.45 |
| [[bld_prompt_marketplace_listing]] | related | 0.42 |
| [[bld_orchestration_marketplace_listing]] | sibling | 0.4 |
| [[bld_architecture_marketplace_listing]] | related | 0.4 |
| [[output-validator-builder]] | related | 0.36 |
