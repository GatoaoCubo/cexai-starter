---
id: p01_kc_prompt_package
kind: knowledge_card
8f: F3_inject
type: kind
pillar: P03
title: "prompt_package: The Stage 1 -> Stage 2 Decompose Handoff Artifact"
version: 1.0.0
created: 2026-07-03
updated: 2026-07-03
author: n07
domain: prompt_package
quality: null
open_vars: []
tags: [prompt_package, p03, INJECT, kind-kc, decompose, mode_b, f6_generation]
tldr: "A frozen, self-contained F1-F4 handoff written by a reasoning model (Stage 1) so a cheap model (Stage 2) can execute F6 PRODUCE alone -- the concrete artifact behind Mode B decomposed 8F"
when_to_use: "Building, reviewing, or reasoning about prompt_package artifacts produced by cex_8f_runner.py Stage 1 or authored manually via prompt-package-builder"
keywords: [prompt-package, decompose, mode-b, f6-generation, stage1, stage2, cheap-model, handoff, cex_decompose.py]
feeds_kinds: [prompt_package]
density_score: null
related:
  - p01_kc_prompt_template
  - p01_kc_prompt_compiler
  - kc_system_prompt
  - p01_kc_reverse_prompt
  - prompt-package-builder
---

# Prompt Package

## Spec
```yaml
kind: prompt_package
pillar: P03
llm_function: INJECT
primary_8f: F3_inject
max_bytes: 16384
naming: p03_pp_{{task_id}}.md   # registered; real files use pp_{target_kind}_{session_id}.md
core: true
depends_on: [prompt_template, system_prompt, prompt_compiler]
```

## What It Is

A `prompt_package` is the FROZEN, self-contained handoff a reasoning-capable model (Opus/Sonnet,
"Stage 1 / THINK") writes after running F1 CONSTRAIN, F2 BECOME, F3 INJECT, and F4 REASON for a
specific target build. A cheap generation-only model (Haiku/Flash/Ollama, "Stage 2 / GENERATE")
then reads that ONE file and executes F6 PRODUCE alone -- with no live tools, no MCP access, and
no memory of Stage 1's reasoning. Tools (Stage 3) then run F7 GOVERN and F8 COLLABORATE. This is
the concrete artifact behind `.claude/rules/8f-reasoning.md`'s "Mode B (decomposed)" 8F execution
mode, and it is the ONLY one of the 9 recently-triaged builder-less kinds flagged `core: true` in
`.cex/kinds_meta.json` -- taxonomy-foundational company alongside `knowledge_card`, `agent`,
`workflow`, `system_prompt`, `prompt_template`, and `prompt_compiler`.

It is NOT a reusable mold (that is `prompt_template`, whose `{{variable}}` fill-slot convention
its own `## TEMPLATE` section reuses) and NOT the mechanism that DECIDES what to build (that is
`prompt_compiler`, which must resolve `target_kind` BEFORE a package is compiled). It embeds a
`system_prompt`-shaped persona in its `## IDENTITY` section but is not itself an identity
definition.

Spec provenance: `N00_genesis/P03_prompt/tpl_prompt_package.md` (authoring template) +
`N00_genesis/P06_schema/p06_if_prompt_package.md` (bilateral Stage1/Stage2 interface contract,
154 lines). Real generator: `_tools/cex_8f_runner.py::_write_prompt_package` (lines 2001-2101)
writes it; `_run_mode_b_generate` (line ~2105) reads it back. Real orchestrator:
`_tools/cex_decompose.py`'s 3-stage subprocess pipeline (module docstring lines 8-9).

## The 2 Real Production Paths (read before building)

Unlike `reverse_prompt`/`approval_request` (purely runtime-emitted, historically with no 12-ISO
builder), `prompt_package` now has BOTH paths:

| Path | Producer | When | Naming used |
|------|----------|------|-------------|
| **Auto-generated** (primary, majority of real instances) | `cex_8f_runner.py::_write_prompt_package`, invoked by `cex_decompose.py --nucleus n0X --task "..."` | Every real `Task tool: dispatch decompose` run | `pp_{target_kind}_{session_id}.md` (121 live gitignored instances found under `.cex/runtime/packages/` this session) |
| **Builder-authored** (manual/example) | `prompt-package-builder` (this scaffold) | Hand-authoring examples/tests, or an LLM composing one directly per the 12-ISO contract | Same convention; the tracked `N00_genesis/P03_prompt/examples/stress_decompose_packages/` corpus (9 files, T01-T09) follows it |

The builder scaffold closes a dispatch dead end (intent resolution could previously route a
"build a prompt_package" request into a kind with no `archetypes/builders/` directory) -- it does
NOT replace the auto-generation path, which remains the dominant real mechanism.

## Boundary (read before building)
| Kind | Pillar | Role | Cardinality | Lifetime |
|------|--------|------|-------------|----------|
| `prompt_compiler` | P03 | RESOLVES which kind/pillar/nucleus/verb to build, BEFORE a package exists | One resolution per user intent | Durable resolution logic |
| `prompt_template` | P03 | The reusable `{{variable}}` MOLD a target kind's builder fills; pattern source for `## TEMPLATE` | One per topic | Durable authored artifact |
| `prompt_package` | P03 | The FROZEN, one-shot HANDOFF carrying F1-F4 state from Stage 1 to Stage 2 | Many (one per decomposed build) | Ephemeral runtime artifact (or example) |
| `system_prompt` | P03 | The fixed agent IDENTITY embedded verbatim in `## IDENTITY` | One per builder/agent | Durable authored artifact |

In one sentence: `prompt_compiler` decides *what* to build, `prompt_template` is *the mold a
builder fills*, `prompt_package` *is one build's entire F1-F4 reasoning, frozen for a cheaper
model to finish*, and `system_prompt` is *the identity riding along inside it*.

## Key Fields
| Field | Type | Required | Description |
|-------|------|----------|--------------|
| package_type | literal | yes | Always `f6_prompt_package` (H02 gate) |
| target_kind | string | yes | The kind Stage 2 must produce; MUST resolve in `.cex/kinds_meta.json` |
| target_pillar / target_nucleus / target_path | string | yes | Where + who produces the target artifact |
| builder_isos_loaded / context_sources | integer | yes | Counts asserting how much Stage 1 actually injected |
| density_target | float 0.80-1.00 | yes | Minimum density Stage 2 must achieve in the OUTPUT artifact |
| max_bytes | integer | yes | <= 32768 (interface ceiling) AND <= the target kind's own registered cap |
| stage / mode | literal | yes | Always `1` / always `B` for this kind |

## Cross-Framework Map
| Framework/Concept | Closest Concept | Notes |
|-------------------|-----------------|-------|
| LangGraph | Serialized graph checkpoint handed to a cheaper node | Both freeze upstream reasoning state for a downstream executor |
| DSPy | Compiled `Signature` + few-shot bootstrap | Both pre-resolve what a cheaper call needs, removing live reasoning from the hot path |
| Model routing (e.g. RouteLLM) | The "easy" request routed to a small model | `prompt_package` is the CONTEXT that makes the small-model request safe to route, not the router itself |
| Agentic "plan-then-execute" pattern | The frozen plan handed to an executor sub-agent | Stage 1 = planner, Stage 2 = executor, package = the plan artifact |

## Patterns
| Pattern | When to Use | Example |
|---------|-------------|---------|
| Schema/template fill-in | `target_kind` is structural (`enum_def`, `type_def`, `env_config`, `input_schema`) | Decompose's proven strong suit -- cheap F6 fills a shape reliably |
| Repair handoff (`mode: repair`) | Fixing a broken artifact via the cheap path | Real precedent: T07, `target_kind: bugloop`, `builder_isos_loaded: 0` |
| Evolve handoff (`mode: evolve`) | Improving a low-quality artifact via the cheap path | Real precedent: T08, `target_kind: optimizer` |
| Escalate-on-floor (A3, opt-in) | Gate-clean but below-quality-floor Stage-2 output | `CEX_DECOMPOSE_ESCALATE=1` climbs the same ladder `cex_mentor_swarm` uses |

## Anti-Patterns
| Anti-Pattern | Why It Fails | Fix |
|-------------|-------------|-----|
| Decomposing a factual-synthesis kind unguarded | MISSION_BENCH measured `knowledge_card` at q=1.2 both rounds via Mode B -- 8.4x worse than frontier | Set `--guard-on-factual upgrade` (self-heals) or route to `solo`/native Sonnet |
| Embedding a live MCP/retrieval call in `## CONTEXT` | Stage 2 has no live tools; the call sits unexecuted | Resolve first, embed the RESULT text |
| Assuming `p03_pp_{{task_id}}.md` is what you will find on disk | Zero real files (tracked examples or the 121 gitignored live instances) use that prefix | Follow the observed convention: `pp_{target_kind}_{session_id}.md` |
| Skipping the Stage-3 W2 wikilink gate | Bench2 measured 3/3 rail-governed cheap producers fabricating `links` | Keep the default `reject` policy; only relax with a documented reason |
| Modeling it as a `prompt_template` | A package is one-shot and frozen; a template is durable and reusable | Author `prompt_template` once; compile a fresh `prompt_package` per decomposed build |

## Integration Graph
```
[prompt_compiler resolves target_kind/pillar/nucleus]
                |
   [Stage 1: Opus/Sonnet runs F1 CONSTRAIN -> F2 BECOME -> F3 INJECT -> F4 REASON]
                |
        cex_8f_runner.py::_write_prompt_package
                |
                v
     [prompt_package .md @ .cex/runtime/packages/pp_{target_kind}_{session_id}.md]
                |
   [Stage 2: cheap model runs F6 PRODUCE only, from the package alone]
                |
                v
        [target artifact written to target_path]
                |
   [Stage 3: W2 wikilink gate -> cex_doctor -> cex_compile -> commit -> signal]
```

## Decision Tree
- IF you are deciding WHICH kind/pillar/nucleus to build (not yet decided) -> that is
  `prompt_compiler` territory, NOT a prompt_package.
- IF you are authoring a REUSABLE `{{variable}}` mold for repeated future invocation -> that is a
  `prompt_template`, NOT a prompt_package.
- IF you are defining a fixed agent identity with no F1-F4 state to freeze -> that is a
  `system_prompt`, NOT a prompt_package.
- IF a reasoning model already ran F1-F4 for ONE specific build and a cheaper model must finish
  it -> this IS a `prompt_package` (auto-generated by `cex_8f_runner.py`, or hand-authored via
  `prompt-package-builder`).
- DEFAULT: prefer the auto-generated path (`cex_decompose.py`) for real builds; use the builder
  scaffold for manual/example authoring or when intent resolution needs a real dispatch target.

## Quality Criteria
- GOOD: `package_type` literal correct; `target_kind` resolves in `.cex/kinds_meta.json`; all 4
  body sections present; `quality: null`.
- GREAT: `## CONTEXT` carries zero unresolved live-tool calls; `## TEMPLATE` embeds the target
  kind's own `bld_output` ISO verbatim; DGUARD acknowledged (or explicitly N/A) for factual kinds;
  the produced downstream artifact passes the Stage-3 W2 wikilink gate.
- FAIL: `target_kind` unregistered; missing `## TEMPLATE`; a live tool call left unresolved in
  `## CONTEXT`; a factual-synthesis kind decomposed with no DGUARD acknowledgement.

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[p01_kc_prompt_template]] | upstream (the mold `## TEMPLATE` reuses) | 0.55 |
| p01_kc_prompt_compiler | upstream (resolves target_kind before compilation) | 0.52 |
| [[kc_system_prompt]] | sibling (identity embedded inside, not this kind itself) | 0.35 |
| p01_kc_reverse_prompt | sibling (P03 runtime-emitted artifact -- contrast: reverse_prompt has no builder path, prompt_package now has both) | 0.33 |
| [[prompt-package-builder]] | downstream (the scaffolded 12-ISO authoring path) | 0.45 |
