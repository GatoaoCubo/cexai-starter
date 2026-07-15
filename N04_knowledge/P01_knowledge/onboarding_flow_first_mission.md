---
id: p05_of_cexai_first_mission
kind: onboarding_flow
pillar: P05
title: "CEXAI Operator Onboarding -- Your First /mission End-to-End"
version: "1.0.0"
created: "2026-06-09"
updated: "2026-06-09"
author: N04_knowledge
domain: operator_onboarding
quality: null
tags: [onboarding, mission, operator, workflow, plan, guide, spec, grid, consolidate]
tldr: "Step-by-step walkthrough of the /plan -> /guide -> /spec -> /grid -> /consolidate workflow. What you decide vs what CEXAI does."
prerequisites:
  - "CEXAI installed and brand bootstrapped (see [[p05_qs_cexai_operator]])"
  - "Claude Code CLI open in the cex repo"
keywords:
  - "/plan /guide /spec /grid /consolidate"
  - "first mission"
  - "operator onboarding"
  - "no-code workflow"
  - "guided decisions"
  - "autonomous dispatch"
related:
  - quickstart_guide_cexai_operator
  - faq_entry_cexai_user
  - api_reference_cex_cli
density_score: 0.95
---

## Overview

A CEXAI `/mission` is the full autonomous lifecycle: you define the goal, CEXAI builds everything.
The workflow has 5 stages. At each stage, the boundary between **what you decide** and **what
CEXAI does** is explicit -- you never lose control, and CEXAI never wastes your time on
mechanical work.

```
/plan -> /guide -> /spec -> /grid -> /consolidate
  |         |        |        |           |
  |         |        |        |           +-- verify + score + clean
  |         |        |        +-------------- dispatch nuclei (autonomous)
  |         |        +----------------------- spec blueprint
  |         +-------------------------------- you decide (co-pilot)
  +------------------------------------------ decompose goal into tasks
```

**Total time for a first mission:** 15-30 min (2-3 min of your decisions + build time).

---

## Stage 1 -- /plan (You: define the goal)

**What you do:** type `/plan` followed by your goal in plain English.

```
/plan build a customer onboarding knowledge base for our SaaS product
```

**What CEXAI does:**
- Resolves your goal into CEX taxonomy (kinds, pillars, nuclei)
- Identifies which artifacts to build and in what order
- Maps dependencies (what must exist before what)
- Outputs a structured task list

**What you see:**
```
Plan for: customer onboarding knowledge base
  Task 1: knowledge_card -- "onboarding concepts" (N04, P01)
  Task 2: faq_entry set  -- "common customer questions" (N04, P01)
  Task 3: agent          -- "onboarding assistant" (N03, P02)
  Task 4: system_prompt  -- "onboarding assistant voice" (N03, P03)
  Dependencies: Task 3 needs Task 1 and Task 4
  Nuclei: N04 (knowledge), N03 (engineering)
```

**Decision you make:** does this plan match your intent? Add or remove tasks, or say
"looks good" to move to /guide.

---

## Stage 2 -- /guide (You: make the subjective decisions)

**What you do:** respond to CEXAI's questions about the WHAT (goals, audience, tone, scope).

```
/guide
```

CEXAI presents Decision Points (DPs) -- one by one, only the choices that are genuinely yours
to make. It never asks you about technical details (those are CEXAI's domain).

Example DPs you will see:

| Decision Point | Example options | Who decides |
|---------------|----------------|-------------|
| Audience | "enterprise IT teams" vs "individual freelancers" | YOU |
| Tone | "formal + technical" vs "friendly + casual" | YOU |
| Depth | "overview (2-3 pages)" vs "comprehensive (10+ pages)" | YOU |
| Scope | "English only" vs "EN + PT-BR" | YOU |

**What CEXAI does:**
- Records your answers in `.cex/runtime/decisions/decision_manifest.yaml`
- This manifest is the single source of truth -- passed to every nucleus at dispatch
- Nuclei never re-ask you the same questions

**Decision you make:** answer each DP. Say "you decide" for any DP you want CEXAI to
choose optimally. The co-pilot ends when all DPs are resolved.

---

## Stage 3 -- /spec (CEXAI: blueprint)

**What you do:** type `/spec` (or it runs automatically after /guide).

```
/spec
```

**What CEXAI does:**
- Generates an exact spec: for each artifact, its kind, pillar, target nucleus,
  quality target, and expected content
- Writes the spec to `.cex/runtime/decisions/`
- No LLM calls to nuclei yet -- this is planning, not building

**What you see:**
```
Spec: customer_onboarding_kb
  Artifact 1: kc_onboarding_concepts.md   kind=knowledge_card  N04  quality>=9.0
  Artifact 2: faq_entry_customer_q.md     kind=faq_entry       N04  quality>=9.0
  Artifact 3: agent_onboarding.md         kind=agent           N03  quality>=9.0
  Artifact 4: sp_onboarding_voice.md      kind=system_prompt   N03  quality>=9.0
  Grid: Wave 1 = N04 (no deps) + Wave 2 = N03 (after Wave 1)
```

**Decision you make:** approve the spec or request changes. Your approval unlocks /grid.

---

## Stage 4 -- /grid (CEXAI: autonomous build)

**What you do:** type `/grid` to dispatch the build.

```
/grid
```

**What CEXAI does (fully autonomous from here):**
1. Dispatches nuclei in waves (respecting dependency order)
2. Each nucleus receives a handoff file with: the task, your decisions from the manifest,
   artifact references to read before producing
3. Each nucleus runs the 8F pipeline internally:
   F1 CONSTRAIN -> F2 BECOME -> F3 INJECT -> F4 REASON -> F5 CALL -> F6 PRODUCE -> F7 GOVERN -> F8 COLLABORATE
4. F7 validates quality (must >= 8.0 to save; retries if below)
5. F8 saves, compiles, commits, signals
6. N07 monitors all waves, dispatches next wave when prior wave signals complete

**What you see (progress):**
```
Wave 1 dispatched: N04 (2 artifacts)
[2 min...]
Wave 1 complete: N04 signaled -- 2 artifacts, quality 9.1/9.3
Wave 2 dispatched: N03 (2 artifacts)
[3 min...]
Wave 2 complete: N03 signaled -- 2 artifacts, quality 9.0/9.2
Grid complete. All 4 artifacts built.
```

**Your role during /grid:** wait (or do other work). CEXAI handles everything.
Intervention is needed ONLY if a quality gate fails below 8.0 (rare; CEXAI retries once
before surfacing).

---

## Stage 5 -- /consolidate (You + CEXAI: verify and close)

**What you do:** type `/consolidate` after all nuclei signal complete.

```
/consolidate
```

**What CEXAI does:**
1. Runs `python _tools/cex_doctor.py` across all new artifacts
2. Stops any idle nucleus processes
3. Reports: file paths created, quality scores, doctor PASS/FAIL
4. Archives signals and handoffs

**What you review:**
```
Consolidation Report
  Files created: 4
    N04_knowledge/P01_knowledge/kc_onboarding_concepts.md    quality: 9.1
    N04_knowledge/P01_knowledge/faq_entry_customer_q.md      quality: 9.3
    N03_engineering/P02_model/agent_onboarding.md             quality: 9.0
    N03_engineering/P03_prompt/sp_onboarding_voice.md         quality: 9.2
  Doctor: 0 FAIL
  Committed: yes
```

**Decision you make:** review the artifacts. If anything needs revision, use
`/evolve <file>` for targeted improvement, or re-dispatch a single nucleus with
`/dispatch n04 "improve kc_onboarding_concepts focus on enterprise IT"`.

---

## Decision Boundary (Quick Reference)

| Stage | You decide (WHAT) | CEXAI does (HOW) |
|-------|-------------------|-----------------|
| /plan | Approve task list | Resolve taxonomy, map dependencies |
| /guide | Audience, tone, scope, depth | Never re-asks; records decisions |
| /spec | Approve the blueprint | Generate exact artifact specs |
| /grid | Nothing (wait) | Build, validate, commit, signal |
| /consolidate | Review + accept/reject | Doctor check, archive, report |

---

## Activation Milestones

| Milestone | Indicator |
|-----------|-----------|
| M1: First mission started | `/plan` completes with a task list |
| M2: Decisions locked | `decision_manifest.yaml` written |
| M3: Artifacts built | 4+ files in pillar directories |
| M4: Quality validated | Doctor reports `0 FAIL` |
| M5: Mission closed | Consolidation report delivered, signals archived |

---

## Tips for Operators

- **Start specific.** "Build a knowledge base for SaaS onboarding" works better than "build knowledge base."
- **Trust the taxonomy.** If CEXAI maps your goal to a kind you don't recognize, ask `/mentor` -- it explains every kind.
- **Use /evolve for refinement.** After a mission, `/evolve N04_knowledge/P01_knowledge/kc_onboarding_concepts.md` runs autonomous improvement until quality >= 9.0.
- **The manifest is your audit trail.** `.cex/runtime/decisions/decision_manifest.yaml` records every choice -- the full paper trail of who decided what.

---

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[p05_qs_cexai_operator]] | upstream | 0.80 |
| faq_entry_cexai_user | sibling | 0.70 |
| api_reference_cex_cli | downstream | 0.60 |
| [[rule_system_overview]] | upstream | 0.55 |
| guided-decisions | upstream | 0.50 |
