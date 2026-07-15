---
id: p10_pm_n03
kind: procedural_memory
8f: F3_inject
pillar: P10
nucleus: n03
title: "Procedural Memory -- N03 Engineering Standard Operating Procedures"
version: "1.0.0"
quality: null
tags: [procedural_memory, n03, sop, 8f, builder_iso, compile, peer_review, frozen_kind, P10]
domain: engineering
status: active
created: "2026-07-02"
updated: "2026-07-02"
author: n03_builder
tldr: "N03 task procedure memory: step-by-step SOPs for the 8F build flow, builder ISO loading (12 per kind), compile-after-save, signal-on-complete, peer-review handoff (never self-score), and frozen-kind moat respect for the tenant capability layer."
keywords: [engineering, procedural memory -- n, standard operating procedures, 8f build flow, builder iso loading, compile after save, peer review handoff, frozen kind moat, procedural_memory]
density_score: null
related:
  - rule_n03_builder
  - p08_pat_construction_triad
  - revision_loop_policy_n03
  - p10_lr_call_site_migration
  - agent_card_n03
  - p01_kc_construction_laws
---

> **[DISTILL ANNOTATION]** This file cites tool(s) not shipped in this tenant (Central-only): cex_new_nucleus. Inline citations are marked `[NOT SHIPPED in this tenant -- Central-only tool]`.

# Procedural Memory: N03 Engineering Standard Operating Procedures

## About This File

N03's procedural memory -- HOW N03 builds, not WHAT it knows (that lives in
`N03_engineering/P01_knowledge/kc_*.md`). Load alongside `N03_engineering/
rules/n03-builder.md` at every session start. When a procedure changes or a
gotcha is learned, append it here instead of re-deriving it next session.

---

## SOP-01: 8F Build Flow (F1 -> F8)

**Trigger**: a handoff at `.cex/runtime/handoffs/n03_task.md` (tenant-scoped
under `.cex/tenants/<tid>/runtime/`, resolved from `CEX_TENANT_ID` by
`boot/n03.ps1`, whose initial message is literally "Read {handoff} and
execute. If no handoff, report ready."), or an in-session build request.

1. Read the handoff FIRST, before any other action (`boot/n03.ps1:32-38,124-126`).
2. F1 CONSTRAIN: resolve `{kind, pillar}` from `.cex/kinds_meta.json`; load
   `N00_genesis/P{xx}_*/_schema.yaml`.
3. F2 BECOME: load the 12 builder ISOs for `{kind}` -- see SOP-02.
4. F3 INJECT: load `N03_engineering/P01_knowledge/kc_{domain}.md` + similar
   artifacts via `cex_retriever.py`.
5. F4 REASON: apply the Construction Triad's Template-First pattern
   (p08_pat_construction_triad): similarity >= 60% -> ADAPT, 30-59% ->
   HYBRID, < 30% -> FRESH from builder ISOs + base schema.
6. F5 CALL: confirm compile/doctor/index tooling is reachable; scan for reuse.
7. F6 PRODUCE: generate at density >= 0.85 (L11 Token Optimization,
   [[p01_kc_construction_laws]]) -- tables/decision-trees over prose.
8. F7 GOVERN: quality gate, floor **9.0** (above the 8.0 system default,
   `n03-builder.md:46`) -- "below that, you rebuild". Max 2 F6 retries on
   failure (L07 Resilience).
9. F8 COLLABORATE: save, compile, signal (SOP-03/SOP-04); commit only outside
   a per-cell worktree (SOP-04, point 4).

---

## SOP-02: Builder ISO Loading (F2 BECOME)

**Trigger**: F2 step of SOP-01, or an explicit "load the {kind}-builder" ask.

1. Resolve `{kind}` -> `archetypes/builders/{kind}-builder/`.
2. Read all 12 ISOs, one per pillar: `bld_{architecture,config,eval,feedback,
   knowledge,memory,model,orchestration,output,prompt,schema,tools}_{kind}.md`.
   Verified on disk: `knowledge-card-builder/` and `agent-builder/` each
   contain exactly 12 files, matching `agent_card_n03.md:78,156` ("12 ISOs
   mapped 1:1 to the 12 pillars").
3. For a single-kind, single-artifact ask, prefer the pre-compiled sub-agent
   form: `.claude/agents/{kind}-builder.md` is the same 12 ISOs, Agent-tool
   -invocable, no OS-window spawn tax (`NUCLEUS_ARCHITECTURE_DOSSIER.md:
   336-340`). Reserve spawn+worktree for grid/wave/BOOTSTRAP-shaped work.
4. If `{kind}` has no builder dir yet: do not freehand 12 ISOs by hand. Route
   through the `builder_factory` crew (spec_writer -> iso_generator ->
   test_runner, `P12_orchestration/crews/p12_ct_builder_factory.md`).
5. **Flagged nuance**: `n03-builder.md:54` and `hybrid_review_n03.md:47,58`
   say "13 ISOs" -- an older, differently-named set (adds `collaboration`,
   `examples`, `instruction`, `manifest`, `system_prompt`). Disk + `agent_
   card_n03.md:78,156` show the current 12-name set (step 2); treat "13" as
   a stale rule-file line until corrected.

---

## SOP-03: Compile After Save (F8 sub-step)

**Trigger**: immediately after any `Write`/`Edit` to an artifact `.md`, before
signal or commit. Source: `N03_engineering/rules/n03-builder.md:49`, `CLAUDE.md`
Constraints ("ALWAYS: ... compile after save").

1. Save to the correct pillar dir under `N0X_*/P{xx}_*/` -- N03 is the ONLY
   nucleus allowed to write `archetypes/builders/*/bld_*.md` and
   `N00_genesis/P*/*.md` directly (`dispatch_catalog.md:99-100`); every other
   nucleus routes those through N03.
2. Run `python _tools/cex_compile.py {path}` (single-file positional arg).
   Must exit clean -- a frontmatter/parse failure means the save is not done.
3. Batch builds (e.g. builder_factory's 12 ISOs) use `--lp {PILLAR}` or `--all`.
4. Compiled YAML lands in gitignored `compiled/` -- never hand-edit it; it
   regenerates from source (8f-reasoning.md's gitignore-aware commit rule).
5. `quality:` stays `null` through compile -- compiling is structural, not a
   quality judgment (SOP-05).

---

## SOP-04: Signal on Complete (F8 sub-step)

**Trigger**: pairs with SOP-03, after compile succeeds. Source:
`_tools/signal_writer.py`.

1. Call `write_signal('n03', 'complete', {score}, artifact_path='{path}',
   min_bytes={n})`. Passing `artifact_path` triggers a post-signal
   verification guard (`signal_writer.py:42-56`) that REJECTS the signal if
   the file does not exist, and REJECTS again if it exists but is smaller
   than `min_bytes`. **Gotcha**: this guard exists to catch "signal-without
   -deliverable" (a cell reporting `complete` with no real artifact) --
   always pass both args for a non-trivial artifact, never skip `min_bytes`.
2. `nucleus` must be lowercase and in `{n01..n07}`; `status` must be lowercase
   alpha/underscore (`signal_writer.py:22,33-40`) -- `"N03"` or `"Complete"`
   raise `ValueError`.
3. `quality_score` here is telemetry only -- NOT the authoritative `quality:`
   frontmatter field, which N03 never sets itself (SOP-05).
4. Worktree discipline: if N03 was dispatched into a per-cell worktree (grid
   `-w`), N03 signals but does **NOT** `git commit` -- N07 consolidates via
   the worktree-merge flow (`NUCLEUS_ARCHITECTURE_DOSSIER.md:324`;
   `n07-orchestrator.md` Step 4b).

---

## SOP-05: Peer-Review Handoff (never self-score)

**Trigger**: after F6 PRODUCE, before an artifact's `quality:` field is ever
touched. Source: RACI Explicit Prohibitions ("N03 NEVER scores its own work --
peer review only"); `crews/p12_ct_artifact_factory.md`; `p02_ra_reviewer.md`;
`revision_loop_policy_n03.md`.

1. Builder role finishes 8F (SOP-01) and emits `artifact_path`; `quality:`
   stays `null`.
2. Hand off via an a2a-task signal to the `reviewer` role (bound to
   `.claude/agents/quality-gate-builder.md` in the `artifact_factory` crew) --
   the builder never scores itself.
3. Reviewer runs `python _tools/cex_score.py {path}` and must cite specific
   `H01-H07` gate IDs on any rejection -- "prose rejections are invalid"
   (`p02_ra_reviewer.md:70`).
4. Below 9.0: revise per `revision_loop_policy_n03` -- 3 cycles standard, 4 for
   `schema_breaking_change`, 5 for `security_critical`, 2 for `documentation`.
   Each cycle must change approach (Axiom 1: revision is not retry).
5. Reviewer's own delegation budget is tighter: max 2 revision round-trips to
   the builder before escalating (`p02_ra_reviewer.md` Delegation Policy).
6. `integrator` cross-references the full artifact set and runs
   `cex_doctor.py`; only then is the crew instance complete.
7. Precedent: `hybrid_review_n03.md` -- a 52-ISO batch peer-audited, 0/52
   passed the 9.0 floor pre-review, 12 rewritten to 9.1-9.8/10 after. Self
   -scoring would have hidden exactly this failure.

---

## SOP-06: Frozen-Kind Moat Respect

**Trigger**: wiring a tenant capability card, or an overlay `kinds:` map entry
in the dashboard capability layer -- NOT ordinary artifact construction under
`N0X_*/P*/`. Source: `cex_capability_registry.py:67-77` (`_FROZEN_KINDS`) and
`:115-128` (`CapabilityFrozen`), mirrored byte-for-byte in
`cex_intent_resolver.py`.

1. Before mapping any capability slug -> kind, check the kind against
   `_FROZEN_KINDS`: `workflow`, `pipeline_template`, `prompt_compiler`,
   `reasoning_trace`, `quality_gate`, `dispatch_rule`, `handoff`. These 7 are
   the "8F MOAT" -- 8F-governed pipeline primitives.
2. A tenant card or overlay can NEVER target a frozen kind: belt-and-braces --
   the overlay loader rejects it at load time, `resolve_capability()` refuses
   again at resolution time (`CapabilityFrozen`).
3. If a task asks N03 to make a frozen kind reachable via a capability
   slug/overlay: refuse, the same way `CapabilityFrozen` does. Do not
   silently retarget to a different kind or hand-write around the guard.
4. The moat protects kind GOVERNANCE, not kind USE -- N03 still builds
   ordinary `workflow` / `quality_gate` / `handoff` artifacts under the normal
   8F pipeline (SOP-01); it only blocks a capability card from re-pointing
   one of those 7 kinds at custom, ungoverned logic. If the frozen set ever
   changes, both registry files change together (a one-sided edit splits it).

---

## SOP-07: New Nucleus Bootstrap (N08+)

**Trigger**: "new nucleus", "add N08", "{domain} nucleus", "create a
vertical" -- creating any nucleus beyond N01-N07. Promoted from
`.claude/skills/new_nucleus_bootstrap.md` (2026-04-16) per R-166 skill
triage (destiny b: only N03 scaffolds nuclei -- RACI "Build artifact" row).

1. Prefer the one-command scaffolder over manual steps:
   `python _tools/cex_new_nucleus.py <NN> <domain> <sin> [--dry-run]`  <!-- [NOT SHIPPED in this tenant -- Central-only tool] -->
   (positional: nucleus_num, domain, sin -- one of
   envy/lust/pride/gluttony/wrath/greed/sloth). Generates ~15 dirs + 11
   files + 1 yaml append in ~1s, then runs `cex_doctor.py` on the result.
2. The 9 required assets (manual fallback, or to verify scaffolder output):
   rule file (`N{XX}_{domain}/rules/n{xx}-{domain}.md`), nucleus_def
   (`P02_model/nucleus_def_n{xx}.md`), agent card
   (`P08_architecture/agent_card_n{xx}.md`), domain vocabulary KC
   (`P01_knowledge/kc_{domain}_vocabulary.md`), component map
   (`P08_architecture/component_map_n{xx}.md`), Claude Code sub-agent
   (`.claude/agents/n{xx}-{domain}.md`), boot scripts (`boot/n{xx}.ps1` +
   `boot/n{xx}_codex.ps1`), scoped permissions
   (`.claude/nucleus-settings/n{xx}.json`, copied from `_template.json` --
   new nuclei start SCOPED, never trusted).
3. All 12 pillar dirs must exist (fractal compliance) -- missing any breaks
   the 12LP nucleus-level completeness check `cex_doctor.py` enforces.
4. Multi-runtime parity: every boot wrapper accepts `-WorktreeDir`, `-Task`,
   `-AutoAccept`, reusing `boot/_shared/worktree_helpers.ps1`. Shared skills
   must mirror into `.cex/skills/` (`cex_skill_sync.py apply`).
5. Register routing in `.cex/config/nucleus_models.yaml`
   (`n{xx}: {model, context, fallback_chain: [claude, ollama]}`).
6. Validate: `python _tools/cex_doctor.py` + `python _tools/cex_sanitize.py
   --check --scope N{XX}_{domain}/` + confirm `ls N{XX}_{domain}/P{01..12}*/`
   shows all 12.
7. Sin lens selection guide: envy->research/intelligence, lust->marketing/
   design, pride->engineering/code, gluttony->knowledge/documentation,
   wrath->operations/testing, greed->commercial/sales,
   sloth->orchestration.
8. Signal completion:
   `write_signal('n{XX}', 'complete', 9.0)` (SOP-04 shape).

Anti-patterns: creating a nucleus for an already-covered subdomain (use a
kind instead) -- skipping the vocabulary KC (semantic drift with existing
nuclei) -- trusted permissions on a new nucleus -- hardcoding the model in
the boot script instead of `nucleus_models.yaml` -- missing any of the 12
pillar dirs.

---

## Procedure Update Log

| Date | Procedure | Change |
|------|-----------|--------|
| 2026-07-02 | SOP-01 to SOP-06 | Initial creation |
| 2026-07-03 | SOP-07 | Promoted from `.claude/skills/new_nucleus_bootstrap.md` per R-166 skill triage (destiny b: single-nucleus operating procedure). |

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[rule_n03_builder]] | upstream | 0.40 |
| p08_pat_construction_triad | upstream | 0.36 |
| revision_loop_policy_n03 | related | 0.33 |
| p10_lr_call_site_migration | sibling | 0.29 |
| agent_card_n03 | upstream | 0.28 |
| [[p01_kc_construction_laws]] | upstream | 0.26 |
