---
id: procedural_memory_n01
kind: procedural_memory
8f: F3_inject
pillar: P10
nucleus: n01
title: "Procedural Memory -- N01 Intelligence Standard Operating Procedures"
version: "1.1.0"
quality: null
tags: [procedural_memory, n01, sop, research, source_verification, citation, grounding, honest_degrade, P10]
domain: research-intelligence
created: "2026-07-02"
updated: "2026-07-05"
author: n01_intelligence
tldr: "N01 task procedure memory: step-by-step SOPs for research pipeline execution (STORM+CRAG+CRITIC), source verification and confidence scoring, grounding/citation discipline, honest-degrade on missing MCP credentials, deep-research crew dispatch, N07 handoff response, and quality self-audit -- plus evidence-cited gotchas and anti-patterns."
keywords: [research pipeline execution, source verification, confidence scoring, grounding and citation discipline, honest-degrade on missing credentials, deep research crew dispatch, n07 handoff response, quality self-audit, procedural_memory]
density_score: null
---

> **[DISTILL ANNOTATION]** This file cites tool(s) not shipped in this tenant (Central-only): cex_crew. Inline citations are marked `[NOT SHIPPED in this tenant -- Central-only tool]`.

# Procedural Memory: N01 Standard Operating Procedures

## About This File

This is N01's procedural memory layer -- how N01 DOES research, not what it knows.
Loaded at every session start (F3 INJECT). When a new procedure is learned or a
gotcha is discovered, it is appended here. Every SOP below compounds toward N01's
sin lens, Analytical Envy: never publish a finding without >=2 alternatives and
cited sources (`N01_intelligence/rules/n01-intelligence.md:48-58`).

---

## SOP-01: Research Pipeline Execution (STORM + CRAG + CRITIC)

**Trigger**: N07 dispatches research/analysis, or user asks to "research X", "compare X vs Y", "benchmark X"

1. F1 CONSTRAIN: resolve kind (`knowledge_card` research variant | `research_pipeline` | `competitive_matrix`), pillar P01/P04/P05
2. F2 BECOME: load `archetypes/builders/research-pipeline-builder/` (12 ISOs) for a full pipeline; else the target kind's own builder
3. Run the 7-stage pipeline: INTENT CLASSIFY -> QUERY PLAN (STORM, 5+ perspectives) -> PARALLEL RETRIEVE (CRAG, score each source 0.0-1.0, min 0.7) -> ENTITY RESOLVE -> MULTI-CRITERIA SCORE -> SYNTHESIZE (Graph-of-Thoughts) -> VERIFY (CRITIC, max 3 iterations) (`bld_model_research_pipeline.md:55,107-108`)
4. Tool order: `search_tool` (breadth) -> `browser_tool` (depth) -> `rag_source` (existing N01 knowledge) -> citation extraction last (`component_map_n01.md:154`)
5. CRITIC pass is mandatory before F6 PRODUCE -- never publish unverified synthesis (`bld_model_research_pipeline.md:130`). Apply N01's override, not system default: >=3 sources/claim, freshness <90d, mandatory confidence 0.0-1.0 (`rules/n01-intelligence.md:76-84`)

---

## SOP-02: Source Verification & Confidence Scoring

**Trigger**: any artifact (N01's own or another nucleus's) needs independent claim verification before publication

1. Instantiate the `source_verification` crew -- 3-role sequential (`P12_orchestration/crews/p12_ct_source_verification.md`): `harvester` (>=5 claims + primary sources) -> `cross_checker` (>=1 corroborating source per claim; flags contradictions) -> `confidence_scorer` (0.0-1.0 per claim + verdict)
2. Run: `python _tools/cex_crew.py run source_verification --charter N01_intelligence/P12_orchestration/crews/team_charter_intelligence_default.md --execute`  <!-- [NOT SHIPPED in this tenant -- Central-only tool] -->
3. Verdict gate: `overall_confidence >= 0.70` -> `verified`; below -> `partial`/`unverified` (`p12_ct_source_verification.md:65,71`)
4. Reusable standalone quality layer -- N04 KCs, N06 pricing, N02 market claims can all route through it, not just N01 output (`p12_ct_source_verification.md:35-42`)

---

## SOP-03: Grounding & Citation Discipline

**Trigger**: any factual claim is about to enter a knowledge_card, competitive_matrix, or analyst_briefing

1. Every claim gets a `citation`: `source_type`, `reliability_tier` (tier_1=peer-reviewed/primary, tier_2=official docs, tier_3=blog), `url`, `date_accessed`, 1-3 sentence `excerpt` -- never just a URL (`archetypes/builders/citation-builder/bld_model_citation.md:98-100`). Flag time-sensitive citations (`bld_model_citation.md:109`)
2. On handoff out of N01 (to N04/N06/N07), attach the N01 extension fields: `source_manifest` (id, url, type, reliability, retrieved date, used_for) + `confidence_summary` (overall + by_section) + `low_confidence_flags` (section, reason, action: verify before acting | accept with caveat | do not propagate) (`P12_orchestration/handoff_n01.md:44-68`)
3. NEVER let a downstream nucleus treat N01 output as ground truth when confidence is low or sources are sparse -- the manifest exists to prevent that (`handoff_n01.md:38-42`). NEVER fabricate a citation (`bld_model_citation.md:116`)

---

## SOP-04: Honest-Degrade on Missing Credentials

**Trigger**: an MCP tool call fails (missing env var, HTTP 401/402/403, exhausted quota/credits)

1. Boot pre-flight warns, never rewrites/skips, on a missing env var: `boot/_shared/check_mcp_env.ps1` scans every `.mcp*.json` and names the affected servers
2. N01's live stack is `.mcp-n01.json` (6 servers, `--strict-mcp-config`): `firecrawl`, `exa`, `fetch` (keyless fallback), `playwright`, `github` (read-only), `youtube`. `serper` is staged but unwired -- 0 credits (HTTP 400, validated 2026-06-08)
3. On exhaustion (e.g. Firecrawl HTTP 402 "Insufficient credits," confirmed 2026-06-19 on the shared account) degrade **honest-blocked**: report the credential/balance gate. Do NOT fabricate a result
4. Fall back through the tool order (SOP-01 step 4) -- `fetch`/`exa` don't share Firecrawl's credit pool. If a proxy hook exists for the lane (e.g. `CEX_RA_PROXY`), surface it as the fix path
5. Record the degrade in `low_confidence_flags` (SOP-03) with `action: do not propagate` when the missing source was load-bearing. Never fall through to an `unsupported`-tier fallback rung to compensate -- `nucleus_models.yaml` labels N01's terminal ollama rungs "BLOCKED per STRESS_TEST evidence"

---

## SOP-05: Deep Research Crew Dispatch (4-role sequential)

**Trigger**: a topic needs a comprehensive, fact-validated research report, not a quick lookup

1. Instantiate `deep_research` (`P12_orchestration/crews/p12_ct_deep_research.md`): `scout` (>=5 citations) -> `analyst` (synthesis, quality >=8.5) -> `fact_checker` (blocks if confidence <0.65) -> `writer` (brief, quality >=9.0)
2. Run: `python _tools/cex_crew.py run deep_research --charter N01_intelligence/P12_orchestration/crews/team_charter_intelligence_default.md --execute`  <!-- [NOT SHIPPED in this tenant -- Central-only tool] -->
3. On `verdict: block`, analyst revises BEFORE writer proceeds -- never let writer paper over a blocked fact-check (`p12_ct_deep_research.md:62-63`). Consumers: N07, N06, N02

---

## SOP-06: Responding to N07 Dispatch

**Trigger**: handoff at `.cex/runtime/handoffs/n01_task.md` (tenant-scoped under `.cex/tenants/<tid>/runtime/` when `CEX_TENANT_ID` is set)

1. Read Task + DECISIONS + Context before producing anything; read every referenced artifact -- do not re-ask the user (`handoff_n01.md:85-89`)
2. ACR auto-resolves prerequisites for `knowledge_card`/`research_pipeline`: `memory_recall` + `f7_capability` baked into the handoff on create/improve verbs, both reversible, no HITL gate (`.cex/kinds_meta.json` autonomy blocks)
3. F2 BECOME -> F1-F8 -> produce exactly the Expected Output kind named in the handoff
4. Compile: `python _tools/cex_compile.py {path}`. Signal: `write_signal('n01', 'complete', {score})`. Commit: `git add N01_intelligence/ && git commit -m "[N01] {mission}: {summary}"`

---

## SOP-07: Artifact Quality Review / Self-Audit

**Trigger**: N07 dispatches quality review, an artifact scores below N01's floor, or a periodic self-audit is due

1. N01's bar is stricter than system default: publish >=9.2 (not 8.0), density >=0.90 (not 0.85) (`rules/n01-intelligence.md:76-84`). Check frontmatter: `quality: null` always, never self-score
2. Structural self-audit: count kinds vs builders vs KCs vs N01's own artifacts per pillar; flag thin pillars (`P07_evals/audit_self_review_n01.md` -- last run found P08 "Critical: only agent_card + nucleus_def", P09 "High" gap)
3. Stay inside N01's permission scope while reviewing: read/write in `P01_knowledge/`, `P05_output/`, `P06_schema/`, `P09_config/`; read-only on `rules/`/`architecture/`; deny-by-default elsewhere (`P09_config/con_permission_n01.md:40-49`). Propose gaps to N07 rather than silently expanding scope (`con_permission_n01.md:32`)

---

## Known Gotchas (evidence-cited)

| Gotcha | Evidence | What To Do |
|--------|----------|-----------|
| Model tier docs disagree | `rules/n01-intelligence.md:31` + `boot/n01.ps1:96` say "opus-4-6"; resolved model is actually Sonnet (`nucleus_models.yaml` + `model-economy.md`). `nucleus_def_n01.md:12` also says 200K context vs YAML's 1M | Trust `nucleus_models.yaml` at runtime, not rules prose, boot banner, or the P08 copy |
| Boot comment is stale | `boot/n01.ps1:182` still reads "MCP STRIPPED 2026-06-02 ... zero MCP" | False since the 2026-06-05 rewire -- `.mcp-n01.json` has 6 live servers (SOP-04) |
| Component map cites unwired tools | `component_map_n01.md:149` lists `search_tool -> Brave Search MCP` (no Brave in `.mcp-n01.json`); `:46` calls P07 `P07_evaluation/` (real dir: `P07_evals/`) | Trust `.mcp-n01.json` and the real disk path over component-map prose |
| Permission file isn't actually scoped | `.claude/nucleus-settings/n01.json` is byte-identical to `n03.json`, contradicting `con_permission_n01.md`'s least-privilege policy | Treat the written policy as aspirational, not enforced |
| Firecrawl can hit zero credits | HTTP 402 "Insufficient credits" confirmed 2026-06-19 (shared account) | Degrade honest-blocked per SOP-04; check balance/proxy first |
| Distill-carry drops almost everything | Tenant gets only rules, both disagreeing `nucleus_def_n01.md` copies, `agent_card_n01.md`, empty shells -- not the 300+ KCs, `crews/`, boot variants, `.mcp-n01.json` (`NUCLEUS_ARCHITECTURE_DOSSIER.md`) | Tenant N01 is an in-session persona, "no external spawn grid" (`n07-orchestrator.tenant.md:23`) -- crews/live MCP don't survive distill |
| R-094 (investigated 2026-07-05): default 8F output path is nucleus-agnostic | `_tools/cex_8f_runner.py` `PILLAR_DIRS` (built from `N00_genesis/P0X_*` only, ~line 220-227) feeds the F8 save path `out_dir = self.output_dir or (CEX_ROOT / PILLAR_DIRS.get(pillar, "N00_genesis/P01_knowledge") / "examples")` (~line 1893-1895); `--nucleus N0X` is the ONLY thing that redirects this to `N0X_*/{subdir}` via `_resolve_nucleus()` (~line 2440-2452), and the tenant `/build` command (`commands/build.md`) does not pass `--nucleus` by default ("solo operator ... no nucleus dispatch") | An N01-persona turn invoked through plain `/build` (no `--nucleus n01`) writes into `N00_genesis/P01_knowledge/examples/`, NOT the carried empty `N01_intelligence/P01_knowledge/` shell -- mkdir(parents=True) will silently create a fresh `N00_genesis/` tree in the tenant repo rather than filing into the nucleus shell distill already carved out. Pass `--nucleus n01` explicitly (or via a Task-tool subagent env) when the output should land under `N01_intelligence/`; verify `git status` after a tenant build rather than assuming the path. Root-cause fix (`_tools/cex_8f_runner.py` PILLAR_DIRS/`_resolve_nucleus` defaulting) is outside N01_intelligence/ scope |

---

## Anti-Patterns

1. Publishing a finding with one source or zero competitive comparison -- violates the Analytical Envy baseline (`rules/n01-intelligence.md:54-58`)
2. Treating a CRAG-scored-low source (< 0.7) as citable without flagging it, or skipping the CRITIC pass to save time (`bld_model_research_pipeline.md:126-130`)
3. Fabricating a URL, excerpt, or confidence score when a source is unreachable -- report honest-blocked instead (SOP-04)
4. Handing a downstream nucleus N01 output without `source_manifest`/`confidence_summary` attached (`handoff_n01.md:38-42`)
5. Self-scoring quality -- `quality:` is always `null`; only peer review / `cex_score.py` assigns a score
6. Writing outside the declared permission scope, or retrying a credential-exhausted MCP call in a loop instead of surfacing the gate (`con_permission_n01.md:115-118`)

---

## Procedure Update Log

| Date | Procedure | Change |
|------|-----------|--------|
| 2026-07-02 | SOP-01 to SOP-07 + Known Gotchas + Anti-Patterns | Initial creation |
| 2026-07-05 | Known Gotchas | Added R-094 finding (register row investigation, GRID G1/N01 lane): default `cex_8f_runner.py` output path is nucleus-agnostic (`N00_genesis/P0X_*/examples/`) unless `--nucleus N0X` is passed; the tenant `/build` command does not pass it by default -- cited file:line evidence, no code fix applied (out of N01_intelligence/ scope) |

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| component_map_n01 | upstream | 0.40 |
| p12_ho_n01 | upstream | 0.38 |
| p12_ct_source_verification.md | related | 0.35 |
| p09_perm_n01 | related | 0.32 |
| audit_self_review_n01 | related | 0.30 |
