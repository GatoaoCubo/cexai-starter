---
kind: architecture
id: bld_architecture_prompt_package
pillar: P08
llm_function: CONSTRAIN
purpose: Component map of prompt_package -- inventory, dependencies, and architectural position in Mode B decompose
quality: null
title: "Architecture Prompt Package"
version: "1.0.0"
author: builder
tags: [prompt_package, builder, decompose, mode-b, examples]
tldr: "How prompt_package sits between Stage 1 (THINK) and Stage 2 (GENERATE) in decomposed 8F, grounded in cex_decompose.py's real 3-stage pipeline."
domain: "prompt package construction"
created: "2026-07-03"
updated: "2026-07-03"
8f: "F1_constrain"
keywords: [component map of prompt_package, mode b decompose, stage 1, stage 2, cex_decompose.py, cex_8f_runner.py, prompt_package, builder, examples]
density_score: 0.90
related:
  - prompt-package-builder
  - bld_memory_prompt_package
  - bld_orchestration_prompt_package
---
# Architecture: prompt_package in the CEX

## Component Inventory

| Name | Role | Owner | Status |
|------|------|-------|--------|
| frontmatter block | Metadata header (package_type, target_kind, target_pillar, target_path, stage, mode, etc.) | prompt-package-builder / `_write_prompt_package` | active |
| `## IDENTITY` section | F2 BECOME persona the Stage-2 model adopts | Stage 1 | active |
| `## CONTEXT` section | F3 INJECT pre-resolved knowledge -- replaces Stage 2's need for live tools | Stage 1 | active |
| `## PLAN` section | F4 REASON section list, approach, density target | Stage 1 | active |
| `## TEMPLATE` section | The target kind's own `bld_output` ISO, frontmatter-stripped | Stage 1 (via `load_iso`) | active |
| DGUARD | Flag-gated factual-synthesis guard on the Stage-2 path | `cex_decompose.py` lines 463-594 | active (opt-in) |
| W2 wikilink gate | Stage-3 gate on the DOWNSTREAM artifact before F8 | `cex_decompose.py` lines 223-289 | active (default `reject`) |
| A3 escalation | Flag-gated re-produce-at-next-tier while below `min_score` | `cex_decompose.py` lines 336-460 | active (opt-in) |

## Dependency Graph

```
system_prompt   --embedded_in-->  IDENTITY section
prompt_template --pattern_for-->  TEMPLATE section shape (fill-slot convention)
prompt_compiler --resolves-->     target_kind BEFORE a package is compiled
prompt_package  --consumed_by-->  Stage 2 (cheap F6 model)
prompt_package  --signals-->      Stage 3 gate/validate/commit/signal
```
| From | To | Type | Data |
|------|----|------|------|
| `prompt_compiler` (P03) | `prompt_package` | dependency | resolved `{kind, pillar, nucleus, verb}` BEFORE Stage 1 writes the package |
| `system_prompt` (P03) | `prompt_package` | data_flow | builder persona text embedded verbatim in `## IDENTITY` |
| `prompt_template` (P03) | `prompt_package` | pattern | the `{{variable}}` fill-slot convention the `## TEMPLATE` section reuses |
| Stage 1 (`cex_8f_runner.py --stage 1`) | `prompt_package` | produces | the frozen handoff file, `.cex/runtime/packages/pp_*.md` |
| `prompt_package` | Stage 2 (`cex_8f_runner.py --stage 2`) | consumed_by | F6 PRODUCE only, no F1-F4 re-run |
| `prompt_package` | Stage 3 (doctor/compile/signal) | signals | completion via `signal_writer.write_signal` |
| `prompt_package` | W2 wikilink gate | gated_by | the DOWNSTREAM artifact (not the package) is checked before F8 |

## Boundary Table

| prompt_package IS | prompt_package IS NOT |
|--------------------|------------------------|
| A frozen, one-shot F1-F4 handoff for ONE build | A reusable `{{variable}}` mold invoked repeatedly (`prompt_template`) |
| Consumed by a DIFFERENT model instance than the one that wrote it | A fixed agent identity/persona (`system_prompt`) |
| Self-contained -- Stage 2 needs no live tools after reading it | The mechanism that DECIDES which kind/pillar/nucleus to build (`prompt_compiler`) |
| Produced by Opus/Sonnet (Stage 1), consumed by Haiku/Flash/Ollama (Stage 2) | A durable, versioned template edited over time |
| `core: true` in `.cex/kinds_meta.json` -- taxonomy-foundational | A place to embed live MCP calls or unresolved retrieval queries |
| Gated at Stage 3 via the artifact it produced (not itself) | The artifact Stage 2 produces (that artifact has its OWN kind/pillar) |

## Layer Map

| Layer | Components | Purpose |
|-------|------------|---------|
| Resolution | `prompt_compiler` | Decide `target_kind`/`target_pillar`/`target_nucleus` BEFORE compiling a package |
| Identity | `system_prompt`, `## IDENTITY` | Supply the persona Stage 2 adopts |
| Structure | `prompt_template` pattern, `## TEMPLATE` | The fill-slot shape Stage 2 completes |
| Handoff | frontmatter, `## CONTEXT`, `## PLAN` | The actual `prompt_package` payload |
| Consumption | Stage 2 (F6 PRODUCE) | Cheap model fills the TEMPLATE, writes `target_path` |
| Governance | W2 gate, DGUARD, A3 escalation, Stage 3 tools | F7-F8 validation + commit + signal, never self-scored |

## Related Artifacts

| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[prompt-package-builder]] | upstream | 0.53 |
| [[bld_knowledge_prompt_package]] | upstream | 0.50 |
| [[bld_memory_prompt_package]] | downstream | 0.49 |
| [[bld_orchestration_prompt_package]] | upstream | 0.42 |
