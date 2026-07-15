---
id: ex_lifecycle_business_mode
kind: case_study
pillar: P01
title: "Business Mode -- Same Artifact, Just the Value"
version: 1.0.0
created: 2026-04-27
quality: null
density_score: 0.88
tags: [example, case_study, business, value]
related:
  - ex_full_lifecycle
  - ex_lifecycle_engineer_mode
---

# Business Mode -- Same Artifact, Just the Value

## What Was Asked

> "I want to teach my team about prompt caching."

One sentence. No spec, no schema, no file paths.

## What Was Produced

A 3,840-byte knowledge card titled **"Prompt Caching -- Reduce Latency and
Cost via Prefix Reuse"** with five structured sections: summary, core
concepts (cache-prefix mechanics, TTL behavior, provider differences),
implementation guidance, anti-patterns table, and cross-framework
references covering Anthropic, OpenAI, and Google.

```yaml
id: p01_kc_prompt_caching
kind: knowledge_card
title: "Prompt Caching -- Reduce Latency and Cost via Prefix Reuse"
quality: null  # peer-reviewed, not self-scored
density_score: 0.89
```

## Time and Cost

| Metric | Value |
|--------|-------|
| Wall time | ~8 minutes |
| Tokens consumed | ~12,000 |
| Estimated cost | ~$0.04 |
| Quality score | 9.1 / 10 |
| Hard gates passed | 7 / 7 |

## What This Saves

| Without CEX | With CEX |
|-------------|----------|
| Ad-hoc Slack message | Versioned .md file in git |
| Scrolls away in 7 days | Searchable by any nucleus, any time |
| No quality check | 7 hard gates + 5D scoring rubric |
| One person's phrasing | Density-gated (0.89) -- every sentence carries weight |
| No cross-references | Wikilinked to related artifacts, indexed for RAG retrieval |
| Copy-paste to share | Peer-reviewable via F7c cross-provider council |

The knowledge card is not a document. It is a **typed, governed, compounding
knowledge asset**. Every future conversation that touches prompt caching will
find it, inject it, and build on it.

## Related Artifacts

| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[ex_full_lifecycle]] | parent | 1.00 |
| [[ex_lifecycle_engineer_mode]] | sibling | 0.95 |
| [[kc_knowledge_card]] | reference | 0.85 |
