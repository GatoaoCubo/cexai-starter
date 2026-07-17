---
id: evolve
kind: instruction
pillar: P11
title: "Evolve"
description: "Autonomously improve an artifact until it hits a quality target. Usage: /evolve <file>"
version: "1.0.0"
author: cexai
quality: null
tags: [command, evolve, autoresearch, quality, autonomous, solo]
tldr: "Autonomous artifact-improvement loop. Python drives it, the LLM suggests one change at a time, cex_score.py is the immutable metric, each round is kept or discarded, budget-tracked."
domain: "tenant CEXAI"
related:
  - validate
  - build
---

You want to autonomously improve an artifact until it reaches a quality target.
`/evolve` runs the AutoResearch loop: Python drives it, the LLM proposes ONE
change at a time, `cex_score.py` scores it (the immutable metric), and each round
is kept (committed) or discarded (restored) -- budget-tracked, stops at the target
or when the budget runs out. You never babysit it.

## Two modes

### agent -- deep improvement (LLM)
```bash
python _tools/cex_evolve.py agent <file>
python _tools/cex_evolve.py agent <file> --budget 50000 --target 9.0 --max-rounds 10
```
The loop: read the artifact -> LLM suggests ONE improvement + new content -> apply
-> `cex_score.py` -> keep (commit) or discard (restore) -> check budget -> continue
or stop. This is the real AutoResearch: budget-enforced, tracked, autonomous.

### heuristic -- fast, no LLM (batch)
```bash
python _tools/cex_evolve.py single <file> --target 9.0
python _tools/cex_evolve.py sweep --target 8.5
python _tools/cex_evolve.py report
```
Python-only mechanical fixes (frontmatter, whitespace, filler). Use for batch
scoring or when LLM budget is tight.

## When to use which

| Situation | Mode |
|-----------|------|
| Improve one important artifact deeply | `agent` |
| "make this better" | `agent` |
| Score / clean many artifacts fast | `sweep` |
| You are away for hours | `agent --budget 200000` |

The metric (`cex_score.py`) is immutable -- the loop can never game its own score.
That is what makes the autonomous improvement trustworthy: the brain gets sharper
with use, on its own, without ever grading its own homework.
