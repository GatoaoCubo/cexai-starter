---
kind: collaboration
id: bld_collaboration_reverse_prompt
pillar: P03
llm_function: COLLABORATE
purpose: How reverse-prompt-builder works in crews with other builders and the canonical synthesizer tool
pattern: each builder must know its ROLE in a team, what it RECEIVES and PRODUCES
quality: null
title: "Collaboration Reverse Prompt"
version: "1.0.0"
author: n03_builder
tags: [reverse_prompt, builder, examples]
tldr: "This builder is a documentarian/repair specialist, never a competitor to GitReverseSynthesizer for real syntheses; crew compositions cover documentation, repair, and judge-calibration."
domain: "reverse prompt construction"
created: "2026-07-03"
updated: "2026-07-03"
8f: "F3_inject"
keywords: [reverse prompt construction, collaboration reverse prompt, reverse_prompt, builder, examples, crew compositions, my role, handoff protocol, calibration pilot]
density_score: 0.90
related:
  - bld_collaboration_prompt_template
  - reverse-prompt-builder
  - p03_ins_reverse_prompt
  - bld_memory_reverse_prompt
  - bld_eval_reverse_prompt
---
# Collaboration: reverse-prompt-builder
## My Role in Crews
I am a NARROW documentarian / repair specialist. I answer: "what does a hand-authored, provenance-disclosed reverse_prompt draft look like, when the real synthesizer cannot or should not run?" I do NOT compete with `GitReverseSynthesizer` for real syntheses.
## Crew Compositions
### Crew: "Repo Synthesis Pipeline (canonical)"
```
  1. GitReverseSynthesizer (tool, not a crew role) -> "extract + synthesize + write, deterministic"
  2. auto-research triangulator                    -> "folds the emitted reverse_prompt into Layer-1 context"
```
(This builder is NOT in this crew -- it is the canonical, tool-driven path.)
### Crew: "Kind Documentation Pack"
```
  1. reverse-prompt-builder  -> "hand-authored worked example for the kind-KC"
  2. knowledge-card-builder  -> "kc_reverse_prompt.md consuming the worked example"
  3. quality-gate-builder    -> "validates the documentation example against H01-H10"
```
### Crew: "Judge Calibration Pilot"
```
  1. reverse-prompt-builder  -> "produces calibration_pair drafts (varied stacks/audiences)"
  2. llm-judge-builder       -> "applies rubric_reverse_prompt_equivalence.md C1-C5"
  3. scoring-rubric-builder  -> "aggregates kappa across the 30-pair pilot"
```
## Handoff Protocol
### I Receive
- seeds: mode (document/dry_run/repair/calibration_pair), source_url, open_var values, (repair only) the original synthesizer-emitted file
- optional: `prompt_template` this instance fills, license text from a real LICENSE/COPYING extract
### I Produce
- `reverse_prompt` artifact (frontmatter + body, max 8192 bytes), committed to `records/pool/prompts/p03_rp_{{name}}.md`
### I Signal
- signal: complete (with quality score from H01-H10 + rubric where applicable)
- if quality < 8.0: signal retry with failure reasons
## Builders I Depend On
- prompt-template-builder: the fixed synthesis template this kind fills (`depends_on: [prompt_template]`)
- knowledge-card-builder: hosts the kind's canonical KC I cross-reference
## Builders That Depend On Me
| Builder | Why |
|---------|-----|
| llm-judge-builder | Consumes `calibration_pair` drafts for rubric piloting |
| knowledge-card-builder | May cite a hand-authored example I produce |

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[bld_collaboration_prompt_template]] | sibling | 0.41 |
| [[reverse-prompt-builder]] | related | 0.39 |
| [[p03_ins_reverse_prompt]] | sibling | 0.39 |
| [[bld_memory_reverse_prompt]] | sibling | 0.37 |
| [[bld_eval_reverse_prompt]] | sibling | 0.36 |
