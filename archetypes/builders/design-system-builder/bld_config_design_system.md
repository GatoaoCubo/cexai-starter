---
id: bld_config_design_system
kind: env_config
pillar: P06
llm_function: CONSTRAIN
8f: F1_constrain
version: 1.0.0
created: "2026-06-15"
updated: "2026-06-15"
author: n03_builder
title: "Config: design_system build knobs"
domain: design_system
quality: null
tags: [design_system, builder, config, P06]
tldr: "Build-time knobs for a design_system: density default, signal count, contrast target, motion stance, type ratio, base unit, and leverage feeds."
density_score: 0.88
related:
  - bld_schema_design_system
  - bld_prompt_design_system
  - bld_eval_design_system
---

# Config: design_system build knobs
CONFIG restricts SCHEMA; it never adds fields the schema does not know.
## Knobs
| Knob | Default | Range | Effect |
|------|---------|-------|--------|
| density | comfortable | comfortable, compact | active space.scale band |
| signal_count | 1 | 1 | accents allowed (hard 1) |
| contrast_target | 4.5 | 4.5..7.0 | minimum WCAG ratio enforced |
| motion_stance | standard | snap, standard, spring | shapes the move recipes |
| type_ratio | 1.25 | 1.2..1.618 | modular scale ratio |
| base_unit | 8 | 4, 8 | spacing base px |
## Leverage defaults
`feeds_kinds` defaults to `[landing_page, interactive_demo, product_tour, onboarding_flow, pitch_deck]`; override per brand surface set. `composes_with` defaults to `[variant_shotgun_taste_loop, user_model, gdp]`.
## Invariants (cannot override)
- signal_count stays 1 (single-signal rule).
- contrast_target floor is 4.5 (never lower).
- quality stays null.
## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[bld_schema_design_system]] | upstream | 0.5 |
| [[bld_prompt_design_system]] | sibling | 0.42 |
| [[bld_eval_design_system]] | downstream | 0.42 |
| p06_vs_design_system | upstream | 0.4 |
| [[kc_design_system]] | related | 0.38 |
