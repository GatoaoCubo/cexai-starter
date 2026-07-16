---
kind: collaboration
id: bld_collaboration_effort_profile
pillar: P12
llm_function: COLLABORATE
purpose: How effort-profile-builder works in crews with other builders
pattern: each builder must know its ROLE in a team, what it RECEIVES and PRODUCES
quality: null
title: "Collaboration Effort Profile"
version: "1.0.0"
author: n03_builder
tags: [effort_profile, builder, examples]
tldr: "Golden and anti-examples for effort profile construction, demonstrating ideal structure and common pitfalls."
domain: "effort profile construction"
created: "2026-04-07"
updated: "2026-04-07"
8f: "F8_collaborate"
keywords: [effort profile construction, collaboration effort profile, effort_profile, builder, examples, "### crew: dispatch pipeline", my role, crew compositions, builder configuration, dispatch pipeline]
density_score: 0.90
related:
  - effort-profile-builder
  - bld_config_effort_profile
  - bld_collaboration_agent
  - bld_collaboration_system_prompt
  - bld_collaboration_memory_scope
---
# Collaboration: effort-profile-builder
## My Role in Crews
I am a SPECIALIST. I answer ONE question: "which model and thinking level should this builder use?"
I specify effort profiles so dispatchers and runtime systems can allocate the right resources.
## Crew Compositions
### Crew: "Builder Configuration"
```
  1. effort-profile-builder -> model + thinking config
  2. runtime-rule-builder -> execution rules
  3. env-config-builder -> environment variables
```
### Crew: "Dispatch Pipeline"
```
  1. effort-profile-builder -> effort allocation
  2. agent-builder -> agent definition
  3. system-prompt-builder -> agent persona
```

## Handoff Protocol
### I Receive
1. seeds: target builder, complexity requirements, budget constraints
2. optional: specific model preferences, upstream artifact references
### I Produce
1. effort_profile artifact (.md + .yaml frontmatter)
2. committed to: `cex/P09_config/examples/p09_effort_{name}.md`
### I Signal
1. signal: complete (with quality score from QUALITY_GATES)
2. if quality < 8.0: signal retry with failure reasons
## Builders I Depend On
None — independent builder (layer 0).
## Builders That Depend On Me
| Builder | Why |
|---------|-----|
| runtime-rule-builder | Uses effort profile for execution planning |
| agent-builder | References model/thinking in agent config |
| system-prompt-builder | Adapts prompt complexity to thinking level |

## Properties

| Property | Value |
|----------|-------|
| Kind | `collaboration` |
| Pillar | P12 |
| Domain | effort profile construction |
| Pipeline | 8F (F1-F8) |
| Scorer | cex_score.py |
| Compiler | cex_compile.py |
| Retriever | cex_retriever.py |
| Quality target | 9.0+ |
| Density target | 0.85+ |

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[effort-profile-builder]] | upstream | 0.38 |
| [[bld_config_effort_profile]] | upstream | 0.34 |
| [[bld_collaboration_agent]] | sibling | 0.33 |
| [[bld_collaboration_system_prompt]] | sibling | 0.33 |
| [[bld_collaboration_memory_scope]] | sibling | 0.33 |
