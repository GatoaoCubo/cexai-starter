---
id: bld_config_motion_scene
kind: env_config
pillar: P05
llm_function: CONSTRAIN
8f: F1_constrain
version: 1.0.0
created: "2026-06-15"
updated: "2026-06-15"
author: n03_builder
title: "Config: motion_scene build knobs"
domain: motion_scene
quality: null
tags: [motion_scene, builder, config, P05]
tldr: "Build-time knobs for a motion_scene: resolution default, fps, primitive type, easing stance, a11y mode, caption margin, and leverage feeds."
density_score: 0.88
related:
  - bld_schema_motion_scene
  - bld_prompt_motion_scene
  - bld_eval_motion_scene
  - p06_vs_motion_scene
  - p01_kc_motion_scene
---

# Config: motion_scene build knobs
CONFIG restricts SCHEMA; it never adds fields the schema does not know.
## Knobs
| Knob | Default | Range | Effect |
|------|---------|-------|--------|
| resolution | [1920, 1080] | [1280,720]..[3840,2160] | render target pixel dimensions |
| fps | 30 | 24, 30, 60 | frames per second |
| primitive | lower_third | lower_third, title_card, counter, scene_transition | canonical scene primitive type |
| easing_stance | ease-out | linear, ease-in, ease-out, spring | default segment easing (override from design_system) |
| a11y_mode | strict | strict, permissive | strict=all spring segments get instant fallback |
| caption_safe_margin_px | 80 | 40..160 | minimum text margin from frame edge |
| codec | libx264 | libx264, libx265 | render codec |
| container | mp4 | mp4 | output container |
## Leverage defaults
`feeds_kinds` defaults to `[course_module, landing_page, social_publisher, interactive_demo]`;
override per brand surface set. `composes_with` defaults to
`[design_system, cli_tool, pipeline_template, voice_pipeline]`.
## Invariants (cannot override)
- quality stays null.
- binds_design_system must reference a real p06_ds_* id (cannot be empty).
- a11y_mode=strict: spring easing ALWAYS gets a prefers_reduced_motion instant fallback.
- All keyframe t values must be strictly increasing per element (schema enforcement).
## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[bld_schema_motion_scene]] | upstream | 0.5 |
| [[bld_prompt_motion_scene]] | sibling | 0.42 |
| [[bld_eval_motion_scene]] | downstream | 0.42 |
| [[p06_vs_motion_scene]] | upstream | 0.4 |
| [[p01_kc_motion_scene]] | related | 0.38 |
