---
name: teach
description: Live, narrated, interactive lesson with synchronized visuals. Five subcommands -- run, explain, practice, list, setup. Auto-picks Obsidian or self-contained HTML. Merges /mentor content + /guide audience interaction + /podcast TTS+Obsidian sync. Founder uses it to present live; anyone running CEXAI at home uses it to self-learn.
id: skill_teach
kind: skill
pillar: P03
nucleus: n03
version: 1.0.0
quality: null
created: "2026-05-29"
updated: "2026-05-29"
author: n03_builder
platform: windows
density_score: 0.92
tags: [skill, teach, lesson, mentorship, obsidian, html, tts, interaction, beat-manifest]
related:
  - cmd_teach
  - skill_podcast
  - cex_say_show
  - mentor
  - podcast
---

> **[DISTILL ANNOTATION]** This file cites tool(s) not shipped in this tenant (Central-only): cex_teach_html, cex_teach_lesson, cex_teach_obsidian, cex_teach_practice, cex_teach_runtime, cex_teach_setup. Inline citations are marked `[NOT SHIPPED in this tenant -- Central-only tool]`.

# /teach -- Live Class + Mentorship

`/teach` turns a beat manifest into a narrated, visually-synced, interactive
lesson. It is the composition of three earlier surfaces:

- `/mentor` provides the **content** (lesson script + 7 metaphor lenses +
  grounding KCs).
- `/guide` provides the **audience interaction** (Decision Points -> answer
  written to `decision_manifest.yaml` -> branching).
- `/podcast` provides the **delivery** (founder-voice TTS via edge-tts +
  Obsidian Advanced URI synchronization via `cex_say_show`).

The single source of truth is a Wave-A beat manifest under
`_courses/video_series/manifests/manifest_teach_*.yaml` (kind:
`podcast_manifest`). The engine walks the manifest once; each beat dispatches
surface verbs (`open_scene`, `focus`, `show_media`, `show_graph`, `clear`,
`prompt`) to the ACTIVE backend. The same lesson runs on Obsidian (rich, the
real consolidated CEXAI vault + graph view) or on a self-contained HTML page
(zero install -- anyone with a browser).

> **Platform**: Windows is the validated runtime (TTS, Obsidian launchers,
> browser handoff). HTML surface is OS-portable in practice; live Obsidian
> sync remains Windows-first per `/podcast` DP3.

## Subcommands

| Sub | Purpose | Required | Optional |
|-----|---------|----------|----------|
| `run <lesson_id>` | Walk a beat manifest end-to-end | `lesson_id` (e.g. `m00_1`) | `--surface`, `--mode`, `--voice`, `--with-practice`, `--dry-run` |
| `explain <concept>` | One-off concept lesson (no manifest) | `concept` | `--lens`, `--lang`, `--surface`, `--voice` |
| `practice` | Narrated mentorship Q&A loop | -- | `--from-lesson`, `--kc`, `--lens`, `--voice`, `--lang`, `--max-turns`, `--dry-run` |
| `list` | List available lesson manifests | -- | `--lesson-dir` |
| `setup` | Preflight TTS + surface deps (GREEN/AMBER/RED checklist) | -- | `--surface`, `--json`, `--quiet`, `--config` |

### `/teach run <lesson_id>`

Resolves `lesson_id` to `<lesson_dir>/manifest_teach_<lesson_id>.yaml`
(`lesson_dir` from `teach.lesson_dir` in `podcast_config.yaml`, default
`_courses/video_series/manifests`). The engine then:

1. Picks a surface (`--surface auto|obsidian|html`, default `auto`). `auto` =
   Obsidian when reachable AND the Advanced URI community plugin is present,
   else the HTML fallback.
2. Picks a mode (`--mode live|prerendered`, default `live`). `live` = TTS per
   beat with one-beat prefetch via `cex_say_show`. `prerendered` = 2-phase
   cache (render all mp3s first, then play cached files -- broadcast safe,
   zero network during playback).
3. Calls the backend tool:
   - Obsidian surface -> `python _tools/cex_teach_obsidian.py --manifest  <!-- [NOT SHIPPED in this tenant -- Central-only tool] -->
     <path> --mode {live|prerendered} [--voice ...] [--write-live] [--dry-run]`
   - HTML surface -> `python _tools/cex_teach_html.py --manifest <path>  <!-- [NOT SHIPPED in this tenant -- Central-only tool] -->
     [--render-audio] [--voice ...] [--with-decisions-sidecar] [--no-open]`
4. Honors interaction beats: each `interaction:` block in the manifest renders
   a Decision Point (Obsidian -> narrated prompt + terminal number-key; HTML
   -> on-page buttons). The answer is appended to the `teach:` block of
   `.cex/runtime/decisions/decision_manifest.yaml` and the runtime resolves
   the next anchor (`goto`/`null`/`open_qa`).
5. On close, prints a recap tally for the lesson via
   `python _tools/cex_teach_runtime.py --recap <lesson_id>  <!-- [NOT SHIPPED in this tenant -- Central-only tool] -->
   [--recap-fmt text|html]`.

Add `--with-practice` to auto-hand off to `/teach practice --from-lesson
<path>` at the final beat (mentorship Q&A grounded on the same lesson).

### `/teach explain <concept> [--lens <name>] [--lang en|pt-br]`

Builds an ephemeral beat manifest from a single concept via
`python _tools/cex_teach_lesson.py --concept "<concept>" --lens <lens>  <!-- [NOT SHIPPED in this tenant -- Central-only tool] -->
--lang <lang> --out <tmp>`, then runs it through the chosen surface (same
selector as `run`). Default lens for `cex_teach_lesson` is governed by
`teach.default_lens` in `podcast_config.yaml` (current default: `kitchen`,
mapped to ato structure). Use `--validate-only` on the underlying tool to
check the manifest without writing.

### `/teach practice [flags]`

Narrated mentorship Q&A loop. Reuses the storyteller engine; degrade-never
via TF-IDF retrieval over the lesson's KCs.

```
python _tools/cex_teach_practice.py \  <!-- [NOT SHIPPED in this tenant -- Central-only tool] -->
    --from-lesson _courses/video_series/manifests/manifest_teach_m00_1.yaml \
    --lens factory \
    --voice pt-BR-FranciscaNeural \
    --lang pt-br
```

Grounding sources are mutually exclusive: pick `--from-lesson <manifest>` OR
one-or-more `--kc <path>` (repeatable). The lens enum in this tool is the
mentor 7-lens vocabulary (`factory|city|biology|game|bible|car|technical`,
default `factory`) -- distinct from the `teach.default_lens` config (lesson
ato vocabulary). Pass `--llm` to attempt the local Ollama router before
falling back to `retrieval_only`; pass `--no-llm` to force retrieval. Use
`--max-turns N` to cap the session, `--dry-run` for one smoke question and
exit.

### `/teach list`

Walks `teach.lesson_dir` and prints lesson IDs + script paths from the
`manifest_teach_*.yaml` files. Output mirrors `/podcast list`. Today this
surface ships 13 manifests (driver: `m00_1`..`m00_4`; paid: `m01`..`m08`).

### `/teach setup`

Preflight every `/teach` dep and print a GREEN/AMBER/RED checklist (sibling
of `/podcast setup`). Implemented by `cex_teach_setup.py` (Wave D3, N05).
Probes cover:

- Python version + the `edge-tts` Python package
- The `teach:` block in `podcast_config.yaml` (default_surface / default_mode
  / default_lens / lesson_dir / output_dir)
- `teach.lesson_dir` populated with at least one `manifest_teach_*.yaml`
- `teach.output_dir` writable for HTML emissions
- For the Obsidian surface: Obsidian launcher resolved + Advanced URI plugin
  listed in `.obsidian/community-plugins.json` + vault detectable
- For the HTML surface: default browser launchable via `webbrowser.open`
- Decision directory writable (for the `teach:` block of
  `decision_manifest.yaml`)

```
/teach setup                                      -- full report
/teach setup --surface obsidian                   -- only the Obsidian-surface deps
/teach setup --surface html --quiet               -- only AMBER/RED rows
/teach setup --json                               -- machine-readable
```

The probe is degrade-never: every check is try/except and downgrades to
AMBER on unknown state. RED fires only when a HARD-required dep is missing
(e.g. `python < 3.11` or the decision directory unwritable).

## Flags (skill-level umbrella)

| Flag | Domain | Default | Behavior |
|------|--------|---------|----------|
| `--surface {auto|obsidian|html}` | `run`, `explain` | `auto` (from `teach.default_surface`) | Picks backend tool. `auto` = Obsidian if reachable + Advanced URI present, else HTML. |
| `--mode {live|prerendered}` | `run`, `explain` | `live` (from `teach.default_mode`) | live: TTS per beat with prefetch. prerendered: 2-phase cache (render then play). |
| `--with-practice` | `run` | off | After the final beat, hand off to `/teach practice --from-lesson <path>`. |
| `--lens <name>` | `explain`, `practice` | `factory` (practice) / `kitchen` (lesson) | Metaphor lens. The `lesson` and `practice` vocabularies differ; see Lens table. |
| `--voice <id>` | all | from `podcast_config.yaml` voices block | edge-tts or ElevenLabs voice ID. Overrides config. |
| `--dry-run` | `run`, `practice` | off | No Obsidian launch, no TTS render; on practice runs one smoke Q and exits. |

Backend-only flags (passed through when the subcommand maps to a specific
tool) include `--render-only` / `--prerendered-only` / `--no-visuals` /
`--no-audio` / `--write-live` / `--settle-ms` / `--dwell-ms` (Obsidian) and
`--render-audio` / `--audio-dir` / `--with-decisions-sidecar` / `--no-open`
/ `--out` (HTML). See each backend's `--help` for the full set.

## Worked examples (paste-ready)

```
# Driver M00.1 -- let auto pick the surface
/teach run m00_1

# Same lesson, force the HTML surface (no Obsidian needed)
/teach run m00_1 --surface html

# Broadcast / OBS: pre-render all beats, then play cached audio with zero
# network during the take
/teach run m00_1 --mode prerendered

# One-off concept explanation through the "vault" lens (PT-BR)
/teach explain "knowledge_card" --lens vault --lang pt-br

# Mentorship Q&A grounded on a lesson manifest
/teach practice --from-lesson _courses/video_series/manifests/manifest_teach_m00_1.yaml --lens factory

# Practice grounded on a specific KC (no manifest), one smoke question and exit
/teach practice --kc CLAUDE.md --lens factory --lang pt-br --dry-run

# Run a lesson, then auto-hand off to mentorship Q&A at the close
/teach run m01 --with-practice

# Preflight every dep (TTS + Obsidian/Advanced URI OR browser)
/teach setup
```

## Integration map (subcommand -> implementing CLI tool)

| Subcommand | Implementing tool | Notes |
|------------|------------------|-------|
| `run` (Obsidian surface) | `_tools/cex_teach_obsidian.py --manifest <path>` | Wave B1+B3 -- surface verbs + render-ahead + `live`/`prerendered` modes. |  <!-- [NOT SHIPPED in this tenant -- Central-only tool] -->
| `run` (HTML surface) | `_tools/cex_teach_html.py --manifest <path>` | Wave B2 -- self-contained page with `<audio>` per beat + interaction buttons. |  <!-- [NOT SHIPPED in this tenant -- Central-only tool] -->
| `explain` | `_tools/cex_teach_lesson.py --concept "<c>" --lens <l>` then route to a surface | Wave A2 -- concept -> ephemeral manifest. |  <!-- [NOT SHIPPED in this tenant -- Central-only tool] -->
| `practice` | `_tools/cex_teach_practice.py --from-lesson <path>` (or `--kc <path>`) | Wave C2 -- narrated Q&A loop (`open_qa` runtime). |  <!-- [NOT SHIPPED in this tenant -- Central-only tool] -->
| `setup` | `_tools/cex_teach_setup.py` | Wave D3 (N05) -- preflight; GREEN/AMBER/RED checklist + `--surface`/`--json`/`--quiet` modes. |  <!-- [NOT SHIPPED in this tenant -- Central-only tool] -->
| `list` | Glob `teach.lesson_dir` for `manifest_teach_*.yaml` | No dedicated tool; in-skill walk. |
| recap (auxiliary) | `_tools/cex_teach_runtime.py --recap <lesson_id>` | C1 -- shared interaction runtime. Used at close of `run`. |  <!-- [NOT SHIPPED in this tenant -- Central-only tool] -->

The interaction runtime (`cex_teach_runtime.py`) is the bridge: both backends
call into it for decision capture, branch resolution, manifest append, and
the closing recap.

## Lens vocabularies

`/teach` exposes two related-but-distinct lens enums depending on
subcommand. Use the right one:

| Used by | Tool | Vocabulary |
|---------|------|-----------|
| `explain` | `cex_teach_lesson.py --lens` | `city | garden | kitchen | dojo | vault | hospital | atelier | factory` (ato-structure mapping; aligned with `teach.default_lens` in config). |
| `practice` | `cex_teach_practice.py --lens` | `factory | city | biology | game | bible | car | technical` (mentor 7-lens; default `factory`). |

Cross-vocabulary terms (`factory`, `city`) work in both. Unknown lenses fall
back to `factory` (per N04's C2 rule).

## Brand canon

Visible text in EVERY context is **CEXAI** -- command name, skill name, HTML
UX, Obsidian docs, frontmatter, labels, anywhere a learner can see it.
"<internal-era-brand>" only appears inside TTS narration `.md` as a phonetic respelling so
PT-BR audio pronounces "CEXAI" correctly. It is **never** visible text.
Narration uses the founder voice (configured via `voices.*` in
`podcast_config.yaml`; edge-tts Francisca / Thalita today, ElevenLabs /
Qwen3 founder clone where wired).

## Decision log

Audience choices land in the `teach:` block of
`.cex/runtime/decisions/decision_manifest.yaml`. The runtime
(`cex_teach_runtime.py`) appends one record per interaction beat with
`lesson_id`, `beat_anchor`, `option_label`, `option_goto`, and a timestamp.
The closing recap (`cex_teach_runtime.py --recap <lesson_id>`) reads this
block and prints a tally per beat (text by default; `--recap-fmt html`
yields a `<section>` fragment suitable for embedding in the HTML page).

This reuses the `/guide` mechanism (Decision Manifest as cross-mode bridge)
without introducing a new kind -- `decision_manifest` already covers it.

## Configuration

All operational variables are open. Resolution order: CLI flags > env vars >
`podcast_config.yaml` > fallback defaults. The `teach:` block in
`.cex/config/podcast_config.yaml` controls:

| Key | Default | Notes |
|-----|---------|-------|
| `teach.default_surface` | `auto` | `auto | obsidian | html` |
| `teach.default_mode` | `live` | `live | prerendered` |
| `teach.default_lens` | `kitchen` | enum aligned with `cex_teach_lesson` ato vocabulary |
| `teach.lesson_dir` | `_courses/video_series/manifests` | scanned by `/teach list` |
| `teach.output_dir` | `_output` | where HTML pages + decisions sidecars land |
| `voices.host` / `voices.guest` | (shared with `/podcast`) | edge-tts or ElevenLabs voice IDs |

## Out of scope (v1)

The following were deliberately deferred per the locked plan:

- **Localhost remote-poll endpoint** -- letting an audience vote from their
  own devices. In v1 the HTML surface uses client-side buttons only (one
  browser, one learner). Remote-poll deferred to v1.5 / v2.
- **A new `slash_command` kind** -- the established CEX pattern is
  `instruction` (command file) + `skill` (full spec). `/teach` follows that
  shape; no taxonomy expansion.
- **Auto-generated video export from a lesson manifest** -- the existing
  media pipeline (`cex_media_produce`) already covers rendered video and is
  the right surface for that.

## Anti-patterns

| Wrong | Right |
|-------|-------|
| Documenting flags that do not exist in the underlying tool | The skill describes what SHIPS; degrade-never. Cross-check `python _tools/cex_teach_*.py --help`. |
| Writing "<internal-era-brand>" anywhere a learner can see it | Visible text is always CEXAI. <internal-era-brand> lives only inside narration `.md` for TTS phonetics. |
| Conflating the two lens vocabularies | `explain` uses the lesson ato vocab; `practice` uses the mentor 7-lens vocab. Both default-fall-back to `factory`. |
| Forking the lesson content per surface | The manifest is the single source of truth. Surface is a runtime flag. |
| Hardcoding voice IDs | Resolve from `--voice` / env / `voices.*` config; never inline a voice string. |
| Silent failure when Obsidian is closed | The runtime surfaces the warning and falls back to HTML when `auto` cannot reach Obsidian. |

## Boundary

The skill **defines** what `/teach` does. It does NOT ship engine code --
that lives in `_tools/cex_teach_obsidian.py`, `_tools/cex_teach_html.py`,  <!-- [NOT SHIPPED in this tenant -- Central-only tool] -->
`_tools/cex_teach_lesson.py`, `_tools/cex_teach_practice.py`, and  <!-- [NOT SHIPPED in this tenant -- Central-only tool] -->
`_tools/cex_teach_runtime.py`. It does NOT define agent identity (no system  <!-- [NOT SHIPPED in this tenant -- Central-only tool] -->
prompt). It does NOT orchestrate multiple agents (no crew). It is one
reusable invocation contract with five subcommands and one umbrella flag
set, riding on top of the Wave A-C engine.

## Related Artifacts

| Artifact | Relationship | Score |
|----------|-------------|-------|
| cmd_teach | sibling (thin launcher) | 0.95 |
| skill_podcast | upstream (engine ancestor; cloned shape) | 0.70 |
| cex_say_show | upstream (Obsidian+TTS engine the backends wrap) | 0.65 |
| [[mentor]] | upstream (content source: lenses + storyteller) | 0.55 |
| podcast | sibling (command-shape sibling) | 0.50 |
