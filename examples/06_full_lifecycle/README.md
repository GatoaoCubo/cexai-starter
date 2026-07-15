---
id: ex_full_lifecycle
kind: context_doc
pillar: P01
title: "Full Lifecycle Example -- Vague Intent to Typed Artifact"
version: 1.0.0
created: 2026-04-27
quality: null
density_score: 0.90
tags: [example, lifecycle, walkthrough, 8f]
related:
  - CLAUDE
  - 8f-reasoning
  - prompt-compiler-builder
---

# Full Lifecycle Example

## What does this help you do?

See the same artifact built two ways: **engineer view** (every step, every
payload) and **business view** (only the value). Pick whichever matches how
you think.

## The Scenario

A team lead types five words into Claude Code:

> "I want to teach my team about prompt caching"

CEX turns that into a versioned, searchable, peer-reviewed knowledge card
in under 10 minutes. Here is how.

## Step 1: Intent Resolution (prompt_compiler)

The prompt compiler receives the raw input and resolves it:

| Field | Resolved Value |
|-------|---------------|
| kind | `knowledge_card` |
| pillar | P01 (Knowledge) |
| nucleus | N04 (Knowledge Gluttony) |
| verb | `document` (canonical action: F6 PRODUCE) |
| confidence | 94% (above 60% threshold -- no GDP needed) |

The user never typed "knowledge_card" or "P01". The prompt compiler
matched "teach my team about" to the `document` verb and "prompt caching"
to the knowledge domain.

## Step 2: 8F Pipeline Executes

```
F1 CONSTRAIN  -- kind=knowledge_card, max_bytes=5120, naming=p01_kc_prompt_caching.md
F2 BECOME     -- knowledge-card-builder loaded (12 ISOs, one per pillar)
F2b SPEAK     -- N04 vocabulary KC loaded (drift prevention active)
F3 INJECT     -- 4 sources: kc_knowledge_card.md + 2 existing KCs + brand context
F4 REASON     -- 5 sections planned, density target 0.85, approach=template
F5 CALL       -- compile + doctor + index ready, 3 similar KCs found
F6 PRODUCE    -- 3,840 bytes, 5 sections, density=0.89
F7 GOVERN     -- 9.1/10, gates 7/7, 12LP 12/12
F8 COLLABORATE -- saved P01/kc_prompt_caching.md, compiled, committed, signaled
```

## Step 3: Before vs After

**Before** (what the user had):

> A vague idea and a Slack message that will scroll away in 7 days.

**After** (what CEX produced):

```yaml
---
id: p01_kc_prompt_caching
kind: knowledge_card
pillar: P01
nucleus: n04
title: "Prompt Caching -- Reduce Latency and Cost via Prefix Reuse"
version: 1.0.0
quality: null
tags: [prompt-caching, latency, cost, anthropic, openai]
density_score: 0.89
---
```

A typed artifact with: summary, core concepts (cache-prefix mechanics, TTL
behavior, provider differences), implementation guidance (cache breakpoints,
static-prefix ordering), anti-patterns (cache-busting via timestamp injection),
and cross-framework references (Anthropic cache_control, OpenAI cached tokens).

Versioned in git. Searchable by any nucleus. Peer-reviewable via F7c COUNCIL.

## Deep Dives

| View | File | What you see |
|------|------|-------------|
| Engineer mode | [engineer_mode.md](engineer_mode.md) | Full 8F trace with JSON payloads, scoring rubric, signal output |
| Business mode | [business_mode.md](business_mode.md) | 4 paragraphs: what was asked, what was produced, cost, value |

## Related Artifacts

| Artifact | Relationship | Score |
|----------|-------------|-------|
| 8f-reasoning | upstream | 0.90 |
| [[p01_kc_knowledge_card]] | reference | 0.85 |
| prompt-compiler-builder | upstream | 0.80 |
| [[ex_lifecycle_engineer_mode]] | child | 1.00 |
| [[ex_lifecycle_business_mode]] | child | 1.00 |
