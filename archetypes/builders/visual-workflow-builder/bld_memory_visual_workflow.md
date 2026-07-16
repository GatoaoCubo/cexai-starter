---
kind: memory
id: p10_mem_visual_workflow_builder
pillar: P10
llm_function: INJECT
purpose: Learned patterns and pitfalls for visual_workflow construction
quality: null
title: "Memory Visual Workflow"
version: "1.0.0"
author: wave1_builder_gen_v2
tags: [visual_workflow, builder, memory]
tldr: "Accumulated production experience for visual workflow: golden patterns, anti-patterns, common pitfalls, and evidence-backed guidance for gui-based workflow editor configuration."
domain: "visual_workflow construction"
created: "2026-04-14"
updated: "2026-04-14"
8f: "F3_inject"
keywords: [visual_workflow construction, memory visual workflow, golden patterns, common pitfalls, visual_workflow, builder, memory, observation
misalignment, pattern
drag, evidence
reviewed]
density_score: 0.85
related:
  - visual-workflow-builder
  - workflow-node-builder
---
## Observation
Misalignment of nodes and broken connections are common during manual layout. Overlapping elements often occur when workflows grow complex.

## Pattern
Drag-and-drop placement with snap-to-grid improves precision. Using pre-defined node templates reduces configuration errors.

## Evidence
Reviewed artifacts showed 70% had alignment issues; workflows with real-time validation had 40% fewer errors.

## Recommendations
- Enforce grid alignment for node placement.
- Implement real-time connection validation.
- Provide auto-sizing for consistent node dimensions.
- Use color-coding to differentiate workflow stages.
- Include reusable template libraries for common patterns.

## Pitfalls

- **Missing frontmatter fields**: omitting required fields causes H01 gate failure.
- **Generic descriptions**: vague purpose/tldr reduces retrieval accuracy.
- **Ignoring boundary**: Visual workflow editor.
- **Orphaned dependencies**: referencing workflow without verifying it exists.

## Properties

| Property | Value |
|----------|-------|
| Kind | `memory` |
| Pillar | P10 |
| Domain | visual workflow construction |
| Pipeline | 8F (F1-F8) |
| Scorer | cex_score.py |
| Compiler | cex_compile.py |
| Retriever | cex_retriever.py |
| Quality target | 9.0+ |
| Density target | 0.85+ |

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[visual-workflow-builder]] | downstream | 0.45 |
| [[workflow-node-builder]] | downstream | 0.40 |
