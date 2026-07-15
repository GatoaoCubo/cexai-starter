---
kind: collaboration
id: bld_collaboration_agent_package
pillar: P12
llm_function: COLLABORATE
purpose: How agent-package-builder works in crews with other builders
pattern: each builder must know its ROLE in a team, what it RECEIVES and PRODUCES
quality: null
title: "Collaboration Agent Package"
version: "1.0.0"
author: n03_builder
tags: [agent_package, builder, examples]
tldr: "Golden and anti-examples for agent package construction, demonstrating ideal structure and common pitfalls."
domain: "agent package construction"
created: "2026-04-07"
updated: "2026-04-07"
8f: "F8_collaborate"
keywords: [agent package construction, collaboration agent package, agent_package, builder, examples, "### crew: distribution pipeline", my role, crew compositions, new agent end, distribution pipeline]
density_score: 0.90
related:
  - bld_collaboration_agent
  - bld_collaboration_boot_config
  - agent-package-builder
  - bld_collaboration_instruction
  - bld_collaboration_system_prompt
---
# Collaboration: agent-package-builder
## My Role in Crews
I am a SPECIALIST. I answer ONE question: "how do I bundle this agent into a portable, self-contained, tier-validated package?"
I do not define agents. I do not write system prompts.
I package agent artifacts so they can be distributed and deployed on any compatible runtime.
## Crew Compositions
### Crew: "New Agent End-to-End"
```
  1. knowledge-card-builder -> "domain knowledge"
  2. agent-builder -> "agent definition"
  3. instruction-builder -> "execution steps"
  4. boot-config-builder -> "provider configuration"
  5. agent-package-builder -> "portable deployable package (manifest + files)"
```
### Crew: "Distribution Pipeline"
```
  1. agent-builder -> "agent definition"
  2. fallback-chain-builder -> "model degradation config"
  3. guardrail-builder -> "safety boundaries"
  4. agent-package-builder -> "self-contained bundle (minimal/standard/complete)"
```
## Handoff Protocol
### I Receive
- seeds: agent name, target tier (minimal/standard/complete/whitelabel)
- optional: file inventory, LP mapping overrides, token budget constraints
### I Produce
- agent_package artifact (manifest.yaml + tier-apownte files)
- committed to: `cex/P02/examples/p02_iso_{agent}/`
### I Signal
- signal: complete (with quality score from QUALITY_GATES)
- if quality < 8.0: signal retry with failure reasons
## Builders I Depend On
- agent-builder: provides agent definition to package
- boot-config-builder: provides provider configs included in package
- instruction-builder: provides execution steps included in package
- fallback-chain-builder: provides degradation config for resilient packages
## Builders That Depend On Me
| Builder | Why |
|---------|-----|
| _builder-builder | Meta-builder ensures package structure follows conventions |

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[bld_collaboration_agent]] | sibling | 0.64 |
| [[bld_collaboration_boot_config]] | sibling | 0.53 |
| [[agent-package-builder]] | upstream | 0.44 |
| [[bld_collaboration_instruction]] | sibling | 0.41 |
| [[bld_collaboration_system_prompt]] | sibling | 0.38 |
