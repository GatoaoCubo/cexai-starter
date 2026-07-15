---
kind: collaboration
id: bld_orchestration_prompt_package
pillar: P03
llm_function: COLLABORATE
purpose: How prompt-package-builder works in the Mode B decompose crew with Stage 1/2/3
pattern: each stage must know its ROLE in the pipeline, what it RECEIVES and PRODUCES
quality: null
title: "Orchestration Prompt Package"
version: "1.0.0"
author: builder
tags: [prompt_package, builder, decompose, mode-b, examples]
tldr: "The Mode B decompose crew topology -- Stage 1 (THINK) produces prompt_package, Stage 2 (GENERATE) consumes it, Stage 3 (tools) gates and ships."
domain: "prompt package construction"
created: "2026-07-03"
updated: "2026-07-03"
8f: "F8_collaborate"
keywords: [prompt package construction, orchestration prompt package, mode b, stage 1, stage 2, stage 3, cex_decompose.py, prompt_package, builder, examples]
density_score: 0.90
related:
  - bld_orchestration_prompt_template
  - bld_orchestration_system_prompt
  - prompt-package-builder
  - bld_architecture_prompt_package
  - bld_memory_prompt_package
---
# Collaboration: prompt-package-builder

## My Role in Crews

I am the HANDOFF COMPILER. I answer ONE question: "what does a model with no live tools and no
memory of this conversation need in hand to execute F6 PRODUCE correctly, right now?"
I produce a frozen, self-contained package -- not a reusable mold, not an agent identity, not an
intent-resolution decision.

## Crew Compositions

### Crew: "Mode B Decompose Pipeline" (the real, load-bearing crew -- `cex_decompose.py`)
```
  1. stage1_think (Opus/Sonnet, F1-F4)  -> "resolves target_kind, harvests IDENTITY/CONTEXT/PLAN"
  2. prompt-package-builder             -> "compiles the 4-section handoff, THIS builder's output"
  3. stage2_generate (cheap model, F6)  -> "reads the package, fills TEMPLATE, writes target_path"
  4. stage3_tools (deterministic)       -> "W2 wikilink gate -> doctor -> compile -> commit -> signal"
```
### Crew: "Agent Prompt Stack" (P03 sibling composition, for context)
```
  1. system-prompt-builder    -> "fixed identity and persona for the agent"
  2. prompt-template-builder  -> "reusable mold with {{variables}} for dynamic invocations"
  3. prompt-package-builder   -> "ONE-SHOT frozen handoff when the invocation must decompose"
```
### Crew: "Factual-Synthesis Guard" (DGUARD, opt-in)
```
  1. prompt-compiler          -> "resolves target_kind; flags factual-synthesis kinds"
  2. prompt-package-builder   -> "compiles the package; DGUARD warns/upgrades/refuses at this seam"
  3. cex_mentor_swarm ladder  -> "escalation-ladder tier lookup for the 'upgrade' policy"
```

## Handoff Protocol

### I Receive
- F1 constraints, F2 identity, F3 context, F4 plan -- ALREADY RESOLVED by the calling model
- `target_kind`/`target_pillar`/`target_nucleus`/`target_path` -- resolved by `prompt_compiler`
  BEFORE I am invoked (I do not resolve intent myself)

### I Produce
- `prompt_package` artifact (YAML frontmatter + 4-section body, max 16384 bytes per this kind's
  registered cap)
- written to: `.cex/runtime/packages/pp_{target_kind}_{session_id}.md` (the REAL convention;
  see `bld_config_prompt_package.md` for the registry-vs-practice naming gap)

### I Signal
- No self-signal -- Stage 3 tools (`cex_decompose.py::stage_3`) run the W2 gate, doctor, compile,
  and `signal_writer.write_signal(nucleus, "complete", 9.0)` AFTER Stage 2 consumes my output
- if a HARD gate in `bld_eval_prompt_package.md` fails: the correction protocol in
  `bld_feedback_prompt_package.md` returns control to Stage 1, not to me directly

## Builders I Depend On

- `prompt-compiler`-class intent resolution: supplies `target_kind`/`target_pillar` BEFORE I compile
- `system-prompt-builder`: supplies the persona text I embed verbatim in `## IDENTITY`
- `prompt-template-builder`: supplies the `{{variable}}` fill-slot CONVENTION my `## TEMPLATE`
  section reuses (not a runtime dependency -- a pattern dependency)
- The TARGET kind's own builder (whichever `{kind}-builder` owns `target_kind`): supplies the
  `bld_output` ISO I embed as `## TEMPLATE`

## Builders That Depend On Me

| Builder / Tool | Why |
|---------|-----|
| `_tools/cex_decompose.py` (Stage 1 caller) | Invokes the harvesting logic this builder's `p03_ins_prompt_package.md` instruction ISO documents |
| `_tools/cex_8f_runner.py` (`--stage 2`) | Consumes my output as its sole input; never re-runs F1-F4 |
| Any `{kind}-builder` dispatched via `decompose` mode | Their `bld_output` ISO becomes MY `## TEMPLATE` section when their kind is the `target_kind` |
| N07 orchestrator | Reads Stage-3 signals to decide whether to re-dispatch or advance the wave |

## Related Artifacts

| Artifact | Relationship | Score |
|----------|-------------|-------|
| bld_orchestration_prompt_template | sibling | 0.41 |
| bld_orchestration_system_prompt | sibling | 0.41 |
| [[prompt-package-builder]] | related | 0.39 |
| [[bld_architecture_prompt_package]] | sibling | 0.39 |
| [[bld_memory_prompt_package]] | sibling | 0.36 |
