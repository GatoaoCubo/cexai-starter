---
kind: collaboration
id: bld_collaboration_content_factory
pillar: P12
llm_function: COLLABORATE
purpose: How content-factory-builder works in crews with other builders
pattern: each builder must know its ROLE in a team, what it RECEIVES and PRODUCES
quality: null
title: "Collaboration Content Factory"
version: "1.0.0"
author: n03_builder
tags: [content_factory, builder, content-fabric]
tldr: "Golden and anti-examples for content_factory construction, demonstrating the brief -> N-row fan-out and common pitfalls."
domain: "content factory construction"
created: "2026-07-03"
updated: "2026-07-03"
8f: "F8_collaborate"
keywords: [content factory construction, collaboration content factory, content_factory, builder, content-fabric, "### crew: content fabric end-to-end", my role, crew compositions, produce review publish, content fabric]
density_score: 0.90
related:
  - content-factory-builder
  - bld_tools_content_factory
---
# Collaboration: content-factory-builder

## My Role in Crews
I am a SPECIALIST. I answer ONE question: "given one brief, how does it fan into N
grounded, channel-ready content_library rows, and what handoffs get it to review + publish?"
I do not write captions myself. I do not implement the review board's persistence. I do
not build a real publish provider. I produce the PRODUCE-stage contract so downstream
builders/tenants can implement the review board and (eventually) a provider arm.

## Crew Compositions

### Crew: "Content Fabric End-to-End"
```
1. knowledge-card-builder    -> "domain knowledge about the business niche and audience"
2. content-factory-builder   -> "brief contract + channel-matrix fan-out + grounding wiring"
3. social-publisher-builder  -> "the publish contract this kind's rows flow into"
4. prompt-template-builder   -> "caption-generation prompts feeding the grounding engine"
5. quality-gate-builder       -> "the approved-list HITL gate criteria"
```

### Crew: "Multi-Channel Campaign Suite"
```
1. content-factory-builder  -> "one brief per campaign moment, fanned across channels"
2. workflow-builder          -> "the review-then-publish approval workflow"
3. scoring-rubric-builder     -> "engagement scoring dimensions per channel"
```

## Handoff Protocol
| I receive from | Data | Format |
|---------------|------|--------|
| knowledge-card-builder | Niche knowledge, audience profile, grounding facts | KC artifact |
| User/N07 | Brief inputs (topic, source_facts, channels) | Mission handoff .md |
| canonical-product (once scaffolded) | Optional product record to enrich grounding | CanonicalProduct dict |

| I send to | Data | Format |
|----------|------|--------|
| social-publisher-builder | The row contract + channel_matrix this kind hands into the publish seam | content_library-shaped rows |
| (the review board, runtime) | Unapproved rows awaiting the approval triad | `ReviewQueue.submit()` input |
| N05_operations | Deploy request once a real provider arm is separately built | Signal (deferred; NOT built yet) |

## Nucleus Routing
| Phase | Nucleus | Why |
|-------|---------|-----|
| Brief + channel-matrix design | N03 (engineering) | Contract and schema work |
| Content strategy / niche voice | N02 (marketing) | Brand, tone, campaign decisions |
| Review-board implementation | N03 -> N05 | Build -> deploy (tenant's own DB/UI) |
| Tenant brief instance | N02 | Business-specific campaign brief |

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[content-factory-builder]] | upstream | 0.34 |
| [[bld_tools_content_factory]] | sibling | 0.27 |
