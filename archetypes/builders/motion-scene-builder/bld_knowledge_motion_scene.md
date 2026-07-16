---
id: bld_knowledge_motion_scene
kind: knowledge_card
pillar: P05
llm_function: INJECT
8f: F3_inject
version: 1.0.0
created: "2026-06-15"
updated: "2026-06-15"
author: n03_builder
title: "Domain Knowledge: motion_scene"
domain: motion_scene
quality: null
tags: [motion_scene, builder, knowledge, keyframes, P05]
tldr: "Atomic facts for building motion scenes: keyframe interpolation, easing taxonomy, ffmpeg filtergraph model, motion primitives, a11y timing discipline, and design_system token resolution."
density_score: 0.92
related:
  - bld_schema_motion_scene
  - p01_kc_motion_scene
  - p06_vs_motion_scene
  - bld_memory_motion_scene
  - motion-scene-builder
---

# Domain Knowledge: motion_scene
## Keyframe model
A keyframe records element state at a discrete time t (seconds). Between keyframes the renderer
interpolates: position (x,y), opacity (0.0-1.0), scale (1.0=identity), rotation (degrees).
t values must be strictly increasing per element. First keyframe at t=0.0 sets initial state.
## Easing taxonomy
Four canonical easing types: `linear` (constant rate), `ease-in` (slow start, fast end),
`ease-out` (fast start, slow end), `spring` (overshoot + settle -- avoid under reduced-motion).
The bound design_system motion.ease token group is the DEFAULT source; override per-segment only
when the scene requires a different rhythm.
## ffmpeg filtergraph model
The renderer translates element keyframes to chained ffmpeg filters: `overlay` (element
compositing), `drawtext` (text elements with font/size/color), `fade` (opacity transitions),
`scale`+`setpts` (zoom/timing), `geq` (per-pixel easing). Output: PNG frame sequence -> libx264
encode. The motion_scene artifact does NOT embed ffmpeg flags -- it declares what to render;
the cli_tool translates.
## Motion primitives
`lower_third`: text element anchored to lower frame region, enters via slide-up with ease-out,
exits via fade. `title_card`: full-frame title element with scale+fade-in, hold, fade-out.
`counter`: numeric element with per-frame value increment, constant position. `scene_transition`:
full-frame transition (fade|wipe|push|cut) between scene segments at a declared at_s.
## Design_system token resolution
Elements reference design_system token keys in their style fields (e.g. `color: design_system.color.signal`,
`font_size: design_system.type.scale.t3`). The renderer resolves token keys at render time from the
bound `p06_ds_*` artifact. Literal values in style fields bypass the token system -- flag as a
gate violation.
## A11y timing discipline
prefers_reduced_motion: all duration values collapse to 0s (instant-cut instead of animated).
poster_frame: a static image at t=0 for environments that cannot render motion. caption_safe_margin_px:
text elements must stay within the safe margin (typically >=80px from each edge for broadcast,
>=40px for web overlays).
## WCAG text contrast
Text-over-background: derived color pair from the bound design_system. ink-on-canvas and signal_ink-on-signal
pairs must achieve >= 4.5:1 (WCAG AA). Verify from the design_system token values, not from the rendered frame.
## Clean-room discipline
Element content (text labels, placeholder copy), keyframe coordinate values, and system names are
original per-scene IP. Never copy a known scene's keyframe table or content verbatim.
Author from the primitive type + the bound design_system coordinate.
## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[bld_schema_motion_scene]] | downstream | 0.5 |
| [[p01_kc_motion_scene]] | sibling | 0.48 |
| [[p06_vs_motion_scene]] | upstream | 0.45 |
| [[bld_memory_motion_scene]] | sibling | 0.4 |
| [[motion-scene-builder]] | related | 0.4 |
