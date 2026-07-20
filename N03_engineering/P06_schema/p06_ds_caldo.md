---
id: p06_ds_caldo
kind: design_system
pillar: P06
nucleus: N03
title: "Caldo -- warm, airy, geometric consumer-light design system"
version: 1.0.0
created: "2026-06-15"
updated: "2026-06-15"
author: n03_builder
domain: design-systems
aesthetic: "Sun-warmed parchment ground, generous air, rounded-square geometry, single terracotta signal, motion that breathes -- friendly precision without a single borrowed curve."
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
  inject_hook: "F3 INJECT: bind Caldo tokens as the sole palette/scale/motion source; compose only from the four recipes; breathe on enter, instant under reduced-motion."
  brand_config_relation: "Realizes a warm consumer or lifestyle brand_config identity into bindable geometric-soft tokens; brand_config selects Caldo for approachable-but-precise surfaces."
  composes_with: [variant_shotgun_taste_loop, user_model, gdp]
  binds_8f: [F1_constrain, F3_inject]
tags: [design-system, tokens, warm, light, geometric, airy, consumer, leverage]
tldr: "Warm airy light-mode system: parchment-tinted canvas, rounded-square 4px radius, geometric grotesque on a 1.45 scale, single terracotta signal, and breath-in motion. Conforms to p06_vs_design_system."
density_score: 0.91
related:
  - p06_vs_design_system
  - p06_ds_ferro
  - p06_ds_sereno
  - p06_ds_vacuo
---

# Caldo

Conforms to [[p06_vs_design_system]]. Caldo is warmth held in structure: parchment ground lit from within, air between every element, geometry that rounds just enough to feel human. It dresses consumer, lifestyle, and brand-forward surfaces -- approachable yet precise, never soft to the point of shapeless. Distinct from [[p06_ds_vacuo]] (cold/hard-edge), [[p06_ds_sereno]] (humanist serif), [[p06_ds_alvura]] (clinical cold).

## color

| Role | Value | Role | Value |
|------|-------|------|-------|
| `canvas` | `#FBF6F0` | `signal` | `#B34D18` |
| `panel` | `#FFFFFF` | `signal_ink` | `#FFFFFF` |
| `ink` | `#2B2118` | `affirm` | `#2A7A4B` |
| `ink_soft` | `#7A6455` | `alert` | `#B83232` |
| `edge` | `#E8DDD3` | | |

## type

- `face.display`: `'Plus Jakarta Sans', 'Inter', 'Helvetica Neue', sans-serif`
- `face.text`: `'Plus Jakarta Sans', ui-sans-serif, system-ui, sans-serif`
- `face.mono`: `'JetBrains Mono', ui-monospace, 'Courier New', monospace`
- `scale.ratio`: `1.45` (mid-fifth -- warm hierarchy, not austere)
- `scale.steps`: `t_1 0.690 | t1 1.0 | t2 1.45 | t3 2.103 | t4 3.049 | t5 4.421 | t6 6.410` (rem)
- `weight`: `reg 400 | med 500 | bold 700`
- `leading`: `tight 1.2 | normal 1.6 | loose 1.85`

## space

- `unit`: `8px`
- `scale`: `s0 0 | s1 0.5 | s2 1 | s3 1.5 | s4 2 | s5 3 | s6 4 | s7 6` (unit multipliers -> 0/4/8/12/16/24/32/48px)

## motion

- `dur`: `instant 0ms | quick 140ms | calm 260ms`
- `ease`: `linear cubic-bezier(0,0,1,1) | standard cubic-bezier(0.25,0,0.1,1) | emphatic cubic-bezier(0.0,0.8,0.2,1)`
- `move`: `enter = calm+emphatic (breath in) | exit = quick+standard | shift = quick+standard`

## form

- `radius`: `none 0 | soft 4px | full 9999px`
- `edge.width`: `1px`
- `shadow`: `flat none | raised 0 1px 3px #2B211814 | float 0 4px 12px #2B211820`

## components

| Component | Recipe |
|-----------|--------|
| `surface` | `panel` + `radius.soft` + `shadow.raised` + `s4` padding |
| `control` | `signal` bg + `signal_ink` + `radius.soft` + `type.text/med` + `move.shift` on press |
| `field` | `panel` + `edge 1px` + `ink` + `radius.soft` + `s3` padding |
| `marker` | `signal` @ 12% tint + `type.mono/t_1` + `radius.full` (pill label) |

## usage

1. **Contrast**: `ink #2B2118` on `canvas #FBF6F0` ~= 13.4:1; `signal_ink #FFFFFF` on `signal #B34D18` ~= 5.05:1 -- both clear WCAG AA.
2. **Reduce-motion**: collapse every `move` to `dur.instant`; the breath-in enter becomes a hard-cut, invisible at this speed.
3. **Single signal**: terracotta `#B34D18` only -- `affirm`/`alert` are status roles, never accent.
4. **Density**: `comfortable` -- active band `s2..s7`; `s0/s1` for hairline insets only. All paddings and gaps must be exact multiples of the `8px` unit.

## CEXAI Leverage

Caldo is an ACTIVE asset, not a token dump. A builder loads exactly one design_system at
F3 INJECT and binds it as the only visual source for the surface it generates:

- **Feeds**: `landing_page`, `interactive_demo`, `product_tour`, `onboarding_flow`, `pitch_deck`
  -- any consumer, lifestyle, or approachable-brand surface renders in Caldo's tokens.
- **Inject hook**: bind tokens as the sole palette/scale/motion source; compose only from the
  four recipes; motion breathes (enter = calm emphatic), collapses to `dur.instant` under reduced-motion.
- **brand_config**: realizes a warm consumer or lifestyle brand identity into bindable
  geometric-soft tokens; the global `brand_config` selects Caldo as the active system.
- **Composes with**: the variant-shotgun + taste loop (Caldo anchors the warm/airy/light/geometric
  corner), `user_model` (founder taste), GDP (founder gate). Binds at F1 CONSTRAIN + F3 INJECT.
