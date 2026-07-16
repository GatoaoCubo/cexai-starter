---
id: bld_feedback_design_system
kind: reward_signal
pillar: P06
llm_function: GOVERN
8f: F7_govern
version: 1.0.0
created: "2026-06-15"
updated: "2026-06-15"
author: n03_builder
title: "Feedback: design_system reward + regression signals"
domain: design_system
quality: null
tags: [design_system, builder, feedback, signals, P06]
tldr: "What to reward and what to flag across design_system builds: coordinate diversity, contrast pass-rate, leverage completeness, clean-room integrity."
density_score: 0.88
related:
  - bld_eval_design_system
  - bld_memory_design_system
---

# Feedback: design_system signals
## Reward signals (reinforce)
| Signal | Meaning |
|--------|---------|
| coordinate_distinct | the system occupies an uncovered corner -> +diversity |
| contrast_pass_first_try | no rejection loop on accessibility |
| leverage_complete | feeds_kinds + inject_hook + brand_config_relation all set |
| founder_approved | taste-loop approval -> update um_founder_taste |
## Regression signals (flag)
| Signal | Meaning |
|--------|---------|
| sibling_collision | shares signal-hue + density + mode with an existing system |
| contrast_fail | any pair < 4.5:1 |
| leverage_missing | passive token dump |
| clean_room_breach | copied name or value -> reject + rebuild |
## Loop hook
Approvals/rejections feed the variant-shotgun taste loop; signals decay ~5%/week and re-weight the next round toward approved corners and uncovered coordinates (p03_ps_design_system_library_scale).
## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[bld_eval_design_system]] | upstream | 0.48 |
| [[bld_memory_design_system]] | sibling | 0.42 |
| p03_ps_design_system_library_scale | related | 0.42 |
| um_founder_taste | related | 0.4 |
| p06_vs_design_system | upstream | 0.38 |
