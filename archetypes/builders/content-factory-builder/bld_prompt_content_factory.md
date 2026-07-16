---
kind: instruction
id: bld_instruction_content_factory
pillar: P03
llm_function: REASON
purpose: Step-by-step production process for content_factory artifacts
pattern: 3-phase pipeline (research -> compose -> validate)
quality: null
title: "Instruction Content Factory"
version: "1.0.0"
author: n03_builder
tags: [content_factory, builder, content-fabric]
tldr: "Golden and anti-examples for content_factory construction, demonstrating the brief -> N-row fan-out and common pitfalls."
domain: "content factory construction"
created: "2026-07-03"
updated: "2026-07-03"
8f: "F6_produce"
keywords: [content factory construction, instruction content factory, content_factory, builder, content-fabric, brief, channel_matrix, grounding, write brief contract, write channel matrix, write row contract]
density_score: 0.90
related:
  - content-factory-builder
  - bld_knowledge_card_content_factory
  - bld_schema_content_factory
  - bld_output_template_content_factory
  - p01_kc_content_factory
---
# Instructions: How to Produce a content_factory

## Phase 1: RESEARCH
1. Identify the target business/domain: niche, tone, persona, channels, audience
2. Determine the grounding source: what `source_facts` exist (product ficha, brief text,
   canonical product record); a caption can ONLY claim what is here or in the topic
3. List target channels + formats via the channel_matrix (default 8: ig_feed 4:5,
   ig_reels 9:16, ig_stories 9:16, fb 1:1, tiktok 9:16, linkedin 1:1, pinterest 2:3, x text_only)
4. Confirm the downstream dependencies this kind registers (`depends_on` in
   `.cex/kinds_meta.json`): `social_publisher` (the publish contract) and
   `supabase_data_layer` (content_library IS an instance of it)
5. Check whether a canonical product rides along (enriches the grounding source via
   `source_text_of()`) or the brief is topic/fact-only
6. Read `N00_genesis/P01_knowledge/library/kind/kc_content_factory.md` -- the kind-KC --
   for the Naming Collision table (THREE unrelated "content factory" systems share this name)
7. Check existing content_factory artifacts to avoid brief/config overlap

## Phase 2: COMPOSE
1. Read `bld_schema_content_factory.md` -- source of truth for the ContentBrief + row fields
2. Read `bld_output_template_content_factory.md` -- template structure
3. Fill frontmatter: id, kind: content_factory, pillar: P04, title, version, quality: null
4. Write Brief Contract section: topic, post_id, source_facts, hashtags, channels,
   base_asset_type, canonical, post_group, alt_text
5. Write Channel Matrix section: {channel -> format} table (default or tenant-overridden)
6. Write Grounding section: which engine (`cex_grounded_copy.extract_copy`) or the
   degrade-never deterministic fallback (no llm injected -> topic+facts projection)
7. Write Row Contract section: every field a produced row carries + its birth-state
   (approved=False, publish_status=pending, storage_url=None)
8. Write Handoffs section: review-gate contract (approval triad) + publish-seam contract
   (fail-closed, hashtag clamp per platform)
9. Ensure zero hardcoded company names -- ALL via `{{variable}}` where the artifact is a
   reusable template; a concrete instance names the real business
10. Ensure UNIQUE(post_id, channel, format) is stated as a hard invariant, not a suggestion

## Phase 3: VALIDATE
1. Check the Brief Contract lists all 9 ContentBrief fields (topic through alt_text)
2. Verify the Channel Matrix covers >= 2 channels (a single-channel brief is valid but
   the fan-out pattern is meant for >= 2)
3. Verify every row-contract field from `bld_schema_content_factory.md` is present
4. Verify the artifact states rows are born `approved=False` / `publish_status=pending`
   -- NEVER pre-approved
5. Verify the publish seam is described as fail-closed / vendor-agnostic (no real
   provider hardcoded)
6. Verify hashtag clamping is stated per-platform (instagram 5, tiktok 30, linkedin 8,
   twitter 3, facebook 30, pinterest 20, threads 5; default 30)
7. Check body <= 8192 bytes per file (this kind's own `max_bytes`)
8. Cross-check: does the artifact accidentally describe the `cexai/cexai/content_factory/`
   VIDEO package (MoneyPrinterTurbo/Chatterbox) instead of THIS kind's produce->review->
   publish trio? If so, fix -- see the Naming Collision table

## ISO Loading

```yaml
loader: cex_skill_loader
injection_point: F3_compose
priority: high
```

```bash
python _tools/cex_skill_loader.py --verify content_factory
```

## Properties

| Property | Value |
|----------|-------|
| Kind | `instruction` |
| Pillar | P03 |
| Domain | content factory construction |
| Pipeline | 8F (F1-F8) |
| Scorer | cex_score.py |
| Compiler | cex_compile.py |
| Retriever | cex_retriever.py |
| Quality target | 9.0+ |
| Density target | 0.85+ |

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[content-factory-builder]] | downstream | 0.47 |
| [[bld_knowledge_card_content_factory]] | upstream | 0.40 |
| [[bld_schema_content_factory]] | upstream | 0.38 |
| [[bld_output_template_content_factory]] | downstream | 0.36 |
| [[p01_kc_content_factory]] | upstream | 0.35 |
