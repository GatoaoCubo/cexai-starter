---
id: p01_ctx_cex_diataxis_coverage_map
kind: context_doc
8f: F3_inject
pillar: P01
nucleus: n04
version: 1.0.0
created: "2026-06-14"
updated: "2026-06-14"
author: n04_knowledge
domain: "CEX-wide documentation"
scope: "Diataxis quadrant coverage sweep across all 8 CEX nuclei (N00-N07), the N05 cybersec vertical, and _docs. Produces a counted coverage matrix and a prioritized doc-gap backlog."
quality: null
tags: [context_doc, diataxis, coverage-map, documentation, gap-analysis, P01, N04, STRESS3]
source_attribution: "Pattern applied: p08_pat_diataxis_for_cex. Framework: Diataxis (c) Divio AG, CC-BY (https://diataxis.fr). Methodology: gstack (garrytan/gstack, MIT, commit 14fc0866d9). Both adapted to CEX taxonomy."
keywords: [diataxis, coverage-map, tutorial, how-to, reference, explanation, gap-backlog, documentation-debt]
density_score: null
related:
  - p01_ctx_n07_diataxis_coverage_map
---

> Coverage map via p08_pat_diataxis_for_cex. Framework: Diataxis (c) Divio AG, CC-BY. Methodology: gstack (garrytan/gstack, MIT, 14fc0866d9).

## Scope

**IN scope** (doc-bearing domains enumerated):
- Nucleus source directories: `N00_genesis/`, `N01_intelligence/`, `N02_marketing/`, `N03_engineering/`, `N04_knowledge/`, `N05_operations/` (general + cybersec sub-vertical), `N06_commercial/`, `N07_admin/` + `.claude/rules/` (N07 untyped rule corpus)
- `_docs/` (specs, research, archive)

**OUT of scope**: `.cex/runtime/`, `.cex/cache/`, `.cex/experiments/`, `archetypes/builders/` (builder ISOs, not end-user docs), `compiled/` subdirs (generated YAML mirrors), `examples/` subdirs (builder training data).

**Doc kinds classified** (per p08_pat_diataxis_for_cex kind->quadrant map):

| Quadrant | Kinds |
|----------|-------|
| Tutorial | `course_module`, `quickstart_guide` |
| How-to | `integration_guide`, `context_doc` |
| Reference | `api_reference`, `glossary_entry`, `knowledge_card` |
| Explanation | `mental_model`, `faq_entry` |

**Enumeration method**: grep `^kind: <doc-kind>` on all `.md` files in scope; count per domain; exclude `compiled/` and `examples/` subdirs. Counts are artifact counts, not depth scores.

---

## Coverage Matrix

Counts = typed artifacts with `kind:` frontmatter matching the Diataxis kind map.
Status: **MISSING** = 0, **THIN** = 1-2, **ADEQUATE** = 3-5, **COVERED** = 6-19, **SATURATED** = 20+.

| Domain | Tutorial | How-to | Reference | Explanation | Total |
|--------|:--------:|:------:|:---------:|:-----------:|------:|
| N00 Genesis | 0 MISSING | 12 COVERED | 766 SATURATED | 1 THIN | 779 |
| N01 Intelligence | 0 MISSING | 4 THIN | 121 SATURATED | 0 MISSING | 125 |
| N02 Marketing | 0 MISSING | 6 COVERED | 30 ADEQUATE | 0 MISSING | 36 |
| N03 Engineering | 0 MISSING | 10 COVERED | 30 ADEQUATE | 1 THIN | 41 |
| N04 Knowledge | 3 THIN | 9 COVERED | 71 COVERED | 3 THIN | 86 |
| N05 Ops (general) | 0 MISSING | 9 COVERED | 34 COVERED | 5 ADEQUATE | 48 |
| N05 Cybersec vertical | 0 MISSING | 0 MISSING | 84 SATURATED | 77 SATURATED | 161 |
| N06 Commercial | 0 MISSING | 7 COVERED | 29 ADEQUATE | 2 THIN | 38 |
| N07 Typed artifacts | 0 MISSING | 1 THIN | 5 THIN | 0 MISSING | 6 |
| _docs | 0 MISSING | 0 MISSING | 2 THIN | 0 MISSING | 2 |

**N07 note**: `.claude/rules/` holds 9 functionally important rule docs (8f-reasoning, n07-orchestrator, system-overview, guided-decisions, dispatch-depth, composable-crew, n07-input-transmutation, raci-matrix, ubiquitous-language) that serve as Explanation + How-to + Reference. However, NONE carry `kind:` frontmatter -- they are UNTYPED. A deeper per-file mapping (see [[p01_ctx_n07_diataxis_coverage_map]]) shows N07 rules cover How-to=3 and Explanation=4 quadrant slots functionally; typed artifact count remains 0/1/5/0.

---

## Gap Analysis by Domain

### N00 Genesis -- Reference-only library
- Reference is SATURATED (766 = 765 KCs + 1 glossary). The N00 archetype is a knowledge factory.
- Tutorial MISSING: no "new nucleus bootstrap" walkthrough exists as a typed Tutorial.
- Explanation THIN (1 mental_model). The `new-nucleus-bootstrap.md` rule fills this functionally but is untyped.
- How-to COVERED but concentrated: 6 context_docs + 3 integration_guides. Adequate for contributors.
- **Verdict**: Not critical -- N00 is a library, not an operator interface. But the Tutorial gap blocks new vertical bootstrappers.

### N01 Intelligence -- Research-heavy, zero Explanation
- Reference SATURATED (120 KCs + 1 api_ref). Research artifacts well-indexed.
- Tutorial MISSING: no "run your first research pipeline" guide.
- Explanation MISSING: no mental_model explaining WHY the Analytical Envy lens works, or how N01 reasons through N00 sources. Practitioners operate N01 without a conceptual map.
- How-to THIN (4 context_docs). Given N01's complexity (carteiro routing, reuse-gate, RAG pipeline), 4 is insufficient.
- **Verdict**: HIGH priority. Tutorial + Explanation gaps leave N01 operators guessing.

### N02 Marketing -- Creative nucleus with no Explanation
- Reference ADEQUATE (29 KCs + 1 api_ref). Sufficient for lookup.
- How-to COVERED (6 context_docs). Campaign workflow covered.
- Tutorial MISSING: no "first marketing campaign" tutorial.
- Explanation MISSING: no mental_model for the Creative Lust lens or brand-voice first principles.
- **Verdict**: MEDIUM. Explanation gap is real; practitioners copy-and-modify without understanding the underlying sin lens.

### N03 Engineering -- Most-built nucleus, zero Tutorial
- How-to COVERED (7 context_docs + 3 integration_guides). Build workflows are documented.
- Reference ADEQUATE (29 KCs + 1 api_ref). OK.
- Tutorial MISSING: despite being the most-invoked nucleus, no "first artifact build" tutorial exists under N03. Operators rely on the N04 quickstart_guides and .claude/rules/ indirectly.
- Explanation THIN (1 mental_model). The Construction Triad (template-first) and Inventive Pride lens lack dedicated explanation artifacts.
- **Verdict**: HIGH priority. N03 is the highest-traffic nucleus; Tutorial gap is the most impactful documentation debt in the repo.

### N04 Knowledge -- Most balanced, still thin
- Only domain with all 4 quadrants represented.
- Tutorial THIN (2 quickstart_guides + 1 course_module spec): the 2 quickstart_guides serve CEX operators generally; the course_module is a spec, not a tutorial. Functional Tutorial coverage exists but is not abundant.
- Explanation THIN (1 mental_model + 2 faq_entries). RAG concepts and the Knowledge Gluttony lens could benefit from additional mental_models.
- **Verdict**: LOW gap priority. N04 is the healthiest domain; incremental improvement only.

### N05 Operations (general) -- Adequate but thin Explanation
- How-to COVERED (8 context_docs + 1 integration_guide). Ops workflows documented.
- Reference COVERED. Adequate.
- Explanation THIN (5 mental_models in general ops portion -- the 77 cybersec mental_models are vertical-specific, not general ops).
- Tutorial MISSING: no "first security audit" or "first cex_doctor run" tutorial.
- **Verdict**: MEDIUM. Tutorial gap and general Explanation thinness are the issues.

### N05 Cybersec Vertical -- Explanation-rich, How-to MISSING
- Explanation SATURATED (77 mental_models, one per skill). Strongest quadrant in the entire repo.
- Reference SATURATED (77 KCs + 7 glossary).
- Tutorial MISSING: no "run your first CEX cybersec assessment" tutorial. The vertical is deep but lacks an entry point.
- How-to MISSING: no integration_guide or context_doc teaching practitioners HOW to apply the 80 skills to real targets. Knowledge exists; actionable procedures are absent.
- **Verdict**: HIGH priority for How-to. The cybersec vertical inverts the systemic pattern: it has deep Explanation but zero How-to. A practitioner can understand each skill but has no procedural path from skill to live assessment.

### N06 Commercial -- Functional but conceptually thin
- How-to COVERED (7 context_docs). Commercial workflows present.
- Reference ADEQUATE. OK.
- Tutorial MISSING: no "first pricing configuration" or "first monetization setup" guide.
- Explanation THIN (2 mental_models). Strategic Greed lens and monetization-first thinking are undocumented conceptually.
- **Verdict**: MEDIUM. Same pattern as N02 (Creative Lust): the sin lens is the missing layer.

### N07 Orchestrator -- Most critical doc gap in the repo
- Typed artifacts: How-to THIN (1 context_doc), Reference THIN (5 KCs), Tutorial + Explanation MISSING.
- Untyped `.claude/rules/` covers How-to + Explanation functionally (see [[p01_ctx_n07_diataxis_coverage_map]]) but these docs are invisible to the typed taxonomy and do not serve as indexed artifacts.
- Tutorial MISSING as typed artifact: the single most used nucleus has no step-by-step Tutorial to guide a new operator through their first `/mission` dispatch. New operators read dense rule files with no guided path.
- Explanation MISSING as typed artifact: no `mental_model` artifact explaining WHY N07 never builds, or WHY 8F is mandatory, or HOW orchestration mindset differs from solo building.
- **Verdict**: CRITICAL. N07 is the entry point for ALL operators. Its documentation gap is the largest mismatch between importance and coverage.

### _docs -- Untyped archive
- Only 2 typed artifacts (knowledge_cards). The remaining ~40 files are specs, research docs, benchmarks, and archive material. These are not doc-kind artifacts; they are work product.
- Tutorial, How-to, Explanation: all MISSING (not applicable -- _docs is not a user-facing doc domain).
- **Verdict**: Not a documentation gap per se; _docs is a working-file archive. A contributor quickstart_guide or CEX setup integration_guide should live in N00 or N04, not _docs.

---

## Prioritized Doc-Gap Backlog

Scoring: **Impact** (1-3, audience size) x **Urgency** (1-3, how blocking) / **Effort** (1-3, lower effort = less work). Higher score = higher priority.

### P1 -- CRITICAL (Score >= 7)

| # | Domain | Quadrant | Kind to Create | Title (suggested) | Score | Rationale |
|---|--------|----------|----------------|-------------------|-------|-----------|
| 1 | N07 | Tutorial | `quickstart_guide` | "First /mission Dispatch in 20 Minutes" | 9 | ALL operators enter via N07; zero typed Tutorial exists; highest leverage doc in the repo |
| 2 | N03 | Tutorial | `quickstart_guide` | "First Artifact Build via 8F in 15 Minutes" | 9 | Highest-traffic nucleus; operators reverse-engineer the pipeline from rule files |
| 3 | N07 | Explanation | `mental_model` | "Why N07 Never Builds -- Orchestration vs. Creation" | 8 | The N07 prohibition on building is the most-violated rule; an Explanation artifact reduces mis-dispatch |
| 4 | N05 Cybersec | How-to | `integration_guide` | "From Skill to Live Assessment -- Cybersec Workflow" | 7 | 80 skills with zero actionable procedure; Explanation SATURATED but How-to MISSING |

### P2 -- HIGH (Score 5-6)

| # | Domain | Quadrant | Kind to Create | Title (suggested) | Score | Rationale |
|---|--------|----------|----------------|-------------------|-------|-----------|
| 5 | N01 | Tutorial | `quickstart_guide` | "First Research Pipeline -- N01 in 20 Minutes" | 6 | Complex nucleus (carteiro, reuse-gate, RAG); Tutorial MISSING; analysts blocked |
| 6 | N01 | Explanation | `mental_model` | "Analytical Envy -- How N01 Reasons Through Sources" | 6 | Practitioners operate N01 without understanding the lens; Explanation MISSING |
| 7 | N07 | How-to | `integration_guide` | "Grid + Worktree Dispatch and Merge-All Workflow" | 6 | Confirmed gap from [[p01_ctx_n07_diataxis_coverage_map]]; grid `-w` merge is undocumented as typed artifact |
| 8 | N07 | Governance | Type the `.claude/rules/` docs | Add `kind:` frontmatter to 9 rule files | 5 | Makes functionally existing Explanation + How-to docs searchable and indexable; zero new content needed |

### P3 -- MEDIUM (Score 3-4)

| # | Domain | Quadrant | Kind to Create | Title (suggested) | Score | Rationale |
|---|--------|----------|----------------|-------------------|-------|-----------|
| 9 | N03 | Explanation | `mental_model` | "Construction Triad -- Template-First for Builders" | 4 | Inventive Pride lens undocumented; the triad is the key N03 concept |
| 10 | N02 | Tutorial | `quickstart_guide` | "First Marketing Campaign with N02" | 4 | Creative Lust nucleus; operators lack a starting point |
| 11 | N02 | Explanation | `mental_model` | "Creative Lust -- Brand Voice as the Sin Lens" | 4 | The sin lens explains N02's bias; currently absent from typed corpus |
| 12 | N06 | Tutorial | `quickstart_guide` | "First Pricing Configuration with N06" | 4 | Strategic Greed nucleus; operators lack a starting point |
| 13 | N06 | Explanation | `mental_model` | "Strategic Greed -- Monetization-First Thinking" | 3 | THIN (2 mental_models); Strategic Greed conceptual underpinning absent |
| 14 | N05 Cybersec | Tutorial | `quickstart_guide` | "First CEX Security Assessment -- From Zero to Report" | 3 | 80 skills, 0 tutorials; entry point missing for the entire vertical |
| 15 | N00 | Tutorial | `quickstart_guide` | "Bootstrap a New Nucleus (N08+) in 30 Minutes" | 3 | `new-nucleus-bootstrap.md` rule is untyped; Tutorial would serve vertical authors |

### P4 -- LOW (Score 1-2)

| # | Domain | Quadrant | Kind to Create | Title (suggested) | Score | Rationale |
|---|--------|----------|----------------|-------------------|-------|-----------|
| 16 | N04 | Tutorial | `course_module` | "RAG Pipeline Build -- End-to-End Tutorial" | 2 | THIN; N04 already has 2 quickstart_guides; a course_module adds depth, not breadth |
| 17 | N00 | Explanation | `mental_model` | "The Fractal: Why 12 Pillars x 8 Nuclei Works" | 2 | N00 Explanation THIN; fractal concept is core but largely implied |

---

## Summary: Systemic Patterns

1. **Tutorial quadrant is the universal gap**: 7 of 9 domains have 0 Tutorial artifacts. This is the highest-leverage investment across the entire repo. P1+P2 gaps are dominated by Tutorial prescriptions.

2. **Reference is oversaturated**: The CEX knowledge factory produces KCs prolifically. N00 alone has 766 Reference artifacts vs. 0 Tutorial. The doc strategy is heavily skewed toward lookup over learning.

3. **Explanation tracks sin-lens understanding**: Domains with Explanation artifacts have them because the sin lens is a conceptual concept worth explaining (N05 cybersec: 77 mental_models). Domains without Explanation leave practitioners using the nucleus without understanding WHY it works the way it does.

4. **N07 is the critical outlier**: The most-used, most-important nucleus has the thinnest typed doc coverage (6 total artifacts). Its working documentation lives in `.claude/rules/` (untyped) -- invisible to the artifact taxonomy.

5. **Cybersec vertical is inverted**: Explanation SATURATED + Reference SATURATED, but How-to MISSING + Tutorial MISSING. The skills exist; the procedures connecting skills to practitioner action do not.

---

## Observations (Non-Gap Notes)

- **`.claude/rules/` governance debt**: 9 rule files serve as N07's actual How-to + Explanation corpus but carry no `kind:` frontmatter. They are functionally ADEQUATE (as shown in [[p01_ctx_n07_diataxis_coverage_map]]) but structurally invisible to the typed artifact taxonomy. Adding `kind: context_doc` (or `kind: mental_model`) frontmatter to each is a low-effort, zero-content governance fix (Backlog #8).
- **N04 as the model**: N04 is the only domain with all 4 quadrants represented. It serves as the reference implementation for balanced documentation coverage.
- **Coverage decays with domain activity**: This map reflects the corpus at 2026-06-14. N05 cybersec coverage will grow as skills are added; N07 coverage decays if rule files proliferate without typed counterparts.
- **Thin does not mean shallow**: `THIN` (1-2 artifacts) can mask high-quality content. Depth assessment per artifact is out of scope for this coverage map; count is a floor metric, not a quality metric.

---

## Assumptions

- Artifact counts include only `.md` files with `kind:` frontmatter matching the 9 doc kinds in scope.
- `examples/` and `compiled/` subdirs are excluded (builder training data, not corpus docs).
- `.cex/runtime/`, `.cex/cache/`, `.cex/experiments/` are excluded (operational state, not documentation).
- `kind: knowledge_card` is classified as Reference (primary). Conceptual KCs could be Explanation; the map does not sub-classify by KC content.
- One artifact counts once (in its primary quadrant); dual-quadrant artifacts are noted in the Gap Analysis text but not double-counted in the matrix.
- `.claude/rules/` files count as ZERO typed artifacts; their functional contribution is noted but not tallied in the matrix.
- Counts reflect source directories; YAML compiled mirrors in `compiled/` are excluded (duplicates).
