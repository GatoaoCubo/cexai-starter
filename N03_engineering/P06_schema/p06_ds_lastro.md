---
id: p06_ds_lastro
kind: design_system
pillar: P06
nucleus: N03
title: "Lastro -- cold, compact, soft-edged, light, mono-first civic design system"
version: 1.0.0
created: "2026-06-15"
updated: "2026-06-15"
author: n03_builder
domain: design-systems
aesthetic: "Fog-white institutional canvas, compact mono-first type, 6px soft corners, single policy-blue signal, motion that advances then settles -- measured by data density and civic legibility, never decoration."
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
  inject_hook: "F3 INJECT: bind Lastro tokens as the sole palette/scale/motion source; compose only from the four recipes; advance on enter, settle on exit, collapse to instant under reduced-motion."
  brand_config_relation: "Realizes a civic, public-sector, or open-data brand_config identity into bindable cold-compact tokens; brand_config selects Lastro for institutional and data-dense surfaces."
  composes_with: [variant_shotgun_taste_loop, user_model, gdp]
  binds_8f: [F1_constrain, F3_inject]
tags: [design-system, tokens, light, cold, compact, mono, civic, dataviz, institutional, leverage]
tldr: "Cold compact light-mode system: fog-white canvas, mono-first type on a 1.25 scale, 6px soft radius, single policy-blue signal, advance-settle motion. Conforms to p06_vs_design_system."
density_score: 0.91
related:
  - p06_vs_design_system
  - p06_ds_ferro
  - p06_ds_alvura
---

# Lastro

Conforms to [[p06_vs_design_system]]. Lastro is the ballast of civic interfaces:
cold without hostility, compact without sacrificing legibility. It dresses open-data
portals, public-service dashboards, and government-adjacent tools where information
density and institutional trust matter more than aesthetic theatre.

## color

| Role | Value | Role | Value |
|------|-------|------|-------|
| `canvas` | `#F4F6F8` | `signal` | `#2E6DA4` |
| `panel` | `#FFFFFF` | `signal_ink` | `#FFFFFF` |
| `ink` | `#1C2530` | `affirm` | `#2E7D4F` |
| `ink_soft` | `#5A6A7A` | `alert` | `#B53030` |
| `edge` | `#D0D8E2` | | |

## type

- `face.display`: `'IBM Plex Mono', 'Courier New', monospace`
- `face.text`: `'IBM Plex Mono', 'Lucida Console', monospace`
- `face.mono`: `'IBM Plex Mono', ui-monospace, monospace`
- `scale.ratio`: `1.25` (major second -- compact, data-legible)
- `scale.steps`: `t_1 0.8 | t1 1.0 | t2 1.25 | t3 1.563 | t4 1.953 | t5 2.441 | t6 3.052` (rem)
- `weight`: `reg 400 | med 500 | bold 700`
- `leading`: `tight 1.2 | normal 1.5 | loose 1.75`

## space

- `unit`: `4px`
- `scale`: `s0 0 | s1 1 | s2 2 | s3 3 | s4 4 | s5 5 | s6 8 | s7 12` (unit multipliers -> 0/4/8/12/16/20/32/48px)

## motion

- `dur`: `instant 0ms | quick 100ms | calm 200ms`
- `ease`: `linear cubic-bezier(0,0,1,1) | standard cubic-bezier(0.25,0,0.1,1) | emphatic cubic-bezier(0.2,0,0,1)`
- `move`: `enter = quick+standard (advance) | exit = calm+standard (settle) | shift = quick+standard`

## form

- `radius`: `none 0 | soft 6px | full 9999px`
- `edge.width`: `1px`
- `shadow`: `flat none | raised 0 1px 3px rgba(28,37,48,0.08), 0 2px 8px rgba(28,37,48,0.06) | float 0 4px 20px rgba(28,37,48,0.12)` (cold diffuse elevation)

## components

| Component | Recipe |
|-----------|--------|
| `surface` | `panel` + `radius.soft 6px` + `shadow.raised` + `s4` padding |
| `control` | `signal` bg + `signal_ink` + `radius.soft` + `type.text/med` + `move.shift` on press |
| `field` | `panel` + `edge 1px` + `ink` + `radius.soft` + `s3` padding |
| `marker` | `signal` @ 14% tint + `type.mono/t_1` + `radius.full` (pill badge) |

## usage

1. **Contrast**: `ink #1C2530` on `canvas #F4F6F8` ~= 13.4:1; `signal_ink #FFFFFF` on `signal #2E6DA4` ~= 7.7:1 -- both clear WCAG AA.
2. **Reduce-motion**: collapse every `move` to `dur.instant`; civic surfaces serve assistive-tech users at high rates.
3. **Single signal**: policy-blue `#2E6DA4` only -- `affirm`/`alert` are status, never accent.
4. **Density**: `compact` -- active band `s0..s5`; `s6/s7` for page gutters and section breaks.

## CEXAI Leverage

Lastro is an ACTIVE asset, not a token dump. A builder loads exactly one design_system
at F3 INJECT and binds it as the only visual source for the surface it generates:

- **Feeds**: `landing_page`, `interactive_demo`, `product_tour`, `onboarding_flow`, `pitch_deck`
  -- civic, public-sector, or open-data surfaces; especially suited to data-table-heavy and
  chart-heavy layouts where mono legibility is a functional requirement.
- **Inject hook**: bind tokens as the sole palette/scale/motion source; compose only from the
  four recipes; advance on enter, settle on exit, collapse to `dur.instant` under reduced-motion.
- **brand_config**: realizes a cold-institutional brand identity into bindable civic tokens;
  `brand_config` selects Lastro for surfaces requiring public-sector trust signaling.
- **Composes with**: variant-shotgun + taste loop (Lastro anchors cold/compact/soft/light/mono),
  `user_model` (data-professional taste), GDP (stakeholder gate). Binds at F1 CONSTRAIN + F3 INJECT.
