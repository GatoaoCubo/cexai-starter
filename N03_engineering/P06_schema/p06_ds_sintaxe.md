---
id: p06_ds_sintaxe
kind: design_system
pillar: P06
title: "Sintaxe -- paper-terminal, cold/compact/stark/mono design system for developer tools"
version: 1.1.0
created: "2026-06-15"
updated: "2026-06-24"
author: n03_builder
domain: developer-tools
aesthetic: "Near-white canvas, ink-graphite type, single indigo accent, monospace-forward ramp on a tight 1.25 scale -- a light-first IDE surface that reads code, not decor."
density: compact
provenance:
  source: "github.com/nexu-io/open-design"
  license: "Apache-2.0"
  lineage_record: "p01_lin_open_design"
  method: "clean_room_concept_extraction"
  derived: "2026-06-24"
quality: null
leverage:
  feeds_kinds: [landing_page, interactive_demo, product_tour, onboarding_flow, pitch_deck, doc_page, cli_reference]
  inject_hook: "F3 INJECT: bind Sintaxe tokens as the sole palette/scale/motion source; compose only from the four recipes; snap motion never springs; code blocks render in face.mono; collapse every move to dur.instant under prefers-reduced-motion."
  brand_config_relation: "Realizes a developer-tools/docs/CLI brand_config identity into bindable paper-terminal tokens; brand_config selects Sintaxe as the active system for that identity."
  composes_with: [variant_shotgun_taste_loop, user_model, gdp]
  binds_8f: [F1_constrain, F3_inject]
tags: [design-system, tokens, light, mono, compact, developer-tools, cli, leverage]
tldr: "Light-mode developer-tools system: near-white paper canvas, ink-graphite type, single indigo signal, monospace-led type on tight 1.25 scale, 4px base grid, snap-fast motion. WCAG-AA on all pairs. Conforms to p06_vs_design_system."
related:
  - p06_vs_design_system
  - p06_ds_ferro
  - p06_ds_sereno
---

# Sintaxe

Conforms to [[p06_vs_design_system]]. Light-first, monospace-native, for developer
tools, CLI dashboards, docs, and API references. Refuses warm hues and decorative
motion: paper canvas, ink-graphite, one cold indigo signal. Code blocks are
first-class in the type ramp. Distinct from Ferro (dark/terminal) -- Sintaxe is the
light-mode counterpart: same discipline, bright field.

## color

| Role | Value | Role | Value |
|------|-------|------|-------|
| `canvas` | `#F5F4F1` | `signal` | `#3D5AF1` |
| `panel` | `#FFFFFF` | `signal_ink` | `#EEF1FF` |
| `ink` | `#1A1D20` | `affirm` | `#1C7C54` |
| `ink_soft` | `#5C6370` | `alert` | `#C0392B` |
| `edge` | `#D0D4D9` | | |

## type

- `face.display`: `'DM Mono', 'Fira Code', ui-monospace, monospace`
- `face.text`: `'DM Sans', ui-sans-serif, system-ui, sans-serif`
- `face.mono`: `'DM Mono', 'Fira Code', ui-monospace, 'Courier New', monospace`
- `scale.ratio`: `1.25` (major second -- tight, utilitarian, tabular-safe)
- `scale.steps`: `t_1 0.8 | t1 1.0 | t2 1.25 | t3 1.563 | t4 1.953 | t5 2.441 | t6 3.052` (rem)
- `weight`: `reg 400 | med 500 | bold 700`
- `leading`: `tight 1.1 | normal 1.45 | loose 1.65`

## space

- `unit`: `4px`
- `scale`: `s0 0 | s1 1 | s2 2 | s3 3 | s4 4 | s5 6 | s6 8 | s7 12` (unit multipliers -> 0/4/8/12/16/24/32/48px)

## motion

- `dur`: `instant 0ms | quick 80ms | calm 150ms`
- `ease`: `linear cubic-bezier(0,0,1,1) | standard cubic-bezier(0.2,0,0,1) | emphatic cubic-bezier(0.15,0,0,1)`
- `move`: `enter = quick+standard | exit = instant+linear | shift = quick+standard`

## form

- `radius`: `none 0 | soft 3px | full 4px` (near-square; markers stay compact, not pill)
- `edge.width`: `1px`
- `shadow`: `flat none | raised 0 0 0 1px #D0D4D9 | float 0 4px 16px rgba(26,29,32,0.12)` (edge-line elevation; blur only at float)

## components

| Component | Recipe |
|-----------|--------|
| `surface` (doc/code card) | `panel` + `radius.soft 3px` + `shadow.raised` (edge-line) + `s4` padding |
| `control` (button) | `signal` bg + `signal_ink` + `radius.soft` + `type.text/med/t1` + `move.shift` on press |
| `field` (command input) | `panel` + `edge 1px` + `ink` + `face.mono/t1` + `radius.soft` + `s3` padding |
| `marker` (badge) | `signal` @ 14% tint (`#D7DBFC`) + `type.mono/t_1/med` + `radius.full 4px` |

## usage

1. **Contrast**: `ink #1A1D20` on `canvas #F5F4F1` ~= 15.8:1; `signal_ink #EEF1FF` on `signal #3D5AF1` ~= 9.0:1; `ink_soft #5C6370` on `canvas` ~= 6.3:1 -- all WCAG AA (>=4.5:1).
2. **Reduce-motion**: collapse every `move` to `dur.instant` under `prefers-reduced-motion: reduce`.
3. **Single signal**: indigo `#3D5AF1` only -- `affirm`/`alert` are status, never accent competitors.
4. **Monospace code blocks**: render inline code and fences in `face.mono/normal` leading; never substitute `face.text` in code contexts.

## CEXAI Leverage

Sintaxe is an ACTIVE asset, not a token dump. Builders load it at F3 INJECT as the sole
visual source for developer-tools and docs surfaces:

- **Feeds**: `landing_page`, `interactive_demo`, `product_tour`, `onboarding_flow`, `pitch_deck`, `doc_page`, `cli_reference` -- developer tools, API docs, CLI dashboards.
- **Inject hook**: bind tokens as sole palette/scale/motion source; compose only from the four recipes; snap (never spring); `face.mono` for all code contexts; collapse to `dur.instant` under reduced-motion.
- **brand_config**: realizes a developer-tools/CLI brand identity into paper-terminal tokens; `brand_config` selects Sintaxe.
- **Composes with**: variant-shotgun + taste loop (cold/compact/stark/light/mono corner), `user_model`, GDP. Binds at F1 CONSTRAIN + F3 INJECT.

## Related Artifacts

| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[p06_vs_design_system]] | upstream | 0.60 |
| [[p06_ds_ferro]] | sibling | 0.44 |
| [[p06_ds_sereno]] | sibling | 0.38 |
