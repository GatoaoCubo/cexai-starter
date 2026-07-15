---
id: bld_tools_design_system
kind: toolkit
pillar: P06
llm_function: CALL
8f: F5_call
version: 1.0.0
created: "2026-06-15"
updated: "2026-06-15"
author: n03_builder
title: "Tools: building + validating a design_system"
domain: design_system
quality: null
tags: [design_system, builder, tools, P06]
tldr: "The tool inventory a design_system build calls: compile, doctor, score, index, contrast check, and the dispatch/swarm entry."
density_score: 0.88
related:
  - bld_prompt_design_system
  - bld_eval_design_system
  - bld_orchestration_design_system
  - p06_vs_design_system
  - design-system-builder
---

# Tools: design_system
## Build + govern
| Tool | Use |
|------|-----|
| `cex_compile.py` | compile the instance .md -> .yaml (mandatory F8) |
| `cex_doctor.py` | builder-dir health (this ISO set passes 12/12) |
| `cex_score.py` | peer score (never self-score) |
| `cex_index.py` | index frontmatter + wikilinks |
## Domain checks
| Check | How |
|-------|-----|
| Contrast | compute WCAG ratio for ink-on-canvas + signal_ink-on-signal (>= 4.5:1) |
| Single-signal | assert exactly one accent role |
| Reduce-motion | assert every move has a dur.instant fallback |
| Leverage | assert leverage.feeds_kinds non-empty |
## Scale
| Tool | Use |
|------|-----|
| `Task tool: dispatch swarm design_system N` | parallel library build over coordinates |
## Discipline
Tools VALIDATE; they never invent values. A design_system's values are authored, then verified. Clean-room is a human + gate check, not a tool output.
## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[bld_eval_design_system]] | upstream | 0.45 |
| [[bld_prompt_design_system]] | related | 0.42 |
| [[bld_orchestration_design_system]] | sibling | 0.4 |
| p06_vs_design_system | upstream | 0.4 |
| [[design-system-builder]] | related | 0.38 |
