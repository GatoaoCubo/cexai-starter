---
id: bld_feedback_motion_scene
kind: reward_signal
pillar: P05
llm_function: GOVERN
8f: F7_govern
version: 1.0.0
created: "2026-06-15"
updated: "2026-06-15"
author: n03_builder
title: "Feedback: motion_scene reward + regression signals"
domain: motion_scene
quality: null
tags: [motion_scene, builder, feedback, signals, P05]
tldr: "What to reward and what to flag across motion_scene builds: coordinate diversity, a11y gate pass-rate, token resolution integrity, leverage completeness, clean-room."
density_score: 0.88
related:
  - bld_eval_motion_scene
  - bld_memory_motion_scene
---

# Feedback: motion_scene signals
## Reward signals (reinforce)
| Signal | Meaning |
|--------|---------|
| coordinate_distinct | the scene covers an uncovered (design_system x primitive) pair -> +diversity |
| a11y_pass_first_try | prefers_reduced_motion + poster_frame declared without a rejection loop |
| token_resolution_clean | all style fields use design_system token keys (no literal values) |
| leverage_complete | binds_design_system + feeds_kinds + inject_hook + brand_config_relation all set |
| founder_approved | taste-loop approval of a rendered MP4 -> update um_founder_taste |
## Regression signals (flag)
| Signal | Meaning |
|--------|---------|
| sibling_collision | same design_system + same primitive already covered by an existing scene |
| non_monotonic_t | keyframe t values out of order -> hard gate H07 fail |
| literal_style_value | style field contains raw hex/px instead of a design_system token key |
| a11y_missing | prefers_reduced_motion or poster_frame absent -> reject |
| binds_empty | leverage.binds_design_system empty -> hard gate H06 fail; rebuild with a real system |
| clean_room_breach | copied element content or keyframe table -> reject + rebuild |
## Loop hook
Rendered-MP4 approvals/rejections feed the swarm taste loop; signals decay ~5%/week and
re-weight the next round toward approved (design_system x primitive) coordinates and uncovered
pairs. Converge per coordinate region when a round adds no fresh signal.
## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[bld_eval_motion_scene]] | upstream | 0.48 |
| [[bld_memory_motion_scene]] | sibling | 0.42 |
