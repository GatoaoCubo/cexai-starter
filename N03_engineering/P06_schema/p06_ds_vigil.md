---
id: p06_ds_vigil
kind: design_system
pillar: P06
nucleus: N03
title: "Vigil -- neutral-balanced geometric SaaS product-dashboard design system"
version: 1.0.0
created: "2026-06-15"
updated: "2026-06-15"
author: n03_builder
domain: design-systems
aesthetic: "Neutral grey-scale canvas, balanced density, 6-8px geometric radii, one clear teal signal, measured motion -- the dependable workhorse for data-dense product dashboards."
density: comfortable
provenance:
  source: "github.com/nexu-io/open-design"
  license: "Apache-2.0"
  lineage_record: "p01_lin_open_design"
  method: "clean_room_concept_extraction"
  derived: "2026-06-24"
quality: null
leverage:
  feeds_kinds: [landing_page, interactive_demo, product_tour, onboarding_flow, pitch_deck]
  inject_hook: "F3 INJECT: bind Vigil tokens as the sole palette/scale/motion source; compose only from the four recipes; motion is measured and purposeful, collapses to dur.instant under reduced-motion."
  brand_config_relation: "Realizes a neutral SaaS/product brand_config identity into bindable grey-scale tokens; brand_config selects Vigil as the active system for data-dense product surfaces."
  composes_with: [variant_shotgun_taste_loop, user_model, gdp]
  binds_8f: [F1_constrain, F3_inject]
tags: [design-system, tokens, light, neutral, geometric, saas, dashboard, leverage]
tldr: "Neutral-balanced light-mode workhorse: true grey-scale canvas, one teal signal, geometric sans on a 1.250 scale, 6-8px corners, balanced density, and purposeful motion. Conforms to p06_vs_design_system."
density_score: 0.90
related:
  - p06_vs_design_system
  - p06_ds_alvura
  - p06_ds_ferro
---

# Vigil

Conforms to [[p06_vs_design_system]]. Vigil (from Latin *vigilia* -- watchfulness) holds
the neutral/balanced/soft/light/geometric corner: the clear-eyed workhorse for SaaS
dashboards, data tables, admin consoles, and form-heavy surfaces where neutral means clarity.

## color

| Role | Value | Role | Value |
|------|-------|------|-------|
| `canvas` | `#F4F5F6` | `signal` | `#1A7F6E` |
| `panel` | `#FFFFFF` | `signal_ink` | `#FFFFFF` |
| `ink` | `#1C2126` | `affirm` | `#256E44` |
| `ink_soft` | `#5A6472` | `alert` | `#C94040` |
| `edge` | `#D3D8DE` | | |

## type

- `face.display`: `'DM Sans', 'IBM Plex Sans', ui-sans-serif, system-ui, sans-serif`
- `face.text`: `'Inter', 'Helvetica Neue', ui-sans-serif, system-ui, sans-serif`
- `face.mono`: `'JetBrains Mono', ui-monospace, 'Consolas', monospace`
- `scale.ratio`: `1.250` (major third -- clear hierarchy without drama; readable at data density)
- `scale.steps`: `t_1 0.8 | t1 1.0 | t2 1.25 | t3 1.563 | t4 1.953 | t5 2.441 | t6 3.052` (rem)
- `weight`: `reg 400 | med 500 | bold 600`
- `leading`: `tight 1.25 | normal 1.5 | loose 1.75`

## space

- `unit`: `8px`
- `scale`: `s0 0 | s1 0.5 | s2 1 | s3 1.5 | s4 2 | s5 3 | s6 4 | s7 6` (unit multipliers -> 0/4/8/12/16/24/32/48px)

## motion

- `dur`: `instant 0ms | quick 100ms | calm 220ms`
- `ease`: `linear cubic-bezier(0,0,1,1) | standard cubic-bezier(0.25,0,0.15,1) | emphatic cubic-bezier(0.2,0,0.05,1)`
- `move`: `enter = calm+standard | exit = quick+standard | shift = quick+standard`

## form

- `radius`: `none 0 | soft 6px | full 8px` (geometric -- tight corners for dense tables, 8px for cards)
- `edge.width`: `1px`
- `shadow`: `flat none | raised 0 1px 2px rgba(28,33,38,0.06), 0 2px 6px rgba(28,33,38,0.04) | float 0 6px 20px rgba(28,33,38,0.09)` (neutral-tinted, low-profile elevation)

## components

| Component | Recipe |
|-----------|--------|
| `surface` | `panel` + `radius.full 8px` + `shadow.raised` + `s5` padding |
| `control` | `signal` bg + `signal_ink` + `radius.soft 6px` + `type.text/med` + `move.shift` on press |
| `field` | `panel` + `edge 1px` + `ink` + `radius.soft 6px` + `s3` vertical + `s4` horizontal padding |
| `marker` | `signal` @ 12% tint + `type.mono/t_1` + `radius.full 8px` |

## usage

1. **Contrast**: `ink #1C2126` on `canvas #F4F5F6` ~= 14.9:1; `signal_ink #FFFFFF` on `signal #1A7F6E` ~= 4.88:1 -- both WCAG AA (>= 4.5:1).
2. **Reduce-motion**: collapse every `move` to `dur.instant`; no spring or bounce -- the instant fallback is imperceptible.
3. **Single signal**: teal `#1A7F6E` only -- `affirm`/`alert` are status roles, not accent competitors.
4. **Density**: `comfortable` default, band `s2..s7`; compact mode tightens to `s1..s5` + `leading.tight` for data table rows.

## CEXAI Leverage

Vigil is an ACTIVE asset, not a token dump. A builder loads it at F3 INJECT as the sole
visual source:

- **Feeds**: `landing_page`, `interactive_demo`, `product_tour`, `onboarding_flow`,
  `pitch_deck` -- the workhorse default when no aesthetic temperature is specified.
- **Inject hook**: sole palette/scale/motion source; four recipes only; motion collapses
  to `dur.instant` under reduced-motion; 6px for controls, 8px for card surfaces.
- **brand_config**: realizes a neutral/versatile/product-first SaaS brand into grey-scale
  tokens; `brand_config` selects Vigil when the brand stance is product-first.
- **Composes with**: variant-shotgun + taste loop (Vigil anchors the neutral/balanced/soft/
  light/geometric corner), `user_model` (density pref), GDP (gate). Binds F1 + F3.
