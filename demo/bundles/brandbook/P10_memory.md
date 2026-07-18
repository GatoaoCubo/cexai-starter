---
id: bld_memory_brandbook
kind: memory_scope
pillar: P10
builder: brandbook-builder
version: 1.0.0
quality: null
title: Memory Scope -- brandbook
author: n06_commercial
tags: [memory_scope, brandbook, P10]
llm_function: INJECT
created: 2026-06-22
updated: 2026-06-22
related:
  - kc_brandbook
  - bld_prompt_brandbook
  - p08_adr_multitenant_hybrid
  - spec
  - brand_context_n03
  - brand_context_n05
  - constitution
  - brand_context_n04
  - p12_dag_mission_bootstrap_2026q1_n07
  - brand_context_n06
---

## Escopo de Memória

| Escopo | O Quê | Retenção | Responsável |
|--------|-------|----------|-------------|
| tenant-persistent | brand_config.yaml (13 campos obrigatórios) | permanente | ferramentas de marca do N06 |
| tenant-persistent | Artefatos brandbook produzidos p05_bb_*.md | permanente | brandbook-builder |
| per-session | Cores de paleta extraídas do logotipo | sessão | Cell A |
| per-session | Texto extraído de materiais PDF/URL | sessão | Cell A |
| cross-nucleus | brand_propagate.py propaga para os 7 núcleos | sob demanda | brand_propagate.py |

## Caminho de Persistência
Os manuais de marca persistem com escopo por tenant, conforme a face
machine do dual-output:
  `.cex/runtime/capabilities/{tenant_id}/brandbook_{brand_slug}/`

## Artefatos de Memória Relacionados
- `N06_commercial/P10_memory/brand_decisions_memory.md` -- registro de decisões de marca
- `N06_commercial/P10_memory/pricing_optimization_memory.md` -- experimentos de precificação
- `.cex/brand/brand_config.yaml` -- o registro oficial de identidade da marca

### Nota de Portabilidade (bundle exportado)
Os escopos acima descrevem a arquitetura de memória do CEXAI **interno**
(onde o brandbook-builder roda dentro do repositório completo, com
`.cex/runtime/` e os 7 núcleos vivos). Rodando como agente standalone em
qualquer IA, a única memória disponível é a nativa da plataforma escolhida
(histórico de conversa do Project/Gem/GPT) -- não há `.cex/runtime/` nem
`brand_propagate.py` nesse contexto. Cole o manual de marca produzido de
volta em uma conversa futura se quiser retomar o contexto ou pedir revisões.

## Related Artifacts

| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[kc_brandbook]] | upstream | 0.22 |
| [[bld_prompt_brandbook]] | upstream | 0.21 |
| [[p08_adr_multitenant_hybrid]] | upstream | 0.19 |
| [[spec]] | related | 0.17 |
| [[brand_context_n03]] | upstream | 0.17 |
| [[brand_context_n05]] | upstream | 0.17 |
| [[constitution]] | related | 0.17 |
| [[brand_context_n04]] | upstream | 0.17 |
| [[p12_dag_mission_bootstrap_2026q1_n07]] | downstream | 0.17 |
| [[brand_context_n06]] | upstream | 0.17 |
