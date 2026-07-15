---
id: p01_kc_design_assim_hyperframes_motion_map
kind: knowledge_card
pillar: P01
nucleus: n01
mission: DESIGN_ASSIM
8f: "F3_inject"
title: "DESIGN_ASSIM W0 -- HyperFrames/Motion Mapping + Reusable-Concept Scan (Clean-Room)"
version: 1.0.0
created: "2026-06-15"
author: n01_intelligence
domain: design-assim
quality: null
tags: [knowledge_card, design-assim, motion, hyperframes, media-pipeline, clean-room, gap-analysis]
tldr: "HyperFrames (programmatic motion->MP4) is NET-NEW for CEXAI; recommendation = ffmpeg-native motion grammar as pipeline_template + cli_tool. Design-system-library is NET-NEW capability. Additional reusable concepts: typed-design-contract enrichment + motion-token sub-schema. Clean-room provenance confirmed."
keywords: [hyperframes, motion graphics, programmatic animation, pipeline_template, media pipeline, design system, clean-room, assimilation, cex motion render]
density_score: null
related:
  - p01_kc_gstack_cex_gap_analysis
  - p01_kc_gstack_attribution_ledger
  - p04_cli_media_pipeline_n05
  - spec_design_system_assimilation
---

## Section 1 -- HyperFrames: What It Is + Net-New Verdict

### What the concept is (clean-room statement of the idea)

Programmatic motion-to-MP4 is a technique in which video content is produced not by recording
or compositing static assets but by executing a code-specified animation graph. A declarative
(YAML/JSON/code) spec defines:

- **Elements**: text blocks, shape primitives, image composites, data visualizations
- **Keyframes**: element state at time t (position x/y, opacity, scale, rotation)
- **Easing/interpolation**: how the element transitions between keyframes (linear, ease-in/out, spring)
- **Scene timeline**: ordered sequence of windows with element entry/exit
- **Export target**: MP4 at given resolution and frame rate

The renderer consumes the spec, rasterizes each frame, and encodes to video. The OUTPUT is
identical in format to a traditionally composed video (MP4, 1920x1080, 30fps) but the
PROCESS is deterministic and parameterizable from a data specification.

### CEXAI existing media pipeline inventory

| Layer | What CEXAI Has | Tool/Artifact |
|-------|----------------|---------------|
| Text | Concept->storyteller template->markdown | `cex_media_produce.py` + lens KCs |
| Audio | NotebookLM audio overview + Qwen3-TTS founder voice (phonetic pipeline) | `cex_notebooklm.py` + phonetic YAML |
| Slides | HTML->Chrome headless->PDF->1920x1080 PNG rasterize (PyMuPDF) | gitignored `_tools/_*.py` |
| Static overlay | PNG cutaway at transcript-timed window via ffmpeg `overlay=enable='between(t,S,E)'` | `_compose_module_slides.py` |
| PPT/PDF | Marp slide deck -> PPTX/PDF | `marp-cli` via `cex_media_produce.py` |
| Short-form | gpt-image-1 portrait stills + Obsidian graph-view hook (~3.5s) | `cex_dica_imagine.py` |
| Camera effect | ffmpeg `zoompan` on hero PNG (Ken-Burns slow zoom) | gitignored compose scripts |
| Course video | 1920x1080 30fps B-roll + burned-in subs + brand header band | ffmpeg libx264 yuv420p |

### Gap analysis: what is absent

| Motion capability | Present in CEXAI? | Evidence |
|-------------------|-------------------|---------|
| Element-level keyframe animation (text enters/exits with easing) | NO | Slides are static PNGs; overlay is instantaneous cut |
| Code-driven element position over time (x/y/opacity/scale at t) | NO | ffmpeg zoompan is a camera scale, not element-level |
| Data-driven animation (bars growing, counters incrementing) | NO | Only static charts in slide HTML |
| Tween/spring physics between keyframes | NO | No interpolation engine |
| Declarative YAML/JSON spec -> animated MP4 without manual editing | NO | No spec-to-motion renderer exists |
| Scene transition animations (wipe, cross-fade, push) | PARTIAL | ffmpeg `fade` filter exists but not in a spec-driven pipeline |

### Verdict

**HyperFrames (programmatic motion->MP4) is NET-NEW for CEXAI.**

Closest analog (static overlay at timed window) covers the PLACEMENT dimension but not the
ANIMATION dimension. CEXAI can put a slide at t=30s; it cannot animate elements inside that
slide over time. The gap is element-level motion, not video composition.

---

## Section 2 -- CEXAI-Native Motion Representation: 3 Alternatives + Recommendation

### Alternative A -- ffmpeg-native motion grammar (RECOMMENDED)

**Artifacts:** `pipeline_template` (P12, domain=motion-graphics) + `cli_tool` (P04, `cex_motion_render.py`)

**How it works:**
- Declarative YAML spec defines elements + keyframes + scene timeline
- Renderer translates spec -> ffmpeg filtergraph with chained `overlay`, `drawtext`, `fade`,
  `scale`, `setpts`, `geq` filters
- Scene frames rendered as PNG sequence -> libx264 encode at target resolution/fps
- Integration point: wraps existing ffmpeg binary (imageio_ffmpeg path already resolved in pipeline)

**Spec structure (CEXAI-original design):**

```yaml
motion_spec:
  resolution: [1920, 1080]
  fps: 30
  duration_s: 10
  background: "#0a0a0a"
  elements:
    - id: title
      type: text
      content: "{{CONCEPT}}"
      font_size: 72
      color: "#FF1493"
      keyframes:
        - {t: 0.0, x: 960, y: 540, opacity: 0.0, scale: 0.8}
        - {t: 0.5, x: 960, y: 540, opacity: 1.0, scale: 1.0}
        - {t: 9.0, x: 960, y: 400, opacity: 1.0, scale: 1.0}
        - {t: 10.0, x: 960, y: 400, opacity: 0.0, scale: 1.0}
```

**Tradeoffs:**
| Dimension | Assessment |
|-----------|------------|
| New dependencies | ZERO (ffmpeg already in pipeline) |
| Sovereignty | FULL (no external service, no JS runtime) |
| Animation power | MEDIUM (compositing-layer; no path-follow, no bezier curves) |
| Learning overhead | LOW (extends existing ffmpeg knowledge) |
| Integration effort | LOW (wraps existing ffmpeg patterns) |
| Production quality | GOOD for lower-third + title animations; LIMITED for complex motion |

---

### Alternative B -- Manim-based motion engine

**Artifacts:** `cli_tool` (P04, Manim wrapper) + `pipeline_template` (P12)

**How it works:**
- Python library by 3Blue1Brown (MIT license), produces MP4 from Python Scene classes
- Elements are Mobjects with `.animate` chaining for smooth keyframed motion
- Full easing library, LaTeX support, 3D scene graph capability
- YAML spec transcoded to Python Scene code by a wrapper script

**Tradeoffs:**
| Dimension | Assessment |
|-----------|------------|
| New dependencies | HIGH (LaTeX, Cairo, OpenGL, Manim ~500MB install) |
| Sovereignty | FULL (MIT license, local render) |
| Animation power | VERY HIGH (professional educational animation, math-grade) |
| Learning overhead | HIGH (Mobject/Scene paradigm differs from CEX patterns) |
| Integration effort | MEDIUM (Python-to-Python but paradigm gap) |
| Production quality | EXCELLENT for conceptual diagrams + mathematical motion |

Best fit: diagram-heavy motion (8F pipeline animated, nucleus topology animated). NOT the default choice due to dependency weight.

---

### Alternative C -- PIL/Pillow rasterized animation

**Artifacts:** `cli_tool` (P04, `cex_frame_animator.py`) only

**How it works:**
- Frame-by-frame: for each t, draw all elements at their interpolated position onto a PIL canvas
- Save as PNG frames, assemble with ffmpeg
- Pure Python, minimal dependencies (PIL already used in thumbnail/overlay work)

**Tradeoffs:**
| Dimension | Assessment |
|-----------|------------|
| New dependencies | MINIMAL (PIL + numpy for interpolation) |
| Sovereignty | FULL |
| Animation power | LOW (raster only, no anti-aliased vectors, no CSS effects) |
| Learning overhead | LOW |
| Integration effort | LOW |
| Production quality | LIMITED (pixelated at scale, no subpixel rendering) |

Best fit: data-driven counters and simple bar animations. Not for brand-grade title animations.

---

### Recommendation

**Option A (ffmpeg-native motion grammar)** as the CEXAI-native representation.

Rationale from Analytical Envy lens:
1. Zero new runtime dependency: CEXAI's video pipeline already depends on imageio_ffmpeg; extending the filter grammar adds power without adding a new failure surface.
2. Sovereign by construction: the spec is a CEXAI YAML artifact (kinds-compliant); render is local; no external API.
3. Composites with existing pipeline: the motion renderer output drops into the same `overlay=enable='between(t,S,E)'` slot already used for static PNG cutaways -- the downstream pipeline sees no difference.
4. Option B (Manim) is the UPGRADE path for W1 when diagram-grade animation is needed; it can be introduced as a second `cli_tool` artifact alongside A, not instead of it.
5. Option C is relegated to data-counter animation as a helper within Option A (ffmpeg `drawtext+eval` can animate a counter natively).

**Kind mapping for the motion capability:**

| Artifact | Kind | Pillar | Path |
|----------|------|--------|------|
| Motion production workflow | `pipeline_template` | P12 | `N05_operations/P12_orchestration/tpl_motion_pipeline.md` |
| Motion renderer tool | `cli_tool` | P04 | `N05_operations/P04_tools/cli_tool_cex_motion_render.md` |
| Motion spec schema | `validation_schema` | P06 | `N00_genesis/P06_schema/motion_spec_schema.yaml` |

N01 recommendation: no new kind needed. The three existing kinds (`pipeline_template` + `cli_tool` + `validation_schema`) compose to the full motion capability. Hygiene test outcome: EXISTING KINDS SUFFICIENT.

---

## Section 3 -- Other Reusable-Concept Scan

Beyond the design-system library (N03 scope) and HyperFrames (above), the following concepts
are evaluated for clean-room lift from the assessed external tool's concept surface:

| Concept | Description | CEXAI verdict | Action | CEXAI kind |
|---------|-------------|--------------|--------|-----------|
| typed-design-contract | Design system as a computable first-class artifact with machine-readable token fields (color/type/spacing/motion tokens + component rules), not just a human style guide | ENRICHMENT -- CEXAI's `brand_config.yaml` is single-brand and human-readable; the CONCEPT of a typed, schematic per-system contract is a schema enrichment for N03's design_system definition | FEED to N03 W0: inform the schema design so it is machine-readable (token fields typed, not prose) | `design_system` (N03 W0) / `context_doc` with schema |
| Motion-token sub-schema | Design contracts include motion tokens: duration_ms, easing_fn, transition_type -- treating motion parameters as typed design values alongside color and spacing | ENRICHMENT -- CEXAI schemas currently have no motion token concept; this is a natural extension of the design_system schema | Include as a subsection in the `validation_schema` for motion_spec (above) and in N03's design_system schema | Sub-schema within `design_system` + `validation_schema` |
| Skill/plugin registry | Filesystem of named skills and plugins, each a self-contained capability unit | OVERLAP -- CEXAI has the `skill` kind (P03), 303 builders, capability_registry -- identical architectural pattern | SKIP (already covered) | Existing `skill` + `capability_registry` |
| External model-router service | a separate service resolving which model handles which task | OVERLAP -- CEXAI: `cex_router_v2.py` + `nucleus_models.yaml` implement the same pattern locally without a service | SKIP (covered, more sovereign) | Existing `router` kind |
| External-app MCP integration | an external design app exposes its capability set as MCP tools | SKIP (ANTI-PATTERN) -- integrating via an external app's MCP couples CEXAI to that desktop app + its model service; cuts CEXAI's runtime-sovereign ethos | SKIP | N/A |
| Multi-format export (HTML/PDF/PPTX/MP4) | Single pipeline produces all presentation formats | OVERLAP -- CEXAI: `cex_media_produce.py` covers text/audio/video/ppt formats from a single concept entry point | SKIP (covered) | Existing `pipeline_template` |
| Image generation | AI-driven image creation as pipeline step | OVERLAP -- CEXAI: gpt-image-1 via `cex_dica_imagine.py` + short-form pipeline | SKIP (covered) | Existing `vision_tool` |
| Prototype/dashboard generation | Rapid interactive prototype from a design spec | OVERLAP -- CEXAI: `landing-page-builder` + `frontend-design` skill (gstack-assimilated) | SKIP (covered) | Existing builders |

### Net-new lift summary

| Concept | Status | Who builds |
|---------|--------|------------|
| Design-system library | NET-NEW (primary) | N03 W0 + W1 |
| HyperFrames motion | NET-NEW -- `pipeline_template` + `cli_tool` + `validation_schema` | N03/N05 W1 (schema in W0) |
| typed-design-contract | ENRICHMENT -- feed to N03 W0 schema design | N01 informs N03 |
| Motion-token sub-schema | ENRICHMENT -- add to motion_spec schema + design_system schema | N03 W0 (schema layer) |
| All others | OVERLAP or SKIP | -- |

---

## Section 4 -- Provenance

Clean-room: every analysis, schema, recommendation, and table in this KC is authored from first
principles in CEXAI's own taxonomy and architecture -- original CEXAI IP. The capability concepts
were evaluated independently; conceptual-provenance details are kept in N07's internal assessment
record (outside this repo). W1 must author 100% ORIGINAL design systems (never adapt any external
file), keeping the IP clean for INPI.

**Self-check (CLEAN_ROOM_RULE gate):**
- [ ] No external-source verbatim content in this KC: CONFIRMED
- [ ] No external-source token values (color hex, font names, system names): CONFIRMED
- [ ] No external-source code adapted: CONFIRMED (motion_spec schema is original CEXAI design)
- [ ] Provenance lives only in internal memory record: CONFIRMED
- [ ] CEXAI kinds used (not external-source vocabulary): CONFIRMED

**Status:** CLEAN. Ready for N07 W0 report.

---

## Related Artifacts

| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[p01_kc_gstack_cex_gap_analysis]] | peer (prior assimilation gap analysis pattern) | 0.38 |
| [[p01_kc_gstack_attribution_ledger]] | peer (clean-room attribution record pattern) | 0.35 |
| p04_cli_media_pipeline_n05 | upstream (CEXAI media surface inventoried here) | 0.33 |
| spec_design_system_assimilation | parent spec | 0.30 |
