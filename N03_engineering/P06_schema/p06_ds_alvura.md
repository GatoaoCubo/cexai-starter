---
id: p06_ds_alvura
kind: design_system
pillar: P06
nucleus: N03
title: "Alvura -- serene, clinical-calm, luminous light design system"
version: 1.0.0
created: "2026-06-15"
updated: "2026-06-15"
author: n03_builder
domain: design-systems
aesthetic: "Cool near-white canvas, generous whitespace, single calm slate-indigo accent, motion that settles -- a system built for trust, not theatre."
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
  inject_hook: "F3 INJECT: bind Alvura tokens as the sole palette/scale/motion source; compose only from the four recipes; motion settles gently, collapses to dur.instant under reduced-motion."
  brand_config_relation: "Realizes a health/SaaS/trustworthy-professional brand_config identity into bindable cool-light tokens; brand_config selects Alvura as the active system."
  composes_with: [variant_shotgun_taste_loop, user_model, gdp]
  binds_8f: [F1_constrain, F3_inject]
tags: [design-system, tokens, light, cold, humanist, clinical, leverage]
tldr: "Clinical-calm light-mode system: cool near-white canvas, one slate-indigo signal, humanist sans on a 1.25 scale, soft 8px corners, and measured motion that settles without spring. Conforms to p06_vs_design_system."
density_score: 0.89
related:
  - p06_vs_design_system
  - p06_ds_ferro
  - p06_ds_sereno
---

# Alvura

Conforms to [[p06_vs_design_system]]. Alvura (from Latin *albura* -- luminous whiteness,
the clarity of first light) holds the cold/airy/soft/light/clinical corner: where ferro
snaps and sereno springs, Alvura settles. It dresses health, SaaS, and trust-first
professional surfaces where whitespace is the primary design element.

## color

| Role | Value | Role | Value |
|------|-------|------|-------|
| `canvas` | `#F5F7F9` | `signal` | `#3F6FBE` |
| `panel` | `#FFFFFF` | `signal_ink` | `#FFFFFF` |
| `ink` | `#1A2229` | `affirm` | `#2A8062` |
| `ink_soft` | `#5C6F7D` | `alert` | `#C0443A` |
| `edge` | `#D1D8DF` | | |

## type

- `face.display`: `'Nunito', 'Trebuchet MS', ui-sans-serif, system-ui, sans-serif`
- `face.text`: `'Inter', ui-sans-serif, system-ui, sans-serif`
- `face.mono`: `'Fira Code', ui-monospace, 'Consolas', monospace`
- `scale.ratio`: `1.25` (major third -- open, unhurried, clinical-readable)
- `scale.steps`: `t_1 0.8 | t1 1.0 | t2 1.25 | t3 1.563 | t4 1.953 | t5 2.441 | t6 3.052` (rem)
- `weight`: `reg 400 | med 500 | bold 700`
- `leading`: `tight 1.3 | normal 1.6 | loose 1.9`

## space

- `unit`: `8px`
- `scale`: `s0 0 | s1 0.5 | s2 1 | s3 1.5 | s4 2 | s5 3 | s6 4 | s7 6` (unit multipliers -> 0/4/8/12/16/24/32/48px)

## motion

- `dur`: `instant 0ms | quick 120ms | calm 240ms`
- `ease`: `linear cubic-bezier(0,0,1,1) | standard cubic-bezier(0.3,0,0.1,1) | emphatic cubic-bezier(0.2,0,0.05,1)`
- `move`: `enter = calm+standard | exit = quick+standard | shift = quick+standard`

## form

- `radius`: `none 0 | soft 8px | full 8px` (Alvura avoids pills; rounded but clinical, not playful)
- `edge.width`: `1px`
- `shadow`: `flat none | raised 0 1px 3px rgba(26,34,41,0.07), 0 2px 8px rgba(26,34,41,0.05) | float 0 8px 24px rgba(26,34,41,0.10)` (cool-tinted, minimal elevation)

## components

| Component | Recipe |
|-----------|--------|
| `surface` | `panel` + `radius.soft 8px` + `shadow.raised` + `s5` padding |
| `control` | `signal` bg + `signal_ink` + `radius.soft` + `type.text/med` + `move.shift` on press |
| `field` | `panel` + `edge 1px` + `ink` + `radius.soft` + `s4` padding |
| `marker` | `signal` @ 10% tint + `type.mono/t_1` + `radius.full` |

## usage

1. **Contrast**: `ink #1A2229` on `canvas #F5F7F9` ~= 14.6:1; `signal_ink #FFFFFF` on `signal #3F6FBE` ~= 4.95:1 -- both clear WCAG AA (>= 4.5:1).
2. **Reduce-motion**: collapse every `move` to `dur.instant`; Alvura has no spring -- even calm+standard settles, not bounces -- so the fallback is imperceptible.
3. **Single signal**: slate-indigo `#3F6FBE` only -- `affirm`/`alert` are status roles, never accent competitors.
4. **Density**: `comfortable` -- active band `s2..s7`; `s0/s1` are hairline insets and icon nudges only.

## CEXAI Leverage

Alvura is an ACTIVE asset, not a token dump. A builder loads exactly one design_system at
F3 INJECT and binds it as the only visual source for the surface it generates:

- **Feeds**: `landing_page`, `interactive_demo`, `product_tour`, `onboarding_flow`, `pitch_deck`
  -- any health-tech, SaaS dashboard, or trust-first surface renders in Alvura's tokens.
- **Inject hook**: bind tokens as the sole palette/scale/motion source; compose only from the
  four recipes; motion settles (never springs) and collapses to `dur.instant` under reduced-motion.
- **brand_config**: realizes a health/SaaS/trustworthy brand identity into cool-light tokens;
  the global `brand_config` selects Alvura as the active system for that identity.
- **Composes with**: the variant-shotgun + taste loop (Alvura anchors the cold/airy/soft/light/humanist
  corner), `user_model` (founder taste), and GDP (founder gate). Binds at F1 CONSTRAIN + F3 INJECT.
