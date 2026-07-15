---
id: bld_orchestration_design_system
kind: workflow
pillar: P06
llm_function: COLLABORATE
8f: F8_collaborate
version: 1.0.0
created: "2026-06-15"
updated: "2026-06-15"
author: n03_builder
title: "Orchestration: dispatching + composing design_system"
domain: design_system
quality: null
tags: [design_system, builder, orchestration, swarm, P06]
tldr: "How design_system builds are dispatched (swarm over coordinates) and composed (taste loop + downstream surface builders)."
density_score: 0.88
related:
  - p03_ps_design_system_library_scale
  - bld_architecture_design_system
  - bld_prompt_design_system
  - p06_vs_design_system
  - design-system-builder
---

# Orchestration: design_system
## Single build
`design-system-builder` runs F1-F8 on one coordinate -> one instance. Standard 8F.
## Library build (swarm)
1. Compute uncovered coordinates from the coverage matrix.
2. `Task tool: dispatch swarm design_system N` -- one cell -> one instance, isolated worktrees.
3. Each cell briefed with a target coordinate + an original archetype + the contract.
## Convergence (taste loop)
Wrap the swarm in the variant-shotgun + taste loop: render a comparison board, founder gives structured approve/reject (GDP), signals re-weight the next round. Converge per axis-region when a round adds no fresh signal (p03_ps_design_system_library_scale).
## Downstream composition
A produced system is injected at F3 by surface builders (landing_page, interactive_demo, product_tour, onboarding_flow, pitch_deck). The design_system is the upstream asset; the surface is the downstream artifact.
## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| p03_ps_design_system_library_scale | upstream | 0.5 |
| [[bld_architecture_design_system]] | sibling | 0.42 |
| [[bld_prompt_design_system]] | related | 0.4 |
| p06_vs_design_system | upstream | 0.4 |
| [[design-system-builder]] | related | 0.4 |
