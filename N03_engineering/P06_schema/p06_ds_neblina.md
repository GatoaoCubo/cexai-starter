---
id: p06_ds_neblina
kind: design_system
pillar: P06
nucleus: N03
title: "Neblina -- cold misty-dark dashboard system for long reading sessions"
version: 1.0.0
created: "2026-06-15"
updated: "2026-06-15"
author: n03_builder
domain: design-systems
aesthetic: "Deep blue-grey surfaces, icy periwinkle signal, humanist sans, and fog-settle motion -- calm and readable for long dark-mode sessions."
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
  inject_hook: "F3 INJECT: bind Neblina tokens as sole palette/scale/motion source; compose from the four recipes; fog-settle on enter, recede on exit, collapse every move to dur.instant under prefers-reduced-motion."
  brand_config_relation: "Realizes a calm/analytical/dark-first brand_config into cold blue-grey tokens; brand_config selects Neblina as the active system for dashboard and data-dense surfaces."
  composes_with: [variant_shotgun_taste_loop, user_model, gdp]
  binds_8f: [F1_constrain, F3_inject]
tags: [design-system, tokens, dark, cold, humanist, soft, dashboard, airy, leverage]
tldr: "Cold dark humanist system: blue-grey canvas, icy periwinkle signal, humanist sans on perfect-fourth scale, soft corners, fog-settle motion. Conforms to p06_vs_design_system."
density_score: null
related:
  - p06_vs_design_system
  - p06_ds_ferro
  - p06_ds_sereno
  - p06_ds_vespera
---

# Neblina

Conforms to [[p06_vs_design_system]]. Neblina occupies the cold-dark-airy-soft-humanist corner --
distinct from [[p06_ds_ferro]] (cold/compact/stark/mono), [[p06_ds_sereno]] (warm/airy/light/humanist),
and [[p06_ds_vespera]] (warm/dark/soft/serif). It dresses dashboard and data-dense surfaces: cool,
spacious, and legible through hours of continuous dark-mode use.

## color

| Role | Value | Role | Value |
|------|-------|------|-------|
| `canvas` | `#1A1F2E` | `signal` | `#7B9FE8` |
| `panel` | `#222840` | `signal_ink` | `#0D1325` |
| `ink` | `#D4DCF0` | `affirm` | `#5BA88A` |
| `ink_soft` | `#7D8BA8` | `alert` | `#C46A6A` |
| `edge` | `#2E3650` | | |

## type

- `face.display`: `'Jost', 'Nunito', 'Trebuchet MS', sans-serif`
- `face.text`: `'Inter', 'Source Sans 3', 'Segoe UI', system-ui, sans-serif`
- `face.mono`: `'Iosevka', 'Cascadia Code', ui-monospace, monospace`
- `scale.ratio`: `1.333` (perfect fourth -- generous but structured)
- `scale.steps`: `t_1 0.75 | t1 1.0 | t2 1.333 | t3 1.777 | t4 2.369 | t5 3.157 | t6 4.209` (rem)
- `weight`: `reg 400 | med 500 | bold 650`
- `leading`: `tight 1.25 | normal 1.6 | loose 1.9`

## space

- `unit`: `8px`
- `scale`: `s0 0 | s1 0.5 | s2 1 | s3 2 | s4 3 | s5 4 | s6 6 | s7 8` (unit multipliers -> 0/4/8/16/24/32/48/64px)

## motion

- `dur`: `instant 0ms | quick 150ms | calm 320ms`
- `ease`: `linear cubic-bezier(0,0,1,1) | standard cubic-bezier(0.25,0.1,0.25,1) | emphatic cubic-bezier(0.2,0.9,0.4,1)`
- `move`: `enter = calm+emphatic (fog-settle: opacity 0->1, translate -6px->0) | exit = quick+standard (recede) | shift = quick+standard`

## form

- `radius`: `none 0 | soft 10px | full 9999px`
- `edge.width`: `1px`
- `shadow`: `flat none | raised 0 2px 10px rgba(10,13,26,0.55),0 1px 3px rgba(10,13,26,0.35) | float 0 12px 40px rgba(10,13,26,0.7),0 2px 8px rgba(10,13,26,0.45)`

## components

| Component | Recipe |
|-----------|--------|
| `surface` | `panel` + `radius.soft 10px` + `shadow.raised` + `s4` padding |
| `control` | `signal` bg + `signal_ink` + `radius.soft` + `type.text/med` + `move.shift` on press |
| `field` | `panel` + `edge 1px` + `ink` + `radius.soft` + `s3` padding |
| `marker` | `signal` @ 15% tint + `type.mono/t_1` + `radius.full` (pill) |

## usage

1. **Contrast**: `ink #D4DCF0` on `canvas #1A1F2E` ~= 9.3:1; `signal_ink #0D1325` on `signal #7B9FE8` ~= 6.7:1 -- both clear WCAG AA (>= 4.5:1).
2. **Reduce-motion**: collapse every `move` to `dur.instant`; no translate, no fade under `prefers-reduced-motion`.
3. **Single signal**: icy periwinkle `#7B9FE8` only -- `affirm`/`alert` are status roles, not accent; `ink_soft` is text-secondary only.
4. **Density**: `comfortable` -- reading band `s3..s6`; line measure 65-80ch; `s0/s1` for tight insets in data-dense cells only.

## CEXAI Leverage

Neblina is an ACTIVE asset, not a token dump. One design_system loads at F3 INJECT as
the sole visual source:

- **Feeds**: `landing_page`, `interactive_demo`, `product_tour`, `onboarding_flow`, `pitch_deck`
  -- any calm, data-dense, or long-session dark surface renders in Neblina tokens.
- **Inject hook**: bind tokens as sole palette/scale/motion source; compose from the four recipes;
  fog-settle on `enter`, recede on `exit`, collapse every `move` to `dur.instant` under reduced-motion.
- **brand_config**: realizes a calm/analytical/dark-first brand identity into cold blue-grey tokens;
  `brand_config` selects Neblina for dashboard surfaces.
- **Composes with**: variant-shotgun + taste loop (cold/dark/soft/airy/humanist corner),
  `user_model` (long-session reader), GDP (founder gate). Binds at F1 CONSTRAIN + F3 INJECT.
