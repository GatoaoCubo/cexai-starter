---
id: bld_prompt_motion_scene
kind: instruction
pillar: P05
llm_function: REASON
8f: F4_reason
version: 1.0.0
created: "2026-06-15"
updated: "2026-06-15"
author: n03_builder
title: "Process: build a motion_scene"
domain: motion_scene
quality: null
tags: [motion_scene, builder, prompt, process, P05]
tldr: "Research > compose > validate process for producing one original, governed motion_scene bound to a design_system and declaring its CEXAI leverage."
density_score: 0.9
related:
  - bld_schema_motion_scene
  - bld_output_motion_scene
  - bld_eval_motion_scene
  - p06_vs_motion_scene
  - p01_kc_motion_scene
---

# Process: build a motion_scene
## Inputs
A target primitive type (lower_third|title_card|counter|scene_transition) + a bound
`design_system` id (e.g. `p06_ds_ferro`) + an intent (e.g. "5-second course intro title") +
the contract [[p06_vs_motion_scene]].
## Step 1 -- RESEARCH (F3 INJECT)
- Load [[bld_schema_motion_scene]] (source of truth) + [[p01_kc_motion_scene]].
- Read the bound design_system to extract color/type/motion tokens.
- Confirm the scene primitive type is not a sibling of an existing scene binding the same system.
- Decide easing stance from the design_system motion.ease tokens.
## Step 2 -- COMPOSE (F6 PRODUCE)
- render: set resolution (default 1920x1080), fps (default 30), duration_s, background
  (token ref or literal hex from the bound design_system canvas token).
- elements[]: define each element (id, type, content, style resolved from design_system tokens).
- keyframes[]: for each element, define {t, x, y, opacity, scale, rotation} with t monotonically
  increasing. All t values in seconds; first keyframe at t=0.0.
- easing: set per-segment easing (linear|ease-in|ease-out|spring) defaulting from the bound
  design_system motion.ease tokens.
- transitions[]: declare scene-level transitions (fade|wipe|push|cut).
- export: codec=libx264, container=mp4, target_path, poster_frame (static fallback at t=0).
- primitives: compose lower_third/title_card/counter/scene_transition from element+keyframe
  slots only (no raw ffmpeg flags).
- a11y: declare prefers_reduced_motion variant (all durations collapse to 0), poster_frame,
  caption_safe_margin_px.
- leverage: declare binds_design_system, feeds_kinds, inject_hook, brand_config_relation,
  composes_with, binds_8f.
## Step 3 -- VALIDATE (F7 GOVERN)
- Run a11y gate: prefers_reduced_motion present, poster_frame declared, caption_safe_margin_px set.
- Confirm keyframe t monotonic per element.
- Confirm leverage block present and binds_design_system non-empty (real p06_ds_* id).
- Confirm body <= 6144 bytes.
- Clean-room self-check: original element content + values; no copied scene.
- Set `quality: null`; compile.
## Output discipline
Emit only the artifact (frontmatter + body) per [[bld_output_motion_scene]]. No preamble, no chatter.
## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[bld_schema_motion_scene]] | upstream | 0.55 |
| [[bld_output_motion_scene]] | downstream | 0.5 |
| [[bld_eval_motion_scene]] | downstream | 0.48 |
| [[p06_vs_motion_scene]] | upstream | 0.45 |
| [[p01_kc_motion_scene]] | related | 0.4 |
