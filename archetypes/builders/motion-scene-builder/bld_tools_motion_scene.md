---
id: bld_tools_motion_scene
kind: toolkit
pillar: P05
llm_function: CALL
8f: F5_call
version: 1.0.0
created: "2026-06-15"
updated: "2026-06-15"
author: n03_builder
title: "Tools: building + validating a motion_scene"
domain: motion_scene
quality: null
tags: [motion_scene, builder, tools, P05]
tldr: "The tool inventory a motion_scene build calls: compile, doctor, score, index, a11y check, token resolution check, and the dispatch/swarm entry."
density_score: 0.88
related:
  - bld_prompt_motion_scene
  - bld_eval_motion_scene
  - bld_orchestration_motion_scene
  - motion-scene-builder
---

# Tools: motion_scene
## Build + govern
| Tool | Use |
|------|-----|
| `cex_compile.py` | compile the instance .md -> .yaml (mandatory F8) |
| `cex_doctor.py` | builder-dir health (this ISO set passes 12/12) |
| `cex_score.py` | peer score (never self-score) |
| `cex_index.py` | index frontmatter + wikilinks |
## Domain checks
| Check | How |
|-------|-----|
| Monotonic t | assert per-element keyframe t is strictly increasing (float sort + diff check) |
| A11y gate | assert prefers_reduced_motion variant present + poster_frame non-empty + caption_safe_margin_px set |
| WCAG contrast | compute contrast for text element color-over-background from bound design_system tokens (>= 4.5:1) |
| Token resolution | assert style fields use design_system token keys, not literal values |
| Leverage | assert leverage.binds_design_system non-empty (real p06_ds_* id) |
| Body size | assert body <= 6144 bytes |
## Render (F8 COLLABORATE)
| Tool | Use |
|------|-----|
| `_tools/cex_motion_render.py` | ffmpeg-native renderer: reads motion_scene .yaml, resolves bound design_system tokens, produces MP4 |
## Scale
| Tool | Use |
|------|-----|
| `_spawn/dispatch.sh swarm motion_scene N` | parallel library build over primitive x design_system coordinates |
## Discipline
Tools VALIDATE; they never invent keyframe values. A motion_scene's element positions and
timing are authored, then verified. Token resolution is a gate check; the renderer reads the
pre-authored token keys and resolves at render time from the bound design_system artifact.
## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[bld_eval_motion_scene]] | upstream | 0.45 |
| [[bld_prompt_motion_scene]] | related | 0.42 |
| [[bld_orchestration_motion_scene]] | sibling | 0.4 |
| [[motion-scene-builder]] | related | 0.38 |
