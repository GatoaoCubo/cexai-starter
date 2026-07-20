---
id: p06_ds_brasa
kind: design_system
pillar: P06
nucleus: N03
title: "Brasa -- warm brutalist terminal design system"
version: 1.0.0
created: "2026-06-15"
updated: "2026-06-15"
author: n03_builder
domain: design-systems
aesthetic: "Near-black canvas scorched by amber signal, zero-radius hard edges, mono-only type on a tight scale, and snap motion -- a developer tool that runs hot."
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
  inject_hook: "F3 INJECT: bind Brasa tokens as the sole palette/scale/motion source; compose only from the four recipes; snap motion; amber stays the single signal."
  brand_config_relation: "Realizes a developer-tool/terminal brand_config identity with amber warmth into bindable dark tokens; brand_config selects Brasa as the active system."
  composes_with: [variant_shotgun_taste_loop, user_model, gdp]
  binds_8f: [F1_constrain, F3_inject]
tags: [design-system, tokens, dark, warm, brutalist, mono, amber, leverage]
tldr: "Warm brutalist dark-mode system: near-black canvas, amber-rust signal on near-black text, monospace-only type stack on a tight 1.2 scale, zero-radius hard edges, and snap-fast motion. Distinct from Ferro (cold) and Sereno (light). Conforms to p06_vs_design_system."
density_score: 0.90
related:
  - p06_vs_design_system
  - p06_ds_ferro
  - p06_ds_sereno
---

# Brasa

Conforms to [[p06_vs_design_system]]. Near-black ash canvas, live-amber signal, zero
radius on every corner. Monospace from display to caption -- no serif, no sans, just
the grid. Snaps, never springs. Dresses developer tools and terminal dashboards that
run hot. Distinct from [[p06_ds_ferro]] (cold teal, 2px radius) and [[p06_ds_sereno]]
(warm light-mode, humanist faces).

## color

| Role | Value | Role | Value |
|------|-------|------|-------|
| `canvas` | `#0E0B07` | `signal` | `#E8831A` |
| `panel` | `#1A140C` | `signal_ink` | `#0D0600` |
| `ink` | `#DCCBA0` | `affirm` | `#6DBF6A` |
| `ink_soft` | `#806E50` | `alert` | `#E05252` |
| `edge` | `#2E2318` | | |

## type

- `face.display`: `'TX-02', 'Courier New', ui-monospace, monospace`
- `face.text`: `'Iosevka', 'Consolas', ui-monospace, monospace`
- `face.mono`: `'Iosevka', 'Consolas', ui-monospace, monospace`
- `scale.ratio`: `1.2` (minor third -- tight, utilitarian, matches terminal density)
- `scale.steps`: `t_1 0.833 | t1 1.0 | t2 1.2 | t3 1.44 | t4 1.728 | t5 2.074 | t6 2.488` (rem)
- `weight`: `reg 400 | med 500 | bold 700`
- `leading`: `tight 1.1 | normal 1.4 | loose 1.65`

## space

- `unit`: `4px`
- `scale`: `s0 0 | s1 1 | s2 2 | s3 3 | s4 4 | s5 6 | s6 8 | s7 12` (unit multipliers -> 0/4/8/12/16/24/32/48px)

## motion

- `dur`: `instant 0ms | quick 80ms | calm 160ms`
- `ease`: `linear cubic-bezier(0,0,1,1) | standard cubic-bezier(0.2,0,0,1) | emphatic cubic-bezier(0.25,0,0,1)`
- `move`: `enter = quick+standard | exit = instant+linear | shift = quick+standard`

## form

- `radius`: `none 0 | soft 0 | full 0` (Brasa rejects all rounding; every edge is hard)
- `edge.width`: `1px`
- `shadow`: `flat none | raised 0 0 0 1px var(edge) | float 0 6px 20px rgba(14,11,7,0.7)` (hairline elevation; depth via opacity only)

## components

| Component | Recipe |
|-----------|--------|
| `surface` | `panel` + `radius.none` + `shadow.raised` (hairline) + `s3` padding |
| `control` | `signal` bg + `signal_ink` + `radius.none` + `type.text/bold` + `move.shift` on press |
| `field` | `panel` + `edge 1px` + `ink` + `radius.none` + `s3` padding |
| `marker` | `signal` @ 18% tint + `type.mono/t_1` + `radius.none` |

## usage

1. **Contrast**: `ink #DCCBA0` on `canvas #0E0B07` ~= 12.2:1; `signal_ink #0D0600` on `signal #E8831A` ~= 7.4:1 -- both clear WCAG AA (floor 4.5:1).
2. **Reduce-motion**: collapse every `move` to `dur.instant` under `prefers-reduced-motion`; Brasa already snaps, so the fallback is invisible.
3. **Single signal**: amber `#E8831A` only -- `affirm`/`alert` are status roles, never accent.
4. **Density**: `compact` -- active band is `s0..s5`; reserve `s6/s7` for page-level gutters only.

## CEXAI Leverage

Brasa is an ACTIVE asset, not a token dump. A builder loads exactly one design_system at
F3 INJECT and binds it as the only visual source for the surface it generates:

- **Feeds**: `landing_page`, `interactive_demo`, `product_tour`, `onboarding_flow`, `pitch_deck`
  -- developer-tool and terminal surfaces render in Brasa's tokens.
- **Inject hook**: bind as sole palette/scale/motion source; compose from the four recipes only;
  amber `signal` is the single accent; every `move` collapses to `dur.instant` under reduced-motion.
- **brand_config**: realizes a developer-tool identity with amber warmth into bindable dark tokens;
  global `brand_config` selects Brasa as the active system.
- **Composes with**: variant-shotgun + taste loop (Brasa owns the warm/compact/stark/dark/mono corner,
  distinct from Ferro's cold corner), `user_model`, and GDP. Binds at F1 CONSTRAIN + F3 INJECT.
