---
id: p01_kc_video_editing_toolchain_2026
kind: knowledge_card
pillar: P01
nucleus: n03
title: "Video Editing Toolchain 2026 -- Long Recording to Shorts Workflow"
version: 1.0.0
created: "2026-05-12"
quality: null
language: en
tags: [video_editing, davinci_resolve, capcut, premiere, final_cut, descript, opus_clip, submagic, ai_editing, shorts_workflow, 2026, inject]
tldr: "2026 toolchain reference for turning a long OBS recording into short clips -- which editor + AI clipper + caption tool to install, and the solo-creator workflow that ties them together."
when_to_use: "Load (F3 INJECT) when choosing a video-editing/shorts toolchain. Consult for 'what do I install today to cut a 60-min recording into captioned shorts?'"
primary_8f: INJECT
related:
  - visual-workflow-builder
---

# Video Editing Toolchain 2026 -- Long Recording to Shorts Workflow

### How to use

```text
8F verb: INJECT (F3). Read as a buying/workflow reference before producing shorts.
Start from the TL;DR for the install list, then follow the workflow stages to go
from a long recording to captioned clips. Tool choices are tradeoffs (free vs paid,
manual vs AI clipper) -- pick per budget + volume.
```

## TL;DR (answer "what do I install today?")

For a solo creator who records 60-min OBS sessions of 50 sequential ~60s items
separated by a 5-second silence buffer (the Dicas-e-Truques pattern), the
fastest 2026 stack is:

| Budget | Stack | Wall time for 50 shorts |
|--------|-------|--------------------------|
| **$0** | DaVinci Resolve 19 (Free) -- detect scene + manual marker nudge + built-in captions | ~3 hours first pass, ~90 min once muscle memory locks |
| **$23/mo** | DaVinci Resolve 19 (Free) cut + **Submagic** captions + B-roll | ~90 min including publish-ready captions |
| **$29/mo** | **Opus Clip Pro** end-to-end (loses your pack structure; AI re-picks moments) | ~25 min to first batch of 10-20 AI-picked clips |
| **$50/mo** | **Adobe Premiere Pro** ($22.99) + **Submagic** ($23) -- auto-reframe + text-based editing | ~75 min, broadcast quality |

If you must pick one tool today: **DaVinci Resolve 19 Free** (zero cost, native
silence detection via scene-detect, vertical timeline, on-device captions).
Add Submagic when caption styling becomes the bottleneck.

> Counter-intuitive: **Opus Clip is the wrong tool for pre-segmented batch
> recordings.** It is built to find virality moments in unstructured podcasts.
> Your 5-second buffer is already a structural marker -- a deterministic
> silence-split tool beats a stochastic LLM picker for this use case.

## Your scenario (the constraint that picks the tool)

You record in OBS:

- One 60-min session = ~50 sequential dicas
- Each dica is 150-180 words read by `edge-tts` Francisca PT-BR (~60s)
- Between dicas: a 5-second silence buffer inserted by `solo_pack_batch.sh:46-49`
- Visuals: Obsidian Reading View with `cssclasses` mode + locked pack image

Mechanical implication: the audio waveform has 50 talking blocks separated by
50 silence valleys >= 5s long. **Any tool with "split on silence" or "detect
scene by audio" gives you 50 perfectly-cut shorts in one pass.** Stochastic AI
re-cutters (Opus Clip, Submagic Magic Clips) will fight that structure.

## Tool comparison matrix

| Tool | 2026 cost | Mobile? | AI auto-cut | Auto-captions | Auto-reframe 9:16 | Long->shorts native | Learning curve |
|------|-----------|---------|-------------|----------------|--------------------|----------------------|------------------|
| **DaVinci Resolve 19 Free** | $0 (one-time) | iPad only | Scene-detect (manual nudge) | Yes (Studio only -- free is manual) | Manual | Manual | High (pro NLE) |
| **DaVinci Resolve Studio 19** | $295 one-time | iPad sync | Yes (speech-to-text + smart reframe) | Yes (on-device) | Yes (AI subject tracking) | Manual cut, AI assist | High |
| **CapCut Desktop** | Free + Pro ~$10/mo | Yes (iOS/Android) | Auto Cut (beat/speech/text prompt) | Yes (multilingual, 99%) | Yes | Templates + Auto Cut | Low |
| **Adobe Premiere Pro 26.x** | $22.99/mo | iPad ($4.99/mo) | Text-based editing, filler removal, Generative Extend | Yes (Adobe Sensei, 27 languages translate) | Yes (Auto Reframe AI) | Manual + AI assist | Medium-High |
| **Final Cut Pro 11** | $299 Mac one-time / $4.99/mo iPad | Yes (M1+) | Magic Mask, AI color | Transcribe to Captions (English only at launch) | Smart Conform | Manual | Medium |
| **Descript** | $0 / $24 / $35 / $65 /mo | Web + Desktop | Text-based editing, remove silences | Yes (multi-lang) | Yes | Yes (clip from transcript) | Low-Medium |
| **Opus Clip** | $0 / $15 / $29 /mo | Web | ClipAnything + virality score (GPT-4 hook model) | Yes (95% accuracy, 25+ lang, 10+ caption templates) | Yes (AI keyframe reframe) | **YES (flagship feature)** | Very Low |
| **Submagic** | $12 / $23 / $41 /mo | Web | AI Auto-Edit (one-click captions+cuts+b-roll) | Yes (99%, modern styles) | Yes | Magic Clips (batch from long) | Very Low |
| **Riverside Magic Clips** | $15-29/mo | Web + iOS | Yes (transcript-driven) | Yes | Yes | Yes (in same recording tool) | Low |
| **Captions.ai** | $9.99-24/mo | iOS/Android | AI Edit + Eye Contact + Pause Removal | Yes | Yes | Yes | Very Low |

Prices verified May 2026 on each vendor's pricing page; see Sources.

## Best tutorial channels per tool

### DaVinci Resolve 19

- **Casey Faris** ([youtube.com/@CaseyFaris](https://www.youtube.com/channel/UCdfDjoLF5L6lLuDCkJw0P3g)) -- the default beginner-to-intermediate channel. Full courses, weekly tips, version-update reactions.
- **Thom Lyons / Visual+Aid Productions** -- Blackmagic Certified Master Trainer, in editing since 2004. Best for editors transitioning from Premiere/FCP.
- **Darren Mostyn** -- 229K subs, 140+ videos, Senior Colorist with 30 yrs broadcast / 15 yrs Resolve. Pure color grading; skip if you only need cut workflow.
- **Jake Wipp** -- 30K subs, 80+ videos. Templates, Fusion effects, motion graphics. Useful for short-form intro stings.
- **Best 2026 starter playlist**: "Introduction to DaVinci Resolve - Full Course for Beginners (2026)" (~3-4 hours, covers cut page + edit page + deliver).
- **Specific long->shorts tutorial**: "From 16:9 to Vertical: Master YouTube Shorts Editing" -- 9:16 timeline conversion, vertical text safe zones, single-clip vertical export.

### CapCut Desktop

- **Official CapCut Help Center** (capcut.com/help) -- best primary source; tutorials track each release.
- **Miracamp** ("The Ultimate Guide to CapCut AutoCut 2026") -- third-party deep dive on Auto Cut, beat sync, voice cut, text-prompt mode.
- **Workflow tip**: Auto Cut is NOT on CapCut Web -- desktop or mobile only. Top-bar "AI" button > Auto Cut > Voice/Speech mode aligns cuts to natural pauses. Set silence threshold to 4s to catch your 5s buffer.

### Adobe Premiere Pro

- **Phantom Editor Blog** ("What's New in Premiere Pro 26.0") -- best 2026 release-tracking source.
- **Envato Tuts+** Premiere AI tutorials -- "How to Use Auto-Editing and Speech-to-Text" covers text-based editing end-to-end.
- **Adobe Help X** (helpx.adobe.com/premiere) -- official, current, deep. The "Text-Based Editing overview" page is the canonical reference.
- **B Square Visuals** ("Adobe Premiere Pro's New AI Features 2025-2026") -- features-focused review.
- **2026 killer feature**: **Generative Extend** lets you stretch a clip by ~2s using AI-generated content. Useful when your edge-tts dica ran 58s and you need 60s for platform parity.

### Final Cut Pro

- **Apple's official Final Cut Pro release notes** (support.apple.com/102825) -- canonical version log.
- **TechRadar** + **9to5Mac** + **MacRumors** -- best update coverage. The Jan 2026 update (Image Playground, iPad portrait orientation, AI color correction Mac) is the current state of the art.
- **Cult of Mac Final Cut Pro archive** -- ongoing tutorial roundups.
- **Caution**: Transcribe to Captions is **English-only at launch (late 2024/2025)** -- PT-BR users should not pick FCP for caption automation in 2026.

### Descript

- **Descript blog** (descript.com/blog) -- canonical product updates, including the 2026 "Overdub on all plans" change.
- **AIWithIt** ("Descript Review 2026: Edit Videos Faster with AI") -- third-party feature walkthrough.
- **QCall.ai** Overdub honest review -- documents Overdub's intonation limits and PT-BR/accent pitfalls. Critical for non-English creators.

### Opus Clip

- **Opus.pro Pricing page** + the in-app "Clip Anything" tutorial -- official.
- **G2 reviews** + **Ssemble 2026 review** + **BIGVU 2026 review** -- expect 20-40% of AI-picked clips to be discarded or tweaked.
- **Unkoa Marketing 2026 review** -- workflow case studies (podcasts, webinars, YouTube long-form).

### Submagic

- **Filmora's Submagic Review 2026** -- features + pricing tear-down.
- **The Business Dive Submagic Review** -- a content creator's actual test footage.
- **Submagic.co/pricing** -- canonical pricing ($12/$23/$41 tiers as of 2026).
- **Quso.ai "Top 10 Submagic AI Alternatives 2026"** -- useful if Submagic's caption styles don't match your brand.

## AI-assisted long-recording-to-shorts (the workflow that matters)

### Workflow A -- "Free + manual" (DaVinci Resolve 19 Free)

1. Drop the OBS .mp4 onto a 9:16 (1080x1920) timeline (Project Settings -> change from 1920x1080 to 1080x1920).
2. Cut page > **Detect Scene Cuts** (Smart Indicator on the source clip). Most cuts will land near the 5s silence valleys; manually nudge any miss.
3. For each of the 50 clips: name `dica_NN_pack_PP.mov`, drop on a separate timeline track or use compound clips.
4. Captions: Edit page > Subtitle track > Auto-detect (Studio) or manually type-along (Free).
5. Color grade: skip for shorts; use default Rec.709 LUT.
6. Deliver page > YouTube Shorts preset > export 50 individual clips (use a render queue with a script-generated naming pattern).

Wall time first pass: ~3 hours. Skill-locked: ~90 minutes.

### Workflow B -- "Cut free, caption paid" (DaVinci Resolve Free + Submagic)

1. Steps 1-3 of Workflow A: cut the 50 clips in DaVinci Free, export each as a raw 9:16 .mp4.
2. Upload all 50 to Submagic in one batch (Magic Clips supports batch).
3. Submagic's AI Auto-Edit adds captions, B-roll, zoom effects, and one-click brand-styled subtitles in <5 minutes per clip.
4. Submagic exports to YouTube Shorts / Reels / TikTok directly via the social scheduler.

Wall time: ~90 min. Cost: $23/mo Submagic Pro.

### Workflow C -- "AI does everything" (Opus Clip Pro)

1. Drag the 60-min .mp4 into Opus Clip.
2. Opus AI scans, picks the top 10-20 "viral hook" moments using a GPT-4 hook model, applies captions, reframes 9:16, scores each clip 0-100 on virality.
3. Review and discard 20-40% (expected churn per BIGVU + G2 reviews).
4. Publish via Opus's social scheduler.

Wall time: ~25 min. Cost: $29/mo (or $14.50/mo annual). **Trade-off: Opus will NOT respect your 50-dica pack boundaries.** It picks what its model thinks is viral. If you NEED 50 specific dicas in order, Opus is the wrong tool.

### Workflow D -- "Pro pipeline" (Premiere + Submagic)

1. Premiere Pro 26.x text-based editing: transcribe the 60-min audio, delete the 5s silence rows from the transcript -- this auto-cuts the timeline at silences.
2. Use Auto Reframe to convert 16:9 to 9:16 with AI subject tracking.
3. Export 50 clips via the multi-out render queue.
4. Pipe each through Submagic for branded captions + B-roll.

Wall time: ~75 min. Cost: $22.99 Premiere + $23 Submagic = $45.99/mo. Highest ceiling, broadcast-grade output.

## Recommended workflow ranked (for your specific scenario)

| Rank | Workflow | Why for you |
|------|----------|--------------|
| 1 | **Workflow B (DaVinci Free + Submagic)** | Free cut + structured 50-clip boundary preserved + branded captions for Reels/Shorts in <5 min/clip. Best ROI per dollar. |
| 2 | **Workflow A (DaVinci Free alone)** | Zero cost. Use when budget is hard $0 or while learning before adding Submagic. |
| 3 | **Workflow D (Premiere + Submagic)** | Best if you already pay Adobe CC or need broadcast-grade auto-reframe. |
| 4 | **Workflow C (Opus Clip)** | Use ONLY for unstructured long-form (podcast Q&A, livestream rambles) -- NOT for your pre-segmented Dicas packs. |

## AI editing features deep-dive (2026 state of the art)

### Auto-caption accuracy benchmarks

| Tool | Claimed accuracy | Languages | PT-BR support |
|------|--------------------|-----------|----------------|
| Submagic | 99% | 100+ | Yes |
| Opus Clip | 95% (clean audio) | 25+ | Yes |
| Premiere Pro (Adobe Sensei) | Industry-leading (translates 27 langs) | 27 (translation) | Yes |
| Descript | Multi-lang | Many | Yes |
| Final Cut Pro Transcribe to Captions | High (on-device LLM) | **English only at launch** | NO |
| DaVinci Resolve Studio | Good | Multiple | Yes |
| CapCut | 99% claimed | Many | Yes |

PT-BR creators: **avoid Final Cut Pro Transcribe to Captions** -- English only.
Top three for PT-BR: Submagic, Opus Clip, Adobe Premiere (Speech to Text).

### Auto-cut quality

- **Best for pre-segmented recordings (your case)**: DaVinci Resolve Detect Scene Cuts, Premiere Pro "remove silences from transcript" -- deterministic, structure-preserving.
- **Best for unstructured long-form**: Opus Clip ClipAnything, Submagic Magic Clips -- LLM-picked moments, stochastic.
- **Best for music/montage**: CapCut Auto Cut beat-sync.

### AI B-roll insertion

- **Submagic**: AI B-roll based on caption keywords. Pro tier.
- **Opus Clip Pro**: AI B-roll. Pro-gated.
- **Premiere Pro**: Manual via stock libraries; no native AI B-roll yet in 26.x.
- **CapCut**: Stock library integration; AI suggestions via Auto Cut text-prompt mode.

### AI voice clone / re-record

- **Descript Overdub**: best-in-class for English re-records. Free + Hobbyist limited to 1000-word vocab; Creator+ ($24/$35/mo) unlimited.
- **Limitation**: Overdub struggles with intonation, emotion, strong accents. PT-BR users should test before committing.
- **Alternative for PT-BR**: ElevenLabs Multilingual v2 (separate from any editor; export and reimport).

### Generative video / extending clips

- **Premiere Pro 26.x Generative Extend** -- stretch a clip ~2s using AI generation. Solves the "edge-tts ran 58s, platform demands 60s" problem cleanly.
- **No other NLE in this matrix has a native equivalent in 2026.**

## Cost ladder (annualized)

| Cost/year | Stack | When |
|-----------|-------|------|
| $0 | DaVinci Resolve Free | Bootstrapping, first 10 episodes |
| $276 ($23/mo) | DaVinci Free + Submagic Pro | Sustainable for 1-3 shorts/day |
| $348 ($29/mo) | Opus Clip Pro (annual $174 = $14.50/mo effective) | Long-form podcast repurposing |
| $551 ($45.99/mo) | Premiere + Submagic | Already in Adobe ecosystem |
| $295 one-time | DaVinci Resolve Studio | Perpetual license, no AI subscription |

## Decision tree

```
Start
 |
 v
Is content pre-segmented (Dicas/lessons/structured pack)?
 |--YES--> Workflow B (DaVinci Free + Submagic) ............... [RECOMMENDED]
 |
 v NO
Is content unstructured long-form (podcast, livestream, Q&A)?
 |--YES--> Workflow C (Opus Clip Pro)
 |
 v NO
Are you already in Adobe CC?
 |--YES--> Workflow D (Premiere + Submagic)
 |
 v NO
Is budget hard $0?
 |--YES--> Workflow A (DaVinci Free, learn the pro path)
```

## Tutorial-channel quick-pick (one channel per tool, 2026)

| Tool | Start here (channel/source) |
|------|------------------------------|
| DaVinci Resolve 19 | **Casey Faris** (YouTube) |
| CapCut Desktop | **Miracamp 2026 AutoCut Guide** + CapCut Help Center |
| Premiere Pro 26.x | **Phantom Editor Blog** + Envato Tuts+ |
| Final Cut Pro 11 | **Apple Final Cut Pro release notes** + MacRumors |
| Descript | **Descript blog** + AIWithIt walkthrough |
| Opus Clip | **Opus.pro in-app tutorial** + G2 reviews |
| Submagic | **Submagic.co/pricing** + Filmora's 2026 review |
| Riverside Magic Clips | **Feisworld Media** ("Riverside Magic Clips Step-by-Step 2026") |

## Pitfalls to avoid (2026)

1. **Opus Clip's per-minute pricing** -- gets expensive fast at high volume. Hidden credit mechanics rank in the top complaints on Trustpilot (4.0/5, 22% 1-star).
2. **Final Cut Pro Transcribe to Captions is English-only** at launch. Do not pick FCP for PT-BR captions in 2026.
3. **CapCut Web does NOT have Auto Cut** -- desktop or mobile only.
4. **DaVinci Resolve Free has no on-device captions** -- only Studio ($295) does. Use a separate captioning tool if you stay on Free.
5. **Descript Overdub** struggles with intonation and accents -- test before committing for non-English re-records.
6. **Submagic Magic Clips** will re-pick moments by AI; if you need exact pack-order preservation, use it for captioning AFTER your cut, not for cutting.

## Glossary (2026 terms)

| Term | Definition |
|------|------------|
| Magic Clips | Riverside/Submagic feature: AI-extracted shorts from a long recording |
| ClipAnything | Opus Clip feature: AI picks clip-worthy moments by prompt or default |
| Virality Score | Opus Clip 0-100 prediction of clip performance |
| Auto Reframe | Premiere / DaVinci Studio: AI 16:9 -> 9:16 with subject tracking |
| Generative Extend | Premiere 26.x: AI-generate ~2s extra footage at a clip's edge |
| Text-Based Editing | Descript / Premiere: edit transcript, NLE applies cuts |
| Magic Mask | Final Cut Pro: AI object/person selection for masking |
| Speaker Coding | Opus / Submagic: auto-color captions per speaker |

## Sources

Verified May 2026. Cite by hyperlink in any republished content.

- [DaVinci Resolve YouTube Shorts step-by-step (CapCut/PremiumBeat)](https://www.capcut.com/resource/how-to-make-youtube-shorts-in-davinci-resolve)
- [Top YouTube channels for DaVinci Resolve (PremiumBeat 2025)](https://www.premiumbeat.com/royalty-free/best-youtube-channels-for-video-editing-tutorials/davinci-resolve)
- [Casey Faris YouTube channel](https://www.youtube.com/channel/UCdfDjoLF5L6lLuDCkJw0P3g)
- [DaVinci Resolve 2026 full course (YouTube)](https://www.youtube.com/watch?v=MCDVcQIA3UM)
- [From 16:9 to Vertical: YouTube Shorts editing (YouTube)](https://www.youtube.com/watch?v=D-zV8i0MOMY)
- [CapCut Auto Cut help center](https://www.capcut.com/help/how-to-use-auto-cut)
- [Miracamp Ultimate Guide to CapCut AutoCut 2026](https://www.miracamp.com/learn/capcut/the-ultimate-guide-to-autocut)
- [CapCut AI-powered editing 2026 (MSN)](https://www.msn.com/en-us/news/other/capcut-rolls-out-ai-powered-editing-tools-for-2026-creators/gm-GM7151757C)
- [Premiere Pro 26.0 release notes (Phantom Editor)](https://phantomeditor.video/blog/whats-new-premiere-pro-26-2026)
- [Premiere Pro AI Auto-Editing + Speech-to-Text (Envato Tuts+)](https://photography.tutsplus.com/articles/premiere-pro-ai--cms-109180)
- [Adobe Text-Based Editing overview](https://helpx.adobe.com/premiere/desktop/edit-projects/edit-video-using-text-based-editing/overview-of-text-based-editing.html)
- [Auto-Reframe in Premiere Pro (Learning Curve Global)](https://learningcurveglobal.com/ai-auto-reframe-in-premiere-pro-optimising-video-for-every-platform/)
- [Adobe Generative Extend overview](https://helpx.adobe.com/premiere/desktop/edit-projects/edit-with-generative-ai/generative-extend-overview.html)
- [Adobe Premiere Pro Review: King of Video Editing 2026 (Ad-Hoc News)](https://www.ad-hoc-news.de/boerse/news/ueberblick/adobe-premiere-pro-review-is-this-still-the-king-of-video-editing-in/68515333)
- [OpusClip pricing (official)](https://www.opus.pro/pricing)
- [Opus Clip Review 2026 (Ssemble)](https://www.ssemble.com/blog/opus-clip-review-2026)
- [Opus Clip 2026 review (BIGVU)](https://bigvu.tv/blog/opus-clips-worth-the-hype)
- [OpusClip G2 reviews](https://www.g2.com/products/opusclip/reviews)
- [Submagic pricing (official)](https://www.submagic.co/pricing)
- [Submagic Review 2026 (Max Productive)](https://max-productive.ai/ai-tools/submagic/)
- [Submagic Review 2026 (Filmora)](https://filmora.wondershare.com/video-editor-review/submagic-review.html)
- [Submagic Review 2026 (Business Dive)](https://thebusinessdive.com/submagic-review)
- [Descript pricing (official)](https://www.descript.com/pricing)
- [Descript Overdub 2026: All Plans (Descript Blog)](https://www.descript.com/blog/article/overdub-on-all-plans)
- [Descript Overdub Review 2026 (QCall.ai)](https://qcall.ai/descript-overdub-review)
- [Final Cut Pro Mac/iPad AI captions update (TechRadar)](https://www.techradar.com/computing/software/apple-just-gave-final-cut-pro-for-the-mac-and-ipad-some-big-upgrades-including-a-new-ai-captions-tool)
- [Final Cut Pro Transcribe to Captions: English only (9to5Mac)](https://9to5mac.com/2024/11/14/final-cut-transcribe-captions/)
- [Final Cut Pro release notes (Apple)](https://support.apple.com/en-us/102825)
- [Apple updates Final Cut Pro Jan 2026 (MacRumors)](https://www.macrumors.com/2026/01/28/final-cut-pro-and-logic-pro-updated/)
- [Riverside Magic Clips step-by-step 2026 (Feisworld Media)](https://www.feisworld.com/blog/riverside-magic-clips-youtube-shorts)
- [AI Video Editing for YouTube 2026 Workflow Guide (Vozo)](https://www.vozo.ai/blogs/youtube/ai-video-editing-youtube-workflow)
- [Premiere Pro AI Auto-Cut deep dive (Softonic)](https://en.softonic.com/articles/adobe-premiere-pro-ai-auto-cut-transform-videos-engaging-shorts)

## Related Artifacts

| Artifact | Relationship | Score |
|----------|-------------|-------|
| p01_kc_workflow | related | 0.23 |
| visual-workflow-builder | related | 0.21 |
| kc_visual_workflow | related | 0.21 |
| p12_qg_visual_workflow | related | 0.20 |
| bld_architecture_workflow | related | 0.19 |
| n00_workflow_manifest | related | 0.19 |
| bld_collaboration_workflow | related | 0.19 |
| workflow-builder | related | 0.16 |
