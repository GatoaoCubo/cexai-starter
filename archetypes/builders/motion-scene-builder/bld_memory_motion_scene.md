---
id: bld_memory_motion_scene
kind: learning_record
pillar: P05
llm_function: INJECT
8f: F3_inject
version: 1.0.0
created: "2026-06-15"
updated: "2026-06-15"
author: n03_builder
title: "Patterns: motion_scene builds"
domain: motion_scene
quality: null
tags: [motion_scene, builder, memory, patterns, P05]
tldr: "Learned patterns + recurring failure modes from motion_scene builds: primitive-first, monotonic t enforcement, design_system token binding, a11y gate upfront, clean-room."
density_score: 0.9
related:
  - bld_knowledge_motion_scene
  - bld_eval_motion_scene
---

# Patterns: motion_scene builds
## What scored high
| Pattern | Why |
|---------|-----|
| Primitive-first | fix the primitive type (lower_third|title_card|counter|scene_transition) before authoring elements -> no scope drift |
| Design_system bound early | reading the bound p06_ds_* tokens before authoring style fields -> style is always in-system |
| Monotonic t verified upfront | checking t order per element at F4 REASON avoids a hard gate fail at F7 |
| A11y gate authored concurrently | writing prefers_reduced_motion + poster_frame alongside the main keyframes -> no retrofit |
| Spring easing with instant fallback | spring reads as organic; the reduced-motion fallback makes it accessible |
| Leverage declared early | binds_design_system forces the scene to be composable, not a standalone artifact |
## Recurring failures
| Failure | Fix |
|---------|-----|
| Non-monotonic t in keyframe table | always sort by t per element before writing; assert strictly increasing |
| Literal hex in style fields | replace with design_system token key (e.g. `design_system.color.signal` not `"#FF1493"`) |
| Missing prefers_reduced_motion | add the variant immediately after authoring main keyframes |
| Spring easing without fallback | add `easing_reduced: instant` for every spring segment |
| Empty binds_design_system | HARD gate fail; always bind a real p06_ds_* id before F6 |
| Sibling scene (same system + same primitive) | shift the scene coordinate (different duration, different element layout, or different primitive) |
## Library shape
p05_ms_ferro_lowerthird = cold/compact/stark system + lower_third primitive. p05_ms_aurora_title = warm/airy system + title_card primitive. Swarm fills interior coordinates (different systems x four primitives x duration variants).
## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[bld_eval_motion_scene]] | upstream | 0.45 |
| [[bld_knowledge_motion_scene]] | sibling | 0.42 |
