---
id: bld_eval_motion_scene
kind: quality_gate
pillar: P05
llm_function: GOVERN
8f: F7_govern
version: 1.0.0
created: "2026-06-15"
updated: "2026-06-15"
author: n03_builder
title: "Gate: motion_scene"
domain: motion_scene
quality: null
tags: [motion_scene, builder, eval, quality_gate, P05]
tldr: "HARD + SOFT gates for motion_scene: six groups, monotonic keyframes, a11y gate, WCAG-safe text-over-background, reduced-motion declared, binds a real design_system, body <= 6144B."
density_score: 0.9
related:
  - bld_schema_motion_scene
  - bld_output_motion_scene
---

# Gate: motion_scene
## HARD gates (any FAIL -> REJECT, no score)
| ID | Check | Rule |
|----|-------|------|
| H01 | Frontmatter parses | valid YAML, complete |
| H02 | id pattern | `^p05_ms_[a-z][a-z0-9_]+$`, equals filename stem |
| H03 | kind literal | `kind` is exactly `motion_scene` |
| H04 | quality null | `quality` is null |
| H05 | six groups present | render, elements, keyframes, easing, transitions, export all present |
| H06 | binds_design_system non-empty | leverage.binds_design_system references a real `p06_ds_*` id |
| H07 | monotonic keyframes | per element, keyframe t values strictly increasing |
| H08 | body within limit | body <= 6144 bytes |
## SOFT scoring (0 or 10 x weight)
| Dimension | Weight | Pass condition |
|-----------|--------|----------------|
| A11y gate complete | 1.0 | prefers_reduced_motion variant + poster_frame + caption_safe_margin_px all declared |
| WCAG text contrast | 1.0 | text element color-over-background contrast >= 4.5:1 (derived from bound design_system tokens) |
| Reduced-motion declared | 1.0 | all move durations collapse to 0s in the prefers_reduced_motion variant |
| Four primitives composed | 1.0 | lower_third/title_card/counter/scene_transition all defined from slots only |
| Design-system token resolution | 1.0 | style fields reference design_system token keys, not literal hex/px values |
| Clean-room | 1.0 | original element content + keyframe values; no copied scene |
| Distinct coordinate | 0.5 | not a sibling of an existing scene (same system + same primitive type) |
| Leverage complete | 0.5 | all six leverage sub-fields non-empty |
Sum weights 8.0; `soft = sum(weight*score)/8.0*10`.
## Actions
| Score | Action |
|-------|--------|
| >= 9.5 | GOLDEN -- canonical library entry |
| >= 8.0 | PUBLISH |
| >= 7.0 | REVISE -- a11y or token resolution needs work |
| < 7.0 | REJECT |
## Golden vs Anti
- GOLDEN: p05_ms_ferro_lowerthird -- six groups, monotonic t, WCAG-safe text, reduced-motion
  variant, all four primitives, binds ferro design_system, leverage complete.
- ANTI: keyframe t non-monotonic; literal hex values not resolved from design_system; missing
  prefers_reduced_motion; binds_design_system empty; spring easing with no reduced-motion fallback.
## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[bld_schema_motion_scene]] | upstream | 0.55 |
| [[bld_output_motion_scene]] | sibling | 0.42 |
