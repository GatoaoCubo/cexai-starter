---
id: p05_qs_cexai_operator
kind: quickstart_guide
pillar: P05
title: "CEXAI Operator Quickstart -- First Artifact in 15 Minutes"
version: "1.0.0"
created: "2026-06-09"
updated: "2026-06-09"
author: N04_knowledge
domain: operator_onboarding
quality: null
tags: [quickstart, operator, onboarding, getting_started, no_code]
tldr: "Clean machine to first CEXAI artifact in under 15 minutes. No prior AI/coding experience required."
prerequisites:
  - "Python 3.12+"
  - "Node.js 18+ (for the Claude CLI)"
  - "git 2.40+"
  - "Claude Code CLI"
  - "Anthropic Max subscription OR ANTHROPIC_API_KEY"
keywords:
  - "first artifact"
  - "operator onboarding"
  - "cexai quickstart"
  - "/init"
  - "/build"
  - "no-code workflow"
related:
  - p05_of_cexai_first_mission
  - p06_ar_cex_cli
  - p01_faq_cexai_user
  - p05_qs_first_builder
density_score: 0.95
---

> **[DISTILL ANNOTATION]** This file cites tool(s) not shipped in this tenant (Central-only): cex_hooks, cex_install. Inline citations are marked `[NOT SHIPPED in this tenant -- Central-only tool]`.

## Overview

CEXAI is an AI brain for your company -- a typed knowledge system that turns conversations into
structured, governed, reusable artifacts. This guide gets you from a clean machine to your first
artifact in under 15 minutes. No coding experience required.

**What you will have at the end:** a real, versioned knowledge artifact saved in your repo,
validated by the quality engine, and ready to feed into your AI workflows.

---

## Prerequisites

| Requirement | Version | How to install |
|-------------|---------|----------------|
| Python | 3.12+ | [python.org](https://www.python.org/downloads/) or `winget install Python.Python.3.12` |
| Node.js | 18+ LTS | [nodejs.org](https://nodejs.org/) or `winget install OpenJS.NodeJS.LTS` |
| git | 2.40+ | [git-scm.com](https://git-scm.com/downloads) or `winget install Git.Git` |
| Claude Code CLI | latest | `npm install -g @anthropic-ai/claude-code` |
| Anthropic auth | Max OR API key | Sign into Claude OR set `ANTHROPIC_API_KEY` in your shell |

**Verify all are installed:**

```bash
python --version    # expect: Python 3.12.x
node --version      # expect: v18.x.x or higher
git --version       # expect: git version 2.40.x or higher
claude --version    # expect: a version string
```

If any check fails, install the missing item before continuing.

> **Don't want to install these by hand?** You only need Python + git to start --
> Step 1 shows the one-command `cex_install` path that auto-installs the Claude CLI,
> Python packages, and the local runtime for you.

---

## Step 1 -- Install CEXAI (2 min)

<!-- [N02 narrative sweep 2026-07-14, DP_B]: the engine repo is closed; this
     tenant repo already IS the clone. Removed the "clone the engine" step. -->
**You already have the repo.** This tenant IS the clone (a sovereign,
pre-fabricated CEXAI brain) -- no `git clone` needed. **Turnkey path
(recommended).** Let CEXAI install every other dependency in one command:

```bash
python _tools/cex_install.py        # detect + auto-install all missing deps, then validate  <!-- [NOT SHIPPED in this tenant -- Central-only tool] -->
python _tools/cex_hooks.py install  # activate the quality-gate pre-commit hook  <!-- [NOT SHIPPED in this tenant -- Central-only tool] -->
```

`cex_install` reads the frozen dependency manifest and auto-installs each missing
required + recommended item (Claude CLI, Python packages, local Ollama runtime, ...),
then re-validates -- no per-step prompts. Want to look first? `--dry-run` previews
without changing anything; `--plan-only` plans without installing.

**Manual path (fallback).** Prefer to install dependencies yourself? Replace the
`cex_install` line above with the editable install:

```bash
pip install -e ".[dev]"
```

**Expected outcome:** no errors. Dependencies are installed and the quality-gate
pre-commit hook is active.

---

## Step 2 -- Health Check (1 min)

```bash
python _tools/cex_doctor.py
```

**Expected outcome:** `0 FAIL` in the summary line. If you see FAILs on a fresh clone,
check your Python version (must be 3.12+) and re-run `pip install -e ".[dev]"`.

---

## Step 3 -- Bootstrap Your Brand (2 min)

CEXAI tailors every artifact to your brand. Run `/init` once to configure it:

```bash
claude   # opens Claude Code CLI in this repo
# then type in the chat:
/init
```

CEXAI will ask you 5 short questions (brand name, tagline, values, voice, audience).
Your answers write `.cex/brand/brand_config.yaml` -- all nuclei auto-inject your brand
from this point forward.

**Expected outcome:** `"Done! CEXAI is now configured for [YOUR BRAND]."` message.
File `.cex/brand/brand_config.yaml` is created.

---

## Step 4 -- Build Your First Artifact (5 min)

Inside the Claude Code CLI session from Step 3, use `/build` with a plain-English intent:

```
/build knowledge card about our main product features
```

CEXAI runs the 8F pipeline automatically:
- F1: resolves `kind=knowledge_card, pillar=P01`
- F2-F5: loads builder ISOs, injects brand context
- F6: generates a structured markdown artifact
- F7: validates quality (must score >= 8.0 to save)
- F8: saves to the correct pillar directory, commits

**Expected outcome:** a file appears in `N04_knowledge/P01_knowledge/` with your
artifact. The final line of output shows the saved path and quality score.

Other example intents you can try:
- `/build FAQ entry answering "what does your product do?"`
- `/build agent that helps customers with onboarding`
- `/build system prompt for a customer support assistant`

---

## Step 5 -- Verify Your Artifact (1 min)

```bash
python _tools/cex_doctor.py
```

**Expected outcome:** `0 FAIL`. Your new artifact passes all quality gates.

---

## What Just Happened

```
Your intent (5 words)
        |
  F1 CONSTRAIN  -> kind=knowledge_card, pillar=P01, schema loaded
  F2 BECOME     -> knowledge-card-builder loaded (12 ISOs)
  F3 INJECT     -> brand voice, domain context, similar artifacts
  F4 REASON     -> plan: sections, approach, density target
  F6 PRODUCE    -> full artifact with frontmatter + structured body
  F7 GOVERN     -> 6 universal gates + kind-specific gates
  F8 COLLABORATE -> saved, compiled, committed
        |
  Production-ready artifact
```

The 8F pipeline is the force multiplier. Your 5-word input became a governed,
versioned, structured knowledge asset. Every `/build` call does the same.

---

## Troubleshooting

| Symptom | Cause | Fix |
|---------|-------|-----|
| `pip install -e ".[dev]"` fails | Build tools missing | `pip install --upgrade pip setuptools wheel` first |
| `cex_doctor.py` shows FAIL on fresh clone | Python 3.11 or older | Upgrade to Python 3.12+ |
| `claude` command not found | Claude Code CLI not installed | `npm install -g @anthropic-ai/claude-code` |
| `/build` produces no file | Quality gate failed (score < 8.0) | Retry with a more specific intent |
| Pre-commit hook blocks commit | Non-ASCII in a `.py` file | `python _tools/cex_sanitize.py --fix --scope _tools/` |

---

## Next Steps

| Goal | Command |
|------|---------|
| Run a full mission (plan -> build -> consolidate) | [[p05_of_cexai_first_mission]] |
| See all CLI tool flags | [[p06_ar_cex_cli]] |
| Common questions answered | p01_faq_cexai_user |
| Contribute a new builder | [[p05_qs_first_builder]] |

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[p05_of_cexai_first_mission]] | downstream | 0.80 |
| p01_faq_cexai_user | downstream | 0.75 |
| [[p06_ar_cex_cli]] | downstream | 0.70 |
| [[p05_qs_first_builder]] | sibling | 0.50 |
| [[p01_faq_cex_common_questions]] | sibling | 0.40 |
