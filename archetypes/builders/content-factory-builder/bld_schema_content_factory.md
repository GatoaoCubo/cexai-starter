---
kind: schema
id: bld_schema_content_factory
pillar: P06
llm_function: CONSTRAIN
purpose: Formal schema -- SINGLE SOURCE OF TRUTH for content_factory brief + row contract
pattern: OUTPUT derives from this. TEMPLATE renders this.
quality: null
title: "Schema Content Factory"
version: "1.0.0"
author: n03_builder
tags: [content_factory, builder, content-fabric]
tldr: "Golden and anti-examples for content_factory construction, demonstrating the brief -> N-row fan-out and common pitfalls."
domain: "content factory construction"
created: "2026-07-03"
updated: "2026-07-03"
8f: "F1_constrain"
keywords: [formal schema, content factory construction, schema content factory, content_factory, builder, content-fabric, brief schema, row schema, validation rules, unique post_id channel format]
density_score: 0.90
related:
  - bld_eval_content_factory
---

# Schema: content_factory

## kinds_meta.json (canonical registration, `.cex/kinds_meta.json`)
| Field | Value |
|-------|-------|
| pillar | P04 |
| llm_function | PRODUCE |
| primary_8f | F6_produce |
| max_bytes | 8192 |
| naming | `p04_content_factory_{{name}}.md` |
| core | false |
| status | stable |
| depends_on | [social_publisher, supabase_data_layer] |
| requires_external_context | true |
| requires_live_tools | false |

## ContentBrief Schema (the input every factory call takes -- mirrors `make_brief()`)
| Field | Type | Required | Default | Example |
|-------|------|----------|---------|---------|
| topic | string | YES | -- | "Cama donut para gatos" |
| post_id | string | NO | `slugify(topic)` | "w03_demo_cama" |
| post_group | string | NO | "content" | "instagram" |
| source_facts | string \| list[string] | NO | [] | ["Cama donut macia... base antiderrapante."] |
| hashtags | list[string] | NO | [] | ["#gato", "#petshop"] |
| channels | map[channel -> format] | NO | default 8-channel matrix | `{ig_feed: "4:5"}` |
| base_asset_type | enum(image,video,carousel) | NO | "image" | "image" |
| canonical | dict \| null | NO | null | a CanonicalProduct dict |
| alt_text | string | NO | "" | "Gato dormindo em uma cama donut." |

## Channel Matrix Schema (default; a tenant may override the whole map)
| Channel | Format | Valid formats (VALID_FORMATS) |
|---------|--------|-------------------------------|
| ig_feed | 4:5 | 9:16, 4:5, 1:1, 2:3, 16:9, text_only |
| ig_reels | 9:16 | (same set) |
| ig_stories | 9:16 | (same set) |
| fb | 1:1 | (same set) |
| tiktok | 9:16 | (same set) |
| linkedin | 1:1 | (same set) |
| pinterest | 2:3 | (same set) |
| x | text_only | (same set) |

Valid channels (VALID_CHANNELS): ig_feed, ig_reels, ig_stories, fb, tiktok, linkedin,
pinterest, threads, x, blog, email. Valid asset types (VALID_ASSET_TYPES): image, video,
carousel, text. An entry whose format is NOT in VALID_FORMATS is skipped (never emits a
malformed row).

## Output Row Schema (content_library-shaped -- mirrors `build_library_rows()`)
| Field | Type | Required | Birth-state |
|-------|------|----------|-------------|
| post_id | string | YES | shared across the whole fan-out |
| post_group | string | YES | from brief.post_group |
| channel | string | YES | one VALID_CHANNELS key |
| format | string | YES | one VALID_FORMATS value |
| asset_type | enum(image,video,carousel,text) | YES | "text" iff format == text_only |
| caption_text | string | YES | the ONE grounded caption (shared across rows) |
| hashtags | list[string] | YES | clamped to the row's platform cap |
| alt_text | string | YES | "" when asset_type == text |
| storage_url | string \| null | YES | null (WIRE stage is DEFERRED) |
| approved | bool | YES | **false** |
| approved_by | string \| null | YES | null |
| approved_at | string \| null | YES | null |
| publish_status | enum(pending,scheduled,published,failed,archived) | YES | **pending** |
| metadata | dict | YES | {} |

## Validation Rules (HARD invariants)
1. UNIQUE(post_id, channel, format) MUST hold across every row of a bundle (enforced by
   construction: the channel_matrix is keyed by channel; duplicate keys are deduplicated)
2. A row's `hashtags` length MUST NOT exceed its platform's cap: instagram 5, tiktok 30,
   linkedin 8, twitter 3, facebook 30, pinterest 20, threads 5 (unknown platform: 30)
3. Every row MUST start `approved=False` and `publish_status="pending"` -- no exception
4. `storage_url` MUST be null until the (deferred) WIRE/media-render stage populates it
5. A caption claim MUST trace to `source_facts` or `topic` -- an unsupported claim is
   OMITTED, never invented (the G1-G10 grounding contract)
6. An invalid `format` value in the channel_matrix MUST be skipped, never emitted as a row

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[bld_eval_content_factory]] | downstream | 0.38 |
