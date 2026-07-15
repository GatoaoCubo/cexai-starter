---
id: p01_kc_clean_arch_ddd_in_cex
kind: knowledge_card
kc_type: teaching_reference
pillar: P01
nucleus: N04
version: 1.1.0
created: "2026-06-03"
updated: "2026-06-03"
author: n04_knowledge
title: "Clean Architecture + DDD Mapeado em CEX: O Mapa Vivo"
domain: architecture
subdomain: ddd_clean_arch
quality: null
tags: [ddd, clean-architecture, bounded-context, aggregate, tactical, strategic, teaching]
tldr: "Cada conceito de Clean Arch (Martin) e DDD (Vernon/Evans) ja existe como kind+builder+pillar em CEX. Os 3 GAPS — anti_corruption_layer, use_case, repository — sao o climax ao vivo da aula_pratica_02."
when_to_use: "Aula Pratica 02 (DDD+Clean Arch ao vivo). Consulta: 'onde esta X no CEX?' para devs e founders."
keywords: [ddd, clean-architecture, aggregate-root, bounded-context, domain-event, value-object, gaps, repository, use-case, anti-corruption]
long_tails:
  - "como DDD esta implementado no CEX kinds e pillars"
  - "quais conceitos de Clean Architecture existem como kind no CEX"
axioms:
  - "ALWAYS: cada conceito DDD/Clean Arch mapeia para um CEX kind — se nao existe kind, e um GAP identificado"
  - "NEVER: confundir db_connector (ferramenta) com repository (contrato de persistencia do aggregate)"
  - "IF bounded context ausente THEN o nucleo N01-N07 ja e o bounded context — nao duplique"
linked_artifacts:
  primary: kc_8f_pipeline
  related: [bounded_context, context_map, aggregate_root, domain_event, value_object]
density_score: 0.91
data_source: "Evans 2003 DDD / Vernon 2013 Implementing DDD / Martin 2017 Clean Architecture / .cex/kinds_meta.json"
related:
  - bld_architecture_kind
  - p06_td_cex_artifact_type_n03
  - p01_kc_kind_gap_analysis
  - bld_knowledge_aggregate_root
  - bld_tools_context_map
  - kind-builder
  - bld_knowledge_card_context_map
  - bld_manifest_aggregate_root
  - bld_collaboration_kind
  - context-map-builder
---

# Clean Architecture + DDD Mapeado em CEX

## Quick Reference

```yaml
topic: DDD + Clean Arch -> CEX kind/pillar/nucleus mapping
scope: Evans DDD 2003, Vernon Implementing DDD 2013, Martin Clean Architecture 2017
owner: N04 (producao) / N03 (gaps a criar)
criticality: high
builders_DDD: aggregate-root, bounded-context, context-map, domain-event, value-object, saga, process-manager (todos 12 ISOs)
gaps: 3 — anti_corruption_layer, use_case, repository
```

## DDD TATICO -> CEX

| Conceito | Autor | CEX kind | First-class? | Pillar |
|----------|-------|----------|-------------|--------|
| Aggregate Root | Evans, Vernon | `aggregate_root` | SIM — 12 ISOs | P06 |
| Entity | Evans | `aggregate_root` / `type_def` | PARCIAL | P06 |
| Value Object | Evans, Vernon | `value_object` | SIM — 12 ISOs | P06 |
| Domain Event | Vernon, Hohpe | `domain_event` | SIM — 12 ISOs | P12 |
| Saga | Garcia-Molina | `saga` | SIM — 12 ISOs | P12 |
| Process Manager | Hohpe, Evans | `process_manager` | SIM — 12 ISOs | P12 |
| **Repository** | Evans, Vernon | **GAP** | NAO | — |
| Factory | GoF + Evans | `type_def` (implicito) | PARCIAL | P06 |
| Domain Service | Evans | `skill` (aprox.) | PARCIAL | P04 |
| Module | Evans | nucleo N01-N07 | SIM (implicito) | P08 |

## DDD ESTRATEGICO -> CEX

| Conceito | Autor | CEX kind | First-class? | Pillar |
|----------|-------|----------|-------------|--------|
| Bounded Context | Evans | `bounded_context` | SIM — 12 ISOs | P08 |
| Context Map | Evans | `context_map` | SIM — 12 ISOs | P08 |
| Ubiquitous Language | Evans | regra + vocab KC | SIM (regra estrutural) | P01 |
| **Anti-Corruption Layer** | Evans | **GAP** | NAO | — |
| Shared Kernel | Evans | `type_def` (implicito) | PARCIAL | P06 |
| Domain Event (pub-sub) | Vernon, Hohpe | `domain_event` + `event_stream` | SIM | P12+P01 |

- **Bounded Context:** N01-N07 SAO bounded contexts. Cada nucleo = linguagem propria + regras internas.
- **Ubiquitous Language:** `.claude/rules/ubiquitous-language.md` + `kc_{domain}_vocabulary.md`. F2b SPEAK enforça.

## CLEAN ARCHITECTURE -> CEX: As 4 Camadas

Martin 2017 — Dependency Rule: dependencias apontam para dentro. P02/P06 nao importam P09.

| Camada | CEX Pillar(s) | CEX kind(s) | Dependency Rule |
|--------|---------------|-------------|-----------------|
| **Entities** (regras puras) | P02 + P06 | `axiom`, `aggregate_root`, `value_object` | P02/P06 nao acoplam P09. Compilador enforça. |
| **Use Cases / Interactors** | **GAP explicit** | 8F pipeline (F1-F8 executa o interactor) | Sem kind `use_case`. Acao modelada por verbo+8F. |
| **Interface Adapters** | P04 + P05 + P06 | `api_client`, `interface`, `formatter`, `parser` | Adapters conhecem Use Cases, nao Entities. |
| **Frameworks & Drivers** | P09 | `env_config`, `db_connector`, `session_backend` | Detalhes externos. `.cex/config/` + MCP. |

**SOLID:** S=1 kind/1 responsabilidade. D=nuclei dependem P02/P06, nao P09.

## OS 3 GAPS: Climax da Aula

| Gap | Livro | Pillar sugerido | Por que importa |
|-----|-------|----------------|-----------------|
| `anti_corruption_layer` | Evans DDD 2003 | P06 ou P12 | Traduz entre BCs. Sem ACL, a traducao fica em codigo ad-hoc (N05). |
| `use_case` | Martin Clean Arch 2017 | P12 ou P03 | Interactor explicito por acao. Hoje: 8F substitui funcionalmente mas sem artifact declarativo. |
| `repository` | Evans DDD 2003, Vernon | P06 ou P04 | Contrato de persistencia do aggregate. `db_connector` e driver (P09), nao contrato DDD. |

- **anti_corruption_layer:** `context_map` descreve; ACL executa. AUSENTE kinds_meta.json.
- **use_case:** `workflow` (P12) aproximacao; semantica diferente. AUSENTE kinds_meta.json.
- **repository:** `db_connector` e driver P09; sem contrato de persistencia DDD. AUSENTE kinds_meta.json.

O fundador cria os 3 kinds no grid ao vivo. CEX assimila em 3-5 minutos.

## Sumario

| Conceito | Status | Kind |
|----------|--------|------|
| Aggregate Root, Value Object, Domain Event, Saga, Process Manager | PRESENTE | P06 + P12 |
| Bounded Context (= nuclei N01-N07), Context Map, Ubiquitous Language | PRESENTE | P08 + P01 |
| Clean Arch Entities, Adapters, Frameworks | PRESENTE | P02+P06 / P04+P05 / P09 |
| **Anti-Corruption Layer** | **GAP** | AUSENTE — Evans 2003 |
| **Use Case** | **GAP** | AUSENTE — Martin 2017 |
| **Repository** | **GAP** | AUSENTE — Evans 2003 |

**CEX e feito de DDD + Clean Arch. Os 3 gaps sao a ultima mao de tinta.**

---


## Related Artifacts

| Artifact | Relationship | Score |
|----------|-------------|-------|
| kc_8f_pipeline | foundational | 0.89 |
| bounded_context | core | 0.85 |
| aggregate_root | core | 0.84 |
| context_map | strategic | 0.82 |
| domain_event | core | 0.80 |
| value_object | core | 0.80 |
| ubiquitous-language | governance | 0.78 |
| 8f-reasoning | foundational | 0.72 |
