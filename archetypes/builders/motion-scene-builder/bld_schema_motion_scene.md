---
id: bld_schema_motion_scene
kind: schema
pillar: P05
llm_function: CONSTRAIN
8f: F1_constrain
version: 1.0.0
created: "2026-06-15"
updated: "2026-06-15"
author: n03_builder
title: "Schema: motion_scene"
domain: motion_scene
quality: null
tags: [motion_scene, builder, schema, keyframes, P05]
tldr: "Single source of truth for a motion_scene: six declarative groups, four motion primitives, a11y gate, and a mandatory leverage block with binds_design_system."
density_score: 0.92
related:
  - p06_vs_motion_scene
  - bld_model_motion_scene
  - bld_output_motion_scene
  - bld_eval_motion_scene
  - p01_kc_motion_scene
---

# Schema: motion_scene
Derivation hierarchy: **SCHEMA (this) > TEMPLATE (bld_output) > CONFIG (bld_config)**.
The defining contract is [[p06_vs_motion_scene]]; this ISO is its builder-facing restatement.

## Frontmatter Fields (required)
| Field | Type | Notes |
|-------|------|-------|
| id | string `p05_ms_{name}` | equals filename stem |
| kind | literal `motion_scene` | type integrity |
| pillar | literal `P05` | pillar assignment |
| title | string | "Name -- one-line description" |
| version | semver | start 1.0.0 |
| primitive | enum `lower_third\|title_card\|counter\|scene_transition` | scene primitive type |
| binds_design_system | string `p06_ds_{name}` | required: the bound design_system id |
| duration_s | number | scene duration in seconds (>0) |
| leverage | block | binds_design_system, feeds_kinds, inject_hook, brand_config_relation, composes_with, binds_8f |
| quality | null | never self-score |
| tags | list >=3 | includes `motion-scene` |

## Six declarative groups (all mandatory)
| Group | Required fields |
|-------|-----------------|
| render | resolution [w,h], fps, duration_s, background (token ref or hex literal) |
| elements[] | id, type (text\|image\|shape\|counter), content, style (font/size/color resolved from design_system tokens) |
| keyframes[] | per element: [{t, x, y, opacity, scale, rotation}] with t monotonically increasing |
| easing | per segment: linear\|ease-in\|ease-out\|spring (defaults from bound design_system motion.ease) |
| transitions[] | scene-level: [{type: fade\|wipe\|push\|cut, at_s, duration_s}] |
| export | codec: libx264, container: mp4, target_path, poster_frame (static fallback t=0) |

## Motion primitives (four mandatory)
`lower_third`, `title_card`, `counter`, `scene_transition` -- element+keyframe compositions
only, never raw ffmpeg flags or filter strings.

## Accessibility gate (mandatory)
1. prefers_reduced_motion: declare a variant where all move durations collapse to 0s.
2. poster_frame: a static fallback image at t=0 (export.poster_frame non-empty).
3. caption_safe_margin_px: text elements must respect a minimum margin from the frame edge.

## Leverage block (mandatory)
`binds_design_system` (a real `p06_ds_*` id) + `feeds_kinds` (>=1 kind) + `inject_hook` +
`brand_config_relation` + `composes_with` + `binds_8f`. Missing or empty binds_design_system
-> FAIL: an unbound scene is not a governed motion_scene.

## Constraints
- max_bytes: 6144 (body); naming `p05_ms_{name}.md`; machine_format yaml.
- id == filename stem; quality: null always; clean-room (original values, no copied scene).
- All keyframe t values are seconds (float >= 0); per element, t must be strictly increasing.

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[p06_vs_motion_scene]] | upstream | 0.6 |
| [[bld_output_motion_scene]] | downstream | 0.5 |
| [[bld_eval_motion_scene]] | downstream | 0.48 |
| [[bld_model_motion_scene]] | sibling | 0.4 |
| [[p01_kc_motion_scene]] | related | 0.4 |
