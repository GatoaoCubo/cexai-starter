---
id: p01_kc_content_factory
kind: knowledge_card
8f: F3_inject
type: kind
pillar: P04
title: "Content Factory — Deep Knowledge for content_factory"
version: 1.0.0
created: 2026-07-02
updated: 2026-07-02
author: builder_agent
domain: content_factory
quality: null
tags: [content_factory, P04, PRODUCE, kind-kc, content-fabric, grounding]
tldr: "Grounded multi-channel content producer: ONE brief fans into N content_library-shaped rows (one per channel/format) via the no-fabrication grounding engine, gated by a post-level approval triad before a vendor-agnostic, provider-deferred publish seam"
when_to_use: "Building, reviewing, or reasoning about content_factory artifacts"
keywords: [content_factory, content_fabric, brief, channel_matrix, grounding, review_queue, publish_seam, content_library]
feeds_kinds: [content_factory]
density_score: null
related:
  - p01_kc_social_publisher
  - p01_kc_content_monetization
  - p01_kc_supabase_data_layer
---

# Content Factory

## Spec
```yaml
kind: content_factory
pillar: P04
llm_function: PRODUCE
max_bytes: 8192
naming: p04_content_factory_{{name}}.md
core: false
status: stable
depends_on: [social_publisher, supabase_data_layer]
requires_external_context: true
primary_8f: F6_produce
```

## What It Is
A content_factory artifact specifies a grounded, multi-channel content production pipeline: ONE brief (topic + source facts + channel matrix) fans into N `content_library`-shaped rows -- one per (channel, format) -- through PRODUCE (grounded caption) > REVIEW (approved-list HITL gate) > PUBLISH-SEAM (vendor-agnostic, provider deferred). NOT `social_publisher` (owns only the publish half -- the 10-stage LOAD>...>ROTATE posting mechanics) nor `content_monetization` (billing/checkout/courses, pillar P11). See Decision Tree below for the full adjacent-kind boundary.

Runtime: PRODUCE=`_tools/cex_content_factory.py` (`make_brief`, `produce_content_bundle`), grounded via `cex_grounded_copy.extract_copy` (G1-G10 no-fabrication gate); REVIEW=`_tools/cex_content_review.py` (`ReviewQueue`); PUBLISH-SEAM=`_tools/cex_channel_publisher.py` (`NoOpPublisher`, fail-closed); proven by `tests/test_content_fabric.py`. No persisted instance of this kind exists yet (verified 2026-07-02) -- the runtime IS the reference implementation.

## Naming Collision (do not confuse)
"Content Factory" names THREE unrelated systems here; only the first is this kind.

| System | Where | What |
|---|---|---|
| **This kind** (`content_factory`, P04) | `_tools/cex_content_factory.py` | brief -> N content_library rows -> review -> publish-seam |
| `cexai.content_factory` package | `cexai/cexai/content_factory/` | short-social VIDEO factory (MoneyPrinterTurbo+Chatterbox); ZERO new kinds, reuses `workflow`/`tts_provider` (`adr_v06_content_factory_taxonomy`) |
| N06 "Content Factory" | `N06_commercial/P08_architecture/integration_content_factory.md` | 2026-04-08 pricing/checkout spec, kind=`content_monetization` (P11) |

## Key Parameters (the ContentBrief -- `make_brief()`)
| Parameter (type) | Default | Notes |
|---|---|---|
| topic (str) | required | headline seed; always a legitimate grounding source |
| post_id (str) | slug(topic) | shared grouping key across fanned rows |
| source_facts (str\|list) | [] | the grounding SOURCE; caption claims only what's here |
| hashtags (list) | [] | clamped to platform cap at fan-out |
| channels (dict) | 8-channel default | reels/tiktok=9:16, feed=4:5, fb/linkedin=1:1, pinterest=2:3, x=text_only |
| base_asset_type (str) | "image" | image/video/carousel for non-text channels |
| canonical (dict\|None) | None | optional product; enriches grounding source |
| post_group (str) | "content" | maps to `content_library.post_group` |
| alt_text (str) | "" | a11y text for media rows |

Output row (`build_library_rows()`): one per channel, `content_library`-shaped, `approved=False`/`publish_status="pending"` at birth; `storage_url=None` until the DEFERRED media-render stage.

## Patterns
| Pattern | When to Use | Evidence |
|---|---|---|
| One-brief, N-row fan-out | one caption must reach 8 channel/format combos | `build_library_rows()` |
| Degrade-never grounding | no `llm` injected, or grounding module unavailable | `_grounded_caption()` fallback |
| Post-level approval triad | approve/revoke must move a whole post together | `ReviewQueue.approve()/revoke()` |
| Vendor-agnostic publish seam | no real provider chosen, or must never publish live | `NoOpPublisher` |

## Anti-Patterns
| Anti-Pattern | Why It Fails | Fix |
|---|---|---|
| Publish a row before `approved=True` | breaks the hard review-gate precondition | route through `ReviewQueue.approved_for_publish()` first |
| Inline edit auto-approves | `queue.edit()` never touches the triad by design | require explicit `queue.approve(post_id)` after edits |
| Real provider wired into the seam | breaks the NO-REAL-PUBLISH invariant | add a provider as a SEPARATE module behind config |
| Caption claims a fact absent from `source_facts` | breaks the grounding guarantee | add the fact to `source_facts`, or let the engine OMIT it |

## Integration Graph
```
[brief: topic+source_facts+channels]
  -> PRODUCE (cex_content_factory.py, grounded via cex_grounded_copy.extract_copy)
  -> N content_library rows (approved=False, publish_status=pending)
  -> REVIEW (cex_content_review.py: ReviewQueue.approved_for_publish() = the ONLY gate)
  -> PUBLISH-SEAM (cex_channel_publisher.py: NoOpPublisher, fail-closed, social_publisher contract)
  -> [DEFERRED real provider: Postiz / Ayrshare / Meta Graph]
```

## Decision Tree
- IF need ONLY the persisted table shape (one row per post_id/channel/format) THEN use `content_library`
- IF need ONLY the posting mechanics (LOAD>FETCH>...>PUBLISH>LOG>NOTIFY>ROTATE) THEN use `social_publisher`
- IF need billing/checkout/credits/courses THEN use `content_monetization` (P11, different pillar)
- IF need the underlying Supabase table/RLS definition THEN use `supabase_data_layer`
- IF need "one grounded brief -> N channel-ready rows -> HITL approval -> publish-ready" THEN `content_factory`
- DEFAULT: `content_factory` when the task starts from ONE brief and must fan out across >= 2 channels with a review gate before anything ships

## Quality Criteria
- GOOD: `source_facts` non-empty; `channels` maps to >= 2 channels; every row carries the required `content_library` fields; rows start `approved=False`/`publish_status="pending"`
- GREAT: full grounding engine used (not the degraded fallback); UNIQUE(post_id,channel,format) holds; hashtags clamped per-platform; approval triad flips atomically per POST; publish seam proven zero real network calls
- FAIL: caption asserts a claim absent from `source_facts`/topic; a row reaches publish with `approved != True`; an inline edit silently sets `approved=True`; the seam performs a real HTTP write

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[p01_kc_social_publisher]] | sibling | 0.50 |
| [[p01_kc_supabase_data_layer]] | upstream | 0.38 |
| [[p01_kc_content_monetization]] | related | 0.32 |
