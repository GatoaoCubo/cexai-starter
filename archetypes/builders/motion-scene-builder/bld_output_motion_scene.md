---
id: bld_output_motion_scene
kind: response_format
pillar: P05
llm_function: PRODUCE
8f: F6_produce
version: 1.0.0
created: "2026-06-15"
updated: "2026-06-15"
author: n03_builder
title: "Template: motion_scene instance"
domain: motion_scene
quality: null
tags: [motion_scene, builder, template, output, P05]
tldr: "The exact shape a motion_scene instance fills: frontmatter (with leverage + binds_design_system) + render/elements/keyframes/easing/transitions/export + primitives + a11y + CEXAI Leverage section."
density_score: 0.88
related:
  - bld_schema_motion_scene
  - bld_prompt_motion_scene
---

# Template: motion_scene instance
Fill every placeholder; keep body <= 6144 bytes. Mirror p05_ms_aurora_title / p05_ms_ferro_lowerthird.
## Frontmatter
```yaml
id: p05_ms_{{name}}
kind: motion_scene
pillar: P05
title: "{{Name}} -- {{one-line description}}"
version: 1.0.0
created: "{{date}}"
author: n03_builder
domain: motion-graphics
primitive: {{lower_third|title_card|counter|scene_transition}}
binds_design_system: p06_ds_{{system_name}}
duration_s: {{number}}
quality: null
leverage:
  binds_design_system: p06_ds_{{system_name}}
  feeds_kinds: [course_module, landing_page, social_publisher, interactive_demo]
  inject_hook: "F3 INJECT: pull (motion_scene + bound design_system) tokens to author branded motion at F6; F8 renders via cli_tool."
  brand_config_relation: "Resolves resolution/fps defaults from media_config.yaml; palette/type/easing from bound design_system p06_ds_{{system_name}}."
  composes_with: [design_system, cli_tool, pipeline_template, voice_pipeline]
  binds_8f: [F6_produce, F8_collaborate]
tags: [motion-scene, {{primitive}}, {{design_system_name}}, P05]
tldr: "{{dense one-line summary}}"
related: [p06_vs_motion_scene, p05_ms_aurora_title, p05_ms_ferro_lowerthird]
```
## Body sections (in order)
1. `# {{Name}}` + one paragraph describing the scene (primitive type + bound system + intent).
2. `## render` -- resolution, fps, duration_s, background (token ref or hex from bound system).
3. `## elements` -- table: id/type/content/style for each element (style resolves from design_system tokens).
4. `## keyframes` -- per-element table: t/x/y/opacity/scale/rotation (t monotonically increasing).
5. `## easing` -- per-segment easing from design_system motion.ease defaults + overrides.
6. `## transitions` -- scene-level transition list (type/at_s/duration_s).
7. `## export` -- codec/container/target_path/poster_frame.
8. `## motion primitives` -- lower_third/title_card/counter/scene_transition compositions.
9. `## a11y` -- prefers_reduced_motion variant, poster_frame, caption_safe_margin_px.
10. `## CEXAI Leverage` -- binds_design_system, feeds, inject hook, brand_config relation, composes-with.
## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[bld_schema_motion_scene]] | upstream | 0.5 |
| [[bld_prompt_motion_scene]] | sibling | 0.42 |
