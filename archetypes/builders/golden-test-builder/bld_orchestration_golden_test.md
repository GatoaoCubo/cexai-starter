---
kind: collaboration
id: bld_collaboration_golden_test
pillar: P12
llm_function: COLLABORATE
purpose: How golden-test-builder works in crews with other builders
pattern: each builder must know its ROLE in a team, what it RECEIVES and PRODUCES
quality: null
title: "Collaboration Golden Test"
version: "1.0.0"
author: n03_builder
tags: [golden_test, builder, examples]
tldr: "Golden and anti-examples for golden test construction, demonstrating ideal structure and common pitfalls."
domain: "golden test construction"
created: "2026-04-07"
updated: "2026-04-07"
8f: "F8_collaborate"
keywords: [golden test construction, collaboration golden test, golden_test, builder, examples, "### crew: builder calibration", my role, crew compositions, quality pipeline, builder calibration]
density_score: 0.90
related:
  - golden-test-builder
---
# Collaboration: golden-test-builder
## My Role in Crews
I am a SPECIALIST. I answer ONE question: "what does a perfect artifact of this kind look like?"
I do not define evaluation criteria. I do not measure performance.
I produce quality-calibration references so evaluation systems have a gold standard for comparison.
## Crew Compositions
### Crew: "Quality Pipeline"
```
  1. golden-test-builder -> "reference examples (quality 9.5+)"
  2. benchmark-builder -> "performance baselines"
  3. e2e-eval-builder -> "end-to-end pipeline validation against golden"
```
### Crew: "Builder Calibration"
```
  1. golden-test-builder -> "perfect artifact example for target kind"
  2. few-shot-example-builder -> "format examples derived from golden"
  3. action-prompt-builder -> "prompt calibrated to produce golden-quality output"
```
## Handoff Protocol
### I Receive
- seeds: target artifact kind, quality gates for that kind
- optional: existing high-quality artifacts (9.5+), rationale mapping
### I Produce
- golden_test artifact (.md + .yaml frontmatter with input/output/rationale)
- committed to: `cex/P07/examples/p07_golden_{kind}.md`
### I Signal
- signal: complete (with quality score from QUALITY_GATES)
- if quality < 8.0: signal retry with failure reasons
## Builders I Depend On
None — independent builder (layer 0). Golden tests are selected from existing high-quality output.
## Builders That Depend On Me
| Builder | Why |
|---------|-----|
| e2e-eval-builder | Compares pipeline output against golden reference |
| few-shot-example-builder | Derives format examples from golden artifacts |
| action-prompt-builder | Calibrates prompts using golden output as target |
| benchmark-builder | Uses golden output quality as performance ceiling |

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[bld_orchestration_few_shot_example]] | sibling | 0.38 |
| [[bld_orchestration_action_prompt]] | sibling | 0.36 |
| [[golden-test-builder]] | upstream | 0.35 |
| bld_collaboration_e2e_eval | sibling | 0.33 |
| [[bld_orchestration_prompt_version]] | sibling | 0.33 |
