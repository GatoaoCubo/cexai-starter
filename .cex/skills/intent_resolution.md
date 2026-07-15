---
name: intent-resolution
description: Auto-resolve free-form user input into a typed CEX tuple kind+pillar+nucleus+verb before any 8F pipeline starts so dispatch is precise.
when:
  - Free-form user input mentions kind-like nouns such as agent, card, workflow, prompt, or schema.
  - Any /build, /mission, or /plan invocation runs without a pre-resolved kind.
  - The LLM is about to dispatch work without first calling the prompt compiler.
kind: skill
pillar: P04
nucleus: all
quality: null
version: 1.0.0
created: 2026-04-27
updated: 2026-04-27
multi_runtime: true
runtimes: [claude, codex, gemini, ollama]
density_score: 0.88
tags: [skill, autofire, intent, transmutation, autowire, layer6]
related:
  - p03_pc_cex_universal
  - n07-input-transmutation
  - p01_kc_prompt_compiler
  - 8f-reasoning
---

# Intent Resolution

## When this fires
- User input is free-form and mentions kind-like nouns (agent, card, workflow, prompt, schema, retriever, judge, evaluation, persona).
- A nucleus is about to enter F1 CONSTRAIN without a resolved {kind, pillar, nucleus, verb} tuple.
- /build, /plan, or /mission is invoked without explicit kind resolution.

## What to do
1. Run `python _tools/cex_intent_resolver.py --input "<user phrase>" --json` BEFORE F1 CONSTRAIN.
2. Read the returned tuple {kind, pillar, nucleus, verb, confidence}.
3. If confidence >= 0.6, proceed with F1 using the resolved tuple as the canonical scope.
4. If confidence < 0.6, present the top-3 candidates to the user via the gdp-on-subjective skill instead of guessing.
5. Cache the resolved tuple in `.cex/runtime/last_intent.json` so generic boots can reuse it.
6. Always load `N00_genesis/P03_prompt/layers/p03_pc_cex_universal.md` as the source-of-truth pattern table when the resolver needs an arbitration tie-break.
7. Skip resolution only when the user explicitly types a fully-qualified kind (e.g. `/build kind=knowledge_card pillar=P01`).

## Example
- User types `make me a landing page about Black Friday`. Skill auto-fires resolver, gets `{kind=landing_page, pillar=P05, nucleus=N02, verb=create, confidence=0.92}`, and N07 dispatches landing-page-builder without asking the user for the kind.

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[p03_pc_cex_universal]] | upstream | 0.80 |
| n07-input-transmutation | upstream | 0.75 |
| p01_kc_prompt_compiler | sibling | 0.65 |
| 8f-reasoning | upstream | 0.55 |
