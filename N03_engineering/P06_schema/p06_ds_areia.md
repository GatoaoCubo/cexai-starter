---
id: p06_ds_areia
kind: design_system
pillar: P06
nucleus: N03
title: "Areia -- neutral, compact, light-mode geometric civic design system"
version: 1.0.0
created: "2026-06-15"
updated: "2026-06-15"
author: n03_builder
domain: design-systems
aesthetic: "Warm sand canvas, prussian-blue civic signal, geometric sans on a minor-third scale, soft rounded edges, and a measured glide motion -- authority without coldness, precision without distance."
density: compact
provenance:
  source: "github.com/nexu-io/open-design"
  license: "Apache-2.0"
  lineage_record: "p01_lin_open_design"
  method: "clean_room_concept_extraction"
  derived: "2026-06-24"
quality: null
leverage:
  feeds_kinds: [landing_page, interactive_demo, onboarding_flow, product_tour, pitch_deck]
  inject_hook: "F3 INJECT: bind Areia tokens as the sole palette/scale/motion source; compose only from the four recipes; glide in, fade out, collapse every move to dur.instant under prefers-reduced-motion."
  brand_config_relation: "Realizes a civic/government/public-services brand_config identity into neutral warm-sand tokens with prussian-blue authority signal; brand_config selects Areia as the active system for institutional and civic-facing surfaces."
  composes_with: [variant_shotgun_taste_loop, user_model, gdp]
  binds_8f: [F1_constrain, F3_inject]
tags: [design-system, tokens, light, neutral, geometric, compact, civic, leverage]
tldr: "Neutral compact light-mode system: warm sand canvas, prussian-blue signal, geometric sans on a 1.25 scale, soft 6px corners, measured glide motion. Civic/govtech domain. Conforms to p06_vs_design_system."
density_score: null
related:
  - p06_vs_design_system
  - p06_ds_sereno
  - p06_ds_ferro
---

# Areia

Conforms to [[p06_vs_design_system]]. Areia (sand) is a neutral, compact, geometric system for civic and public-service surfaces:
government portals, civic-tech platforms, institutional dashboards. Authority without coldness;
legible under strict a11y scrutiny. Distinct from [[p06_ds_sereno]] (warm/humanist/editorial)
and [[p06_ds_ferro]] (stark/mono/dark). De-saturated palette: status tokens carry full signal.

## color

| Role | Value | Role | Value |
|------|-------|------|-------|
| `canvas` | `#F5F3EE` | `signal` | `#1B4F8A` |
| `panel` | `#FFFFFF` | `signal_ink` | `#F5F3EE` |
| `ink` | `#1A1A2E` | `affirm` | `#2D6A4F` |
| `ink_soft` | `#5C5C70` | `alert` | `#C0392B` |
| `edge` | `#D9D5CC` | | |

## type

- `face.display`: `'DM Sans', 'Inter', ui-sans-serif, sans-serif`
- `face.text`: `'DM Sans', 'Inter', ui-sans-serif, sans-serif`
- `face.mono`: `'JetBrains Mono', ui-monospace, monospace`
- `scale.ratio`: `1.25` (minor third -- compact, legible, institutional)
- `scale.steps`: `t_1 0.8 | t1 1.0 | t2 1.25 | t3 1.563 | t4 1.953 | t5 2.441 | t6 3.052` rem
- `weight`: `reg 400 | med 500 | bold 700`
- `leading`: `tight 1.25 | normal 1.5 | loose 1.75`

## space

- `unit`: `8px`
- `scale`: `s0 0 | s1 .5 | s2 1 | s3 1.5 | s4 2 | s5 3 | s6 4 | s7 6` (unit multipliers -> 0/4/8/12/16/24/32/48px)

## motion

- `dur`: `instant 0ms | quick 120ms | calm 240ms`
- `ease`: `linear cubic-bezier(0,0,1,1) | standard cubic-bezier(0.4,0,0.2,1) | emphatic cubic-bezier(0.2,0,0,1)`
- `move`: `enter = calm+standard (glide in) | exit = quick+standard (fade) | shift = quick+standard`

## form

- `radius`: `none 0 | soft 6px | full 9999px`
- `edge.width`: `1px`
- `shadow`: `flat none | raised 0 1px 3px rgba(26,26,46,.08), 0 2px 8px rgba(26,26,46,.06) | float 0 8px 24px rgba(26,26,46,.12)`

## components

| Component | Recipe |
|-----------|--------|
| `surface` | `panel` bg + `radius.soft 6px` + `shadow.raised` + `s4` padding |
| `control` | `signal` bg + `signal_ink` + `radius.soft` + `type.text/med` + `move.shift` on press |
| `field` | `panel` bg + `edge 1px` border + `ink` text + `radius.soft` + `s3` padding |
| `marker` | `signal` @ 12% tint bg + `signal` text + `type.mono/t_1` + `radius.full` (pill) |

## usage

1. **Contrast**: `ink #1A1A2E` on `canvas #F5F3EE` ~16:1; `signal_ink #F5F3EE` on `signal #1B4F8A` ~9:1 -- WCAG AA + AAA.
2. **Reduce-motion**: collapse `enter`/`exit`/`shift` to `dur.instant`; no glide under `prefers-reduced-motion`.
3. **Single signal**: prussian `#1B4F8A` only -- `affirm`/`alert` are status, never accent replacements.
4. **Density**: `compact` -- active band `s2..s5`; `s6/s7` layout-level only.

## CEXAI Leverage

Areia is an ACTIVE asset, not a token dump. Load exactly one design_system at F3 INJECT;
bind its tokens as the only visual source for the surface being generated:

- **Feeds**: `landing_page`, `interactive_demo`, `onboarding_flow`, `product_tour`, `pitch_deck`
  -- any civic or institutional surface renders in Areia tokens.
- **Inject hook**: sole palette/scale/motion source; four recipes only; glide `enter`,
  fade `exit`, collapse every `move` to `dur.instant` under `prefers-reduced-motion`.
- **brand_config**: realizes civic/government identity into warm-sand + prussian-blue tokens;
  `brand_config` selects Areia as the active system for institutional surfaces.
- **Composes with**: variant-shotgun + taste loop (neutral/compact/soft/light/geometric corner),
  `user_model` (institutional persona), GDP (a11y gate). Binds at F1 CONSTRAIN + F3 INJECT.
