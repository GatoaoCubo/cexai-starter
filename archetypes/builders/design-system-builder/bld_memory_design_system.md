---
id: bld_memory_design_system
kind: learning_record
pillar: P06
llm_function: INJECT
8f: F3_inject
version: 1.0.0
created: "2026-06-15"
updated: "2026-06-15"
author: n03_builder
title: "Patterns: design_system builds"
domain: design_system
quality: null
tags: [design_system, builder, memory, patterns, P06]
tldr: "Learned patterns + recurring failure modes from design_system builds: coordinate-first, signal discipline, contrast verification, clean-room."
density_score: 0.9
related:
  - bld_knowledge_design_system
  - bld_eval_design_system
---

# Patterns: design_system builds
## What scored high
| Pattern | Why |
|---------|-----|
| Coordinate-first | fix temperature/density/form/mode/type-voice before picking values -> no sibling collisions |
| One signal, committed | a single confident accent reads as designed, not decorated |
| Contrast computed | verifying >= 4.5:1 up front avoids a rejection loop |
| Motion matched to stance | snap for engineered systems, spring for humanist ones |
| Leverage declared early | the feeds/inject hook forces the system to be composable, not a palette |
## Recurring failures
| Failure | Fix |
|---------|-----|
| Two accents creep in | demote one to status (affirm/alert) or a tint |
| Spring under reduce-motion | always add the dur.instant fallback |
| Sibling of an existing system | move along an axis (warm<->cold, compact<->airy) |
| Copied palette or name | reject; re-author from the coordinate (clean-room) |
| Passive token dump | add the leverage block; declare feeds_kinds |
## Corner map (W0 anchors)
p06_ds_ferro = cold/compact/stark/dark/mono. p06_ds_sereno = warm/airy/soft/light/humanist. W1 fills the interior + other corners (p03_ps_design_system_library_scale).
## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[bld_eval_design_system]] | upstream | 0.45 |
| [[bld_knowledge_design_system]] | sibling | 0.42 |
| p03_ps_design_system_library_scale | related | 0.42 |
| p06_ds_ferro | example | 0.4 |
| p06_ds_sereno | example | 0.4 |
