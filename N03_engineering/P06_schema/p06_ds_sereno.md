---
id: p06_ds_sereno
kind: design_system
pillar: P06
nucleus: N03
title: "Sereno -- warm, humanist, editorial-calm design system"
version: 1.1.0
created: "2026-06-15"
updated: "2026-06-15"
author: n03_builder
domain: design-systems
aesthetic: "Paper canvas, soft corners, terracotta signal, motion that breathes and springs -- a system that feels handled, not generated."
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
  inject_hook: "F3 INJECT: bind Sereno tokens as the sole palette/scale/motion source; compose only from the four recipes; spring on enter, instant under reduced-motion."
  brand_config_relation: "Realizes an editorial/wellness/human brand_config identity into bindable warm tokens; brand_config selects Sereno as the active system."
  composes_with: [variant_shotgun_taste_loop, user_model, gdp]
  binds_8f: [F1_constrain, F3_inject]
tags: [design-system, tokens, light, warm, humanist, leverage]
tldr: "Warm light-mode system: off-white paper canvas, humanist serif display over a generous 1.333 scale, soft 10px corners, a terracotta signal, and breathing spring motion. Conforms to p06_vs_design_system."
density_score: 0.89
related:
  - p06_vs_design_system
  - p06_ds_ferro
---

# Sereno

Conforms to [[p06_vs_design_system]]. Sereno is the deliberate opposite of [[p06_ds_ferro]]:
warmth over starkness, breathing room over density, springs over snaps. It dresses
editorial, wellness, and human-facing consumer surfaces.

## color

| Role | Value | Role | Value |
|------|-------|------|-------|
| `canvas` | `#FBF7F0` | `signal` | `#A84B36` |
| `panel` | `#FFFFFF` | `signal_ink` | `#FFF9F2` |
| `ink` | `#2B2622` | `affirm` | `#4F7A55` |
| `ink_soft` | `#6E635A` | `alert` | `#B23A48` |
| `edge` | `#E7DDD0` | | |

## type

- `face.display`: `'Fraunces', 'Georgia', serif`
- `face.text`: `'Source Sans 3', ui-sans-serif, system-ui, sans-serif`
- `face.mono`: `'IBM Plex Mono', ui-monospace, monospace`
- `scale.ratio`: `1.333` (perfect fourth -- generous, editorial)
- `scale.steps`: `t_1 0.75 | t1 1.0 | t2 1.333 | t3 1.777 | t4 2.369 | t5 3.157 | t6 4.209` (rem)
- `weight`: `reg 400 | med 600 | bold 700`
- `leading`: `tight 1.2 | normal 1.6 | loose 1.85`

## space

- `unit`: `8px`
- `scale`: `s0 0 | s1 0.5 | s2 1 | s3 1.5 | s4 2 | s5 3 | s6 4 | s7 6` (unit multipliers -> 0/4/8/12/16/24/32/48px)

## motion

- `dur`: `instant 0ms | quick 160ms | calm 320ms`
- `ease`: `linear cubic-bezier(0,0,1,1) | standard cubic-bezier(0.4,0,0.2,1) | emphatic cubic-bezier(0.34,1.56,0.64,1)`
- `move`: `enter = calm+emphatic (spring in) | exit = quick+standard | shift = quick+standard`

## form

- `radius`: `none 0 | soft 10px | full 9999px` (soft corners; pills welcome)
- `edge.width`: `1px`
- `shadow`: `flat none | raised 0 1px 2px rgba(43,38,34,0.06), 0 4px 12px rgba(43,38,34,0.05) | float 0 12px 32px rgba(43,38,34,0.12)` (soft warm elevation)

## components

| Component | Recipe |
|-----------|--------|
| `surface` | `panel` + `radius.soft 10px` + `shadow.raised` (soft) + `s5` padding |
| `control` | `signal` bg + `signal_ink` + `radius.soft` + `type.text/med` + `move.shift` (spring) on press |
| `field` | `panel` + `edge 1px` + `ink` + `radius.soft` + `s4` padding |
| `marker` | `signal` @ 12% tint + `type.mono/t_1` + `radius.full` (pill) |

## usage

1. **Contrast**: `ink #2B2622` on `canvas #FBF7F0` ~= 12:1; `signal_ink #FFF9F2` on `signal #A84B36` ~= 5.1:1 -- both clear WCAG AA.
2. **Reduce-motion**: collapse every `move` (including the spring `enter`) to `dur.instant`; never spring under reduced-motion.
3. **Single signal**: terracotta `#A84B36` only -- `affirm`/`alert` are status, never accent.
4. **Density**: `comfortable` -- the active band is `s2..s7`; `s0/s1` are hairline insets only.

## CEXAI Leverage

Sereno is an ACTIVE asset, not a token dump. A builder loads exactly one design_system at
F3 INJECT and binds it as the only visual source for the surface it generates:

- **Feeds**: `landing_page`, `interactive_demo`, `product_tour`, `onboarding_flow`, `pitch_deck`
  -- any editorial, wellness, or human-facing consumer surface renders in Sereno's tokens.
- **Inject hook**: bind tokens as the sole palette/scale/motion source; compose only from the
  four recipes; spring on `enter`, and collapse every `move` to `dur.instant` under reduced-motion.
- **brand_config**: realizes an editorial/human brand identity into bindable warm tokens; the
  global `brand_config` selects Sereno as the active system for that identity.
- **Composes with**: the variant-shotgun + taste loop (Sereno anchors the warm/airy/soft/light/humanist
  corner), `user_model` (founder taste), and GDP (founder gate). Binds at F1 CONSTRAIN + F3 INJECT.
