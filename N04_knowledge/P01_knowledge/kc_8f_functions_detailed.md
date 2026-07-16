---
quality: null
id: kc_8f_functions_detailed
kind: knowledge_card
kc_type: meta_kc
pillar: P01
nucleus: N04
version: 1.0.0
created: "2026-06-03"
updated: "2026-06-03"
author: n04_knowledge
title: "The 8 Functions of 8F -- In Detail (Class Reference)"
domain: meta
subdomain: pipeline_functions
tags: [8f, pipeline, constrain, become, inject, reason, call, produce, govern, collaborate, teaching, reference]
tldr: "Per-function reference for the 8F reasoning protocol: for each of F1 CONSTRAIN through F8 COLLABORATE, what it does, its input, its output, and a one-line example. A single intent -- 'make me a landing page' -- is threaded through all eight so a class can watch one artifact move down the line."
when_to_use: "Teaching 8F live; onboarding a new nucleus or contributor; quick lookup of what any single 8F function consumes and produces."
keywords: [8f functions, constrain, become, inject, reason, call, produce, govern, collaborate, sub-steps, 8f trace, mode a, mode b, pipeline reference]
density_score: null
related:
  - kc_8f_pipeline_implementation
  - p01_kc_concept_graph
---

# The 8 Functions of 8F -- In Detail

8F is how CEX thinks. Every task -- research, copy, code, deploy, orchestrate -- runs the
same eight functions in order. Each function has one job, reads the state the prior
functions produced, and adds its own. This card is the per-function reference: for every
function, **what it does, what goes in, what comes out, and a one-line example.** The
running example is a single intent -- *"make me a landing page"* -- followed end to end so
you can watch one artifact move down the assembly line.

## The Pipeline at a Glance

```
INTENT -> F1 -> F2 -> F3 -> F4 -> F5 -> F6 -> F7 -> F8 -> ARTIFACT
         CON   BEC   INJ   REA   CAL   PRO   GOV   COL
```

| F# | Name | The question it answers |
|----|------|-------------------------|
| F1 | CONSTRAIN | What are the rules? |
| F2 | BECOME | Who am I? |
| F3 | INJECT | What do I know? |
| F4 | REASON | How will I build it? |
| F5 | CALL | What can I use? |
| F6 | PRODUCE | Make it. |
| F7 | GOVERN | Does it pass? |
| F8 | COLLABORATE | Ship it. |

## The 8 Functions in Detail

### F1 CONSTRAIN -- "What are the rules?"
Resolves the kind and loads every limit that bounds the artifact, before any creative work starts.
- **Input:** raw user intent + the kind it resolves to
- **Output:** constraints (pillar, max_bytes, id pattern, naming rule, schema)
- **Example:** "make me a landing page" -> kind=landing_page, pillar=P05, max=8KB

### F2 BECOME -- "Who am I?"
Loads the builder's identity so the model writes as the right specialist, not a generic assistant.
- **Input:** the builder ISOs for the resolved kind
- **Output:** identity (persona, voice, domain, knowledge boundary)
- **Example:** load landing-page-builder persona -- conversion-focused, mobile-first

### F3 INJECT -- "What do I know?"
Pulls all relevant knowledge into context. The heaviest function -- up to ~9 sources.
- **Input:** kind KC + few-shot examples + build memory + brand + retrieved similar artifacts
- **Output:** a knowledge bundle + a Template-First match score
- **Example:** load kc_landing_page + 2 past pages + brand_config (match 72%)

### F4 REASON -- "How will I build it?"
Plans the artifact before writing it. Also the GDP gate: unresolved user decisions halt the run here.
- **Input:** everything F1-F3 accumulated
- **Output:** a build plan (sections, density target, template / hybrid / fresh approach)
- **Example:** plan 12 sections, mobile-first, reuse the matched template

### F5 CALL -- "What can I use?"
Inventories available tools and scans for existing similar artifacts to avoid duplicate work.
- **Input:** the tools ISO + the pillar's existing artifacts
- **Output:** a tool list + artifacts to reuse or differentiate against
- **Example:** compile + doctor + index ready; 3 similar pages found

### F6 PRODUCE -- "Make it."
Composes the full prompt from all prior state and calls the model once to generate the artifact.
- **Input:** the assembled prompt (identity + constraints + knowledge + plan + tools)
- **Output:** the raw artifact -- frontmatter + body, with quality: null
- **Example:** emit a responsive HTML landing page (dark mode, SEO, a11y)

### F7 GOVERN -- "Does it pass?"
Validates against hard gates and scores soft dimensions. Retries F6 on failure (max 2).
- **Input:** the produced artifact
- **Output:** a verdict (hard gates pass/fail, soft score, issues to fix)
- **Example:** 9.0/10, 7/7 hard gates pass -> accept

### F8 COLLABORATE -- "Ship it."
Saves, compiles, indexes, commits, and signals. The artifact formally enters the system.
- **Input:** the validated artifact
- **Output:** saved file + compiled .yaml twin + git commit + completion signal
- **Example:** save P05/landing_x.md, compile, commit, signal N07

## Sub-Steps (the optional half-functions)

These hang off a main function and run only when relevant. Knowing they exist explains the
F2b / F3b / F3c / F7b / F7c markers you see in a trace.

| Sub-step | Hangs off | Job |
|----------|-----------|-----|
| F2b SPEAK | F2 | Load the controlled vocabulary so output uses canonical terms (no drift) |
| F3b PERSIST | F3 | Declare new entities / facts / learnings to save back to memory |
| F3c GROUND | F3 | Record provenance for each cited source (path, confidence, freshness) |
| F7b LEARN | F7 | Capture reward + regression signals from the score for next time |
| F7c COUNCIL | F7 | Cross-provider judges vote; block publish if divergence > 0.3 |

## Reading an 8F Trace

Every build prints a trace proving all eight functions ran. No trace = no proof = rejected.

```
=== 8F PIPELINE ===
F1 CONSTRAIN: kind=landing_page, pillar=P05, max=8192B
F2 BECOME: landing-page-builder loaded (12 ISOs)
F3 INJECT: kc_landing_page + 2 examples. Match: 72%
F4 REASON: 12 sections, approach=template
F5 CALL: compile+doctor+index ready. 3 similar found.
F6 PRODUCE: 6,400 bytes, 12 sections, density=0.88
F7 GOVERN: 9.0/10. Gates: 7/7.
F8 COLLABORATE: saved P05/landing_x.md. Compiled. Committed.
===================
```

## Mode A vs Mode B

The same eight functions run in one of two modes, auto-detected from the model tier:
- **Mode A (monolithic):** one capable model (Opus, Sonnet) runs F1 -> F8 end to end.
- **Mode B (decomposed):** Opus/Sonnet plans F1-F4 into a prompt_package, a cheap model
  runs F6 PRODUCE, and tools run F7-F8. Used for cheaper kinds; ~25-30% of solo cost.

## Related Artifacts

| Artifact | Relationship | Score |
|----------|-------------|-------|
| kc_8f_pipeline | upstream | 0.55 |
| [[kc_8f_pipeline_implementation]] | related | 0.42 |
| pattern_8f_full_trace | sibling | 0.40 |
| reasoning_trace_8f_constrain | sibling | 0.38 |
| p01_kc_8f_pipeline | upstream | 0.35 |
