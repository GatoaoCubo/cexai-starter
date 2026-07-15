---
kind: feature_template
feature_name: content_factory
vertical: 16_company_stack
round_added: 22
pillars: [P03, P05, P10]
adr_019_packages: [tools/web/, memory/]
feature_dependencies: [feature_brand_vault]
brand_niche_constraints: null
open_vars:
  - name: brand_name
    type: str
    description: "Brand name in generated copy."
    filler_role: compiler
    filler_stage: F1_CONSTRAIN
    context_hints: [brand_config.brand_name]
    constraints: {min_length: 1, max_length: 80}
    default_filler_strategy: use_first_context_hint
    required: true
    default_value: null
    rebind_allowed: true
  - name: brand_niche
    type: str
    description: "Drives content topic generation + voice constraints."
    filler_role: compiler
    filler_stage: F1_CONSTRAIN
    context_hints: [brand_config.brand_niche]
    constraints: {min_length: 1, max_length: 200}
    default_filler_strategy: use_first_context_hint
    required: true
    default_value: null
    rebind_allowed: true
  - name: target_audience
    type: str
    description: "Drives content tone, vocabulary, register."
    filler_role: n02
    filler_stage: F3_INJECT
    context_hints: [brand_config.target_audience]
    constraints: {min_length: 3, max_length: 150}
    default_filler_strategy: use_first_context_hint
    required: true
    default_value: null
    rebind_allowed: true
  - name: primary_language
    type: enum
    description: "Output language for generated content."
    filler_role: compiler
    filler_stage: F1_CONSTRAIN
    allowed_values: ["PT-BR", "EN", "ES", "FR", "DE", "IT", "JA", "ZH"]
    context_hints: [brand_config.primary_language]
    constraints: {}
    default_filler_strategy: use_first_context_hint
    required: false
    default_value: "EN"
    rebind_allowed: true
  - name: brand_voice
    type: dict
    description: "Voice attributes: archetype, tone, prohibited phrases, mandatory phrases."
    filler_role: n02
    filler_stage: F3_INJECT
    context_hints: [brand_config.brand_voice]
    constraints: {}
    default_filler_strategy: gdp_ask
    required: true
    default_value: null
    rebind_allowed: true
  - name: visual_style
    type: dict
    description: "Visual identity: color palette, typography, logo positioning, aspect ratios."
    filler_role: n02
    filler_stage: F3_INJECT
    context_hints: [brand_config.visual_style]
    constraints: {}
    default_filler_strategy: gdp_ask
    required: true
    default_value: null
    rebind_allowed: true
  - name: enabled_formats
    type: list[str]
    description: "Which content formats are generated (e.g., ['carousel', 'reel', 'static_image', 'short_video', 'long_video', 'blog_post'])."
    filler_role: user
    filler_stage: F4_REASON
    context_hints: [brand_config.enabled_formats]
    constraints: {min_items: 1}
    default_filler_strategy: gdp_ask
    required: true
    default_value: null
    rebind_allowed: true
  - name: tts_provider
    type: enum
    description: "Text-to-speech provider for video narration."
    filler_role: n05
    filler_stage: F3_INJECT
    allowed_values: ["edge_tts", "elevenlabs", "openai_tts", "google_tts", "azure_tts", "none"]
    context_hints: [brand_config.tts_provider]
    constraints: {}
    default_filler_strategy: use_default_value
    required: false
    default_value: "edge_tts"
    rebind_allowed: true
---

# Feature Template: Content Factory

**Purpose**: an automated content generation pipeline that turns brief/topic inputs into per-channel content variants (carousels, reels, static posts, blog posts) calibrated to the brand voice + visual style.

---

## Pipeline architecture

```
brief (topic + format + channel set)
  -> script generation (LLM via router)
  -> scene composition (per format)
  -> media assembly (TTS + visuals from brand_vault + endcard)
  -> per-channel variant (cropping, captioning, hashtag policy)
  -> approval gate (content_library row, approved=false default)
  -> publishing (feature_publishing.md)
```

Each step is provider-agnostic where possible (LLM via router; TTS via configurable provider; visual assembly via ffmpeg or equivalent).

---

## Data schema (recommended)

```yaml
# Content library schema
table: content_library
columns:
  - name: id                       # uuid PK
  - name: post_id                  # logical content identifier
  - name: post_group               # campaign / theme grouping
  - name: channel                  # ig_feed | ig_reels | fb | tiktok | linkedin | pinterest | threads | youtube_shorts | blog | ...
  - name: format                   # carousel | reel | static | short_video | long_video | blog_post
  - name: asset_type               # image | video | gif | text_only
  - name: storage_url              # public URL of the rendered asset
  - name: caption_text             # final caption (post-substitution)
  - name: hashtags                 # text[] respecting per-channel cap
  - name: scheduled_at             # timestamp for publishing
  - name: approved                 # bool; gates publishing
  - name: publish_status           # pending | scheduled | published | failed | archived (NOT 'cancelled')
  - name: publishing_job_id        # ID returned by feature_publishing.md
  - name: brief_id                 # FK to brief that generated this row
  - name: created_at
  - name: updated_at
```

**Note on `publish_status`**: `archived` is the canonical "do not publish" state. NEVER `cancelled` -- avoid that token to keep DB CHECK constraints simple.

---

## Briefs

Briefs are markdown files with YAML frontmatter describing what to generate:

```yaml
# Brief frontmatter
brief_id: <unique>
post_group: <campaign>
topic: <topic text>
formats: [carousel, reel, static]
channels: [ig_feed, ig_reels, tiktok]
scheduled_base_date: 2026-06-01
duration_seconds: [10, 60]   # for video formats
scene_pool: <pool_name>      # references brand_vault
narration_voice: <voice_id>  # for TTS
notes: <free-form>
```

A brief is the deterministic input; the factory's output (content_library rows) is the deterministic result. Re-running the factory upserts -- which RESETS `scheduled_at` to `scheduled_base_date` and `approved` to false. **Lesson**: edit briefs, not rows.

---

## Hashtag policy per channel

Channels cap hashtag counts. The factory enforces:

| Channel | Hashtag cap | Notes |
|---------|-------------|-------|
| ig_feed | 5 | Lower is often higher-performing per platform algo. |
| ig_reels | 5 | Same as feed. |
| threads | 5 | Per Threads guidance. |
| facebook | 8 | More tolerant. |
| linkedin | 8 | Professional audience tolerates more. |
| tiktok | 30 | Discovery-driven; cap is generous. |
| pinterest | 30 | Discovery-driven. |
| ig_stories | (disabled in v1) | Re-enable only after channel-specific smoke test. |

Deployer overrides per channel via `enabled_channels` extension.

---

## Brand vault dependency

The factory consumes assets from `feature_brand_vault.md` (deferred to R23). v1 deployers may provide a flat directory of brand-approved images/videos/music. R23's brand_vault formalizes this.

Asset categories (recommended):
- `art_pool/` -- editable scene images (Midjourney exports, stock photo licensed, original photography)
- `brand_lifestyle/` -- branded photography
- `videos/` -- B-roll, short clips
- `gifs/` -- looping accents
- `music/` -- licensed (CC-BY or commercial) audio tracks with attribution requirements
- `logo_loop.gif` -- endcard logo animation

Each asset has a license file documenting source + attribution requirements (e.g., Kevin MacLeod CC-BY 4.0 requires the `"Music: Kevin MacLeod (incompetech.com), CC-BY 4.0"` line in the caption).

---

## Determinism

- Script generation runs at `temperature=0.0` for the same brief input -> same script.
- Scene composition is deterministic given the same brief + asset pool + RNG seed.
- TTS output is deterministic given the same provider + voice + text.

This enables re-runnable factory output, but ALSO means the upsert RESETS scheduled_at on every re-run. Deployer documents this for their ops team.

---

## Approval gate

Generated content_library rows ship with `approved = false`. A human reviewer in `/admin/conteudo` (or `/admin/content`) toggles `approved = true` per row. Only approved rows enter the publishing queue.

This gate prevents auto-publishing of low-quality or off-brand outputs.

---

## Integration contracts

- Consumes from: `feature_brand_vault.md` (assets), `feature_catalog.md` (product references in promo content).
- Provides to: `feature_publishing.md` (publishes approved rows).
- LLM dispatch via `cexai.foundation.invocation.router` (provider-agnostic).
- TTS dispatch via `tts_provider` open_var.

---

## Out of scope

- Image generation via diffusion models (deployer extends; brand_vault assets are pre-existing).
- Video editing UI (factory is automated; no UI for manual scene editing).
- A/B testing of variants (deferred to R23 `feature_experiments.md`).
- Performance attribution (clicks, conversions back to specific posts) -- requires analytics; deferred to R23 `feature_analytics.md`.
