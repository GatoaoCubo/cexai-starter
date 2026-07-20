---
id: p06_ds_fausto
kind: design_system
pillar: P06
nucleus: N03
title: "Fausto -- opulent restraint, luxury fashion e-commerce design system"
version: 1.0.0
created: "2026-06-15"
author: design-system-builder
domain: luxury-fashion
aesthetic: "Deep charcoal canvas, champagne ink, brushed-gold signal, motion that glides and suspends -- a system that whispers authority rather than announcing it."
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
  inject_hook: "F3 INJECT: bind Fausto tokens as the sole palette/scale/motion source; compose only from the four recipes; glide on enter, collapse to instant under reduced-motion."
  brand_config_relation: "Realizes a high-end boutique / couture brand_config identity into bindable dark-luxury tokens; brand_config selects Fausto as the active system for editorial product surfaces."
  composes_with: [variant_shotgun_taste_loop, user_model, gdp]
  binds_8f: [F1_constrain, F3_inject]
status: DRAFT
tags: [design-system, tokens, dark, warm, luxury, fashion, serif, editorial, leverage]
tldr: "Dark luxury system: deep charcoal canvas, champagne ink on a high-contrast serif display scale (1.414 ratio), brushed-gold signal, generous airy spacing, and slow-glide motion with soft 6px radii. Conforms to p06_vs_design_system."
density_score: 0.89
related:
  - p06_vs_design_system
  - p06_ds_ferro
  - p06_ds_sereno
---

# Fausto

Conforms to [[p06_vs_design_system]]. Fausto is opulent restraint: deep charcoal
grounds the editorial surface; champagne type breathes in generous space; a single
brushed-gold signal threads through without gilding every surface. Motion arrives
slowly and suspends before departing -- tempo fitting a garment, not a dashboard.

## color

| Role | Value | Role | Value |
|------|-------|------|-------|
| `canvas` | `#1A1714` | `signal` | `#C9A96E` |
| `panel` | `#232018` | `signal_ink` | `#1A1510` |
| `ink` | `#E8DFC4` | `affirm` | `#6FAE88` |
| `ink_soft` | `#9A9080` | `alert` | `#C4614A` |
| `edge` | `#3A342C` | | |

## type

- `face.display`: `'Cormorant Garamond', 'Didot', 'Bodoni MT', Georgia, serif`
- `face.text`: `'Jost', 'Gill Sans MT', ui-sans-serif, system-ui, sans-serif`
- `face.mono`: `'Courier Prime', ui-monospace, 'Courier New', monospace`
- `scale.ratio`: `1.414` (augmented fourth -- high contrast display for editorial)
- `scale.steps`: `t_1 0.707 | t1 1.0 | t2 1.414 | t3 2.0 | t4 2.828 | t5 4.0 | t6 5.657` (rem)
- `weight`: `reg 300 | med 400 | bold 600`
- `leading`: `tight 1.15 | normal 1.65 | loose 2.0`

## space

- `unit`: `8px`
- `scale`: `s0 0 | s1 0.5 | s2 1 | s3 2 | s4 3 | s5 5 | s6 8 | s7 13` (unit multipliers -> 0/4/8/16/24/40/64/104px)

## motion

- `dur`: `instant 0ms | quick 200ms | calm 480ms`
- `ease`: `linear cubic-bezier(0,0,1,1) | standard cubic-bezier(0.25,0.1,0.25,1) | emphatic cubic-bezier(0.16,1,0.3,1)`
- `move`: `enter = calm+emphatic (slow glide in) | exit = quick+standard | shift = quick+standard`

## form

- `radius`: `none 0 | soft 6px | full 9999px`
- `edge.width`: `1px`
- `shadow`: `flat none | raised 0 2px 8px rgba(10,8,6,0.35), 0 1px 2px rgba(10,8,6,0.25) | float 0 20px 48px rgba(10,8,6,0.55), 0 4px 12px rgba(10,8,6,0.3)` (deep warm elevation)

## components

| Component | Recipe |
|-----------|--------|
| `surface` | `panel` + `radius.soft 6px` + `shadow.raised` + `s5` padding |
| `control` | `signal` bg + `signal_ink` + `radius.soft` + `type.text/med` + `move.shift` on press |
| `field` | `panel` + `edge 1px` + `ink` + `radius.soft` + `s4` padding |
| `marker` | `signal` @ 14% tint + `type.mono/t_1` + `radius.full` (price badge / edition label) |

## usage

1. **Contrast**: `ink #E8DFC4` on `canvas #1A1714` ~= 13.4:1; `signal_ink #1A1510` on `signal #C9A96E` ~= 8.1:1 -- both clear WCAG AA. `ink_soft #9A9080` on `canvas` ~= 6.0:1 (large / UI text cleared).
2. **Reduce-motion**: collapse every `move` (including the slow `enter` glide) to `dur.instant`; never animate on motion-restricted contexts.
3. **Single signal**: brushed-gold `#C9A96E` only -- `affirm`/`alert` are status roles, never decorative accent.
4. **Density**: `comfortable` -- the active band is `s3..s7`; reserve `s1/s2` for micro-insets and hairline separators.

## CEXAI Leverage

Fausto is an ACTIVE asset, not a token dump. A builder at F3 INJECT binds it as the sole
visual source for every surface it generates:

| Field | Value |
|-------|-------|
| **Feeds** | `landing_page`, `interactive_demo`, `product_tour`, `onboarding_flow`, `pitch_deck` -- luxury boutique, jewelry, couture surfaces |
| **Inject hook** | Bind tokens as sole palette/scale/motion source; compose from four recipes; glide on `enter`; collapse to `instant` under reduced-motion |
| **brand_config** | Realizes high-end boutique/couture brand identity into dark tokens; `brand_config` selects Fausto as active system |
| **Composes with** | `variant_shotgun_taste_loop` (warm/airy/soft/dark/serif corner), `user_model`, `gdp` |
| **Binds 8F** | F1 CONSTRAIN + F3 INJECT |
