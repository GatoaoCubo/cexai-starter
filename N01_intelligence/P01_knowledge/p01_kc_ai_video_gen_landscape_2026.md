---
id: p01_kc_ai_video_gen_landscape_2026
kind: knowledge_card
card_type: domain_kc
pillar: P01
nucleus: n01
domain: competitive-intelligence
title: "AI Video Generation Landscape 2026 -- Competitive Analysis"
version: 1.0.0
created: "2026-05-12"
quality: null
language: en
author: n01_intelligence
sin_lens: analytical_envy
tldr: "Veo 3.1 + Seedance 2.0 share the cinematic ceiling; Hailuo 02 owns the price floor at $0.028/sec; Sora 2 is a dead end (web/app shutdown April 26, 2026 + API shutdown September 24, 2026); for solo creators the optimal stack is Seedance free tier for drafts + Hailuo 02 paid for shorts + Kling 3.0 when character lock matters."
when_to_use: "When evaluating which AI video tool to integrate, prompt, or recommend for a 2026 solo-creator pipeline; when pricing video infrastructure; when planning multi-model routing or fallback chains"
axioms:
  - "ALWAYS quote per-second cost, max-duration, and native-audio support together -- any benchmark missing one of the three is incomplete"
  - "ALWAYS check the deprecation horizon before committing to a model (Sora 2 is the cautionary tale of 2026)"
  - "NEVER recommend a single tool without naming the second-best alternative -- analytical envy demands a comparison"
  - "NEVER assume free-tier output is watermark-free -- Seedance and Google AI Studio are exceptions, not defaults"
keywords: [ai_video_generation, runway, sora_2, kling_3, pika_2_5, veo_3_1, hailuo_02, luma_ray_3, seedance_2_0, competitive_analysis, 2026, solo_creator]
8f: "F3_inject"
primary_8f: INJECT
tags: [ai_video_generation, competitive_analysis, runway, sora, kling, pika, veo, hailuo, luma, seedance, 2026, solo_creator]
feeds_kinds: [competitive_matrix, decision_record, model_provider, content_monetization]
related:
  - p01_kc_runway_api
  - p01_kc_competitor_langchain
  - p01_kc_content_formats_global
---

> **[DISTILL ANNOTATION]** This file cites tool(s) not shipped in this tenant (Central-only): cex_image_gallery. Inline citations are marked `[NOT SHIPPED in this tenant -- Central-only tool]`.

# AI Video Generation Landscape 2026

> N01 Analytical Envy lens: insatiable hunger for benchmarks, ruthless cross-comparison, no single tool wins all axes.

---

## TL;DR (3 sentences)

Veo 3.1 and ByteDance Seedance 2.0 share the cinematic-quality ceiling in 2026, with Kling 3.0 close behind on character consistency and the only one in the top three that solves multi-shot character drift natively. Sora 2 is dead-tier infrastructure -- OpenAI announced the consumer experience shuts down April 26, 2026 and the API on September 24, 2026, making it the riskiest pipeline anchor of the year. For a solo creator entrepreneur the optimal 2026 stack is Seedance 2.0 free tier (100 credits/day, no watermark) for drafts, Hailuo 02 at $0.028/sec for finished shorts, and Kling 3.0 Pro for any scene requiring identical-face character locking across cuts.

---

## Comparison Matrix

| Tool | Latest Version | Max Duration | Resolution | Native Audio | Price (USD/sec) | API Available | Best For |
|------|----------------|--------------|------------|--------------|-----------------|---------------|----------|
| Runway | Gen-4.5 + Gen-4 Turbo | 60s (chained) | up to 4K | yes | ~$0.05 (Turbo) / $0.12 (Gen-4) credits | yes | Multi-model aggregator subscription |
| OpenAI Sora | Sora 2 / Sora 2 Pro | 15-25s | 720p (base) / 1024p (Pro) | yes (dialogue + SFX) | $0.10 base / $0.30-0.50 Pro | yes (until 2026-09-24) | DEPRECATED -- do not anchor pipelines |
| Kuaishou Kling | Kling 3.0 (Feb 2026) | 15s multi-shot | 4K @ 48fps | yes (Omni, multi-language) | $0.084-0.168 official, ~$0.126 via Atlas Cloud | yes (Fal, WaveSpeed, Atlas) | Character consistency + cinematic motion |
| Pika | Pika 2.5 + PikaStream | ~10s | 1080p | partial (effects only) | credit-based ($8-76/mo) | limited | Effects (Pikaswaps, Pikadditions, frames) |
| Google Veo | Veo 3.1 + 3.1 Fast | 140s+ chained (20 clips) | 1080p (Pro) / 4K (Ultra) | yes (native conv + SFX) | $0.15 Fast / $0.40 Standard via Gemini API | yes (Gemini + Vertex AI) | Best overall cinematic + 4K + scene extension |
| MiniMax Hailuo | Hailuo 02 / 2.3 | 10s | 1080p @ 24-30fps | yes (in 2.3) | $0.028/sec ($0.28 per 10s video) | yes (Fal, BytePlus) | Cheapest 1080p; physics + dynamics |
| Luma | Ray 3 / Ray 3.14 | 10s | 1080p native + HDR | yes | ~$0.08-0.10/s (800 credits / 10s) | yes | HDR pipeline, reasoning-driven, draft mode |
| ByteDance Seedance | Seedance 2.0 (Feb 2026) | up to 12s multi-shot | 1080p multi-shot | yes (unified audio-video joint) | $0.05-0.14/s (PiAPI / Atlas / BytePlus) | yes (PiAPI, Atlas, BytePlus, OpenRouter) | NEWCOMER -- top 2026 ranking; multi-shot storytelling |

> Notes on the matrix: prices are official primary-vendor rates; aggregators like Higgsfield, Fal, WaveSpeed, and Atlas Cloud routinely shave 20-30% by buying bulk capacity. Resolution claims are vendor-quoted -- real-world output frequently downgrades when motion complexity rises.

---

## Per-tool deep dive

### Runway Gen-4.5

- **Features**: Gen-4.5 is the latest flagship; Gen-4 supports up to 60 seconds with temporal consistency in 4K; Gen-4 Turbo generates 10-second clips in ~30 seconds (5x faster than standard Gen-4) at lower quality. As of 2026, Runway transitioned from a pure first-party model house into a multi-model aggregator -- one Runway subscription includes Veo, Kling, Seedance, FLUX, Seedream.
- **Pricing**: Standard $15/mo ($12/mo annual), Pro $35/mo ($28/mo annual), Unlimited $95/mo ($76/mo annual), Enterprise custom. Credit system: Gen-4 Turbo = 5 credits/sec, Gen-4 = 12 credits/sec.
- **Strengths**: Subscription aggregator means no model lock-in; world-consistency feature for camera motion; mature API (kc_runway_api documents the v1 REST surface); Turbo tier is genuinely fast at acceptable quality.
- **Limitations**: First-party Gen-4.5 is no longer top-3 against Veo 3.1 / Kling 3.0 / Seedance 2.0; pricing-per-second is opaque (credit system) compared with the per-second clarity Veo and Hailuo offer.
- **Best for**: Studios that want one bill and one API to access multiple model families.
- **Demo / docs**: [Runway pricing](https://runwayml.com/pricing) - [Gen-4.5 research](https://runwayml.com/research/introducing-runway-gen-4.5) - [Gen-4 research](https://runwayml.com/research/introducing-runway-gen-4).

### OpenAI Sora 2 (DEPRECATED 2026)

- **Features**: Released 2026-09-30 (note: prior to the deprecation announcement). 15-25 second clips with synchronized dialogue, sound effects, music. Both text-to-video and image-to-video. Cameo feature for character carryover. Sora 2 Pro adds 1024p resolution.
- **Pricing**: API = $0.10/sec (base, 720p), $0.30/sec (Pro 720p), $0.50/sec (Pro 1024p). Consumer access via ChatGPT Plus ($20/mo) and Pro ($200/mo) -- as of 2026-01-10 free users lost video generation entirely.
- **Strengths**: Best-in-class realistic physics, fluid, gravity simulations across the matrix; native synchronized audio with character voices; the only model with the cameo persistence feature.
- **Limitations**: **OpenAI announced March 2026 that Sora web/app discontinues 2026-04-26 and the API discontinues 2026-09-24.** Building a pipeline on Sora 2 in mid-2026 is acquiring infrastructure debt with a known expiration date. Even before sunset, the $0.30-0.50/sec Pro tier was the most expensive top-tier option per second.
- **Best for**: Nothing forward-looking. Use only for legacy migrations or to harvest archived outputs.
- **Demo / docs**: [Sora 2 guide](https://wavespeed.ai/blog/posts/openai-sora-2-complete-guide-2026/) - [Sora 2 Pro pricing](https://openrouter.ai/openai/sora-2-pro) - [Policy update](https://help.apiyi.com/en/openai-sora-2-policy-change-plus-pro-only-en.html).

### Kuaishou Kling 3.0

- **Features**: Released 2026-02-05. Extended clip length up to 15 seconds (versus Kling 2.6's 10s ceiling). 4K image generation. Chain-of-Thought reasoning for scene coherence. **Multi-shot scene logic with consistent characters across cuts** (Elements 3.0 video-reference system that locks facial geometry, scars, iris color). Native multi-language audio. Motion Brush feature. Kling 2.6 (Dec 2025) was the first Kling to generate synchronized audio + video in a single pass at 1080p @ 48fps.
- **Pricing**: Standard $6.99/mo (includes commercial rights). Basic ~$10/mo (660 credits = 33 standard 720p videos or 3,300 images). Pro ~$37/mo (3,000 credits = 150 standard videos). Kling 3.0 API: $0.084/sec standard, $0.168/sec Pro mode with video input; Atlas Cloud reseller ~30% cheaper.
- **Strengths**: The only top-3 model with a documented solution for character drift across multi-shot scenes. Cinematic lighting and complex motion (hair, liquids, fabric) are best-in-class alongside Veo 3.1. Commercial license at $6.99/mo undercuts most US competitors.
- **Limitations**: Onboarding for overseas developers is rough (vendor-quoted -- documentation is unclear for non-Chinese accounts). 22M user base is large but skews toward Asia-Pacific creators -- Western-centric prompts may need adaptation.
- **Best for**: Solo creators needing character continuity across cuts; narrative shorts where the same person appears in 3+ shots.
- **Demo / docs**: [Kling 2.6 announcement](https://medium.com/@CherryZhouTech/kling-2-6-elevates-ai-video-integrate-advanced-voice-and-motion-control-944677780c50) - [Kling 3.0 review](https://www.atlascloud.ai/blog/guides/kling-3.0-review-features-pricing-ai-alternatives) - [Pricing comparison](https://aitoolanalysis.com/kling-ai-complete-guide/).

### Pika 2.5

- **Features**: Scene Ingredients (upload your own characters / objects). Pikaframes (turn 2-5 images into smooth transition video). Pikaswaps (replace an object in a video with full lighting + motion preservation). Pikadditions (insert new characters / objects into footage). PikaStream 1.0 = real-time model that gives AI agents a face + voice + live presence in video meetings (Google Meet integration).
- **Pricing**: Free tier (limited). Pika $8/mo (entry creator). Pro $76/mo (2,300 credits, faster generation). Fancy (6,000 credits/mo, premium speed, commercial-grade).
- **Strengths**: Effects-first feature set is uncontested -- no other top tool has Pikaswaps or Pikadditions as a primitive. PikaStream is the most novel 2026 feature in the matrix (live agent face / voice for meetings).
- **Limitations**: Raw text-to-video quality has fallen behind Veo 3.1 / Kling 3.0 / Seedance 2.0. Native audio is partial (effects-driven, not full dialogue). Resolution caps at 1080p with 480p on lower tiers.
- **Best for**: Creators whose value-add is editing existing footage with effects, not generating from scratch; livestreamers / virtual presenters via PikaStream.
- **Demo / docs**: [Pika pricing](https://pika.art/pricing) - [Pika 2.5 review](https://genra.ai/blog/pika-2-5-complete-guide-review).

### Google Veo 3.1

- **Features**: Five versions live via API -- Veo 2, Veo 3, Veo 3 Fast, Veo 3.1, Veo 3.1 Fast. Text-to-video + image-to-video. Native synchronized audio (conversations + SFX) for Veo 3, 3.1, and the Fast variants. 1080p (Pro) / 4K (Ultra) output. **Scene extension up to 20 chained clips for 140+ second narratives.** Frames-to-video transitions between two images. Vertical Shorts mode. 4K upscaling.
- **Pricing**: Google AI Plus $7.99/mo (Veo 3.1 Fast via Flow). Google AI Pro $19.99/mo (up to 90 Veo 3.1 Fast videos / month via Gemini app). Google AI Ultra $249.99/mo. API: Veo 3.1 Fast $0.15/sec, Veo 3.1 Standard $0.40/sec via Gemini API. Vertex AI charges $0.50/sec for Veo 2 -- ~30% premium over Gemini API. Third-party providers (fal.ai, Replicate) start at $0.10/sec for Veo 3.1 Fast.
- **Strengths**: The benchmark for prompt adherence and 4K output across the matrix. Native audio rivals Kling 3.0 Omni and Seedance 2.0. Scene extension to 140+ seconds is uncontested -- no other vendor offers chained narratives at this length. The $7.99/mo entry tier is the cheapest first-party path to a top-3 model.
- **Limitations**: Vertex AI pricing premium over Gemini API is unjustified for most use cases (~30% surcharge for the same model). Ultra at $249.99/mo is premium-priced relative to Runway Unlimited at $95/mo for similar generation volume.
- **Best for**: Solo creators wanting cinematic B-roll; narrative shorts longer than 15 seconds (chain multiple clips); anyone building on Google's infrastructure who already pays for Workspace / Cloud.
- **Demo / docs**: [Gemini API pricing](https://ai.google.dev/gemini-api/docs/pricing) - [Veo 3.1 API guide](https://www.veo3gen.app/blog/veo-3-1-api-access-cost) - [Veo 3 pricing 2026](https://www.veo3ai.io/blog/veo-3-pricing-2026).

### MiniMax Hailuo 02

- **Features**: Released June 2025 (with Hailuo 2.3 follow-on enhancing dynamic expression). 1080p resolution, up to 10 seconds, 24-30 FPS. NCR architecture: 2.5x faster training/inference, 3x larger parameter count, 4x training data vs Hailuo 01. **Accurate object interactions, fluid dynamics, and natural motion -- handles extreme physics (acrobatics) reportedly better than Sora 2 at a fraction of the price.**
- **Pricing**: **$0.028/sec ($0.28 per 10-second 1080p video) is the lowest top-tier price in the matrix.** Free tier: ~3-5 videos/day. Max plan: $199.99/mo (20,000 credits + unlimited Relax Mode).
- **Strengths**: The price-quality leader for finished 1080p shorts. Physics simulation is class-leading among non-Sora tools. Subscription tier ($9.99/mo entry) plus per-video pricing flexibility.
- **Limitations**: 10-second hard cap on duration (no chaining feature like Veo 3.1). Hailuo 02 native audio is only added in Hailuo 2.3 -- 02 standalone is silent. Character consistency is weaker than Kling 3.0.
- **Best for**: Cost-conscious solo creators producing 5-30 second shorts at 1080p; B-roll where price-per-output matters more than character lock.
- **Demo / docs**: [Hailuo 02 benchmarks](https://ucstrategies.com/news/hailuo-02-1080p-ai-video-at-0-28-specs-benchmarks-pricing-2026/) - [MiniMax Hailuo 02](https://www.minimax.io/news/minimax-hailuo-02) - [Hailuo pricing](https://hailuoai.video/subscribe).

### Luma Ray 3 / Ray 3.14

- **Features**: Ray 3 is a reasoning-driven model designed with entertainment / advertising / gaming creatives. Best-in-class video-to-video including character reference and keyframes. Draft Mode for rapid exploration. **First-to-market HDR pipeline -- studio-grade HDR through native high dynamic range color generation, exported as 16-bit EXR.** Ray 3.14 adds native 1080p, 4x faster performance, 3x lower cost.
- **Pricing**: Free (30 generations/month). Standard $30/mo (120 generations). Pro $90/mo (400 generations). A 10-second video on Ray 3.14 at 1080p ~ 800 credits. Annual billing saves ~20%.
- **Strengths**: The only model in the matrix with native HDR pipeline -- relevant for cinema / broadcast workflows. Reasoning capabilities (think in concepts, evaluate self, iterate) are uncontested as a primitive. Free tier (30 generations) is more generous than Veo or Sora.
- **Limitations**: Generation count caps (400/mo Pro) feel constrained vs Hailuo's per-video pricing where heavy use scales linearly. Character consistency lags Kling 3.0.
- **Best for**: Workflows targeting HDR delivery (Apple TV, Dolby Vision); creators in entertainment / advertising verticals with high-color-spec requirements.
- **Demo / docs**: [Luma pricing](https://lumalabs.ai/pricing) - [Ray 3 / Dream Machine](https://lumalabs.ai/ray) - [Luma Dream Machine pricing 2026](https://lumadreammachine.com/pricing/).

### ByteDance Seedance 2.0 (NEWCOMER 2026)

- **Features**: Released February 2026. **First AI video model with unified audio-video joint generation (not post-processed).** Multi-shot storytelling from a single prompt. Phoneme-level lip-sync in 8+ languages. Accepts text, images, videos, audio as inputs (up to 12 assets in a single generation). Cinematic multi-shot video with native audio sync, consistent characters, frame-level precision. Currently ranks #1 in independent comparisons (Higgsfield, TeamDay.ai, Atlas Cloud benchmarks).
- **Pricing**: $0.05-$0.14/sec depending on provider tier. PiAPI: seedance-2 from $0.10/sec, seedance-2-fast from $0.08/sec. Atlas Cloud: $0.10/sec Standard, $0.081/sec Fast. BytePlus: $0.15 for 5-second Pro clip. Official ByteDance: 46 CNY per 1M tokens (~1 CNY/sec ~ $0.14/sec) for pure generation. **Free tier: 100 credits/day, no credit card, no watermark, 1080p output.**
- **Strengths**: Top-ranked across multiple independent 2026 benchmarks. Unified audio-video generation is structurally superior to post-processed audio. Multi-shot from a single prompt eliminates the chained-clip stitching tax Veo 3.1 requires. Free tier is the most generous in the matrix (Veo only gives Studio access, Sora gave nothing as of Jan 2026).
- **Limitations**: Only 3 months old -- track record is shorter than Veo / Kling / Runway. As of mid-2026, official API access is still gated behind quota / free experience -- production-grade access depends on PiAPI / Atlas / BytePlus resellers. Multi-shot duration cap of ~12s falls short of Veo 3.1's 140s+ chained narratives.
- **Best for**: Solo creators wanting top-tier output without paying the premium API price; multi-shot narrative shorts with native audio; daily prototyping via free tier.
- **Demo / docs**: [Seedance 2.0](https://higgsfield.ai/seedance/2.0) - [ByteDance Seedance](https://seed.bytedance.com/en/seedance2_0) - [Seedance complete guide](https://www.atlascloud.ai/blog/guides/seedance-2.0-complete-guide) - [Seedance pricing](https://aicost.org/blog/seedance-2-0-api-pricing-breakdown-2026).

### Bonus -- Other 2026 newcomers worth tracking

- **Vidu Q3** -- Smart Cuts technology generates a 16-second multi-camera sequence from a single prompt; positioned as the "Narrative Director" model.
- **Alibaba Wan 2.7 / Wan 2.6 / Wan 2.2** -- Open-source models; Wan 2.2 specifically can run locally for unlimited generation with no watermark and full commercial rights.
- **APOB AI** -- Purpose-built for AI influencer / creator-avatar continuity; Advanced Face-Lock for identical-character output across many videos.
- **LTX Video 2.0** -- Available via Fal.AI side-by-side comparison rigs.

These are not in the primary matrix because their adoption / API maturity is still well below the top eight, but a solo creator running 6-month-out planning should monitor them.

---

## Verdict for solo creators

| Need | Recommended Tool | Runner-up | Reason |
|------|------------------|-----------|--------|
| Best free tier (no watermark) | **Seedance 2.0** (100 credits/day, 1080p, no watermark) | Google AI Studio with Veo 3.1 trial | Seedance is more generous and watermark-free out of the box; Veo Studio is cloud-based with daily limits but no daily credit refresh equivalent. |
| Best paid for shorts (price-quality) | **Hailuo 02** at $0.028/sec / $0.28 per 10s 1080p video | Seedance 2.0 at $0.05-0.08/sec via Fast tier | Hailuo's per-video flat rate is the cheapest 1080p in the matrix and physics is class-leading among non-Sora tools. |
| Best for cinematic B-roll | **Google Veo 3.1** ($0.15/sec Fast, $0.40 Standard) | Kling 3.0 Pro ($0.168/sec) | Veo 3.1 wins prompt adherence + 4K + scene extension to 140+ seconds; Kling 3.0 matches lighting and motion fidelity at a similar price. |
| Best for character consistency across cuts | **Kling 3.0** with Elements 3.0 video-reference | APOB AI for influencer / avatar workflows | Kling explicitly locks facial geometry, scars, iris color across multi-shot scenes -- the only top-3 model with a named solution for character drift. |
| Best for narrative multi-shot from one prompt | **Seedance 2.0** | Vidu Q3 (16-second smart-cut sequences) | Seedance generates multi-shot stories in one pass; Vidu Q3 offers smart-cut camera changes from a single prompt. |
| Best for HDR / broadcast delivery | **Luma Ray 3.14** | Veo 3.1 Ultra (4K, but SDR) | Luma is first-to-market with native HDR pipeline and 16-bit EXR export. |
| Best for live agent / virtual presence | **Pika PikaStream 1.0** | n/a | Only product with real-time face + voice in video meetings (Google Meet integration). |
| Best aggregator subscription (one bill) | **Runway** at $35/mo Pro | Higgsfield (Seedance, Kling, Veo, Sora, Wan in one workspace) | Runway includes Veo, Kling, Seedance, FLUX, Seedream in a single subscription; Higgsfield is web-only but accesses more model families. |

### What to NOT use

- **Sora 2 / Sora 2 Pro** -- deprecated. Web/app shutdown 2026-04-26, API shutdown 2026-09-24. Any new build on Sora 2 is acquiring known-expiring infrastructure.
- **Free tiers with watermarks** for client-delivered work -- only Seedance, CapCut desktop, and local Wan 2.2 are watermark-free at zero cost.

---

## Cross-reference notes (CEX context)

- The existing CEX integration `p01_kc_runway_api` (Runway Gen-4) is still valid for first-party Runway video calls, but in 2026 the Runway subscription is more useful as a multi-model aggregator than as a Gen-4-only endpoint.
- `_tools/cex_image_gallery.py` follows the same provider-routing pattern (OpenAI gpt-image-1) that would apply if a `cex_video_gallery.py` were authored -- Seedance / Hailuo / Veo all expose comparable REST surfaces.  <!-- [NOT SHIPPED in this tenant -- Central-only tool] -->
- `reference_short_form_image_pipeline.md` (Dicas e Truques Pack 04) used gpt-image-1 at $2.10 per 50-image pack. The equivalent 50-video pack at 10s each in 1080p would cost ~$14 via Hailuo 02 or ~$25-40 via Seedance 2.0 paid tier -- still well below Sora 2 Pro's $150 for the same volume.

---

## Sources (all retrieved 2026-05-12)

1. [Runway pricing](https://runwayml.com/pricing)
2. [Runway Gen-4.5 research](https://runwayml.com/research/introducing-runway-gen-4.5)
3. [Runway Gen-4 research](https://runwayml.com/research/introducing-runway-gen-4)
4. [Runway pricing guide 2026 (Somake)](https://www.somake.ai/blog/runway-ai-pricing)
5. [Sora 2 complete guide 2026 (WaveSpeed)](https://wavespeed.ai/blog/posts/openai-sora-2-complete-guide-2026/)
6. [Sora 2 API pricing 8 tiers](https://www.aifreeapi.com/en/posts/sora-2-api-pricing-quotas)
7. [Sora 2 Plus/Pro policy change](https://help.apiyi.com/en/openai-sora-2-policy-change-plus-pro-only-en.html)
8. [Sora 2 Pro OpenRouter](https://openrouter.ai/openai/sora-2-pro)
9. [Kling 3.0 review (Atlas Cloud)](https://www.atlascloud.ai/blog/guides/kling-3.0-review-features-pricing-ai-alternatives)
10. [Kling 2.6 (Medium)](https://medium.com/@CherryZhouTech/kling-2-6-elevates-ai-video-integrate-advanced-voice-and-motion-control-944677780c50)
11. [Kling complete guide (AI Tool Analysis)](https://aitoolanalysis.com/kling-ai-complete-guide/)
12. [Pika art pricing](https://pika.art/pricing)
13. [Pika 2.5 review (Genra.ai)](https://genra.ai/blog/pika-2-5-complete-guide-review)
14. [Pika labs pricing (ImagineArt)](https://www.imagine.art/blogs/pika-labs-pricing)
15. [Veo 3.1 API access & cost](https://www.veo3gen.app/blog/veo-3-1-api-access-cost)
16. [Veo 3 pricing 2026](https://www.veo3ai.io/blog/veo-3-pricing-2026)
17. [Gemini API pricing](https://ai.google.dev/gemini-api/docs/pricing)
18. [Hailuo 02 specs and benchmarks](https://ucstrategies.com/news/hailuo-02-1080p-ai-video-at-0-28-specs-benchmarks-pricing-2026/)
19. [MiniMax Hailuo 02 announcement](https://www.minimax.io/news/minimax-hailuo-02)
20. [MiniMax Hailuo 2.3](https://www.minimax.io/news/minimax-hailuo-23)
21. [Hailuo AI subscribe](https://hailuoai.video/subscribe)
22. [Luma plans and pricing](https://lumalabs.ai/pricing)
23. [Luma Ray 3 / Dream Machine](https://lumalabs.ai/ray)
24. [Luma Dream Machine pricing 2026](https://lumadreammachine.com/pricing/)
25. [Seedance 2.0 (ByteDance)](https://seed.bytedance.com/en/seedance2_0)
26. [Seedance 2.0 (Higgsfield)](https://higgsfield.ai/seedance/2.0)
27. [Seedance 2.0 complete guide (Atlas)](https://www.atlascloud.ai/blog/guides/seedance-2.0-complete-guide)
28. [Seedance 2.0 pricing breakdown](https://aicost.org/blog/seedance-2-0-api-pricing-breakdown-2026)
29. [Best AI video generators 2026 (Higgsfield)](https://higgsfield.ai/blog/best-ai-video-generators-2026)
30. [Best AI video models 2026 (TeamDay)](https://www.teamday.ai/blog/best-ai-video-models-2026)
31. [AI video generation 2026 comparison (Lushbinary)](https://lushbinary.com/blog/ai-video-generation-sora-veo-kling-seedance-comparison/)
32. [Top 4 free AI video generators (Atlas)](https://www.atlascloud.ai/blog/guides/top-4-free-ai-video-generators-for-consistent-characters-lip-sync)
33. [7 best AI tools for character consistency (Scribe)](https://scribehow.com/page/7_Best_AI_Tools_for_Character_Consistency_Across_Scenes_2026_for_Filmmakers_Designers_and_Creators__B8Q63QIWRyKgulaUFjZF3w)
34. [APOB AI review for solo creators](https://scribehow.com/page/APOB_AI_Review_2026_The_Most_Consistent_AI_Influencer_Generator_for_Solo_Creators___6Z8qvrCQzyvzPjqM3XPPg)
35. [Best free AI video generators 2026 (Veo3AI)](https://www.veo3ai.io/blog/best-free-ai-video-generators-2026)

---

### How to use

```text
ROLE: You are N05/N02 selecting an AI video tool from this landscape.
ACT:
  - Match the stage need (text-to-video, character consistency, lip-sync, free
    tier) to the tool whose row leads that capability.
  - Prefer tools with an API for the automated content pipeline over UI-only ones.
  - Re-verify pricing/availability before committing; this space moves fast.
OUTPUT: a per-stage video-tool selection grounded in the compared rows.
```

## Related Artifacts

| Artifact | Relationship | Score |
|----------|--------------|-------|
| p01_kc_runway_api | upstream (Runway API surface still valid in 2026) | 0.45 |
| [[p01_kc_content_formats_global]] | related (short-form video formats) | 0.35 |
| [[p01_kc_competitive_intelligence_methods]] | methodology | 0.28 |
| component_map_n01 | identity | 0.25 |
