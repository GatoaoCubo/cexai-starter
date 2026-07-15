---
id: p10_pm_n05
kind: procedural_memory
8f: F3_inject
pillar: P10
nucleus: N05
title: "Procedural Memory -- N05 Operations Standard Operating Procedures"
version: "1.0.0"
quality: null
tags: [procedural_memory, n05, sop, gate, deploy, ascii, escalation, P10]
domain: "operations and release engineering"
status: active
created: "2026-07-02"
updated: "2026-07-02"
author: n05_operations
tldr: "N05 task procedure memory: release gate sequence (doctor/sanitize/pytest/compile/flywheel), Railway deploy + rollback discipline, ASCII enforcement sweep, browser/computer-use guardrails, and the model-quality escalation ladder."
keywords: [operations sop, procedural memory -- n05, gate execution, doctor sanitize pytest, deploy discipline, ascii enforcement, browser computer-use guardrail, escalation ladder, regression check, gating wrath, procedural_memory]
density_score: null
related:
  - p10_pm_n04_knowledge
  - procedural_memory_n06
  - p07_rc_ops
  - p05_oval_deploy_checklist_n05
  - ex_director_ops_health_monitor
  - n05_operations
---

> **[DISTILL ANNOTATION]** This file cites tool(s) not shipped in this tenant (Central-only): _courses_notebooklm_pipeline, _<internal-era-brand>_validator, _shorts_v51_karaoke, _shorts_v5_compose, cex_evolve, cex_flywheel_audit, cex_hooks, cex_mentor_swarm, cex_system_test. Inline citations are marked `[NOT SHIPPED in this tenant -- Central-only tool]`.

# Procedural Memory: N05 Operations Standard Operating Procedures

## About This File

N05's procedural memory layer -- how N05 DOES things, not what it knows.
Sin lens: Gating Wrath -- gates are never negotiated
(`.claude/rules/raci-matrix.md`: "N05 NEVER negotiates quality criteria
(gate is gate)"). Append to the log below when a procedure is refined.

---

## SOP-01: Release Gate Sequence (doctor / sanitize / pytest)

**Trigger**: PR/push touching `_tools/`, `archetypes/`, or any `N0X_*/`
pillar dir; or an explicit "run the gates" / "/cex-doctor" request.

1. Lint: `ruff check _tools/*.py _tools/tests/ --select E,F,W --ignore E501,E402,W291,W293`
2. Test: `cd _tools && python -m pytest tests/ -v --tb=short -m "not slow" --cov=.`
3. Compile: `python _tools/cex_compile.py --all` (doctor reads compiled output -- compile runs first)
4. Doctor: `python _tools/cex_doctor.py` (12-pillar ISO + density + completeness; exit 0 required)
5. Flywheel audit: `python _tools/cex_flywheel_audit.py audit` (109 wires, 7 layers)  <!-- [NOT SHIPPED in this tenant -- Central-only tool] -->
6. System test, offline: `CEX_USE_API=0 python _tools/cex_system_test.py --quick`  <!-- [NOT SHIPPED in this tenant -- Central-only tool] -->
7. Any FAIL blocks merge/dispatch -- no manual override.

The job graph is load-bearing: `doctor` needs `[test, compile]`;
`system-test` needs `[doctor, flywheel]`. Source: `.github/workflows/ci.yml`
(secret-scan -> lint -> test -> compile -> doctor -> flywheel ->
system-test); KC-scoped variant on push-to-main:
`.github/workflows/quality.yml` (score -> floor-check -> compile ->
release-gate via `cex_release_check.py`).

N05 also runs 6 zero-tolerance detectors on every PR (threshold 0, any hit
blocks): `unicode_crash`, `orphan_processes`, `signal_storm`,
`self_scoring` (`quality:` != null), `cross_nucleus_write` (diff outside
`N05_operations/`), `compile_drift` (`.md` newer than its `.yaml`).
Unresolved after 30 min: N07 halts grid dispatch. Source:
`N05_operations/P07_evals/regression_check_ops.md` (detection commands +
remediation + 90-clean-run retirement policy).

---

## SOP-02: ASCII Enforcement Sweep

**Trigger**: any `.py` / `.ps1` / `.sh` / `.cmd` / `.bat` staged for commit,
or `unicode_crash` fires (SOP-01).

1. Check: `python _tools/cex_sanitize.py --check --scope <dir>` (repeatable `--scope`)
2. Fix: `python _tools/cex_sanitize.py --fix --scope <dir>`, then re-check for 0
3. Already enforced pre-commit: `.git/hooks/pre-commit` calls
   `python _tools/cex_hooks.py pre-commit` and blocks the commit on non-ASCII code  <!-- [NOT SHIPPED in this tenant -- Central-only tool] -->
4. Narrow exceptions: `.ps1` may carry a UTF-8 BOM at byte 0; `.py` may use
   `\uXXXX` escapes for runtime non-ASCII values. Narration / TTS / phonetic
   / subtitle `.md` content is OUT of scope -- never strip PT-BR accents
   there (a shipped regression class, not hypothetical)
5. `.md` / `.yaml` content files are not swept -- only the 5 executable extensions

Source: `.claude/rules/ascii-code-rule.md` (3-layer enforcement: pre-commit
hook + sanitizer + CI gate); `_tools/cex_sanitize.py --help`;
`N05_operations/P01_knowledge/kc_pre_commit_hooks_for_ai.md`.

---

## SOP-03: Deploy & Rollback Discipline (Railway 4-service)

**Trigger**: `release_gate` crew PASS verdict, an explicit deploy request,
or a rollback trigger below.

Deploy: (1) validate `railway.toml` + 63 env vars + asyncpg pool health,
(2) `railway up`, (3) `/health` returns 200 within 30s, (4) verify all 4
services (api/frontend/dashboard/gateway) + CORS/rate-limit/auth
middleware, (5) sign off only once a rollback plan is pre-written. Prefer
the `deploy_pipeline` crew (`pre_checker` -> `deployer` -> `smoke_tester`):
`deployer` has an ABORT gate -- BLOCKED from `pre_checker` halts before
production and `smoke_tester` emits SKIPPED. `max_concurrent: 1`.

| Rollback trigger | Action | SLA |
|-------------------|--------|-----|
| Health non-200 within 30s of deploy | auto-rollback | 60s |
| p95 latency > 2x baseline | alert + manual decision | 5min |
| Error rate > 5% for 2 min | auto-rollback | 120s |
| DB migration failure | halt, rollback migration | immediate |
| Startup < 14/14 checks pass | halt, investigate | immediate |

Rollback: assess 4-service blast radius -> `MAINTENANCE_MODE=true` if
critical -> DB rollback first (staging-tested) -> `railway rollback
--service <svc> --to-deployment [ID]` -> health verify -> restore traffic.
RTOs are HARD SLAs: critical-path <= 5min (else S0, page on-call); full
recovery <= 15min (else S1, escalate to N05 lead); rollback DECISION itself
<= 60s from smoke FAIL (else kill-switch arms, manual approval for 24h).

Source: `N05_operations/P05_output/{deploy_checklist_template,rollback_plan_template}.md`;
`N05_operations/P12_orchestration/crews/p12_ct_deploy_pipeline.md`;
`N05_operations/P08_architecture/agent_card_n05.md`.

---

## SOP-04: Browser / Computer-Use Guardrail Check

**Trigger**: any task dispatched to N05 needing `browser_tool`,
`computer_use`, or live web/UI interaction.

1. Confirm the session is on Opus -- N05 is a named DO-NOT-FLIP guardrail
   ("browser_tool / computer_use require the strongest model"), per
   `.claude/rules/model-economy.md`
2. `boot/n05.ps1` is the only nucleus boot script (of n01-n07) with NO
   `--no-chrome` flag -- verified: `grep -l no-chrome boot/n0*.ps1` matches
   n01/n02/n03/n04/n06/n07; n05 is absent. Browser/computer-use work must
   run through the `n05` boot path
3. Before relying on `postgres`/`github` MCP as `agent_card_n05.md`
   documents: check `.mcp-n05.json` -- it is currently `{"mcpServers":{}}`,
   loaded with `--strict-mcp-config`, so a freshly spawned N05 has ZERO live
   MCP servers. Verify before depending on it; if genuinely needed, escalate
   to N07 rather than silently degrading or fabricating results
4. Kinds requiring live MCP hard-route to Claude only, never
   Codex/Gemini/Ollama: `browser_tool`, `mcp_server`, `interactive_demo`,
   `computer_use`, `db_connector`

Source: `boot/n05.ps1` (grep-confirmed vs all 7 boot scripts); `.mcp-n05.json`;
`.claude/rules/model-economy.md` (Opus Guardrails item 1);
`N05_operations/P08_architecture/agent_card_n05.md`;
`docs/NUCLEUS_ARCHITECTURE_DOSSIER.md` N05 section.

---

## SOP-05: Escalation Ladder

**Trigger A -- quality**: an artifact clears its HARD gates (SOP-01) but
scores below its producer tier's floor.

| Tier | Alias | Stop condition |
|------|-------|-----------------|
| haiku | haiku | score < 7.0 -> escalate to sonnet |
| sonnet | sonnet | score < 8.0 -> escalate to opus |
| opus | opus | terminal -- accept whatever it produces |

Serial, one producer/one tier at a time. Re-produce the SAME artifact at
the next (stronger) tier -- never skip a rung. Cross-provider producers
climb their OWN ladder via `nucleus_models.yaml::tiers.escalation_ladders`,
never a hardcoded "if claude" branch. Money-touching/ship sessions start at
Opus directly (`CEX_MODEL_OVERRIDE=claude-opus-4-8`). N05 (SOP-04) and N07
(keystone verify) are fixed at Opus, never entering at haiku/sonnet.
Source: `_tools/cex_mentor_swarm.py` (`ESCALATION_LADDER`,  <!-- [NOT SHIPPED in this tenant -- Central-only tool] -->
`load_escalation_ladder()`); `.claude/rules/model-economy.md`.

**Trigger B -- health/incident**: a threshold crossing, a `deploy_pipeline`
UNHEALTHY verdict, or a `quality_sweep` FAIL verdict.
`ex_director_ops_health_monitor` runs wave 1 (`process-monitor` +
`signal-monitor` + `resource-monitor`, parallel) then wave 2
(`artifact-monitor`), blocked if wave 1 emits ESCALATE. Action matrix:
warning -> ALERT (auto); critical -> RESTART (N07 confirms); multiple
criticals in one wave -> ESCALATE (halt dispatch, operator gate);
quarantine blocks compile until N05 reviews. Crew-to-crew: `deploy_pipeline`
UNHEALTHY triggers `incident_response` (`detector`->`responder`->`analyst`->`reporter`);
`quality_sweep` FAIL feeds `release_gate` as a blocker. `reporter` opens a
NEW `regression_check` entry (SOP-01) to catch the failure automatically
next time. Source: `N05_operations/P08_architecture/supervisor_n05.md` +
`agent_card_n05.md` (Crew-to-Crew Escalation) +
`P12_orchestration/crews/p12_ct_incident_response.md`.

---

## SOP-06: Suggest Evolve on Low Quality (never auto-mutate)

**Trigger**: F7 GOVERN returns a within-model/council score < 8.0 on a freshly
produced artifact; a doctor/score sweep flags an existing artifact < 8.0; or
the user expresses evolve-style intent ("fix the artifacts that turned out
bad" / "melhore os artefatos ruins"). Promoted from `.claude/skills/
evolve_on_low_quality.md` (2026-04-27, N04-authored autofire skill) --
provenance line added at the promoted skill's stub per R-166.

1. SUGGEST `python _tools/cex_evolve.py --target <path>` to the user; do NOT  <!-- [NOT SHIPPED in this tenant -- Central-only tool] -->
   auto-fire on user-authored content without consent.
2. For build outputs from the CURRENT 8F run, allow at most 2 F6 retry rounds
   before suggesting evolve (mirrors N03's SOP-01 step 8 floor-retry rule).
3. If accepted, run with sensible defaults: `--max-rounds 2 --target 9.0
   --mode heuristic` (heuristic is free; agent mode burns tokens).
4. Capture before/after scores in `.cex/learning_records/` so quality trends
   are visible later (feeds SOP-05 Trigger A ladder history).
5. NEVER mutate the original artifact in place without saving a `.bak` copy.
6. 3 consecutive evolve rounds failing to clear 8.0 -> escalate to the user
   with the dissent rationales (do not silently keep retrying).

Example: N03 builds a prompt_template, F7 returns 7.4. This SOP surfaces the
score and suggests `cex_evolve --target P03/.../prompt_x.md --max-rounds 2`.
User accepts; round 1 reaches 8.6 (clears floor); change is committed.

---

## SOP-07: CEXAI-Factory Media Pipeline (video production execution)

**Trigger**: any request naming a video/shorts/landing deliverable in
`_courses/video_series/` -- "novo shorts pro modulo X", "consertar acentos",
"re-renderizar", "regenerar karaoke", "limpar pasta", "verificar entrega".
Promoted from `.claude/skills/cexai-factory.md` (35KB, split 2026-07-03 per
R-166 -- brand canon half moved to `N02_marketing` PM SOP-07; this SOP holds
the EXECUTION half). The trigger skill itself stays lean at
`.claude/skills/cexai-factory.md` (subcommand table + pointers here).

### Pipeline (8 stages, idempotent, versioned vN -> vN.1, never overwrite)

```
[1 SCRIPT] narration .md (full PT-BR diacritics from char 1, brand canon -- see N02 PM SOP-07)
[2 VALIDATE] _tools/_<internal-era-brand>_validator.py -- diacritics + paroxytone + lexical diversity + canon  <!-- [NOT SHIPPED in this tenant -- Central-only tool] -->
[3 TTS] Qwen3-TTS clone (founder voice, LOCKED 2026-05-21) -> _rendered_<voice>_<date>_<lang>/
[4 WHISPER] faster-whisper large-v3 cuda float16, word_timestamps=True -> per-word offsets JSON
[5 KARAOKE] _tools/_shorts_v51_karaoke.py -> .ass \kf fill (shorts) OR _v10_1_srt_aligned.py -> .srt (landing)  <!-- [NOT SHIPPED in this tenant -- Central-only tool] -->
[6 MOTION] LTX clips (ComfyUI windows portable) curated via _v9_heuristic_curation.py
[7 COMPOSE] _tools/_shorts_v5_compose.py OR _v10_compose_landing.py -- drawtext+motion+karaoke+brand bar+LUT  <!-- [NOT SHIPPED in this tenant -- Central-only tool] -->
[8 DASHBOARD] _dashboard.html update + _dashboard_cleanup.py dead-link audit
```

### Subcommands (10, all idempotent)

`new-shorts <module>` . `validate <script.md>` . `render-tts <script.md>`
(30-60min) . `karaoke <rendered-dir>` . `compose-shorts <rendered-dir>`
(5min) . `compose-landing <rendered-dir>` (20-30min) . `verify <video.mp4>` .
`cleanup [--scope all|safe]` . `dashboard-refresh` . `bucket-status`.

### File conventions

`_courses/video_series/_module_N_<kind>_v<X>.mp4` (deliverable) .
`_<kind>_v<X>_karaoke.ass` / `_v<N>_subs.srt` (subs) .
`_module_N_entry_letter_v<X>.md` (canonical script) .
`_BRANDBOOK_v<X>.md` (brand canon SoT) . `_rendered_<voice>_<date>_<lang>/`
(reusable TTS WAVs) . `_clips_bucket/` (LTX motion registry) .
`_dashboard.html` (preview + status).

### Recipes (paste-ready)

1. **Fix accents, no TTS re-render**: edit each `drawtext text=` string
   directly (ffmpeg accepts UTF-8 with `segoeuib.ttf`) -> re-run
   `_shorts_v5_compose.py` (5min) -> verify with a frame extract.
2. **Switch subtitle format**: karaoke needs `_shorts_v51_karaoke.py`
   (per-segment whisper word_timestamps); big-bold/outline edits
   `force_style` in the compose script -> re-run compose.
3. **Re-render TTS for one segment**: fix the phonetic spelling in that
   segment's `.md` (never touch others) -> `_courses_render_module.py
   --segment <id>` -> re-run karaoke + compose.
4. **Clean production folder**: audit `du -sh`, move superseded MP4s to
   `_archive/`, keep current deliverables + reusable bucket + source docs,
   re-audit dashboard.
5. **Bootstrap new module shorts**: author script with full diacritics ->
   `_<internal-era-brand>_validator.py` FIRST (catches issues before TTS burns 30min) ->
   TTS render -> karaoke -> compose -> verify frames + dashboard update.

### NLM Hybrid Pipeline (parallel track, validated 2026-05-21)

For 3-format output (video+slides+infographic) from one narration: Chrome
CDP (`boot/chrome_cdp.ps1 -Port 9222`) -> Playwright
`chromium.connect_over_cdp` (no MCP) -> `_tools/_courses_notebooklm_pipeline.py  <!-- [NOT SHIPPED in this tenant -- Central-only tool] -->
{generate|status|download}` against NotebookLM (free tier, ~17min/asset,
$0). PT-BR UI selectors are aria-label-based (`button[aria-label="Adicionar
fonte"]` -- singular; IDs like `#mat-input-N` are UNSTABLE across opens).
Pitfalls: "Personalizado" style closes the modal (fall back to "Selecao
automatica"); NLM MCP supports Audio Overview ONLY, Video/Slides/Infographic
need Playwright; never force-kill Chrome (graceful close preserves session
cookies). Quality gate: sample n=8000 pixels, dark-navy 45-95%, rosa-cerebro
+dourado-quente trace-5%+, pink-Barbie 0% (forbidden). M00.1 baseline:
9.5/10 composite brand fidelity.

### Troubleshooting (symptom -> root cause -> fix)

`UnicodeEncodeError` on print -> non-ASCII under cp1252 terminal -> `cex_
sanitize.py --fix --scope <tool>`. Diacritics missing in TTS -> source .md
lacks accents -> edit + re-render (45min). Subs corrupted on Windows burn-in
-> no `charenc=UTF-8` -> add to the subtitles filter. Karaoke ASS not
rendering -> Windows path needs `C\:` escape. Whisper mistranscribed an
English tech word -> Qwen3-TTS PT mispronounced source -> phonetic respell
+ re-render OR swap to WhisperX. ffmpeg not found in bash -> not on PATH ->
`imageio_ffmpeg.get_ffmpeg_exe()`. ASS colors wrong -> ASS uses BGR not RGB
(`#D4A847` -> `&H0047A8D4`).

### Verification checklist (every render)

File exists + expected size -> duration matches plan (`ffmpeg -i ... | grep
Duration`) -> extract 5 frames at narrative checkpoints, read each PNG for
diacritics/karaoke-timing/brand-bar-text/canon-colors/no-neon-pink ->
`grep <file> _dashboard.html` to confirm the ref landed.

### Cost reference (per deliverable, local stack = $0)

Shorts re-render (no TTS) 5min/$0 . shorts full (with TTS) 45-60min/$0 .
landing v10-class 60-90min/$0 . hero image pack (50, gpt-image-1) 5min/$2.10
. cloud TTS (ElevenLabs) 30min/~$5-15 . cloud motion (Replicate) per-clip
~$0.05-0.20.

### Evolution paths (swap-in matrix, when the stack hits a wall)

TTS PT-BR: Qwen3-TTS -> F5-TTS (better EN-word pronunciation) or XTTS-v2
(multilingual) or ElevenLabs Pro (studio-grade, $$). Forced alignment:
free-form whisper -> WhisperX (aligns KNOWN text, eliminates "Cloud" vs
"Claude" class errors) or aeneas (pure-Python, no GPU). Karaoke: custom ASS
-> Captacity ($$ API) or aegisub manual (pixel-perfect, not idempotent).
Motion: LTX -> HunyuanVideo (24GB VRAM min) or Wan2.1-T2V-14B or Replicate
hailuo-02 (cloud). Composition: ffmpeg shell -> Remotion (React, type-safe)
or MoviePy (Python-native, 5-10x slower) or DaVinci Resolve API ($$).
Distribution: libx264 CRF19 -> SVT-AV1 (30-50% smaller, 3-5x encode time).

### Tenant-carry caveat (runnability, PM-2/3 evidence 2026-07-03)

12 of the tools this SOP references (Qwen3-TTS local render, faster-whisper
cuda, ComfyUI LTX motion, NotebookLM Playwright pipeline) are dev-machine
GPU-bound and NOT present in tenant carries -- this SOP is a Central-only
execution manual. A tenant session hitting this trigger should surface
"[NOT SHIPPED] -- media pipeline is Central-only" rather than attempting a
degraded run.

---

## Procedure Update Log

| Date | Procedure | Change |
|------|-----------|--------|
| 2026-07-02 | SOP-01 to SOP-05 | Initial creation, grounded in N05_operations/rules + docs/NUCLEUS_ARCHITECTURE_DOSSIER.md + CI YAML + live boot-script/MCP-config inspection. |
| 2026-07-03 | SOP-06 | Promoted from `.claude/skills/evolve_on_low_quality.md` per R-166 skill triage (destiny b: single-nucleus operating procedure). |
| 2026-07-03 | SOP-07 | Promoted (execution half) from `.claude/skills/cexai-factory.md` per R-166 skill triage (destiny d: SPLIT -- brand canon half went to N02 PM SOP-07). |

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[p10_pm_n04_knowledge]] | sibling | 0.35 |
| [[procedural_memory_n06]] | sibling | 0.33 |
| p07_rc_ops | upstream | 0.32 |
| p05_oval_deploy_checklist_n05 | upstream | 0.31 |
| ex_director_ops_health_monitor | related | 0.28 |
| [[n05_operations]] | upstream | 0.25 |
