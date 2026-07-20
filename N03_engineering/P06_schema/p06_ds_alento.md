---
id: p06_ds_alento
kind: design_system
pillar: P06
nucleus: N03
title: "Alento -- warm, airy, humanist design system for nonprofit and social-impact"
version: 1.0.0
created: "2026-06-15"
author: design-system-builder
domain: nonprofit
aesthetic: "Warm white canvas, deep forest-green signal, amber warmth in affirm, airy generous type -- a system that breathes mission and invites giving."
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
  inject_hook: "F3 INJECT: bind Alento tokens as the sole palette/scale/motion source; compose only from the four recipes; enter breathes in, exit lifts out, all collapse to dur.instant under reduced-motion."
  brand_config_relation: "Realizes a nonprofit/charity/social-impact brand_config identity into bindable warm-forest tokens; brand_config selects Alento as the active system for donation and campaign surfaces."
  composes_with: [variant_shotgun_taste_loop, user_model, gdp]
  binds_8f: [F1_constrain, F3_inject]
tags: [design-system, tokens, light, warm, humanist, nonprofit, giving, leverage]
tldr: "Hopeful-giving light system: warm white canvas, deep forest-green signal, amber affirm, generous 1.25 type scale, airy 8px spacing, soft 12px corners, and breathing motion. Conforms to p06_vs_design_system."
density_score: 0.89
related:
  - p06_vs_design_system
  - p06_ds_sereno
  - p06_ds_ferro
---

# Alento

Conforms to [[p06_vs_design_system]]. Forest-green for trust, amber for hope, airy
type that breathes mission text. Dresses donation flows, campaign pages, and NGO sites
-- surfaces where every pixel must signal safety and invite giving.

## color

| Role | Value | Role | Value |
|------|-------|------|-------|
| `canvas` | `#FAF8F3` | `signal` | `#2D6A4F` |
| `panel` | `#FFFFFF` | `signal_ink` | `#F4FBF7` |
| `ink` | `#1C2B20` | `affirm` | `#B8600A` |
| `ink_soft` | `#4D6655` | `alert` | `#9B2C2C` |
| `edge` | `#DEEAE2` | | |

## type

- `face.display`: `'Lora', 'Georgia', serif`
- `face.text`: `'Nunito', ui-sans-serif, system-ui, sans-serif`
- `face.mono`: `'Fira Mono', ui-monospace, monospace`
- `scale.ratio`: `1.25` (major second -- warm, readable, not overpowering)
- `scale.steps`: `t_1 0.8 | t1 1.0 | t2 1.25 | t3 1.563 | t4 1.953 | t5 2.441 | t6 3.052` (rem)
- `weight`: `reg 400 | med 600 | bold 700`
- `leading`: `tight 1.3 | normal 1.65 | loose 1.9`

## space

- `unit`: `8px`
- `scale`: `s0 0 | s1 0.5 | s2 1 | s3 1.5 | s4 2 | s5 3 | s6 4 | s7 6` (unit multipliers -> 0/4/8/12/16/24/32/48px)

## motion

- `dur`: `instant 0ms | quick 180ms | calm 340ms`
- `ease`: `linear cubic-bezier(0,0,1,1) | standard cubic-bezier(0.35,0,0.15,1) | emphatic cubic-bezier(0.28,1.4,0.58,1)`
- `move`: `enter = calm+emphatic (lift in) | exit = quick+standard (lift out) | shift = quick+standard`

## form

- `radius`: `none 0 | soft 12px | full 9999px`
- `edge.width`: `1px`
- `shadow`: `flat none | raised 0 1px 3px rgba(28,43,32,0.07), 0 4px 14px rgba(28,43,32,0.05) | float 0 10px 36px rgba(28,43,32,0.11)`

## components

| Component | Recipe |
|-----------|--------|
| `surface` | `panel` + `radius.soft` + `shadow.raised` + `s5` padding |
| `control` | `signal` bg + `signal_ink` + `radius.soft` + `type.text/med` + `move.shift` on press |
| `field` | `panel` + `edge 1px` + `ink` + `radius.soft` + `s4` padding |
| `marker` | `signal` @ 14% tint + `type.mono/t_1` + `radius.full` |

## usage

1. **Contrast**: `ink #1C2B20` on `canvas #FAF8F3` ~= 14.5:1; `signal_ink #F4FBF7` on `signal #2D6A4F` ~= 5.6:1; `affirm #B8600A` on `canvas #FAF8F3` ~= 5.7:1 -- all clear WCAG AA.
2. **Reduce-motion**: collapse every `move` (including `emphatic` lift-in) to `dur.instant`; never spring or breathe under reduced-motion.
3. **Single signal**: forest-green `#2D6A4F` only -- `affirm` (amber) and `alert` are status, never accent; gold/amber never competes with signal.
4. **Donation-progress semantics**: progress bars and impact badges use `signal` as the fill against `edge` track; always label with a plain-language goal ("$4,200 of $6,000 raised") in `ink` at `type.text/reg`; never show a bare percentage without a milestone anchor.

## CEXAI Leverage

Alento is an ACTIVE asset, not a token dump. Builder loads it at F3 INJECT as the sole visual source:

- **Feeds**: `landing_page`, `interactive_demo`, `product_tour`, `onboarding_flow`, `pitch_deck` -- donation flows, campaign pages, NGO sites render in Alento tokens.
- **Inject hook**: bind as sole palette/scale/motion; compose from the four recipes; `enter` lifts (emphatic), `exit` lifts out; all collapse to `dur.instant` under reduced-motion.
- **brand_config**: realizes a nonprofit/charity/social-impact identity into warm-forest tokens; `brand_config` selects Alento for giving surfaces.
- **Composes with**: variant-shotgun taste loop (warm/airy/soft/giving corner), `user_model` (donor empathy), GDP (mission-owner gate). Binds F1 CONSTRAIN + F3 INJECT.
