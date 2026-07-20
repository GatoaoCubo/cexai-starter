---
id: p06_ds_lamina
kind: design_system
pillar: P06
nucleus: N03
title: "Lamina -- cold compact stark light-mode devtools system for daylight sessions"
version: 1.0.0
created: "2026-06-15"
updated: "2026-06-15"
author: n03_builder
domain: design-systems
aesthetic: "Cool-grey canvas, hairline edges, one electric indigo signal, mono-first type on a tight 1.200 scale, snap motion -- blade-edge workhorse for terminals, data grids, and log tooling on bright shared screens."
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
  inject_hook: "F3 INJECT: bind Lamina tokens as sole palette/scale/motion source; four recipes only; linear snap, never spring; collapse every move to dur.instant under prefers-reduced-motion."
  brand_config_relation: "Realizes a devtools/CLI/data-engineering brand_config into compact cool-grey tokens; brand_config selects Lamina when contrast and density outweigh ornament on bright shared screens."
  composes_with: [variant_shotgun_taste_loop, user_model, gdp]
  binds_8f: [F1_constrain, F3_inject]
tags: [design-system, tokens, light, cold, compact, stark, mono, devtools, leverage]
tldr: "Cold compact stark light-mode system: cool-grey canvas, hairline edges, indigo signal, mono-first type on a 1.200 scale, zero radius default, linear snap motion. Conforms to p06_vs_design_system."
density_score: 0.90
related:
  - p06_vs_design_system
  - p06_ds_ferro
  - p06_ds_alvura
---

# Lamina

Conforms to [[p06_vs_design_system]]. Lamina (Latin: thin blade, plate, layer) holds the
cold/compact/stark/light/mono corner. [[p06_ds_ferro]] is the same temperature and density
but dark; [[p06_ds_alvura]] is cold-light but comfortable and humanist. Lamina is for
meeting rooms: terminal-precise, daylight-readable, zero decoration tax.

## color

| Role | Value | Role | Value |
|------|-------|------|-------|
| `canvas` | `#F0F2F5` | `signal` | `#2B55CC` |
| `panel` | `#FFFFFF` | `signal_ink` | `#FFFFFF` |
| `ink` | `#121820` | `affirm` | `#1B6B3A` |
| `ink_soft` | `#4A5668` | `alert` | `#B83232` |
| `edge` | `#C8CDD6` | | |

## type

- `face.display`: `'JetBrains Mono', 'Iosevka', ui-monospace, monospace`
- `face.text`: `'IBM Plex Mono', ui-monospace, monospace`
- `face.mono`: `'JetBrains Mono', 'Fira Code', ui-monospace, monospace`
- `scale.ratio`: `1.200` (minor third -- tight, tabular-readable, no headline drama)
- `scale.steps`: `t_1 0.833 | t1 1.0 | t2 1.2 | t3 1.44 | t4 1.728 | t5 2.074 | t6 2.488rem`
- `weight`: `reg 400 | med 500 | bold 700`
- `leading`: `tight 1.2 | normal 1.45 | loose 1.65`

## space

- `unit`: `4px`
- `scale`: `s0 0 | s1 1 | s2 2 | s3 3 | s4 4 | s5 6 | s6 8 | s7 12` (unit multipliers -> 0/4/8/12/16/24/32/48px)

## motion

- `dur`: `instant 0ms | quick 80ms | calm 160ms`
- `ease`: all `cubic-bezier(0,0,1,1)` -- pure linear, snap only
- `move`: `enter = calm+linear | exit = quick+linear | shift = quick+linear`

## form

- `radius`: `none 0 | soft 2px | full 3px`
- `edge.width`: `1px`
- `shadow`: `flat none | raised 0 1px 0 rgba(18,24,32,0.12) | float 0 2px 6px rgba(18,24,32,0.14), 0 1px 2px rgba(18,24,32,0.08)`

## components

| Component | Recipe |
|-----------|--------|
| `surface` | `panel` + `radius.soft 2px` + `shadow.raised` + `edge 1px` + `s4` padding |
| `control` | `signal` bg + `signal_ink` + `radius.soft 2px` + `type.text/med` + `move.shift` on press |
| `field` | `panel` + `edge 1px` + `ink` + `radius.none 0` + `s2` vertical + `s3` horizontal padding |
| `marker` | `signal` @ 10% tint + `type.mono/t_1` + `radius.soft 2px` |

## usage

1. **Contrast**: `ink #121820` on `canvas #F0F2F5` ~= 16.8:1; `signal_ink #FFFFFF` on `signal #2B55CC` ~= 6.4:1; `ink_soft #4A5668` on `canvas #F0F2F5` ~= 6.6:1 -- all WCAG AA (>= 4.5:1).
2. **Reduce-motion**: collapse every `move` to `dur.instant`; no translate, no fade under `prefers-reduced-motion`.
3. **Single signal**: indigo `#2B55CC` only -- `affirm`/`alert` are status roles, not accent; `ink_soft` is secondary text only.
4. **Density**: `compact` -- active band `s1..s5`; `s6/s7` for page gutters only; `leading.tight` default for data rows, `leading.normal` for prose.

## CEXAI Leverage

Lamina is an ACTIVE asset, not a token dump. One instance loads at F3 INJECT as the sole
visual source:

- **Feeds**: `landing_page`, `interactive_demo`, `product_tour`, `onboarding_flow`,
  `pitch_deck` -- CLI doc sites, data-grid tools, log viewers, technical surfaces that
  must read cleanly on a bright shared screen.
- **Inject hook**: sole palette/scale/motion source; four recipes only; always linear
  snap; collapse every `move` to `dur.instant` under `prefers-reduced-motion`.
- **brand_config**: realizes a devtools/CLI/data-engineering identity into compact
  cool-grey tokens; `brand_config` selects Lamina when precision and daylight legibility
  outweigh ornament.
- **Composes with**: variant-shotgun + taste loop (cold/compact/stark/light/mono corner),
  `user_model` (high-density preference), GDP (founder gate). Binds F1 + F3.
