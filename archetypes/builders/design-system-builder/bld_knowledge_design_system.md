---
id: bld_knowledge_design_system
kind: knowledge_card
pillar: P06
llm_function: INJECT
8f: F3_inject
version: 1.0.0
created: "2026-06-15"
updated: "2026-06-15"
author: n03_builder
title: "Domain Knowledge: design_system"
domain: design_system
quality: null
tags: [design_system, builder, knowledge, tokens, P06]
tldr: "Atomic facts for building design systems: token taxonomy, modular type scales, spacing ladders, motion easing, elevation, and WCAG contrast."
density_score: 0.92
related:
  - bld_schema_design_system
  - p01_kc_design_system
  - p06_vs_design_system
  - bld_memory_design_system
  - design-system-builder
---

# Domain Knowledge: design_system
## Token taxonomy (the five groups)
A design token is a named, reusable decision. Group them: color (semantic roles, not raw hex names), type (faces + a modular scale), space (one base unit x a ladder), motion (duration + easing + named moves), form (radius + edge + elevation).
## Modular type scale
`step(n) = base * ratio^n`. Common ratios: 1.2 minor third (tight/utilitarian), 1.25 major third, 1.333 perfect fourth (editorial), 1.5 perfect fifth, 1.618 golden. One ratio per system.
## Spacing ladder
Pick a base unit (4px or 8px). Derive s0..s7 as unit multipliers (e.g. 0,1,2,3,4,6,8,12). Density mode selects the active band.
## Motion
Duration buckets: instant 0ms, quick 80-160ms, calm 180-320ms. Easing: linear, standard (ease-out cubic-bezier), emphatic (spring/overshoot). Named moves compose dur+ease for enter/exit/shift.
## Elevation
Express raised/float via shadow recipes (offset+blur+alpha) or a hairline edge. Dark systems often use a hairline; light systems use soft shadows.
## WCAG contrast
AA body text needs >= 4.5:1; large text >= 3:1. Always verify ink-on-canvas and signal_ink-on-signal with a contrast formula, not eyeballing.
## Single-signal discipline
One accent (signal) role per system. affirm/alert are STATUS colors, never a second accent. Two accents destroy hierarchy.
## Clean-room
Token values + system names are original IP. Never copy a known system's palette, scale, or name. Author from the aesthetic coordinate, not from a reference.
## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[bld_schema_design_system]] | downstream | 0.5 |
| [[p01_kc_design_system]] | sibling | 0.48 |
| p06_vs_design_system | upstream | 0.45 |
| [[bld_memory_design_system]] | sibling | 0.4 |
| [[design-system-builder]] | related | 0.4 |
