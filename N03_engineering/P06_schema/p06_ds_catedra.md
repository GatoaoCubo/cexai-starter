---
id: p06_ds_catedra
kind: design_system
pillar: P06
nucleus: N03
title: "Catedra -- approachable-academic, humanist e-learning design system"
version: 1.0.0
created: "2026-06-15"
author: design-system-builder
domain: e-learning-mooc
aesthetic: "Warm-white canvas, focused indigo-blue primary, motivating amber progress accent, generous humanist type -- a system that invites study without intimidating."
density: comfortable
provenance:
  source: "github.com/nexu-io/open-design"
  license: "Apache-2.0"
  lineage_record: "p01_lin_open_design"
  method: "clean_room_concept_extraction"
  derived: "2026-06-24"
quality: null
status: DRAFT
leverage:
  feeds_kinds: [landing_page, interactive_demo, product_tour, onboarding_flow, pitch_deck, course_module]
  inject_hook: "F3 INJECT: bind Catedra tokens as the sole palette/scale/motion source; compose only from the four recipes; ease on enter, instant under reduced-motion."
  brand_config_relation: "Realizes an e-learning/MOOC brand_config identity into bindable warm-indigo tokens; brand_config selects Catedra as the active system for adult-learner surfaces."
  composes_with: [variant_shotgun_taste_loop, user_model, gdp]
  binds_8f: [F1_constrain, F3_inject]
tags: [design-system, tokens, light, humanist, e-learning, mooc, indigo, amber, leverage]
tldr: "Approachable-academic light system: warm-white canvas, focused indigo-blue primary (7.9:1), motivating amber progress (4.8:1 with dark ink), humanist sans over 1.25 scale, 8px soft corners, and calm ease-in-out motion. Conforms to p06_vs_design_system."
density_score: 0.89
related:
  - p06_vs_design_system
  - p06_ds_ferro
  - p06_ds_sereno
---

# Catedra

Conforms to [[p06_vs_design_system]]. Catedra is built for adult learners: light-first,
never glaring; indigo focus that reads as structured without feeling corporate; amber
progress that motivates without alarming. It dresses course players, lesson pages,
certificate surfaces, and MOOC dashboards.

## color

| Role | Value | Role | Value |
|------|-------|------|-------|
| `canvas` | `#F5F4F8` | `signal` | `#3D3ABA` |
| `panel` | `#FFFFFF` | `signal_ink` | `#FFFFFF` |
| `ink` | `#1F1D2E` | `affirm` | `#2A7D4F` |
| `ink_soft` | `#5C5872` | `alert` | `#B53B2C` |
| `edge` | `#D8D4E8` | `progress` | `#C97A10` |

> `progress` is a secondary status token (amber, motivating) used only in the
> progress/completion marker recipe. It is NOT a second signal: the single `signal`
> role remains indigo `#3D3ABA`. `affirm`/`alert`/`progress` are status, never accent.

## type

- `face.display`: `'Nunito', 'Trebuchet MS', ui-sans-serif, sans-serif`
- `face.text`: `'Lato', 'Segoe UI', ui-sans-serif, system-ui, sans-serif`
- `face.mono`: `'Fira Code', ui-monospace, 'Courier New', monospace`
- `scale.ratio`: `1.25` (major second -- balanced, readable, not crowded)
- `scale.steps`: `t_1 0.8 | t1 1.0 | t2 1.25 | t3 1.563 | t4 1.953 | t5 2.441 | t6 3.052` (rem)
- `weight`: `reg 400 | med 600 | bold 700`
- `leading`: `tight 1.25 | normal 1.6 | loose 1.85`

## space

- `unit`: `8px`
- `scale`: `s0 0 | s1 0.5 | s2 1 | s3 1.5 | s4 2 | s5 3 | s6 4 | s7 6` (unit multipliers -> 0/4/8/12/16/24/32/48px)

## motion

- `dur`: `instant 0ms | quick 150ms | calm 280ms`
- `ease`: `linear cubic-bezier(0,0,1,1) | standard cubic-bezier(0.25,0,0.25,1) | emphatic cubic-bezier(0.4,0,0.2,1)`
- `move`: `enter = calm+standard | exit = quick+standard | shift = quick+standard`

## form

- `radius`: `none 0 | soft 8px | full 9999px`
- `edge.width`: `1px`
- `shadow`: `flat none | raised 0 1px 3px rgba(31,29,46,0.07), 0 4px 14px rgba(31,29,46,0.06) | float 0 8px 28px rgba(31,29,46,0.13)` (cool-tinted soft elevation)

## components

| Component | Recipe |
|-----------|--------|
| `surface` | `panel` + `radius.soft 8px` + `shadow.raised` + `s5` padding (lesson card, course tile) |
| `control` | `signal` bg + `signal_ink` + `radius.soft` + `type.text/med` + `move.shift` on press (CTA, enroll button) |
| `field` | `panel` + `edge 1px` + `ink` + `radius.soft` + `s4` padding (quiz input, search) |
| `marker` | `progress #C97A10` + `ink #1F1D2E` (text) + `type.mono/t_1` + `radius.full` (progress pill, completion badge) |

## usage

1. **Contrast**: `ink #1F1D2E` on `canvas #F5F4F8` = 14.4:1; `signal_ink #FFFFFF` on
   `signal #3D3ABA` = 7.9:1; `ink #1F1D2E` on `progress #C97A10` = 4.8:1 -- all clear
   WCAG AA (text >=4.5:1, UI >=3:1). `ink_soft #5C5872` on `canvas` = 5.9:1.
2. **Reduce-motion**: collapse every `move` (including `enter`) to `dur.instant` under
   `prefers-reduced-motion`; never ease-in on reduced-motion contexts.
3. **Single signal**: indigo `#3D3ABA` only -- `affirm`/`alert`/`progress` are status
   tokens; none competes as a primary accent. One focus color across all surfaces.
4. **Progress semantics**: use `progress #C97A10` exclusively on the `marker` recipe
   (completion badge, progress bar fill, streak counter). Never apply it to CTAs,
   borders, or navigation -- it reads as motivating achievement, not interaction.
   Density: `comfortable` -- active band `s2..s7`; `s0/s1` for hairline insets only.

## CEXAI Leverage

Catedra is an ACTIVE asset, not a token dump. A builder loads exactly one design_system at
F3 INJECT and binds it as the only visual source for the surface it generates:

- **Feeds**: `landing_page`, `interactive_demo`, `product_tour`, `onboarding_flow`,
  `pitch_deck`, `course_module` -- any e-learning, MOOC, or adult-education surface
  renders in Catedra's tokens; the indigo signal frames learning intent; amber progress
  marks achievement.
- **Inject hook**: bind tokens as the sole palette/scale/motion source; compose only
  from the four recipes; ease-in on `enter`, collapse every `move` to `dur.instant`
  under reduced-motion; apply `progress` only within the `marker` recipe.
- **brand_config**: realizes an e-learning/MOOC brand identity into bindable
  warm-indigo tokens; the global `brand_config` selects Catedra as the active system
  for adult-learner product surfaces.
- **Composes with**: the variant-shotgun + taste loop (Catedra anchors the
  cool/balanced/soft/light/humanist corner), `user_model` (learner preference), and
  GDP (founder gate). Binds at F1 CONSTRAIN + F3 INJECT.
