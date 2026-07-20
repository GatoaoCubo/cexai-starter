---
id: p06_ds_termas
kind: design_system
pillar: P06
nucleus: N03
title: "Termas -- cool, airy, restorative spa-wellness design system"
version: 1.0.0
created: "2026-06-15"
author: design-system-builder
domain: spa-wellness
aesthetic: "Warm-white canvas, eucalyptus signal, stone-warm accents, humanist letterforms, unhurried motion -- a system that feels like stepping into a thermal hall."
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
  feeds_kinds: [landing_page, interactive_demo, product_tour, onboarding_flow, pitch_deck]
  inject_hook: "F3 INJECT: bind Termas tokens as the sole palette/scale/motion source; compose only from the four recipes; motion settles (calm+standard), never springs, collapses to dur.instant under reduced-motion."
  brand_config_relation: "Realizes a spa/thermal-wellness brand_config identity into bindable cool-airy tokens; brand_config selects Termas as the active system."
  composes_with: [variant_shotgun_taste_loop, user_model, gdp]
  binds_8f: [F1_constrain, F3_inject]
tags: [design-system, tokens, light, spa, wellness, eucalyptus, thermal, leverage]
tldr: "Cool-airy light-mode system: warm-white canvas, eucalyptus-green signal, warm-stone edge accent, humanist sans display on a 1.25 scale, generous 8px-base spacing, calm settling motion, and soft rounded form. Conforms to p06_vs_design_system."
density_score: 0.89
related:
  - p06_vs_design_system
  - p06_ds_ferro
  - p06_ds_sereno
---

# Termas

Conforms to [[p06_vs_design_system]]. Termas occupies the cool/airy/soft/LIGHT-first corner:
distinct from [[p06_ds_sereno]] (warm/terracotta/spring) and [[p06_ds_ferro]] (dark/snap/compact).
It dresses spa, thermal-bath, and wellness-retreat surfaces -- hushed, restorative, unhurried.

## color

| Role | Value | Role | Value |
|------|-------|------|-------|
| `canvas` | `#F5F1EC` | `signal` | `#2E6B55` |
| `panel` | `#FDFCFA` | `signal_ink` | `#EEF8F4` |
| `ink` | `#2C2926` | `affirm` | `#3A7E62` |
| `ink_soft` | `#6B6158` | `alert` | `#9B3A36` |
| `edge` | `#C4A882` | | |

## type

- `face.display`: `'Nunito Sans', 'Gill Sans MT', ui-sans-serif, sans-serif`
- `face.text`: `'Lato', ui-sans-serif, system-ui, sans-serif`
- `face.mono`: `'Fira Code', ui-monospace, 'Courier New', monospace`
- `scale.ratio`: `1.25` (major second -- airy, not cramped, not editorial-wide)
- `scale.steps`: `t_1 0.8 | t1 1.0 | t2 1.25 | t3 1.563 | t4 1.953 | t5 2.441 | t6 3.052` (rem)
- `weight`: `reg 400 | med 500 | bold 700`
- `leading`: `tight 1.3 | normal 1.65 | loose 1.9`

## space

- `unit`: `8px`
- `scale`: `s0 0 | s1 0.5 | s2 1 | s3 1.5 | s4 2 | s5 3 | s6 5 | s7 8` (unit multipliers -> 0/4/8/12/16/24/40/64px)

## motion

- `dur`: `instant 0ms | quick 150ms | calm 300ms`
- `ease`: `linear cubic-bezier(0,0,1,1) | standard cubic-bezier(0.4,0,0.2,1) | emphatic cubic-bezier(0.2,0,0,1)`
- `move`: `enter = calm+standard (settle in) | exit = quick+standard | shift = quick+standard`

## form

- `radius`: `none 0 | soft 8px | full 9999px`
- `edge.width`: `1px`
- `shadow`: `flat none | raised 0 1px 3px rgba(44,41,38,0.07), 0 4px 14px rgba(44,41,38,0.06) | float 0 10px 28px rgba(44,41,38,0.11)` (soft cool elevation)

## components

| Component | Recipe |
|-----------|--------|
| `surface` | `panel` + `radius.soft 8px` + `shadow.raised` + `s5` padding |
| `control` | `signal` bg + `signal_ink` + `radius.soft` + `type.text/med` + `move.shift` on press |
| `field` | `panel` + `edge 1px` + `ink` + `radius.soft` + `s4` padding |
| `marker` | `signal` @ 14% tint + `type.mono/t_1` + `radius.full` (pill) |

## usage

1. **Contrast**: `ink #2C2926` on `canvas #F5F1EC` ~= 12.97:1; `signal_ink #EEF8F4` on `signal #2E6B55` ~= 8.23:1; `ink_soft #6B6158` on `canvas` ~= 4.66:1 -- all clear WCAG AA.
2. **Reduce-motion**: collapse every `move` to `dur.instant`; Termas never springs; the calm settle also fades to zero.
3. **Single signal**: eucalyptus `#2E6B55` only -- `affirm`/`alert` are status; `edge #C4A882` is stone-warm decoration, never an accent role.
4. **Density**: `comfortable` -- the active band is `s2..s7`; `s0/s1` are hairline insets and micro-gaps only.

## CEXAI Leverage

Termas is an ACTIVE asset, not a token dump. A builder loads exactly one design_system at
F3 INJECT and binds it as the only visual source for the surface it generates:

- **Feeds**: `landing_page`, `interactive_demo`, `product_tour`, `onboarding_flow`, `pitch_deck`
  -- any spa, thermal-wellness, or retreat surface renders in Termas tokens.
- **Inject hook**: bind tokens as the sole palette/scale/motion source; compose only from the
  four recipes; motion settles (calm+standard), never springs, and collapses to `dur.instant`
  under `prefers-reduced-motion`.
- **brand_config**: realizes a thermal-wellness brand identity into cool-airy bindable tokens;
  the global `brand_config` selects Termas as the active system for that identity.
- **Composes with**: variant-shotgun + taste loop (Termas anchors the cool/airy/soft/LIGHT-first/
  humanist corner -- distinct from Sereno warm and Ferro dark), `user_model` (founder taste),
  GDP (founder gate). Binds at F1 CONSTRAIN + F3 INJECT.
