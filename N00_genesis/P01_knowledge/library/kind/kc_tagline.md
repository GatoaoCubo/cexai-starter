---
id: kc_tagline
kind: knowledge_card
8f: F3_inject
pillar: P01
title: "KC: Tagline"
version: 1.0.0
created: 2026-04-06
author: n07_orchestrator
quality: null
tags: [knowledge-card, tagline, marketing, brand, copy]
keywords: [aida, pas, before/after, question, command, metaphor, billboard test, competitor swap test, memory test, cex_retriever]
density_score: 1.0
updated: "2026-04-07"
domain: "knowledge management"
tldr: "Defines the knowledge card specification for kc: tagline, with structural rules, validation gates, and integration points."
when_to_use: "When producing a short memorable phrase that captures brand essence for hero sections or ads"
related:
  - tagline-builder
---
# Knowledge Card: tagline

## Definition
A **tagline** is a short, memorable phrase (3-15 words) that captures a brand's essence,
value proposition, or emotional promise. Used across: hero sections, social bios, ad
headlines, email subjects, pitch decks.

## Builder
`tagline-builder` (12 ISOs) — Pillar P03

## Frameworks
| Framework | Pattern | Example |
|-----------|---------|---------|
| AIDA | Attention→Interest→Desire→Action | "Stop guessing. Start knowing." |
| PAS | Problem→Agitate→Solution | "Tired of X? Y changes everything." |
| Before/After | Old state → New state | "From chaos to clarity." |
| Question | Provocative question | "What if your code tested itself?" |
| Command | Direct imperative | "Just Do It." |
| Metaphor | Analogy-based | "The Swiss Army knife of AI." |

## Quality Tests
1. **Billboard test**: Understood in 3 seconds at 60mph
2. **Competitor swap test**: Could NOT be used by a rival
3. **Memory test**: Recalled 24h later without notes

## Relations
- Consumed by: landing-page-builder (hero headline)
- Consumed by: social-publisher-builder (bio, captions)
- Consumed by: content-monetization-builder (product taglines)
- Depends on: brand_config.yaml (tone, audience, industry)

## Retrieval Example

```yaml
# Query this card via cex_retriever.py
query: "KC: Tagline"
kind_filter: knowledge_card
threshold: 0.7
```

```bash
# CLI retrieval
python _tools/cex_retriever.py "KC: Tagline" --top 5
```

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[bld_knowledge_tagline]] | sibling | 0.53 |
| [[tagline-builder]] | downstream | 0.42 |
| [[bld_orchestration_tagline]] | downstream | 0.39 |
| n00_tagline_manifest | sibling | 0.37 |
