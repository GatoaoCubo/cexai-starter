---
id: p06_ds_morada
kind: design_system
pillar: P06
nucleus: N03
title: "Morada -- warm, airy, humanist design system for real estate"
version: 1.0.0
created: "2026-06-15"
author: design-system-builder
domain: real-estate
aesthetic: "Soft-white canvas, warm taupe structure, sage-green signal, spacious leading -- a system that says home, not transaction."
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
  inject_hook: "F3 INJECT: bind Morada tokens as the sole palette/scale/motion source; compose only from the four recipes; settle on enter, collapse to instant under reduced-motion."
  brand_config_relation: "Realizes a real-estate/home brand_config identity into bindable warm-taupe tokens; brand_config selects Morada as the active system for that brand."
  composes_with: [variant_shotgun_taste_loop, user_model, gdp]
  binds_8f: [F1_constrain, F3_inject]
tags: [design-system, tokens, light, warm, humanist, real-estate, leverage]
tldr: "Airy light-mode system for property/home surfaces: soft-white canvas, warm taupe panel, sage-green signal, humanist serif display on a 1.250 scale, generous 8px spacing, soft 12px corners, and calm settling motion. Conforms to p06_vs_design_system."
density_score: 0.89
related:
  - p06_vs_design_system
  - p06_ds_ferro
  - p06_ds_sereno
---

# Morada

Conforms to [[p06_vs_design_system]]. Morada means dwelling -- warmth before efficiency,
openness before density. Taupe grounds; sage signals without shouting; space breathes.
Dresses property listing, agent, and home-search surfaces.

## color

| Role | Value | Role | Value |
|------|-------|------|-------|
| `canvas` | `#FAFAF7` | `signal` | `#4F7A55` |
| `panel` | `#FFFFFF` | `signal_ink` | `#FAFAF7` |
| `ink` | `#302820` | `affirm` | `#3A7D5C` |
| `ink_soft` | `#6E6358` | `alert` | `#A8382A` |
| `edge` | `#DDD5C8` | | |

## type

- `face.display`: `'Canela', 'Palatino Linotype', Georgia, serif`
- `face.text`: `'Atkinson Hyperlegible', ui-sans-serif, system-ui, sans-serif`
- `face.mono`: `'Fira Code', ui-monospace, monospace`
- `scale.ratio`: `1.250` (major third -- spacious, readable)
- `scale.steps`: `t_1 0.8 | t1 1.0 | t2 1.25 | t3 1.563 | t4 1.953 | t5 2.441 | t6 3.052` (rem)
- `weight`: `reg 400 | med 500 | bold 650`
- `leading`: `tight 1.25 | normal 1.65 | loose 1.9`

## space

- `unit`: `8px`
- `scale`: `s0 0 | s1 0.5 | s2 1 | s3 1.5 | s4 2 | s5 3 | s6 4 | s7 6` (unit multipliers -> 0/4/8/12/16/24/32/48px)

## motion

- `dur`: `instant 0ms | quick 150ms | calm 300ms`
- `ease`: `linear cubic-bezier(0,0,1,1) | standard cubic-bezier(0.4,0,0.2,1) | emphatic cubic-bezier(0.22,1,0.36,1)`
- `move`: `enter = calm+emphatic (settle in) | exit = quick+standard | shift = quick+standard`

## form

- `radius`: `none 0 | soft 12px | full 9999px`
- `edge.width`: `1px`
- `shadow`: `flat none | raised 0 1px 3px rgba(48,40,32,0.07), 0 4px 14px rgba(48,40,32,0.05) | float 0 16px 40px rgba(48,40,32,0.11)` (warm diffuse elevation)

## components

| Component | Recipe |
|-----------|--------|
| `surface` (property card) | `panel` + `radius.soft 12px` + `shadow.raised` + `s5` padding; listing image fills top 56% of card |
| `control` (CTA button) | `signal` bg + `signal_ink` + `radius.soft` + `type.text/med` + `move.shift` on press |
| `field` (search input) | `panel` + `edge 1px` + `ink` + `radius.soft` + `s4` padding |
| `marker` (price/feature badge) | `signal` @ 10% tint + `type.mono/t_1` + `radius.full` (pill) |

## usage

1. **Contrast**: `ink #302820` on `canvas #FAFAF7` ~= 12.8:1; `signal_ink #FAFAF7` on `signal #4F7A55` ~= 4.68:1 -- both clear WCAG AA (>=4.5:1). `ink_soft #6E6358` on `canvas` ~= 5.2:1 (large/UI text, clears 3:1 large and 4.5:1 normal).
2. **Reduce-motion**: collapse every `move` (including the `emphatic` settle on `enter`) to `dur.instant`; never animate under `prefers-reduced-motion`.
3. **Single signal**: sage `#4F7A55` only -- `affirm`/`alert` are status roles, never accent competitors.
4. **Density**: `comfortable` -- active band is `s2..s7`; `s0/s1` are inset hairlines only.

## CEXAI Leverage

Morada is an ACTIVE asset, not a token dump. A builder loads exactly one design_system at
F3 INJECT and binds it as the only visual source for the surface it generates:

- **Feeds**: `landing_page`, `interactive_demo`, `product_tour`, `onboarding_flow`, `pitch_deck` -- property listing, agent bio, home-search surfaces.
- **Inject hook**: bind tokens as sole palette/scale/motion source; compose only from the four recipes; `enter` settles (calm+emphatic); every `move` collapses to `dur.instant` under reduced-motion.
- **brand_config**: realizes a real-estate/home brand identity into bindable warm-taupe tokens; `brand_config` selects Morada as the active system.
- **Composes with**: variant-shotgun + taste loop (Morada anchors warm/airy/soft/light/humanist corner), `user_model` (buyer/seller taste), GDP (brand gate). Binds at F1 CONSTRAIN + F3 INJECT.
