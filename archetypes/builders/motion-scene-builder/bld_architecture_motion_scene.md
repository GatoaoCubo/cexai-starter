---
id: bld_architecture_motion_scene
kind: pattern
pillar: P05
llm_function: CONSTRAIN
8f: F1_constrain
version: 1.0.0
created: "2026-06-15"
updated: "2026-06-15"
author: n03_builder
title: "Architecture: where motion_scene sits"
domain: motion_scene
quality: null
tags: [motion_scene, builder, architecture, composition, P05]
tldr: "How motion_scene fits CEXAI: governed by the contract, bound to a design_system for tokens, rendered by cli_tool, orchestrated by pipeline_template, injected into surface kinds."
density_score: 0.9
related:
  - p06_vs_motion_scene
  - p08_adr_motion_scene_kind
  - p01_kc_motion_scene
  - bld_orchestration_motion_scene
  - p01_kc_design_assim_hyperframes_motion_map
---

# Architecture: where motion_scene sits
## Position in the kind graph
| Relation | Kind | Direction |
|----------|------|-----------|
| governed by | validation_schema ([[p06_vs_motion_scene]]) | upstream contract |
| binds (tokens) | design_system (`p06_ds_*`) | upstream token source |
| rendered by | cli_tool ([[cli_tool_cex_motion_render]]) | upstream renderer |
| orchestrated by | pipeline_template ([[tpl_motion_pipeline]]) | upstream workflow |
| injected into | course_module, landing_page, social_publisher, interactive_demo | downstream consumers |
| scaled by | swarm dispatch over primitive x design_system coordinates | sideways (library growth) |
## Layering
motion_scene is a P05 OUTPUT asset (declarative scene that renders to MP4), distinct from:
- the P06 CONTRACT ([[p06_vs_motion_scene]] -- the typed schema shape, not the authored scene)
- the P04 RENDERER ([[cli_tool_cex_motion_render]] -- the ffmpeg tool, not the authored scene)
- the P12 WORKFLOW ([[tpl_motion_pipeline]] -- the pipeline, not the authored scene)
- the design_system (the token source, bound at leverage.binds_design_system)
The scene binds at F1 CONSTRAIN (declared as a constraint) and F6 PRODUCE (authored), then
renders at F8 COLLABORATE (cli_tool invoked with the compiled scene yaml).
## Why a kind, not a composition
A pipeline_template + cli_tool + validation_schema per scene would fragment each scene across
3+ files with no atomic "pick this scene" handle. The library use case (150 design systems x
4 primitives = 600 scenes) demands an atomic, selectable, swarm-buildable unit -- the new-kind
signal (justified in [[spec_motion_scene_kind]] by the design_system precedent and the 5-Q test).
## Library shape
Scenes form a coverage matrix over two axes: design_system (150 systems) x primitive type
(lower_third/title_card/counter/scene_transition). Each instance owns a distinct coordinate.
## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[p06_vs_motion_scene]] | upstream | 0.5 |
| [[p01_kc_design_assim_hyperframes_motion_map]] | upstream | 0.48 |
| [[spec_motion_scene_kind]] | upstream | 0.45 |
| [[bld_orchestration_motion_scene]] | sibling | 0.4 |
| [[p01_kc_motion_scene]] | related | 0.4 |
