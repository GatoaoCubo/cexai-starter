---
id: p06_ds_capital
kind: design_system
pillar: P06
nucleus: N03
title: "Capital -- cold, geometric, dark-first fintech design system"
version: 1.0.0
created: "2026-06-15"
author: design-system-builder
domain: fintech
aesthetic: "Deep navy canvas, hairline geometry, one mint signal, tabular numerals -- a system that reads like a balance sheet, not a marketing page."
density: compact
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
  inject_hook: "F3 INJECT: bind Capital tokens as the sole palette/scale/motion source; compose only from the four recipes; numbers always tabular; motion clips, never springs."
  brand_config_relation: "Realizes a trust/growth fintech brand_config identity into bindable dark-navy tokens; brand_config selects Capital as the active system for digital-banking surfaces."
  composes_with: [variant_shotgun_taste_loop, user_model, gdp]
  binds_8f: [F1_constrain, F3_inject]
tags: [design-system, tokens, dark, fintech, geometric, tabular, leverage]
tldr: "Cold dark-first fintech system: deep navy canvas, mint-green signal for growth actions, geometric sans with tabular numerals, 1.25 scale, clip-fast motion, and hairline elevation. Conforms to p06_vs_design_system."
density_score: 0.9
related:
  - p06_vs_design_system
  - p06_ds_ferro
  - p06_ds_sereno
---

# Capital

Conforms to [[p06_vs_design_system]]. Capital is built for account dashboards,
transfer flows, and investing surfaces: data-dense, dark-first, geometric.
Every number renders in tabular figures. Elevation is a hairline or a
z-shadow -- never a glow. Motion clips; it never springs.

## color

| Role | Value | Role | Value |
|------|-------|------|-------|
| `canvas` | `#0A0F1E` | `signal` | `#1EE8A0` |
| `panel` | `#111827` | `signal_ink` | `#031A0E` |
| `ink` | `#E6EDF7` | `affirm` | `#22D37A` |
| `ink_soft` | `#6B7DA8` | `alert` | `#F5495A` |
| `edge` | `#1E2A45` | | |

## type

- `face.display`: `'DM Sans', 'Arial', sans-serif`
- `face.text`: `'Inter', ui-sans-serif, system-ui, sans-serif`
- `face.mono`: `'Roboto Mono', ui-monospace, 'Courier New', monospace`
- `scale.ratio`: `1.25` (major second -- dense, data-ready)
- `scale.steps`: `t_1 0.8 | t1 1.0 | t2 1.25 | t3 1.563 | t4 1.953 | t5 2.441 | t6 3.052` (rem)
- `weight`: `reg 400 | med 500 | bold 600`
- `leading`: `tight 1.15 | normal 1.5 | loose 1.7`
- `tabular_nums`: `font-variant-numeric: tabular-nums; font-feature-settings: "tnum" 1`
  (mandatory on all money, percentage, and account-number spans)

## space

- `unit`: `4px`
- `scale`: `s0 0 | s1 1 | s2 2 | s3 3 | s4 4 | s5 6 | s6 8 | s7 12`
  (unit multipliers -> 0/4/8/12/16/24/32/48px)

## motion

- `dur`: `instant 0ms | quick 80ms | calm 160ms`
- `ease`: `linear cubic-bezier(0,0,1,1) | standard cubic-bezier(0.2,0,0,1) | emphatic cubic-bezier(0.25,0,0,1)`
- `move`: `enter = quick+standard | exit = instant+linear | shift = quick+standard`
- `reduce_motion`: every `move` collapses to `dur.instant`; no spring, no overshoot

## form

- `radius`: `none 0 | soft 3px | full 3px`
  (Capital stays near-square; even markers are geometric rectangles)
- `edge.width`: `1px`
- `shadow`: `flat none | raised 0 0 0 1px #1E2A45 | float 0 8px 28px rgba(10,15,30,0.7)`
  (hairline border as raised elevation; blur only at modal/overlay layer)

## components

| Component | Recipe |
|-----------|--------|
| `surface` | `panel #111827` + `radius.soft 3px` + `shadow.raised` (hairline) + `s4 16px` padding |
| `control` | `signal #1EE8A0` bg + `signal_ink #031A0E` + `radius.soft` + `type.text/med` + `move.shift` on press |
| `field` | `panel #111827` + `edge 1px #1E2A45` + `ink #E6EDF7` + `radius.soft` + `s3 12px` padding; amounts use `tabular_nums` |
| `marker` | `signal #1EE8A0` @ 14% tint + `type.mono/t_1` + `radius.full 3px`; status text `type.mono/reg` |

## usage

1. **Contrast**: `ink #E6EDF7` on `canvas #0A0F1E` ~= 15.8:1 (WCAG AA text: PASS);
   `signal_ink #031A0E` on `signal #1EE8A0` ~= 10.1:1 (WCAG AA text: PASS);
   `affirm #22D37A` on `canvas #0A0F1E` ~= 7.1:1 (WCAG AA large/UI: PASS).
2. **Reduce-motion**: collapse every `move` to `dur.instant`; Capital clips by default --
   the fallback is already the natural feel; never spring under reduced-motion.
3. **Single signal**: mint `#1EE8A0` only -- `affirm`/`alert` are status indicators,
   never competing accents.
4. **Tabular numerals**: apply `tabular_nums` (tnum feature) to every money amount,
   account number, percentage, and data table cell; never proportional figures on figures.

## CEXAI Leverage

Capital is an ACTIVE asset, not a token dump. A builder loads exactly one design_system
at F3 INJECT and binds it as the only visual source for the surface it generates:

- **Feeds**: `landing_page`, `interactive_demo`, `product_tour`, `onboarding_flow`,
  `pitch_deck` -- any account dashboard, transfer flow, or investing surface renders in
  Capital's tokens.
- **Inject hook**: bind tokens as the sole palette/scale/motion source; compose only from
  the four recipes; tabular numerals mandatory on all financial figures; motion clips and
  collapses to `dur.instant` under reduced-motion.
- **brand_config**: realizes a trust/growth fintech identity into bindable dark-navy
  tokens; the global `brand_config` selects Capital as the active system for digital-banking
  surfaces.
- **Composes with**: the variant-shotgun + taste loop (Capital anchors the
  cold/compact/stark/dark/geometric corner of the fintech coordinate), `user_model`
  (founder taste for data-density), and GDP (founder gate). Binds at F1 CONSTRAIN +
  F3 INJECT.
