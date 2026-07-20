---
id: p06_ds_grafeno
kind: design_system
pillar: P06
nucleus: N03
title: "Grafeno -- neutral, compact, soft-geometric, dark dataviz design system"
version: 1.0.0
created: "2026-06-15"
updated: "2026-06-15"
author: n03_builder
domain: design-systems
aesthetic: "Graphite-slate canvas, data-dense compact grid, soft 3px geometric radii, single acid-green signal, motion that pulses then steadies -- a system built for charts, not decoration."
density: compact
provenance:
  source: "github.com/nexu-io/open-design"
  license: "Apache-2.0"
  lineage_record: "p01_lin_open_design"
  method: "clean_room_concept_extraction"
  derived: "2026-06-24"
quality: null
leverage:
  feeds_kinds: [landing_page, interactive_demo, product_tour, onboarding_flow, pitch_deck]
  inject_hook: "F3 INJECT: bind Grafeno tokens as the sole palette/scale/motion source; compose only from the four recipes; pulse on data-change, collapse to instant under reduced-motion."
  brand_config_relation: "Realizes a dataviz/science/research brand_config identity into bindable dark neutral tokens; brand_config selects Grafeno for data-dense product surfaces."
  composes_with: [variant_shotgun_taste_loop, user_model, gdp]
  binds_8f: [F1_constrain, F3_inject]
tags: [design-system, tokens, dark, neutral, geometric, compact, dataviz, science, leverage]
tldr: "Dark neutral compact system: graphite-slate canvas, 4px grid on a 1.25 scale, soft 3px geometric radii, single acid-green signal, pulse-then-steady motion. For dataviz and science consoles. Conforms to p06_vs_design_system."
density_score: 0.91
related:
  - p06_vs_design_system
  - p06_ds_ferro
  - p06_ds_vigil
---

# Grafeno

Conforms to [[p06_vs_design_system]]. Named after graphene -- the atom-thin data-conducting
lattice. Dresses science dashboards, research consoles, and dataviz-heavy surfaces where
information density is the primary constraint. Distinct from [[p06_ds_ferro]]
(zero radius, snap, teal, near-black mono) and [[p06_ds_vigil]] (light, balanced).

## color

| Role | Value | Role | Value |
|------|-------|------|-------|
| `canvas` | `#141820` | `signal` | `#39E87A` |
| `panel` | `#1E2330` | `signal_ink` | `#071A0F` |
| `ink` | `#D9DDE8` | `affirm` | `#4ADE80` |
| `ink_soft` | `#6B7491` | `alert` | `#F05A5A` |
| `edge` | `#2C3347` | | |

## type

- `face.display`: `'DM Sans', 'Inter', 'Arial', sans-serif`
- `face.text`: `'DM Sans', ui-sans-serif, system-ui, sans-serif`
- `face.mono`: `'DM Mono', ui-monospace, 'Courier New', monospace`
- `scale.ratio`: `1.25` (major second, tight, data-precise)
- `scale.steps`: `t_1 0.8 | t1 1.0 | t2 1.25 | t3 1.563 | t4 1.953 | t5 2.441 | t6 3.052` rem
- `weight`: `reg 400 | med 500 | bold 600`
- `leading`: `tight 1.15 | normal 1.5 | loose 1.75`

## space

- `unit`: `4px`
- `scale`: `s0 0 | s1 1 | s2 2 | s3 3 | s4 4 | s5 5 | s6 8 | s7 12` (0/4/8/12/16/20/32/48px)

## motion

- `dur`: `instant 0ms | quick 100ms | calm 220ms`
- `ease`: `linear cubic-bezier(0,0,1,1) | standard cubic-bezier(0.3,0,0.1,1) | emphatic cubic-bezier(0.0,0,0.2,1)`
- `move`: `enter = calm+emphatic (expand from center) | exit = quick+linear (fade-collapse) | shift = quick+standard (data pulse)`

## form

- `radius`: `none 0 | soft 3px | full 9999px`; `edge.width`: `1px`
- `shadow`: `flat none | raised 0 0 0 1px var(edge) | float 0 6px 20px rgba(0,0,0,.45), 0 0 0 1px var(edge)`

## components

| Component | Recipe |
|-----------|--------|
| `surface` | `panel` + `radius.soft` + `shadow.raised` + `s4` padding |
| `control` | `signal` bg + `signal_ink` + `radius.soft` + `type.text/med` + `move.shift` on press |
| `field` | `panel` + `edge 1px` + `ink` + `radius.soft` + `s3` padding |
| `marker` | `signal` @ 14% tint + `type.mono/t_1` + `radius.full` |

## usage

1. **Contrast**: `ink #D9DDE8` on `canvas #141820` ~= 9.8:1; `signal_ink #071A0F` on `signal #39E87A` ~= 7.2:1 -- both exceed WCAG AA 4.5:1 floor.
2. **Reduce-motion**: collapse every `move` (including the data-pulse `shift`) to `dur.instant`.
3. **Single signal**: acid-green `#39E87A` only -- `affirm` is a status role (success state), never a second accent; `alert` is error/threshold only.
4. **Density**: `compact` -- active band `s1..s5`; `s6/s7` for section gutters only; charts and grids use `s2/s3` padding.

## CEXAI Leverage

Grafeno is an ACTIVE asset, not a token dump. One design_system loads at F3 INJECT
and binds as the sole visual source for the surface being generated:

- **Feeds**: dataviz, science, and research-console surfaces; charts and data tables inherit
  the compact scale and acid-green signal as the active-data marker.
- **Inject hook**: bind tokens as sole palette/scale/motion source; compose from the four
  recipes; pulse on data-change (shift), instant under reduced-motion.
- **brand_config**: selects Grafeno for dark-mode dataviz product identities.
- **Composes with**: variant-shotgun + taste loop (neutral/compact/soft/dark/geometric corner),
  `user_model`, GDP. Binds at F1 CONSTRAIN + F3 INJECT.

## Related Artifacts

| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[p06_vs_design_system]] | upstream | 0.60 |
| [[p06_ds_ferro]] | sibling | 0.42 |
| [[p06_ds_vigil]] | sibling | 0.42 |
