---
kind: collaboration
id: bld_collaboration_fallback_chain
pillar: P12
llm_function: COLLABORATE
purpose: How fallback-chain-builder works in crews with other builders
pattern: each builder must know its ROLE in a team, what it RECEIVES and PRODUCES
quality: null
title: "Collaboration Fallback Chain"
version: "1.0.0"
author: n03_builder
tags: [fallback_chain, builder, examples]
tldr: "Golden and anti-examples for fallback chain construction, demonstrating ideal structure and common pitfalls."
domain: "fallback chain construction"
created: "2026-04-07"
updated: "2026-04-07"
8f: "F8_collaborate"
keywords: [fallback chain construction, collaboration fallback chain, fallback_chain, builder, examples, "### crew: full dispatch setup", my role, crew compositions, resilient agent deployment, full dispatch setup]
density_score: 0.90
related:
  - bld_collaboration_boot_config
  - bld_collaboration_dispatch_rule
  - bld_collaboration_agent
  - bld_collaboration_model_provider
  - bld_collaboration_agent_package
---
# Collaboration: fallback-chain-builder
## My Role in Crews
I am a SPECIALIST. I answer ONE question: "what sequence of models should be tried when the primary fails?"
I do not sequence prompts. I do not define routing rules.
I design model degradation chains so systems remain available when primary models fail or exceed limits.
## Crew Compositions
### Crew: "Resilient Agent Deployment"
```
  1. agent-builder -> "agent definition"
  2. boot-config-builder -> "provider configuration"
  3. fallback-chain-builder -> "model degradation sequence (e.g., opus -> sonnet -> haiku)"
  4. benchmark-builder -> "latency/cost baselines per model tier"
```
### Crew: "Full Dispatch Setup"
```
  1. dispatch-rule-builder -> "routing rules to primary target"
  2. fallback-chain-builder -> "degradation path when primary fails"
  3. guardrail-builder -> "safety boundaries during degradation"
```
## Handoff Protocol
### I Receive
- seeds: primary model, fallback models in order, quality threshold per step
- optional: timeout per step, circuit breaker config, cost budget, max retries
### I Produce
- fallback_chain artifact (.md + .yaml frontmatter)
- committed to: `cex/P02/examples/p02_fallback_{scope}.md`
### I Signal
- signal: complete (with quality score from QUALITY_GATES)
- if quality < 8.0: signal retry with failure reasons
## Builders I Depend On
- benchmark-builder: provides latency/cost data to calibrate timeouts and thresholds
- boot-config-builder: provides provider constraints that affect fallback viability
## Builders That Depend On Me
| Builder | Why |
|---------|-----|
| dispatch-rule-builder | References fallback chain as alternative routing path |
| agent-package-builder | Includes fallback config in portable agent package |

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[bld_collaboration_boot_config]] | sibling | 0.45 |
| bld_collaboration_dispatch_rule | sibling | 0.43 |
| [[bld_collaboration_agent]] | sibling | 0.42 |
| [[bld_collaboration_model_provider]] | sibling | 0.40 |
| [[bld_collaboration_agent_package]] | sibling | 0.38 |
