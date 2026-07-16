---
kind: architecture
id: bld_architecture_personality
pillar: P08
llm_function: CONSTRAIN
purpose: Structural constraints and layering model for personality artifacts
quality: null
title: "Architecture: personality"
version: "1.0.0"
author: n03_builder
tags:
  - "personality"
  - "builder"
  - "architecture"
  - "P02"
  - "hermes_origin"
  - "hot_swap"
  - "soul_md"
tldr: "personality sits in the P02 voice layer above agent and below system_prompt. Hot-swap via /personality command at runtime."
domain: "persona construction"
created: "2026-04-18"
updated: "2026-04-18"
8f: "F1_constrain"
keywords:
  - "persona construction"
  - "hot-swap via"
  - "personality command at runtime"
  - "personality"
  - "builder"
  - "architecture"
  - "hermes_origin"
  - "hot_swap"
  - "soul_md"
  - "| | injection | agent loads"
density_score: 0.89
related:
  - kc_personality
  - personality-builder
  - bld_memory_personality
---
# Architecture: personality

## Layer Position

```
P02 Identity Stack (top to bottom):
  system_prompt    -- full prompt context (static)
  personality      -- voice/tone/values overlay (HOT-SWAPPABLE) <-- THIS KIND
  agent_profile    -- runtime AI configuration
  agent            -- full spec (capabilities, memory, tools)
```

personality sits ABOVE agent_profile (it overrides how the agent speaks, not how it runs)
and BELOW system_prompt (system_prompt may reference personality but personality does not
contain the full prompt).

## Component Diagram

```
Agent (N03) ---- runs on ----> agent definition
                |
                +-- injects --> personality (active via /personality [name])
                |                 voice.register
                |                 voice.verbosity
                |                 voice.humor
                |                 values[]
                |                 tone_examples[]
                |                 anti_patterns[]
                |
                +-- configures -> agent_profile (model, temperature, etc.)
```

## Hot-Swap Mechanics

| Phase | Action |
|-------|--------|
| Boot | Agent loads default personality (or none) |
| Activation | User types `/personality [name]` |
| Injection | Agent loads `p02_per_{{name}}.md` from P02 store |
| Override | Voice register/verbosity/humor apply to all subsequent responses |
| Deactivation | User types `/personality default` |
| Restore | Agent reverts to default voice |

## Boundary Matrix

| Kind | Overlaps | Does NOT overlap |
|------|----------|-----------------|
| agent | persona name in identity | capabilities, tools, memory, routing |
| agent_profile | may reference active personality | model selection, temperature, max_tokens |
| system_prompt | may instruct "adopt personality X" | full prompt text, tool instructions |
| lens | domain perspective | routing rules, pillar assignments |

## File Naming
```
Artifact: p02_per_{{name}}.md
Compiled: p02_per_{{name}}.yaml
Location: N0X_*/P02_model/ (or N00_genesis/P02_model/ for archetype)
```

## Registry
Active personality is stored in agent_profile or session_state:
```yaml
active_personality: per_researcher  # references personality id
personality_store: N00_genesis/P02_model/  # or nucleus-local P02
```

## Constraints
- max_bytes: 3072 -- voice layer must be inlined cheaply into context
- No tool definitions -- personality cannot add capabilities
- No memory config -- personality cannot alter retention
- hot_swap_compatible: true default -- switching must be instant (no session restart)

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[kc_personality]] | upstream | 0.65 |
| [[bld_knowledge_personality]] | upstream | 0.62 |
| [[personality-builder]] | upstream | 0.58 |
| n00_personality_manifest | upstream | 0.56 |
| [[bld_memory_personality]] | downstream | 0.52 |
