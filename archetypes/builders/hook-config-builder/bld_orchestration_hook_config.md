---
kind: collaboration
id: bld_collaboration_hook_config
pillar: P12
llm_function: COLLABORATE
purpose: How hook-config-builder works in crews with other builders
pattern: each builder must know its ROLE in a team, what it RECEIVES and PRODUCES
quality: null
title: "Collaboration Hook Config"
version: "1.0.0"
author: n03_builder
tags: [hook_config, builder, examples]
tldr: "Golden and anti-examples for hook config construction, demonstrating ideal structure and common pitfalls."
domain: "hook config construction"
created: "2026-04-07"
updated: "2026-04-07"
8f: "F8_collaborate"
keywords: [hook config construction, collaboration hook config, hook_config, builder, examples, "### crew: execution framework", my role, crew compositions, builder pipeline, execution framework]
density_score: 0.90
related:
  - hook-config-builder
  - bld_collaboration_hook
  - hook-builder
  - bld_collaboration_retriever_config
  - bld_knowledge_card_hook_config
---
# Collaboration: hook-config-builder
## My Role in Crews
I am a SPECIALIST. I answer ONE question: "which hooks fire at each build phase and under what conditions?"
I declare hook lifecycle configurations so builders and pipelines can bind events.
## Crew Compositions
### Crew: "Builder Pipeline"
```
  1. hook-config-builder -> hook lifecycle ofclaration
  2. quality-gate-builder -> quality scoring rules
  3. lifecycle-rule-builder -> archive/promote policy
```
### Crew: "Execution Framework"
```
  1. hook-config-builder -> event bindings
  2. plugin-builder -> extension modules
  3. agent-builder -> agent execution config
```

## Handoff Protocol
### I Receive
1. seeds: target builder, pipeline phases, hook requirements
2. optional: specific event bindings, upstream artifact references
### I Produce
1. hook_config artifact (.md + .yaml frontmatter)
2. committed to: `cex/P04_execution/examples/p04_hookconf_{name}.md`
### I Signal
1. signal: complete (with quality score from QUALITY_GATES)
2. if quality < 8.0: signal retry with failure reasons
## Builders I Depend On
None — independent builder (layer 0).
## Builders That Depend On Me
| Builder | Why |
|---------|-----|
| hook-builder | Implements hooks declared by this config |
| quality-gate-builder | May bind quality-fail hooks |
| lifecycle-rule-builder | May bind archive/promote hooks |

## Properties

| Property | Value |
|----------|-------|
| Kind | `collaboration` |
| Pillar | P12 |
| Domain | hook config construction |
| Pipeline | 8F (F1-F8) |
| Scorer | cex_score.py |
| Compiler | cex_compile.py |
| Retriever | cex_retriever.py |
| Quality target | 9.0+ |
| Density target | 0.85+ |

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[hook-config-builder]] | upstream | 0.44 |
| [[bld_collaboration_hook]] | sibling | 0.41 |
| [[hook-builder]] | upstream | 0.37 |
| [[bld_collaboration_retriever_config]] | sibling | 0.36 |
| [[bld_knowledge_card_hook_config]] | upstream | 0.36 |
