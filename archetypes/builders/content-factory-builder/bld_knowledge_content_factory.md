---
kind: knowledge_card
id: bld_knowledge_card_content_factory
pillar: P01
llm_function: INJECT
purpose: Domain knowledge for content_factory pipeline design
sources: "_tools/cex_content_factory.py, _tools/cex_content_review.py, _tools/cex_channel_publisher.py, _tools/cex_grounded_copy.py, tests/test_content_fabric.py (14 passing)"
quality: null
title: "Knowledge Card Content Factory"
version: "1.0.0"
author: n03_builder
tags: [content_factory, builder, content-fabric]
tldr: "Golden and anti-examples for content_factory construction, demonstrating the brief -> N-row fan-out and common pitfalls."
domain: "content factory construction"
created: "2026-07-03"
updated: "2026-07-03"
8f: "F3_inject"
keywords: [content factory construction, knowledge card content factory, content_factory, builder, content-fabric, naming collision, grounding, channel matrix, hashtag caps, executive summary]
density_score: 0.90
related:
  - content-factory-builder
  - p01_kc_content_factory
  - p01_kc_social_publisher
  - p01_kc_content_library
  - bld_instruction_content_factory
---
# Domain Knowledge: content_factory

## Executive Summary
content_factory (P04, PRODUCE) is the produce third of the content fabric: ONE brief
(topic + source facts + channel matrix) fans into N `content_library`-shaped rows -- one
per (channel, format) -- through a no-fabrication grounding engine, then hands off to a
review gate and a vendor-agnostic publish seam. The reference implementation
(`_tools/cex_content_factory.py`) writes nothing: no DB, no network. Every row is born
unapproved; only the review board's approval triad makes a row publish-eligible, and even
then the seam is fail-closed (no real provider is wired).

## Naming Collision (do not confuse -- 3 systems share the name)
| System | Where | What | Is this kind? |
|--------|-------|------|----------------|
| **content_factory kind (P04)** | `_tools/cex_content_factory.py` | brief -> N content_library rows -> review -> publish-seam | YES -- this builder |
| `cexai.content_factory` package | `cexai/cexai/content_factory/` | short-social VIDEO factory (MoneyPrinterTurbo+Chatterbox); ZERO new kinds, reuses `workflow`/`tts_provider` | NO |
| N06 "Content Factory" spec | `N06_commercial/P08_architecture/integration_content_factory.md` | pricing/checkout spec, kind=`content_monetization` (P11) | NO |

## Pipeline -- 3 Stages (this kind covers Stage 1 only)
| Stage | Owner module | Input | Output | This kind? |
|-------|--------------|-------|--------|------------|
| 1. PRODUCE | `cex_content_factory.py` | ContentBrief | N unapproved content_library rows | YES |
| 2. REVIEW | `cex_content_review.py` | submitted rows | approved_for_publish() subset | reused, not owned |
| 3. PUBLISH-SEAM | `cex_channel_publisher.py` | approved rows | refused PublishResult (fail-closed) | reused, not owned |

## Channel Matrix (default 8 channels)
| Channel | Format | Asset Type (non-text) |
|---------|--------|------------------------|
| ig_feed | 4:5 | image/video/carousel |
| ig_reels | 9:16 (master) | image/video/carousel |
| ig_stories | 9:16 | image/video/carousel |
| fb | 1:1 | image/video/carousel |
| tiktok | 9:16 | image/video/carousel |
| linkedin | 1:1 | image/video/carousel |
| pinterest | 2:3 | image/video/carousel |
| x | text_only | text |

## Hashtag Caps (HARD clamp, per `cex_channel_publisher.HASHTAG_CAPS`)
| Platform | Cap |
|----------|-----|
| instagram | 5 |
| tiktok | 30 |
| linkedin | 8 |
| twitter | 3 |
| facebook | 30 |
| pinterest | 20 |
| threads | 5 |
| (unknown platform) | 30 (default) |

## The Grounding Contract (reused from W2, G1-G10 -- BLOCKING severities)
| Rule | Guarantee |
|------|-----------|
| G3/G4 | Never invent dimensions/materials/weight/capacity/compatibility (BLOCKING) |
| G5 | Never invent a safety/health claim (BLOCKING) |
| G6 | Absent fact -> OMIT the section, never fabricate one |
| G10 | Omitting is safe; fabricating is not -- when unsure, DISCARD |

With no `llm` injected, the factory falls back to a deterministic caption built directly
from `topic` + joined `source_facts` -- grounded by construction, fully offline-testable.

## Anti-Patterns
| Anti-Pattern | Why It Fails |
|-------------|-------------|
| A row reaches publish with `approved != True` | Breaks the hard review-gate precondition (FR-011/SC-006) |
| Inline edit sets `approved=True` | `queue.edit()` never touches the triad by design (FR-009) |
| A real provider wired into the seam | Breaks the NO-REAL-PUBLISH invariant (founder decision 2026-06-23) |
| Caption claims a fact absent from `source_facts` | Breaks the grounding guarantee (G1-G10) |
| Treating this kind as the video-factory package | Naming collision -- see table above; wrong depends_on (video pkg reuses `workflow`/`tts_provider`, NOT `social_publisher`/`supabase_data_layer`) |
| Skipping an invalid channel_matrix format loudly | The reference impl skips silently (degrade-never) -- an artifact should describe this, not add scary errors |

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[content-factory-builder]] | downstream | 0.56 |
| [[p01_kc_content_factory]] | upstream | 0.53 |
| [[p01_kc_social_publisher]] | sibling | 0.47 |
| [[p01_kc_content_library]] | sibling | 0.44 |
| [[bld_instruction_content_factory]] | downstream | 0.40 |
