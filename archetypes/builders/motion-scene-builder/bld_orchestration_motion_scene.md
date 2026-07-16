---
id: bld_orchestration_motion_scene
kind: workflow
pillar: P05
llm_function: COLLABORATE
8f: F8_collaborate
version: 1.0.0
created: "2026-06-15"
updated: "2026-06-15"
author: n03_builder
title: "Orchestration: dispatching + composing motion_scene"
domain: motion_scene
quality: null
tags: [motion_scene, builder, orchestration, swarm, P05]
tldr: "How motion_scene builds are dispatched (swarm over design_system x primitive coordinates) and composed (taste loop + downstream surface builders + cli_tool renderer)."
density_score: 0.88
related:
  - p01_kc_motion_scene
  - bld_architecture_motion_scene
  - bld_prompt_motion_scene
  - p06_vs_motion_scene
  - motion-scene-builder
---

# Orchestration: motion_scene
## Single build
`motion-scene-builder` runs F1-F8 on one (design_system x primitive) coordinate -> one instance.
Standard 8F: F1 constrains kind/pillar, F2 loads ISOs, F3 injects the bound design_system tokens,
F4 plans the keyframe layout, F5 checks tools, F6 authors the scene, F7 validates gates,
F8 compiles + invokes cli_tool renderer.
## Library build (swarm)
1. Compute uncovered (design_system x primitive) pairs from the coverage matrix.
2. `bash _spawn/dispatch.sh swarm motion_scene N` -- one cell -> one instance, isolated worktrees.
3. Each cell briefed with a target design_system id + primitive type + an intent phrase.
4. After swarm: `_tools/cex_motion_render.py --batch` renders all new scenes to MP4.
## Convergence (taste loop)
Wrap the swarm in the render-preview + taste loop: render MP4 thumbnails, founder gives structured
approve/reject (GDP), signals re-weight the next round toward approved coordinates and uncovered
pairs. Converge per axis-region when a round adds no fresh signal.
## Downstream composition
A produced scene is injected at F3 by surface builders (course_module, landing_page, social_publisher,
interactive_demo). The motion_scene is the upstream authored asset; the surface is the downstream
artifact. The render output (MP4) drops into the same `overlay=enable='between(t,S,E)'` slot
already used for static PNG cutaways -- downstream pipeline sees no difference.
## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[p01_kc_motion_scene]] | upstream | 0.5 |
| [[bld_architecture_motion_scene]] | sibling | 0.42 |
| [[bld_prompt_motion_scene]] | related | 0.4 |
| [[p06_vs_motion_scene]] | upstream | 0.4 |
| [[motion-scene-builder]] | related | 0.4 |
