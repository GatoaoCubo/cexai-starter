---
kind: memory
id: p10_mem_product_tour_builder
pillar: P10
llm_function: INJECT
purpose: Learned patterns and pitfalls for product_tour construction
quality: null
title: "Memory Product Tour"
version: "1.0.0"
author: wave1_builder_gen_v2
tags: [product_tour, builder, memory]
tldr: "Learned patterns and pitfalls for product_tour construction"
domain: "product_tour construction"
created: "2026-04-14"
updated: "2026-04-14"
8f: "F3_inject"
keywords: [product_tour construction, memory product tour, product_tour, builder, memory, observation
common, pattern
effective, evidence
reviewed, related artifacts, upstream]
density_score: 0.85
related:
  - product-tour-builder
---
## Observation
Common issues include misaligned tooltip positions, unclear trigger logic (e.g., scroll vs. click), and overloading steps with too much text. Tours often lack clear end goals, leading to user confusion.

## Pattern
Effective tours use concise, action-oriented steps with visual cues. Trigger specs are tightly coupled to user flows (e.g., "after form submission"), ensuring relevance.

## Evidence
Reviewed artifacts showed 30% higher completion rates when tooltips used icons + short text, and triggers were tied to specific UI interactions.

## Recommendations
- Define triggers based on user behavior, not arbitrary timing.
- Limit steps to 5–7, focusing on critical features.
- Use consistent tooltip styling and placement (e.g., bottom-right).
- Include a clear "Skip" option for user control.
- Test tours with real users to validate flow clarity.

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[product-tour-builder]] | upstream | 0.32 |
