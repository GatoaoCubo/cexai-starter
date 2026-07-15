---
id: guide
kind: instruction
pillar: P08
title: "Guide"
description: "Guided Decision Mode -- ask me before building. Usage: /guide [goal]"
version: "1.0.0"
author: cexai
quality: null
tags: [command, gdp, co-pilot, lean, solo]
tldr: "Co-pilot mode -- surface the subjective decisions, lock them to the manifest via cex_gdp, then build in-session."
domain: "tenant CEXAI"
related:
  - build
  - validate
---

# /guide -- co-pilot mode (Guided Decisions)

Switch from "assume everything" to "ask, then build". Use this whenever a goal
has **subjective** choices (audience, tone, layout, CTA, brand voice).

## Behaviour

### 1. Identify what needs deciding
From the goal in `$ARGUMENTS`, list the subjective decisions only (structure,
code and file naming are handled for you). Example:

```
Goal: "build a landing page"
I need your call on 3 things before I start:
  1. Who is it for?        (audience)
  2. What is the message?  (hero copy)
  3. What should they do?  (CTA)
```

### 2. Present decision points
For each decision: 3-5 numbered options, one marked Recommended (with a reason),
free-text always accepted. Ask 2-3 at a time, preview between rounds.

### 3. Lock the decisions
Record the answers to the decision manifest
(`.cex/runtime/decisions/decision_manifest.yaml`) so the build is reproducible:

```bash
python _tools/cex_gdp.py --pending                          # see open decisions
python _tools/cex_gdp.py --resolve <id> "<choice>" --rationale "<why>"
python _tools/cex_gdp.py --status                           # confirm all resolved
```

### 4. Build
Once the manifest is complete, drop GDP and build in-session:

```bash
python _tools/cex_8f_runner.py "<goal>" --execute --verbose
```

## Exit rules
- "you decide" / "just do it" -> apply every Recommended option, flag auto-filled.
- "skip" on one decision -> apply its Recommended option.
- All decisions resolved -> guide mode ends, build proceeds.

## The rule
When in doubt, `/guide`. When the manifest exists, build. Every subjective
choice you make up front is a revision you avoid later.
