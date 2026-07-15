---
id: bld_prompt_design_system
kind: instruction
pillar: P06
llm_function: REASON
8f: F4_reason
version: 1.0.0
created: "2026-06-15"
updated: "2026-06-15"
author: n03_builder
title: "Process: build a design_system"
domain: design_system
quality: null
tags: [design_system, builder, prompt, process, P06]
tldr: "Research > compose > validate process for producing one original, governed design_system bound by the contract and declaring its CEXAI leverage."
density_score: 0.9
related:
  - bld_schema_design_system
  - bld_output_design_system
  - bld_eval_design_system
  - p06_vs_design_system
  - p03_ps_design_system_library_scale
---

# Process: build a design_system
## Inputs
A target name/brand archetype + an aesthetic coordinate (temperature, density, form, mode, type-voice) + the contract p06_vs_design_system.
## Step 1 -- RESEARCH (F3 INJECT)
- Load [[bld_schema_design_system]] (source of truth) + [[kc_design_system]].
- Fix the aesthetic coordinate; confirm it is not a sibling of an existing system.
- Decide the single signal hue + the dark/light mode + the type voice.
## Step 2 -- COMPOSE (F6 PRODUCE)
- color: pick canvas/panel/ink/ink_soft/edge + ONE signal + signal_ink + affirm/alert. Original values.
- type: choose display/text/mono faces, a modular ratio, the step ladder, weights, leading.
- space: pick a base unit and the s0..s7 ladder.
- motion: set dur (instant/quick/calm), ease curves, and the enter/exit/shift recipes.
- form: set radius, edge width, and the flat/raised/float shadow ladder.
- components: compose surface/control/field/marker from slots only.
- leverage: declare feeds_kinds, inject_hook, brand_config_relation, composes_with, binds_8f.
## Step 3 -- VALIDATE (F7 GOVERN)
- Run the four usage rules: contrast >= 4.5:1, reduce-motion fallback, single signal, density band.
- Confirm the leverage block is present and non-empty.
- Clean-room self-check: original name + values; no copied system.
- Set `quality: null`; compile.
## Output discipline
Emit only the artifact (frontmatter + body) per [[bld_output_design_system]]. No preamble, no chatter.
## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[bld_schema_design_system]] | upstream | 0.55 |
| [[bld_output_design_system]] | downstream | 0.5 |
| [[bld_eval_design_system]] | downstream | 0.48 |
| p06_vs_design_system | upstream | 0.45 |
| p03_ps_design_system_library_scale | related | 0.4 |
