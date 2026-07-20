---
id: kc_content_library
kind: knowledge_card
8f: F3_inject
type: kind
pillar: P04
title: "Content Library — Deep Knowledge for content_library"
version: 1.0.0
created: 2026-07-20
updated: 2026-07-20
author: knowledge_agent
domain: content_library
quality: null
tags: [content_library, P04, CALL, kind-kc]
tldr: "Multi-channel content data layer: one row per (post_id, channel, format) with an approval triad and a publish-status lifecycle."
when_to_use: "Building, reviewing, or reasoning about content_library artifacts"
keywords: [content library, multi-channel content, approval triad, publish lifecycle, content data layer, supabase data layer]
feeds_kinds: [content_library]
density_score: null
aliases: ["content data layer", "post store", "publish queue table", "multi-channel content table"]
user_says: ["store my social posts in one table", "build a content calendar with an approval step", "I need one table for every channel's posts", "add a review gate before anything publishes"]
long_tails: ["I need one table that holds a post for every channel before it publishes", "add an approval gate so nothing publishes without a human sign-off", "design a data layer a content producer writes to and a publisher reads from", "stop the same post from double-publishing to the same channel"]
cross_provider:
  buffer: "Queue entry -- one post fans into N channel-specific queue rows"
  contentful: "Entry + workflow state -- closest general analogy: content model with review states"
  ayrshare: "Provider-side post queue -- content_library is the vendor-agnostic precursor"
related:
  - kc_supabase_data_layer
  - kc_content_factory
  - kc_social_publisher
  - supabase-data-layer-builder
---

# Content Library

## Spec
```yaml
kind: content_library
pillar: P04
llm_function: CALL
max_bytes: 8192
naming: p04_content_library_{{slug}}.md + .yaml
id_pattern: "^p04_content_library_[a-z][a-z0-9_]*$"
core: false
```

## What It Is
A `content_library` is the multi-channel content DATA LAYER: one row per `(post_id, channel,
format)`, carrying an approval triad (`approved` / `approved_by` / `approved_at`) and a
`publish_status` lifecycle. It is an INSTANCE of `supabase_data_layer` (a table plus row-level
security policy), not a generic backend or a pipeline. It sits between two verbs: a producer
WRITES unapproved rows into it, a publisher READS only approved rows out. It is NOT
`social_publisher` (what publishes) and NOT `content_factory` (what produces the copy) --
content_library is the shared table both sit around.

## Cross-Framework Map
| Framework/Provider | Class/Concept | Notes |
|---|---|---|
| Buffer / Later | Queue entry | Same shape: 1 post fans into N channel-specific queue rows |
| Contentful / Sanity | Entry + workflow state | Closest general analogy: content model + review states |
| Ayrshare / Postiz | Provider-side post queue | content_library is the vendor-agnostic precursor |

## Key Fields
| Field | Type | Required | Notes |
|---|---|---|---|
| post_id | string | yes | Grouping key; every channel/format of one post shares it |
| channel | enum | yes | Registry-defined (e.g. feed post, stories, short-form video, blog, email) |
| format | enum | yes | Aspect-ratio shaped (e.g. `9:16`, `1:1`, `16:9`, `text_only`) -- NOT a content-type label |
| asset_type | enum | yes | `image \| video \| carousel \| text` |
| caption_text | string | yes | Blocks publish if empty |
| storage_url | string | conditional | Required when `asset_type` is non-text |
| approved / approved_by / approved_at | bool / string / timestamp | yes | The approval triad -- set together, reset together, never partial |
| publish_status | enum | yes | `pending \| scheduled \| published \| failed \| archived` (never `cancelled`) |

## Patterns
| Pattern | When to Use | Example |
|---|---|---|
| Approval triad | Any table where a human must sign off before an automated action fires | `approved=true` only when all three triad fields are set together |
| Single bridge to publish | Preventing any code path from reading unapproved data | A publisher reads exclusively through the "approved rows only" query -- no other read path exists |
| Unique row identity | Preventing the same content from firing twice | `UNIQUE(post_id, channel, format)` makes double-publish structurally impossible |

## Anti-Patterns
| Anti-Pattern | Why It Fails | Fix |
|---|---|---|
| Row enters pre-approved | An untrusted source or import script ships `approved: true` directly | Force `approved=false` on ingestion, unconditionally |
| Partial approval triad | `approved=true` but `approved_by`/`approved_at` left null | Always set/reset all three triad fields together, never independently |
| Treating `format` as a content-type | Whitelist is aspect-ratio shaped (`9:16`), not a label like "reel" | Validate against the registered format enum, not free text |
| Public/anon read access | Content rows, even unpublished ones, are internal data | Restrict row access to admin + service roles only |

## Integration Graph
```
[producer: brief -> N rows] --> [content_library] --> [publisher: reads approved rows only]
                                        |
                              [supabase_data_layer: hosting table + RLS]
```

## Decision Tree
- IF you need the multi-channel STORE (one row per post x channel x format + an approval gate) THEN content_library
- IF you need the PRODUCER that fills it with copy THEN content_factory
- IF you need the PUBLISH PIPELINE that reads FROM it THEN social_publisher
- IF you need a generic Supabase backend beyond this one table THEN supabase_data_layer
- DEFAULT: content_library for any per-(post, channel, format) content row with an approval gate

## Quality Criteria
- GOOD: Row schema defined; approval triad present; `UNIQUE(post_id, channel, format)` enforced
- GREAT: RLS scoped to admin+service only; format/channel/asset_type validated against a registered enum; publish_status lifecycle has no dead-end states
- FAIL: No approval gate before publish; rows can be created pre-approved; no uniqueness constraint (silent double-publish risk)

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[kc_supabase_data_layer]] | upstream (hosting kind) | 0.55 |
| [[kc_content_factory]] | related (upstream writer) | 0.45 |
| [[kc_social_publisher]] | related (downstream reader) | 0.45 |
| [[supabase-data-layer-builder]] | upstream | 0.40 |
