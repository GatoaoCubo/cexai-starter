---
kind: collaboration
id: bld_collaboration_few_shot_example
pillar: P12
llm_function: COLLABORATE
purpose: How few-shot-example-builder works in crews with other builders
pattern: each builder must know its ROLE in a team, what it RECEIVES and PRODUCES
quality: null
title: "Collaboration Few Shot Example"
version: "1.0.0"
author: n03_builder
tags: [few_shot_example, builder, examples]
tldr: "Golden and anti-examples for few shot example construction, demonstrating ideal structure and common pitfalls."
domain: "few shot example construction"
created: "2026-04-07"
updated: "2026-04-07"
8f: "F8_collaborate"
keywords: [few shot example construction, collaboration few shot example, few_shot_example, builder, examples, "### crew: format teaching", my role, crew compositions, prompt quality stack, format teaching]
density_score: 0.90
related:
  - bld_collaboration_action_prompt
  - bld_collaboration_golden_test
  - bld_collaboration_input_schema
  - few-shot-example-builder
  - bld_collaboration_response_format
---
# Collaboration: few-shot-example-builder
## My Role in Crews
I am a SPECIALIST. I answer ONE question: "what input/output pair best teaches this format?"
I do not evaluate quality. I do not test correctness.
I craft format-exemplifying pairs so prompts can teach LLMs the expected output shape.
## Crew Compositions
### Crew: "Prompt Quality Stack"
```
  1. context-doc-builder -> "domain context"
  2. action-prompt-builder -> "task-focused prompt"
  3. few-shot-example-builder -> "input/output examples for the prompt"
  4. golden-test-builder -> "quality reference for evaluation"
```
### Crew: "Format Teaching"
```
  1. input-schema-builder -> "input contract definition"
  2. few-shot-example-builder -> "examples that demonstrate the format"
  3. formatter-builder -> "output formatting rules"
```
## Handoff Protocol
### I Receive
- seeds: target format/artifact type, difficulty level (easy/medium/hard)
- optional: edge cases to cover, domain context, output schema
### I Produce
- few_shot_example artifact (.md + .yaml, max 1024 bytes)
- committed to: `cex/P01/examples/p01_fewshot_{scope}.md`
### I Signal
- signal: complete (with quality score from QUALITY_GATES)
- if quality < 8.0: signal retry with failure reasons
## Builders I Depend On
- input-schema-builder: provides the format contract that examples must demonstrate
## Builders That Depend On Me
| Builder | Why |
|---------|-----|
| action-prompt-builder | Embeds few-shot examples in task prompts |
| chain-builder | Uses examples to calibrate chain step outputs |
| golden-test-builder | References examples as starting point for quality refs |

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[bld_orchestration_action_prompt]] | sibling | 0.51 |
| [[bld_orchestration_golden_test]] | sibling | 0.44 |
| [[bld_orchestration_input_schema]] | sibling | 0.42 |
| [[few-shot-example-builder]] | upstream | 0.41 |
| [[bld_orchestration_response_format]] | sibling | 0.39 |
