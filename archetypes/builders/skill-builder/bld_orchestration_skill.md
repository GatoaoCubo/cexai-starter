---
kind: collaboration
id: bld_collaboration_skill
pillar: P12
llm_function: COLLABORATE
purpose: How skill-builder works in crews with other builders
pattern: each builder must know its ROLE in a team, what it RECEIVES and PRODUCES
quality: null
title: "Collaboration Skill"
version: "1.0.0"
author: n03_builder
tags: [skill, builder, examples]
tldr: "Golden and anti-examples for skill construction, demonstrating ideal structure and common pitfalls."
domain: "skill construction"
created: "2026-04-07"
updated: "2026-04-07"
8f: "F8_collaborate"
keywords: [skill construction, collaboration skill, skill, builder, examples, "### crew: skill library expansion", my role, crew compositions, new skill end, skill library expansion]
density_score: 0.90
related:
  - skill-builder
  - bld_architecture_skill
  - bld_memory_skill
  - n00_skill_manifest
  - p03_ins_skill_builder
---
# Collaboration: skill-builder

## My Role in Crews
I am a SPECIALIST. I answer ONE question: "what is this reusable skill — its trigger, phases, inputs, outputs, and boundary?"
I do not write agents. I do not define workflows or system prompts.
I produce skill definitions so downstream builders can integrate skills into agents and workflows.

## Crew Compositions

### Crew: "New Skill End-to-End"
```
  1. knowledge-card-builder -> "domain knowledge for skill expertise"
  2. skill-builder -> "skill definition (trigger + phases + reusable boundary)"
  3. instruction-builder -> "execution steps for skill usage"
  4. agent-builder -> "agent that uses this skill"
```

### Crew: "Skill Library Expansion"
```
  1. skill-builder -> "define the skill"
  2. schema-builder -> "input/output schema for skill"
  3. examples-builder -> "usage examples"
  4. quality-gate-builder -> "validation criteria"
```

## What I Receive
- Domain KC, pattern description, user intent
## What I Produce
- Skill definition: trigger, phases, inputs, outputs, boundary, anti-patterns

## Pipeline Integration

1. Created via 8F pipeline from F1-Focus through F8-Furnish
2. Scored by cex_score across three structural layers
3. Compiled by cex_compile for structural validation
4. Retrieved by cex_retriever for context injection
5. Evolved by cex_evolve when quality regresses below target

## Properties

| Property | Value |
|----------|-------|
| Kind | `collaboration` |
| Pillar | P12 |
| Domain | skill construction |
| Pipeline | 8F (F1-F8) |
| Scorer | cex_score.py |
| Compiler | cex_compile.py |
| Retriever | cex_retriever.py |
| Quality target | 9.0+ |
| Density target | 0.85+ |

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[skill-builder]] | upstream | 0.59 |
| [[bld_architecture_skill]] | upstream | 0.55 |
| [[bld_memory_skill]] | upstream | 0.52 |
| [[n00_skill_manifest]] | upstream | 0.45 |
| [[p03_ins_skill_builder]] | upstream | 0.45 |
