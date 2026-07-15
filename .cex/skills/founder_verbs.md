---
name: founder-verbs
description: Fires when the founder issues a bare improvement verb (melhorar / tirar debt tecnico / preencher gaps / otimizar, or the EN synonyms improve / fix debt / fill gaps / optimize) WITHOUT naming a specific target file, artifact, or nucleus. Binds the bare verb to docs/IMPROVEMENT_REGISTER.md — the deterministic, executable backlog seeded by the NUCLEUS_STUDY_2026_07_02 mission. Filters the register by verb, refreshes signals cheaply, picks the top slice by impact/effort that fits the session, never auto-picks founder-gated rows, executes via the proven session cadence, and reports the delta back into the register.
when:
  - User says a bare improvement verb with no specific target — "melhorar", "melhora isso", "tira o debt tecnico", "preenche os gaps", "otimiza", "improve the system", "fix the debt", "fill the gaps", "optimize", "clean up the drift" — and does NOT name a file, artifact, kind, or nucleus to act on.
  - User references "o register" / "a fila" / "the backlog" / "the improvement register" without further qualification.
  - A session has idle capacity after its primary task and the founder says something like "enquanto isso, vai melhorando" / "in the meantime, keep improving" (background-improvement grant, same pattern as the standing overnight /loop grant).
kind: skill
pillar: P12
nucleus: n07
quality: null
version: 1.1.0
created: "2026-07-02"
updated: "2026-07-02"
multi_runtime: true
runtimes: [claude, codex, gemini, ollama]
density_score: 0.88
tags: [skill, autofire, governance, backlog, layer6, n07_enforcement, founder_verbs, improvement_register]
related:
  - improvement_register
  - dispatch_before_build
  - gdp_on_subjective
  - n07-orchestrator
  - raci-matrix
---

> **[DISTILL ANNOTATION]** This file cites tool(s) not shipped in this tenant (Central-only): cex_flywheel_audit. Inline citations are marked `[NOT SHIPPED in this tenant -- Central-only tool]`.

# Founder Verbs

> **The core rule this enforces**: a bare founder verb ("melhorar", "otimizar", "tirar debt",
> "preencher gaps") is a real directive, not small talk — but it names no target. Without a
> binding mechanism, N07 either guesses (risking scope drift / re-litigating already-closed
> questions) or asks the founder to enumerate the backlog by hand every time. This skill makes
> the binding deterministic: the founder's bare verb resolves to a filtered slice of
> `docs/IMPROVEMENT_REGISTER.md`, the single seeded, evidence-grounded backlog produced by the
> `NUCLEUS_STUDY_2026_07_02` mission (see `docs/NUCLEUS_ARCHITECTURE_DOSSIER.md` for the full
> architecture context every register row is grounded in).

## When this fires

Trigger A — **bare verb, no target** (PT-BR + EN):
- `melhorar`, `melhora`, `melhore` / `improve`
- `tirar debt (tecnico)`, `tira o debt` / `fix (the) debt`, `pay down debt`
- `preencher gaps`, `preenche os gaps` / `fill (the) gaps`, `fill in gaps`
- `otimizar`, `otimiza` / `optimize`
- Compound/loose forms: "deixa isso melhor", "limpa o drift", "clean this up", "make it better",
  "polish", "harden" — WITHOUT a specific file/artifact/nucleus named in the same sentence.

If the founder names a target ("melhora o boot/n07.ps1", "fix the debt in N02's agent card"),
this skill does NOT fire — that is a normal, targeted dispatch; route it directly (see
`dispatch_before_build.md`) instead of through the register.

Trigger B — **explicit register reference**: "o register", "a fila de melhoria", "the backlog",
"the improvement register", "what's still open".

Trigger C — **idle-capacity grant, same-session only** (corrected 2026-07-02 fix round — see
below): the founder explicitly grants background improvement time in the CURRENT session without
naming a target (e.g. "enquanto isso, vai melhorando" / "in the meantime, keep improving"). This
live, explicit instruction is itself the founder's GDP answer for THIS session — per
`.claude/rules/guided-decisions.md`'s own table ("User says 'just do it' / 'you decide' -> NO
[GDP needed], user explicitly waives GDP"), a real-time explicit grant satisfies GDP for the
mechanical register-pop-and-fix work this skill performs (Steps 1-7). It is **NOT** a standing,
skill-manufactured waiver that carries into future sessions — each session's Trigger C fire needs
its OWN live founder grant; this skill does not infer, remember, or reuse a waiver across
sessions, and it is a narrower, separately-scoped grant from the overnight `/loop` grant
(`feedback-overnight-autonomous-loop-2026-06-21` in memory) — the two are cited together only for
pattern-recognition (same shape of "explicit idle-capacity grant"), never treated as one shared
or transitive authorization.
  Even under an active Trigger C grant, this waiver covers ONLY the mechanical pick-and-fix work —
  it does NOT cover: (a) rows Step 5b flags via the RACI/GDP cross-check (subjective/brand/
  pricing-shaped items), or (b) rows Step 5c flags as architecture-level default-policy proposals.
  Those still route to `gdp_on_subjective.md` or surface as a proposal, every time, regardless of
  Trigger C.

## Verb -> register-column mapping

| Founder says (PT-BR or EN) | Register `verb` column filter |
|---|---|
| melhorar, melhora, melhore, improve, "make better", "harden", "polish" | `melhorar` |
| tirar debt, tira o debt tecnico, fix debt, pay down debt, "clean up drift" | `debt` |
| preencher gaps, preenche os gaps, fill gaps, fill in gaps, "close the holes" | `gap` |
| otimizar, otimiza, optimize, "make it faster/cheaper/leaner" | `otimizar` |
| No verb specified, just "melhora o sistema" / "improve the system" (fully generic) | ALL FOUR buckets, sorted verb-then-impact as the register already is — read top-to-bottom |

## Procedure

1. **Read** `docs/IMPROVEMENT_REGISTER.md` in full (it is small enough to read whole — do not
   grep-sample it; a partial read risks missing a `gated` row and picking it by accident).
2. **Filter rows** by the verb column, using the mapping table above. If the founder's phrasing
   maps to more than one bucket (rare) or to none specifically, treat it as ALL FOUR buckets.
3. **Refresh signals cheaply** before picking, only if stale (do not run these unconditionally —
   check timestamps first):
   - `python _tools/cex_doctor.py` (fast tier) — if a picked row's `owner` nucleus has doctor
     FAILs newer than the register's own `created`/last-updated date, that nucleus's rows may
     already be stale; re-verify the specific evidence path before executing.
   - `python _tools/cex_flywheel_audit.py` — only if its own last-run report predates the  <!-- [NOT SHIPPED in this tenant -- Central-only tool] -->
     register (Layer-0 audit; catches drift the register itself doesn't track, e.g. new
     KC_coverage gaps).
   - If a row's evidence path no longer matches reality (the finding was already fixed by other
     work since 2026-07-02), do NOT execute it — flip its status inline (append an outcome note,
     see Step 7) and move to the next row. This mirrors the correction pattern already applied
     once during register seeding (AUDIT gap #2 and round-3 item (b) were both found already
     fixed and excluded rather than executed a second time).
4. **Pick the top slice** by impact/effort that fits the session budget:
   - Prefer H-impact/S-effort rows first (highest leverage per token spent).
   - A "slice" is 1-5 rows for a normal session; more only under an explicit overnight/loop grant
     (Trigger C) with its own budget ceiling.
   - Prefer rows sharing one `owner` nucleus when picking >1 row, to keep the dispatch/session
     scoped (matches `.claude/rules/dispatch-depth.md`'s scoping bias) — UNLESS the founder asked
     for breadth across nuclei explicitly.
   - Respect any `see R-XXX` dedupe pointers in the register (`status` cell) — never execute a
     pointer row independently of the row it points to; resolve the canonical row once.
5. **NEVER pick a row whose `status` starts with the literal token `gated`.** Surface them
   instead: name the row, its evidence, and why it is gated (founder action required, blocked on
   creds, needs an explicit founder decision, or an architecture-level default-policy proposal —
   see Step 5c). This is a hard rule, not a preference — gated rows exist specifically because
   CLAUDE.md's founder-gated list (push tenant/deploy/prod/live/real-$/produtos fix), an open
   founder decision, or the Decision Authority table's "architecture changes" boundary sits
   upstream of them. Surfacing is not optional; silently skipping them without telling the
   founder is also wrong — say what's blocked and why, every time this skill fires.
   Do not rely on the literal-string check alone as your only defense, though —
   `docs/IMPROVEMENT_REGISTER.md`'s own Columns section states the convention explicitly: any row
   needing founder action/approval MUST carry a `status` starting literally with `gated`; an
   `open (...)` parenthetical is informational only. If you ever encounter a row whose `item` or
   parenthetical text uses founder-decision language ("founder decision", "founder validation",
   "founder approval", "requires founder approval", "GDP required", "requires GDP",
   "GDP decision", "GDP candidate", or any other "GDP ..."-prefixed requirement phrase) but
   whose `status` does NOT start with
   `gated`, treat it as gated anyway, do not execute it, and flag the register itself for a
   status-column fix before proceeding — this exact drift was caught and corrected twice already
   (R-139/R-140 originally read `open (founder decision)` / `open (needs founder
   validation...)`; R-006 originally read `open (GDP required ...)` — fixed to `gated` by the
   N07 keystone 2026-07-02, which is also when the GDP phrases were added to this list).
5b. **Cross-check every picked row against RACI + GDP triggers before executing it** — do this
   for every row, not just ones that look risky; the register's `owner`/`status` columns are a
   snapshot from the seeding session (2026-07-02) and can be wrong or drift stale:
   - Compare the row's `owner` against `.claude/rules/raci-matrix.md`'s Responsible party for the
     decision type it touches (e.g. brand/white-labeling/theming work is N06-Responsible per the
     "Brand decisions" row; monetization is N06-Responsible per "Monetize"). If the register's
     `owner` omits the RACI-Responsible nucleus for the row's actual subject matter, do not
     dispatch it as ordinary technical work under the listed owner(s) alone — route it through
     the correct nucleus and treat it as a GDP candidate (see R-006, corrected 2026-07-02: owner
     was `N03/N02`, missing N06, for a structurally brand/white-label decision).
   - Compare the row's `item` text against `.claude/rules/guided-decisions.md`'s GDP-trigger
     table (tone, audience, style, layout, CTA, colors, brand identity, pricing — any subjective
     choice). If the item structurally matches a GDP-trigger category, route it through
     `.claude/skills/gdp_on_subjective.md` BEFORE executing, regardless of what the register's
     `status` column literally says — a plain `open` does not mean "no GDP needed"; the register
     was seeded once and never re-audited against RACI/GDP after the fact.
5c. **NEVER auto-pick a row that proposes an architecture-level default-policy change** — a new
   DEFAULT posture across Central or a nucleus (e.g. changing the default dispatch mechanism,
   model tier, or security posture going forward) — merely because its `status` reads `open` and
   its impact/effort profile looks attractive (H-impact/M-effort rows are exactly what Step 4
   prefers, which is precisely the trap). Cross-check the row's scope against
   `.claude/rules/n07-orchestrator.md`'s Decision Authority table: "HOW to build (kind, pillar,
   nucleus, pipeline) | N07 (autonomous)" covers producing a single artifact/build; "Architecture
   changes | N07 proposes, user approves" covers everything else, including "adopt X as the new
   default for Y going forward" or an "N07-level synthesis" of several per-nucleus proposals. A
   row whose `item` reads that way is the latter, not the former, no matter how small each
   individual step sounds. R-114, R-115, R-117 through R-121 (in-session-dispatch-as-default
   proposals, one per nucleus + the N07-level umbrella) are architecture-level per this test and
   are marked `gated (...)` in the register for exactly this reason (corrected from plain `open`
   in the 2026-07-02 fix round) — surface them as proposals per the Decision Authority table's
   own language ("N07 proposes, user approves"), never execute them autonomously under this
   skill, even under an active Trigger C idle-capacity grant.
6. **Execute via the proven session cadence** (per `n07_task.md`'s own stated load-bearing
   pattern, repeated across every session in this mission's history):
   ```
   ultracode Workflow (build + adversarial verify + judges)
     -> N07 INDEPENDENT keystone (re-run the gates + read the diff MYSELF, never trust the cell's claim)
     -> revert incidental churn (.cex/*.json cache, score_cache, etc.)
     -> path-scoped commit
     -> push (pull --rebase if the branch is shared)
   ```
   For a single small (S-effort) row, a full Workflow may be overkill — a direct fix + doctor
   verify + commit is fine, but the independent-keystone step (re-verify yourself, don't trust
   a sub-agent's self-report) is never skippable, per `.claude/rules/8f-reasoning.md` Rule 4
   (`quality: null`, never self-score) and the Working Discipline in `CLAUDE.md`.
   Route construction work through the correct nucleus, not directly from N07 — this skill
   selects WHAT to work on; `dispatch_before_build.md` still governs HOW N07 hands it off.
7. **Update register statuses + report the delta.** After execution:
   - Flip the picked row(s) `status` (`open` -> `in-flight` while working, then remove/mark done
     once landed — the register's own header documents "flip status and append an outcome note").
   - Add a one-line outcome note per picked row (what actually happened — fixed as described,
     fixed differently, found already stale, or partially done with a residual).
   - Report to the founder: which rows were picked, why (impact/effort rationale), what shipped,
     what's still open, and the full list of any `gated` rows surfaced but not touched.

## Fallback — register missing or stale beyond repair

If `docs/IMPROVEMENT_REGISTER.md` is missing, or its `source_mission` frontmatter field points at
a mission whose findings are clearly obsolete (e.g. the codebase has moved on by months and the
register was never refreshed), do NOT invent a new backlog from memory. Rebuild it from the same
seeding recipe the register's own header documents:
1. `python _tools/cex_doctor.py` (current FAILs/WARNs = a real gap signal).
2. `python _tools/cex_flywheel_audit.py` (Layer-0 doc-vs-practice drift).  <!-- [NOT SHIPPED in this tenant -- Central-only tool] -->
3. `.cex/runtime/handoffs/n07_task.md` (the live self-handoff — read its current top block for
   whatever round/queue is open now, the same way this register folded in ROUND-3).
4. Any current `docs/AUDIT_*` report, if one exists and postdates the stale register.
Then write a fresh `docs/IMPROVEMENT_REGISTER.md` following the same column shape (ID, verb,
item, evidence, impact, effort, owner, status) before resuming Step 1 of the main Procedure.

## Anti-patterns (BLOCKED)

| Pattern | Why blocked | Correct path |
|---------|-------------|--------------|
| Picking a `status: gated` row because it's H-impact and tempting | Founder-gated means founder-gated — no exception for leverage | Surface it, don't touch it |
| Inventing new backlog items from memory instead of reading the register | Bypasses the grounded, evidence-cited seeding this skill exists to leverage | Read the register; use the Fallback only if it's genuinely absent/stale |
| Executing a picked row without re-verifying its evidence still holds | The register was seeded once (2026-07-02); code moves — a stale row executed blind can "fix" something already fixed, or fix the wrong thing | Step 3's cheap-refresh + spot-check before executing |
| Skipping the independent-keystone re-verify because "the sub-agent said it passed" | `quality: null` / never self-score is a hard 8F rule, not a suggestion | Always re-run gates + read the diff yourself |
| Silently dropping a `gated` row from the report because it's not actionable this session | The founder needs to know what's blocked and why, every time, not just once | Always list gated rows surfaced, even if untouched |
| Treating this skill as license to touch unrelated code "while I'm here" | Violates CLAUDE.md Working Discipline clause 4 (don't touch unrelated code) | Stay scoped to the picked slice |
| Auto-picking a row whose `owner`/`status` don't reflect the real RACI/GDP requirement (register drift since seeding) | The register is a snapshot, not a live source of truth — a plain `open` + wrong/incomplete `owner` can silently smuggle a subjective/brand decision through as "ordinary technical work" | Step 5b's RACI + GDP cross-check, every row, not just risky-looking ones |
| Auto-picking an "adopt X as the default" row because it's H-impact/M-effort and `status: open` | Architecture-level default-policy changes require founder approval per the Decision Authority table, never autonomous N07 execution, regardless of register status | Step 5c's scope test; treat as gated/proposal, always |
| Treating Trigger C (idle-capacity grant) as a standing, cross-session GDP waiver | Each Trigger C fire needs its OWN live founder grant in that session; borrowing authority from a different, narrower standing grant (overnight `/loop`) or from a past session's Trigger C is an unauthorized self-extension | Re-earn the grant every session; Trigger C never overrides Step 5b/5c regardless |

## Cross-references at runtime

- The register itself: `docs/IMPROVEMENT_REGISTER.md`
- Full architecture grounding for every row: `docs/NUCLEUS_ARCHITECTURE_DOSSIER.md`
- Dispatch routing once a target is chosen: `.claude/skills/dispatch_before_build.md`
- GDP for any row whose fix requires a subjective call: `.claude/skills/gdp_on_subjective.md`
- RACI Responsible/Accountable check (Step 5b): `.claude/rules/raci-matrix.md`
- GDP-trigger table (Step 5b): `.claude/rules/guided-decisions.md`
- Architecture-change scope test (Step 5c): `.claude/rules/n07-orchestrator.md` Decision Authority table
- Doctor (fast health check): `python _tools/cex_doctor.py`
- Flywheel audit (Layer-0 doc-vs-practice): `python _tools/cex_flywheel_audit.py`  <!-- [NOT SHIPPED in this tenant -- Central-only tool] -->
- Live self-handoff (current round/queue context): `.cex/runtime/handoffs/n07_task.md`

## Related Artifacts

| Artifact | Relationship | Score |
|----------|-------------|-------|
| improvement_register | the backlog this skill pops from | 0.95 |
| dispatch_before_build | sibling skill — governs HOW work routes once this skill picks WHAT | 0.70 |
| gdp_on_subjective | downstream — fires if a picked row's fix requires a subjective founder call | 0.55 |
| n07-orchestrator | upstream rule — the dispatch cadence this skill's Procedure follows + the Decision Authority table Step 5c enforces | 0.80 |
| raci-matrix | upstream rule — Step 5b cross-checks every picked row's `owner` against this before auto-executing | 0.55 |
