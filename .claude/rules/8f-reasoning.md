---
glob: "**"
alwaysApply: true
description: "8F Universal Reasoning Protocol — every nucleus, every task, every time"
quality: 9.0
title: "8F-Reasoning"
version: "1.0.0"
author: n03_builder
tags: [artifact, builder, examples]
tldr: "Golden and anti-examples for CEX system, demonstrating ideal structure and common pitfalls."
domain: "CEX system"
created: "2026-04-07"
updated: "2026-04-07"
density_score: 0.90
related:
  - p01_kc_8f_pipeline
  - p06_td_cex_artifact_type_n03
  - p01_faq_cex_common_questions
  - p03_sp_n03_creation_nucleus
  - kind-builder
---

# 8F Universal Reasoning Protocol

**MANDATORY for ALL nuclei (N01-N07). Every task. No exceptions.**

8F is not a "build checklist" — it's how CEX THINKS. Whether you're researching,
writing copy, building code, organizing knowledge, deploying, pricing, or orchestrating
— you follow the same 8 reasoning steps. This is what makes a 5-word user input
produce professional output: the 8F pipeline does the work the user can't.

## Detection

ANY task activates 8F. Not just "build" — also research, analyze, write, plan,
deploy, price, orchestrate. If a nucleus receives work, 8F runs.

## The 8 Functions (execute in sequence, show evidence)

### F1 CONSTRAIN
```
Read: .cex/kinds_meta.json → resolve kind
Read: P{xx}/_schema.yaml → load schema
Output: "F1: kind={kind}, pillar={pillar}, max_bytes={max}, naming={pattern}"
```
> ACR: if the resolved kind has an `autonomy` block, the dispatch preflight
> auto-resolves its prerequisites into the handoff (`## Prerequisites (auto-resolved
> by ACR)`) -- see `.claude/rules/n07-orchestrator.md` + `.cex/capability_policy.json`.

### F2 BECOME
```
Read: archetypes/builders/{kind}-builder/bld_model_{kind}.md
Read: archetypes/builders/{kind}-builder/bld_prompt_{kind}.md
Output: "F2: Builder loaded ({N} ISOs, 12-pillar). Identity: {role}"
```

### F3 INJECT
```
Read: P01_knowledge/library/kind/kc_{kind}.md
Search: examples/ and compiled/ for similar artifacts
Read: any relevant domain KCs
Output: "F3: Injected {N} knowledge sources. Template-First match: {score}%"
```

### F3b PERSIST (sub-step, optional)
```
After assembling context, declare what new knowledge should be persisted:
- New entities discovered -> entity_memory
- Updated facts -> knowledge_card update
- Session learnings -> learning_record
Output: "F3b: Persist {N} items (entities: {n1}, facts: {n2}, learnings: {n3})"
```

### F3c GROUND (sub-step, when sources cited)
```
For each injected source, record provenance:
- Source path/URL
- Retrieval confidence score
- Freshness (last updated timestamp)
Output: "F3c: Grounded {N} sources. Avg confidence: {X}%"
```

### F4 REASON
```
Plan: sections, approach, references, estimated density
Apply: Construction Triad (Template-First if match >= 60%)
Output: "F4: Plan — {N} sections, approach: {template|hybrid|fresh}"
```

### F5 CALL
```
List: available tools (compile, doctor, index, signal)
Scan: existing similar artifacts for reuse
Output: "F5: Tools ready. {N} similar artifacts found."
```

### F6 PRODUCE
```
Generate: complete artifact with frontmatter + body
Follow: builder instructions from F2
Apply: density target >= 0.85
Output: "F6: Draft generated ({bytes} bytes, {sections} sections)"
```

### F7 GOVERN
```
Validate: H01-H06 universal gates + kind-specific gates from bld_eval ISO
  Universal: H01 frontmatter parses, H02 id matches, H03 kind matches,
             H04 quality is null, H05 required fields, H06 body <= max_bytes
  Kind-specific: H07+ defined per-kind in archetypes/builders/{kind}-builder/bld_eval_{kind}.md
Check: 12LP (nucleus-level pillar completeness -- enforced by cex_doctor.py, not per-artifact)
Score: 5D dimensions (D1-D5 weighted)
Output: "F7: Score {X}/10. Gates: {pass}/{total}."
If FAIL: return to F6 (max 2 retries)
```

> **H02 status: TWO mechanisms, one LIVE (corrected by N07 keystone 2026-07-04 --
> the first draft of this note claimed H02 "never fired"; an adversarial judge
> REFUTED that by direct execution and N07 reproduced it).** H02's id_pattern has
> two supply lanes in `_tools/cex_8f_runner.py`: (1) the `_schema.yaml`
> `kinds.{kind}.id_pattern` key -- unpopulated for 0/316 kinds, genuinely dormant;
> (2) a LIVE extraction (the R-264 structurally-scoped `## ID Pattern`-section
> extractor, ~lines 551-559 as of 2026-07-07 -- successor to the original
> whole-body scan at ~503-511; two w7q verifiers flagged the old citation stale)
> that pulls the per-kind regex out of `bld_schema_{kind}.md` ISO prose
> (``Regex: `...` `` -- the label is REQUIRED: w7q proved an unlabeled bare
> pattern line extracts None, i.e. H02 silently dormant for that kind, the
> nucleus_def case cured 2026-07-07) -- this lane populates the real F1->F7
> path and the H02 gate FIRES today (live repro: `cex_8f_runner.py "create a benchmark ..."
> --dry-run` emits `! H02: id '' does not match pattern /^p07_bm_.../`).
> Distinct from `cex_doctor.py`'s "Name" column and `cex_wave_validator.py`'s
> `check_h02_id_pattern`, which validate builder ISO SCAFFOLDING filenames, not
> produced-artifact `id:` fields. OPERATIONAL CONSEQUENCE (inverted from the
> first draft): measured non-compliance vs the documented regexes is 9/27 (33%)
> `benchmark`, 9/18 (50%) `guardrail`, 6/11 (55%) `prompt_template` spot-check --
> so NEW 8F builds of these kinds risk real H02 failures TODAY whenever their id
> drifts from the ISO-prose pattern, and the existing corpora would fail a
> retroactive sweep. The dedicated id-rename sweep (register row R-263) is
> therefore load-bearing, not optional hygiene. See `docs/SPEC_R259_SCHEMA_
> PRACTICE_RECONCILIATION_2026_07_04.md` Sections 1+8 for the field audit.

### F7b LEARN (sub-step, optional)
```
After scoring, capture feedback signals:
- What patterns led to high/low scores -> reward_signal
- Which gates commonly fail -> regression_check
- Quality trends over time -> quality metrics
Output: "F7b: Learn {N} signals (rewards: {n1}, regressions: {n2})"
```

### F7c COUNCIL (sub-step, optional, opt-in)

Triggers (any one):
- Artifact frontmatter has `requires_council: true`
- CLI invoked with `--council` flag
- Within-model score >= 9.5 (sycophancy heuristic)

Invokes the `cross_provider_council` crew_template instance
(p12_ct_cross_provider_council). Each judge runs the same `scoring_rubric`
independently against a different LLM provider. Output: consensus_score
(mean of N) + divergence_score (stddev) + per-judge dissent rationales.

Block publication if `divergence_score > 0.3` (configurable). Surface dissent
rationales to the user -- do NOT auto-suppress lone outliers; they may be the
correct dissent.

Cost: N x token-budget where N = providers (default 3, premium 4). Budget
guardrail: artifact frontmatter `council_budget_tokens` overrides default.

```
Output: "F7c: consensus={score} divergence={d} dissent_count={n} -- {DECISION}"
```

### F8 COLLABORATE
```
Save: write .md file to correct pillar directory
Compile: python _tools/cex_compile.py {path}
Index: python _tools/cex_index.py (if available)
Commit: git add + git commit  (gitignore-aware -- see rule below)
Signal: python -c "from _tools.signal_writer import write_signal; write_signal('{nucleus}', 'complete', {score})"
Output: "F8: Saved {path}. Compiled. Committed. Signal sent."
```

> **Gitignore-aware commit (mandatory).** Before `git add`, the commit must be
> gitignore-aware: if the deliverable path is gitignored (intentionally
> ephemeral -- `.cex/runtime/`, `**/compiled/`, `_docs/`, `_reports/`), SKIP the
> commit -- the file stays on disk; the collector / N07 reads it directly. NEVER
> `git add -f` a gitignored deliverable (force-adding pollutes the tree with
> files meant to be ephemeral). Report `committed` honestly: "nothing to commit"
> is committed=False, never a false success. Tools use
> `_tools/cex_git_safe.safe_artifact_commit`.

## Mode A vs Mode B (Execution Modes)

The 8F pipeline runs in two modes, auto-detected from the model tier:

| Mode | Who runs F1-F8 | Model requirement | When |
|------|---------------|-------------------|------|
| **Mode A** (monolithic) | Single model runs F1 through F8 | full_8f tier (Opus, Sonnet) | Default for capable models |
| **Mode B** (decomposed) | Stage 1: Opus/Sonnet (F1-F4), Stage 2: cheap model (F6), Stage 3: tools (F7-F8) | f6_generation tier (Haiku, Gemini Flash) | Auto for cheap models |

### Mode A Flow (default)
One model executes the entire pipeline: F1 -> F2 -> F3 -> F4 -> F5 -> F6 -> F7 -> F8.

### Mode B Flow (decomposed)
Stage 1 (THINK): Opus/Sonnet runs F1-F4, writes a prompt_package to .cex/runtime/packages/.
Stage 2 (GENERATE): Cheap model reads the prompt_package, executes F6 PRODUCE only.
Stage 3 (VALIDATE): Tools run F7 GOVERN (structural_score) + F8 COLLABORATE (compile + commit + signal).

### Auto-detection
`cex_router_v2.get_mode(model)` reads `.cex/config/nucleus_models.yaml` tiers section.
CLI: `python _tools/cex_8f_runner.py "intent" --mode auto --model haiku` (auto-detects Mode B).
Override: `--mode A` or `--mode B` forces the mode regardless of model.

### prompt_package (Mode B artifact)
Template: `N00_genesis/P03_prompt/tpl_prompt_package.md`
Spec: `_docs/compiled/spec_8f_decompose.yaml`

## Output Format

Every build MUST show the 8F trace:

```
=== 8F PIPELINE ===
F1 CONSTRAIN: kind=agent, pillar=P02, max=5120B
F2 BECOME: agent-builder loaded (12 ISOs)
F3 INJECT: kc_agent.md + 2 examples. Match: 72%
F4 REASON: 4 sections, approach=template (adapt from match)
F5 CALL: compile+doctor+index ready. 3 similar found.
F6 PRODUCE: 3,200 bytes, 4 sections, density=0.88
F7 GOVERN: 9.0/10. Gates: 6/6 universal + kind-specific.
F8 COLLABORATE: saved P02/agent_x.md. Compiled. Committed.
===================
```

## Why 8F Matters (The Leverage Principle)

The user will ALWAYS have a knowledge gap. Their input will be vague, incomplete,
non-technical. CEX compensates by running 8F on every input:

```
User: "make me a landing page"  (5 words, zero spec)
                │
  F1 CONSTRAIN  │→ kind=landing_page, pillar=P05, schema loaded, constraints set
  F2 BECOME     │→ landing-page-builder loaded (12 ISOs), sin lens injected
  F3 INJECT     │→ 10 context sources: KC, examples, memory, brand, similar artifacts
  F4 REASON     │→ plan: 12 sections, mobile-first, Tailwind, conversion-optimized
  F5 CALL       │→ tools executed, references fetched, sub-agents if needed
  F6 PRODUCE    │→ complete HTML page (responsive, dark mode, SEO, a11y)
  F7 GOVERN     │→ quality gate: 7 HARD gates, retry if < 8.0
  F8 COLLABORATE│→ saved, compiled, committed, signaled
                │
                ▼
Output: production-ready landing page (5 words in → professional artifact out)
```

This IS the product. The 8F pipeline is the force multiplier that makes CEX
outperform raw LLM calls. Every nucleus uses it. Every time.

## 8F by Nucleus

8F is the SAME protocol — the content changes per domain.

### N07 Orchestrator — "/mission build CRM"
```
F1 CONSTRAIN → scope: what kind of CRM? what nuclei needed? what wave structure?
F2 BECOME    → Orchestrating Sloth lens: ruthless quality, precise dispatch
F3 INJECT    → load mission plans, decision manifest, signal history
F4 REASON    → plan: 3 waves, 5 nuclei, dependency graph
F5 CALL      → provider discovery, agent spawn validation, PID tracking
F6 PRODUCE   → write handoffs + mission plan + wave schedule
F7 GOVERN    → validate: all handoffs have frontmatter? all nuclei have boot scripts?
F8 COLLABORATE → dispatch grid, monitor signals, consolidate on completion
```

### N01 Intelligence — "research competitor pricing in EdTech"
```
F1 CONSTRAIN → kind=knowledge_card, pillar=P01, domain=edtech pricing
F2 BECOME    → Analytical Envy lens: insatiable data hunger
F3 INJECT    → load KCs on pricing, EdTech market, existing competitor intel
F4 REASON    → plan: 6 competitors, 3 pricing dimensions, source map
F5 CALL      → retriever finds existing pricing KCs, query discovers related builders
F6 PRODUCE   → structured intelligence brief with pricing tables + sources
F7 GOVERN    → validate: sources cited? data density >= 0.85? no speculation?
F8 COLLABORATE → save to N01_intelligence/, compile, signal N07
```

### N02 Marketing — "write ad copy for Black Friday campaign"
```
F1 CONSTRAIN → kind=prompt_template, pillar=P03, domain=ad copy
F2 BECOME    → Creative Lust lens: seductive, irresistible prose
F3 INJECT    → load brand voice, audience persona, past campaign KCs
F4 REASON    → plan: 3 ad variants (urgency, FOMO, value), A/B structure
F5 CALL      → brand config loaded, memory recalls past conversion data
F6 PRODUCE   → 3 ad copy variants with hooks, CTAs, and character limits
F7 GOVERN    → validate: brand voice match? CTA present? length within platform limits?
F8 COLLABORATE → save to N02_marketing/, compile, signal N07
```

### N06 Commercial — "design pricing tiers for SaaS product"
```
F1 CONSTRAIN → kind=content_monetization, pillar=P11, domain=SaaS pricing
F2 BECOME    → Strategic Greed lens: maximize every revenue stream
F3 INJECT    → load competitor pricing KC, market research, customer segments
F4 REASON    → plan: 3 tiers (free/pro/enterprise), feature gating, annual discount
F5 CALL      → retriever finds existing monetization artifacts, brand config loaded
F6 PRODUCE   → pricing model with tier table, feature matrix, revenue projections
F7 GOVERN    → validate: tiers differentiated? no cannibalization? margins positive?
F8 COLLABORATE → save to N06_commercial/, compile, signal N07
```

## Severity Matrix

| Severity | Doctor state | When | Action |
|----------|--------------|------|--------|
| BLOCKING | FAIL | Hard gate violated (frontmatter missing, schema invalid, density < min) | Halt build. No publication. |
| HIGH | FAIL | Quality below floor (8.0). Compile broken. Wikilink target missing. | Block + retry F6 once with feedback. |
| MEDIUM | WARN | Size > soft cap. Density 0.78-0.85. Missing related artifacts. | Log + proceed. Auto-improve in next /evolve cycle. |
| OBSERVATION | PASS (info) | Stylistic preference. Could be denser. | No action. Log for trend analysis. |
| OPTIONAL | (advisory) | Suggestion that doesn't affect quality score. | User decides. |

Mapping to existing tools: `cex_doctor.py` FAIL=BLOCKING/HIGH, WARN=MEDIUM, no-warn=OBSERVATION.

## Anti-Patterns (BLOCKED)

1. Processing a task without 8F trace — ANY task, not just builds
2. Skipping F7 validation
3. Saving without F8 (compile + commit + signal)
4. "I'll just do a quick..." — NO. Every task goes through 8F.
5. N07 dispatching without F1 (constraining scope) and F4 (planning approach)

## Related Artifacts

| Artifact | Relationship | Score |
|----------|-------------|-------|
| p01_kc_8f_pipeline | related | 0.33 |
| p06_td_cex_artifact_type_n03 | related | 0.33 |
| [[p01_faq_cex_common_questions]] | related | 0.31 |
| p03_sp_n03_creation_nucleus | related | 0.31 |
| kind-builder | related | 0.30 |
