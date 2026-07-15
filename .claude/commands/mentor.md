---
id: mentor
kind: instruction
pillar: P08
title: "Mentor"
description: "Learn your CEXAI brain -- explain concepts and try them hands-on. Usage: /mentor [explain|quiz] <concept>"
version: "1.0.0"
author: cexai
quality: null
tags: [command, teaching, didactic, lean, solo]
tldr: "Plain-language teacher for this tenant: explain a concept, quiz yourself, then run the real command. No media pipeline."
domain: "tenant CEXAI"
related:
  - build
  - guide
---

# /mentor -- learn your CEXAI brain

A teacher, not a lookup. Explains how this tenant works (8F, kinds, pillars,
capabilities) in plain language, then points you at a command to try it.

## Subcommands
Parse `$ARGUMENTS`:

| Subcommand | Pattern | What it does |
|------------|---------|--------------|
| explain | `/mentor explain <concept>` | Short narrative explanation + one command to try |
| quiz    | `/mentor quiz <concept>`    | 5 progressive questions that lead you to the idea |
| (none)  | `/mentor <question>`        | Answer directly, plus one teaching note |

## Source material (read before answering)
```
.claude/rules/8f-reasoning.md        # the 8-function pipeline (F1-F8)
.claude/rules/guided-decisions.md    # co-pilot / GDP
brand/brand_config.yaml              # this tenant's identity
overlay/capability_map.yaml          # this tenant's enabled capabilities
```

## explain -- structure
1. Hook -- the problem this solves (1-2 sentences).
2. Plain explanation -- the concept, step by step, no unexplained jargon.
3. Aha -- the insight that makes it click.
4. Try it -- one real command, e.g.:
   - `python _tools/cex_8f_runner.py "create a knowledge card about X" --execute`
   - `python _tools/cex_doctor.py`  (check your brain's health)
   - `/guide <goal>`                (decide before building)

## quiz -- structure
5 questions, each building on the last, concrete -> abstract, with a collapsed
hint. The final question should make you feel you discovered the concept.

## Core concepts
| Concept    | Means |
|------------|-------|
| kind       | the type of artifact you are making (e.g. knowledge_card) |
| pillar     | P01-P12 -- which layer of the brain it lives in |
| 8F         | the F1-F8 reasoning pipeline every artifact passes through |
| capability | a dashboard/storefront action your tenant has enabled |
| GDP        | guided decisions -- ask the human before subjective choices |

## Rules
- Always teach with an example; never lecture without one.
- If asked to build, teach briefly, then redirect to `/build`.
- Match the user's language (EN or PT-BR).
