---
kind: architecture
id: bld_architecture_content_factory
pillar: P08
llm_function: CONSTRAIN
purpose: Component map of the content_factory pipeline -- inventory, dependencies, data flow
quality: null
title: "Architecture Content Factory"
version: "1.0.0"
author: n03_builder
tags: [content_factory, builder, content-fabric]
tldr: "Golden and anti-examples for content_factory construction, demonstrating the brief -> N-row fan-out and common pitfalls."
domain: "content factory construction"
created: "2026-07-03"
updated: "2026-07-03"
8f: "F1_constrain"
keywords: [data flow, content factory construction, architecture content factory, content_factory, builder, content-fabric, component inventory, dependency map, depends_on, wire deferred]
density_score: 0.90
related:
  - content-factory-builder
  - bld_tools_content_factory
---
# Architecture: content_factory in the CEX

## Component Inventory
| Name | Role | Owner | Status |
|------|------|-------|--------|
| ContentBrief | Typed input (topic + source + channels) | caller | required |
| grounding engine | Generates ONE grounded caption from the brief source | `cex_grounded_copy.extract_copy` | required (degrades to deterministic) |
| fan-out builder | ONE caption -> N content_library-shaped rows | `build_library_rows()` | required |
| voice profile | Optional voice knob shaping the caption's register | `cex_tenant_voice_profile.load_voice_profile` | optional |
| canonical enrichment | Optional product fields folded into the grounding source | `cex_canonical_product` via `source_text_of()` | optional |
| review queue | Approved-list HITL gate (reused, not owned) | `cex_content_review.ReviewQueue` | required downstream |
| publish seam | Vendor-agnostic, fail-closed publish attempt (reused, not owned) | `cex_channel_publisher.NoOpPublisher` | required downstream |
| media render (WIRE) | Populates `storage_url` on media rows | DEFERRED -- not built | deferred |
| real provider arm | Actual Postiz/Ayrshare/Meta-Graph publish | DEFERRED -- not built | deferred |

## Data Flow
```
ContentBrief (topic, source_facts, channels, canonical?)
        |
        v
brief_source() -- unions topic + source_facts + canonical.source_text_of()
        |
        v
_grounded_caption() -- extract_copy() [G1-G10 gate] or deterministic fallback
        |
        v
ONE grounded caption (shared across all rows of the post)
        |
        v
build_library_rows() -- fans across channel_matrix {channel -> format}
        |
        v
N content_library-shaped rows (approved=False, publish_status=pending, storage_url=None)
        |
        v
cex_content_review.ReviewQueue.submit() -- STAMPS approved=False/pending on ingest
        |
        v
[HUMAN] .approve(post_id, by=) -- flips the triad on EVERY row of the post
        |
        v
.approved_for_publish() -- the ONLY bridge to the seam
        |
        v
cex_channel_publisher.get_publisher(channel).publish() -- FAIL-CLOSED (NoOp refuses)
        |
        v
[DEFERRED] a real provider arm (Postiz / Ayrshare / Meta Graph)
```

## Dependency Map (`.cex/kinds_meta.json` depends_on: [social_publisher, supabase_data_layer])
| Component | Depends On | Why |
|-----------|-----------|-----|
| Row shape | `supabase_data_layer` | content_library IS an instance of supabase_data_layer; this kind's rows are content_library-shaped |
| Publish handoff | `social_publisher` | the seam's CHANNEL_TO_PLATFORM map + 10-step pipeline is the social_publisher kind contract |
| Grounding | (internal reuse, not a kind dependency) | `cex_grounded_copy` -- the W2 P3 no-fabrication engine |
| Voice | (internal reuse) | `cex_tenant_voice_profile.load_voice_profile` |
| Canonical | (internal reuse) | `cex_canonical_product` (when a post is about a product) |

## Position in CEX
```
P04_tools/            <- template + examples live here
  templates/tpl_content_factory.md
  examples/ex_content_factory_*.md
  compiled/content_factory_*.yaml

N02_marketing/         <- nucleus instance lives here (brand/campaign briefs)
  tools/content_factory_campaign.md
  knowledge/kc_content_briefs.md

_instances/{tenant}/N02_marketing/   <- tenant-specific brief
  content_factory_brief.md
```

## Boundaries
| This builder handles | Other builder/system handles |
|---------------------|----------------------|
| Brief contract + channel-matrix fan-out | Caption prompt authoring -> prompt-template-builder |
| Grounding-engine wiring (which engine, what degrades) | The grounding engine's own internals -> `cex_grounded_copy.py` (not a builder) |
| Row contract + birth-state | Review-board persistence/UI -> the tenant's DB + admin surface |
| Publish-seam handoff description | Real provider implementation -> social-publisher-builder / a future provider arm |
| N/A (out of scope entirely) | The short-social VIDEO package `cexai/cexai/content_factory/` (different system, see Naming Collision) |

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[content-factory-builder]] | upstream | 0.30 |
| [[bld_tools_content_factory]] | sibling | 0.28 |
