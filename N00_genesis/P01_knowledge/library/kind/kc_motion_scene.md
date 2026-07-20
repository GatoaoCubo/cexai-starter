---
id: p01_kc_motion_scene
kind: knowledge_card
8f: F3_inject
type: kind
pillar: P05
title: "Motion Scene -- Deep Knowledge for motion_scene"
version: 1.0.0
created: "2026-06-15"
updated: "2026-06-15"
author: n03_builder
domain: motion-graphics
quality: null
tags: [motion_scene, P05, INJECT, kind-kc, keyframes, ffmpeg, motion, design-system, leverage]
tldr: "Declarative programmatic-motion artifact (render/elements/keyframes/easing/transitions/export) that binds one design_system and compiles to MP4 via an ffmpeg-native renderer. Four canonical primitives: lower_third, title_card, counter, scene_transition. Mandatory a11y gate: reduced_motion_variant + poster_frame."
when_to_use: "Building, reviewing, or reasoning about motion_scene artifacts"
keywords: [motion scene, programmatic animation, keyframes, ffmpeg, design system, lower third, title card, counter, scene transition, mp4, render, easing]
feeds_kinds: [motion_scene]
density_score: 0.95
linked_artifacts:
  primary: p06_vs_motion_scene
  related: []
related:
  - p06_vs_motion_scene
  - spec_motion_scene_kind
  - p01_kc_design_assim_hyperframes_motion_map
  - kc_design_system
  - p06_vs_design_system
---

# Motion Scene

## Spec

```yaml
kind: motion_scene
pillar: P05
llm_function: PRODUCE
max_bytes: 6144
naming: p05_ms_{{name}}.md
core: false
```

## What It Is

A `motion_scene` (P05) is one declarative, programmatic-motion artifact expressed as
six typed groups (render / elements / keyframes / easing / transitions / export) plus a
CEXAI leverage declaration. A motion-scene builder authors the scene at F6 PRODUCE; the
ffmpeg-native renderer compiles it to MP4 at F8 COLLABORATE. The rendered MP4 drops into
the same timed-overlay slot used by static PNG cutaways -- the downstream pipeline sees
no difference except the asset now carries element-level animation.

NOT `pipeline_template` (the orchestration workflow that runs the renderer, not the
authored scene itself). NOT `cli_tool` (the renderer is the cli_tool; the scene is what
the renderer consumes). NOT `validation_schema` (defines the contract SHAPE, not the
authored scene with concrete values). NOT `design_system` (the design_system supplies
tokens; the motion_scene binds them and declares animated behavior).

The contract every instance satisfies is p06_vs_motion_scene.

## Six required groups

| Group | Holds | Key slots |
|-------|-------|-----------|
| `render` | Frame target | resolution [w,h], fps, duration_s, background |
| `elements[]` | Compositable units | id, type, content, style (font/color/opacity) |
| `keyframes[]` | Per-element animation | t, x, y, opacity, scale, rotation |
| `easing` | Interpolation defaults | default, reduce_motion_fallback, dur_unit_ms |
| `transitions[]` | Scene-level transitions | id, type (fade/wipe/push/cut), duration_s, at_t |
| `export` | Render output spec | codec, container, target_path, poster_frame_t |

## Design-system token binding

Every `style.*` field in `elements[]` and the `easing.default` field MAY reference a
bound design_system token using the ref pattern `ds.{group}.{slot}`. Examples:

| Scene field | Token ref | Resolves from |
|-------------|-----------|---------------|
| `style.color` | `ds.color.signal` | bound system's color.signal hex |
| `style.font_face` | `ds.type.face.text` | bound system's type.face.text font stack |
| `easing.default` | `ds.motion.ease.standard` | bound system's motion easing |
| `background` | `ds.color.canvas` | bound system's color.canvas |

The renderer resolves all `ds.*` refs at compile time from the instance named in
`leverage.binds_design_system`. This is the composition hook: the 150-system design
library x motion_scene = branded animated assets where each scene inherits its
palette/type/easing from the chosen system.

## Four canonical motion primitives

| Primitive | Use | elements[] minimum | Typical duration_s |
|-----------|-----|--------------------|--------------------|
| `lower_third` | Speaker name + role overlay | 2 (text + text or shape) | 3..6 |
| `title_card` | Section or chapter title | 1 (text headline) | 4..8 |
| `counter` | Animated numeric count-up | 1 (counter type) | 2..5 |
| `scene_transition` | Cross-cut visual bridge | 0..1 + transitions entry | 0.5..1.5 |

Declare by adding `primitive: lower_third` (or other) to instance frontmatter. Optional
but recommended -- the validator applies primitive-specific checks when declared.

## Accessibility gate (mandatory in every instance)

The `accessibility` block is NOT optional:

| Field | Constraint |
|-------|-----------|
| `reduced_motion_variant` | MUST be `true` -- declare that reduced-motion behavior is handled |
| `poster_frame_t` | MUST match `export.poster_frame_t` -- static fallback confirmed |
| `caption_safe_margin_px` | Recommended -- guards text from caption overlay collision |

Rationale: CEXAI's motion pipeline targets course modules and social content consumed on
devices that may have `prefers_reduced_motion` set. Every scene must declare its
reduced-motion posture explicitly; the renderer uses `easing.reduce_motion_fallback`
(which MUST be `linear` or `ease_in`) to collapse all animation to instant cuts.

## CEXAI leverage model

Each scene carries "its own CEXAI leverage capabilities." Every instance declares a
`leverage:` block:

| Field | Role |
|-------|------|
| `binds_design_system` | ID of the bound `p06_ds_*` instance (palette/type/motion token source) |
| `feeds_kinds` | Kinds that embed the rendered MP4 (course_module, landing_page, social_publisher, interactive_demo) |
| `inject_hook` | How the builder resolves design_system tokens at F3 INJECT |
| `brand_config_relation` | How render defaults (fps, resolution) relate to media_config.yaml / brand_config.yaml |
| `composes_with` | design_system (tokens) + cli_tool (render) + pipeline_template (orchestrate) + voice_pipeline (TTS track) |
| `binds_8f` | F6_produce (author) + F8_collaborate (render + commit) |

This is the difference between a static spec and an active asset: the scene declares
its own wiring into the 8F pipeline and the kind graph.

## W2 ffmpeg-native render path

At F8 COLLABORATE the bound `cli_tool` (`cex_motion_render.py`) translates the scene
spec to an ffmpeg filtergraph:

```
elements -> drawtext / overlay / geq filters (one per element per keyframe window)
keyframes -> setpts + scale + opacity via geq expr interpolation
easing -> cubic approximation via geq or linear setpts offset
transitions -> fade / xfade / overlay with time-bounded enable
poster_frame -> single-frame PNG extracted via -ss {poster_frame_t} -frames:v 1
PNG sequence -> libx264 yuv420p at render.fps
```

The output MP4 is drop-in compatible with the existing `overlay=enable='between(t,S,E)'`
timed-overlay slot in the course video pipeline. Downstream compositor sees no change.

## Integration graph

```
[design_system (p06_ds_*)] --token source--> [motion_scene] --F8 render--> [MP4]
[p06_vs_motion_scene] --GOVERNs--> [motion_scene]
[cli_tool (cex_motion_render)] --renders--> [motion_scene -> MP4]
[pipeline_template (tpl_motion_pipeline)] --orchestrates--> [cli_tool]
[course_module | landing_page | social_publisher] --embeds--> [MP4 at timed window]
```

## Decision tree

- IF you need a rendered animated overlay (lower-third, title, counter, transition)
  THEN motion_scene (P05)
- IF you need the SHAPE/contract of such a scene THEN validation_schema (p06_vs_motion_scene)
- IF you need the render workflow (input scene -> ffmpeg -> output MP4)
  THEN pipeline_template (tpl_motion_pipeline)
- IF you need the renderer itself as a callable tool THEN cli_tool (cex_motion_render)
- DEFAULT: motion_scene for any authored animated artifact that outputs MP4

## Anti-patterns

| Anti-pattern | Why it fails |
|-------------|-------------|
| No `leverage.binds_design_system` | Unresolvable `ds.*` token refs; non-composable |
| `reduced_motion_variant: false` | Fails the a11y gate; every scene must declare posture |
| No `poster_frame_t` in export | No static fallback for non-motion contexts |
| Keyframes out of ascending t order | Renderer cannot interpolate; compile error |
| Copying external motion-tool value sets (easing curves, timing signatures) | Clean-room breach; all values must be CEXAI-original |
| `quality` set to a score | Never self-score; peer review assigns |

## Quality criteria

- GOOD: six groups complete, four primitive-compatible shape, a11y block present, leverage declared
- GREAT: all `ds.*` token refs verified against the bound design_system, reduced-motion behavior tested, original clean-room values
- FAIL: missing leverage, missing accessibility block, no poster_frame_t, quality not null

## Related Artifacts

| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[p01_kc_design_assim_hyperframes_motion_map]] | peer (gap analysis + render grammar) | 0.45 |
| [[kc_design_system]] | peer (token source kind) | 0.42 |
