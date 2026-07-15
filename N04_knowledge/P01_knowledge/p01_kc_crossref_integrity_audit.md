---
id: p01_kc_crossref_integrity_audit
kind: knowledge_card
pillar: P01
nucleus: N04
title: Cross-Reference Integrity Audit -- CEXAI Knowledge Base
version: 3.0.0
quality: null
tags:
  - stress_test
  - wikilinks
  - coverage_analysis
  - knowledge_gluttony
audit_date: 2026-04-28
audit_scope: all_nuclei
related:
  - bld_knowledge_card_nucleus_def
  - audit_self_review_n05
  - p12_ct_cex_full_grid
  - audit_self_review_n01
  - p07_bm_kind_gap_audit_m1
  - kc_orchestration_vocabulary
  - audit_self_review_n03
  - bld_architecture_default
  - p01_kc_cex_project_overview
when_to_use: "Load when working on Cross-Reference Integrity Audit -- CEXAI Knowledge Base in P01. Consult for how to act on this knowledge_card."
slots:
  query_context: "<the question this card is recalled to answer>"
  target_audience: "<who consumes the answer>"
---

# Cross-Reference Integrity Audit

## Executive Summary

The CEXAI knowledge base contains **6,661 eligible .md files** and **6,463 indexed artifact IDs** across 7 nuclei (N01-N07) and 12 pillars (P01-P12). Live wikilink resolution is **92.8%** (3,807 of 4,103 unique targets resolve), confirming strong linkage with 296 broken targets remaining. Real orphan count: **446 artifacts** receive zero incoming references -- 10x higher than v2.0 estimates, driven by template stubs and N01 atlas fragments. **N07 critically underdocumented** (3 KCs vs. 34 in N01). P02 Model and P08 Architecture are the thinnest pillars system-wide.

---

## Health Dashboard

| Nucleus | Domain | Artifacts (recursive) | KCs | KC % | Wikilink Status |
|---------|--------|-----------------------|-----|------|-----------------|
| N01 | Intelligence | 247 | 34 | 33.3% | STRONG |
| N02 | Marketing | 164 | 17 | 10.4% | ADEQUATE |
| N03 | Engineering | 203 | 8 | 3.9% | WEAK -- pattern gaps |
| N04 | Knowledge | 186 | 13 | 7.0% | ADEQUATE |
| N05 | Operations | 181 | 13 | 7.2% | ADEQUATE |
| N06 | Commercial | 181 | 14 | 7.7% | ADEQUATE |
| N07 | Orchestrator | 85 | 3 | 3.5% | CRITICAL -- underdocumented |
| **TOTAL** | -- | **1,247** | **102** | **8.2%** | **HEALTHY (92.8% resolution)** |

**Retriever index**: 6,261 documents, 32,216 vocabulary terms. Builder health: 301/301 PASS, 0 WARN, 0 FAIL. Compiled artifacts: 91 (7.3% of 1,247).

---

## Coverage Heatmap (Artifact Count: Pillar x Nucleus, Recursive)

| Pillar | N01 | N02 | N03 | N04 | N05 | N06 | N07 | Total |
|--------|-----|-----|-----|-----|-----|-----|-----|-------|
| P01 Knowledge | 85 | 28 | 17 | 37 | 20 | 29 | 10 | **226** |
| P02 Model | 6 | 6 | 10 | 8 | 6 | 6 | 6 | **48** |
| P03 Prompt | 11 | 13 | 9 | 8 | 8 | 11 | 3 | **63** |
| P04 Tools | 14 | 8 | 22 | 9 | 9 | 5 | 2 | **69** |
| P05 Output | 31 | 31 | 17 | 26 | 30 | 36 | 3 | **174** |
| P06 Schema | 12 | 12 | 19 | 15 | 13 | 12 | 5 | **88** |
| P07 Evaluation | 27 | 14 | 26 | 16 | 21 | 16 | 2 | **122** |
| P08 Architecture | 4 | 4 | 16 | 9 | 8 | 8 | 4 | **53** |
| P09 Config | 6 | 7 | 12 | 6 | 19 | 6 | 6 | **62** |
| P10 Memory | 15 | 7 | 7 | 19 | 9 | 10 | 13 | **80** |
| P11 Feedback | 11 | 6 | 10 | 8 | 13 | 14 | 4 | **66** |
| P12 Orchestration | 25 | 28 | 38 | 25 | 25 | 28 | 27 | **196** |
| **Total** | **247** | **164** | **203** | **186** | **181** | **181** | **85** | **1,247** |

**Key observations:**
- **P01 Knowledge** densest (226 artifacts) -- led by N01 atlas subdirectory (85 files incl. atom fragments)
- **P12 Orchestration** second (196) -- well-distributed across all nuclei
- **P05 Output** strong (174) -- N06 Commercial leads with 36 output templates
- **P02 Model** weakest (48) -- 6 per nucleus average; structural minimum only
- **P08 Architecture** thin (53) -- N01 and N02 have only 4 each; agent cards + nucleus defs only
- **N07 only nucleus below 10 in P01** -- 10 KCs (includes rules/, not pure library)
- **N03 engineering weak in P01** (17) but strong in P04 Tools (22) and P07 Eval (26)

---

## Wikilink Integrity (Live Audit)

| Metric | Value | Assessment |
|--------|-------|------------|
| Eligible .md files | 6,661 | Full corpus |
| Artifact IDs indexed | 6,463 | 97.0% of files have frontmatter id |
| Total wikilink references | 13,332 | 11.0 refs per file avg |
| Unique wikilink targets | 4,103 | Rich cross-referencing |
| Resolved targets | 3,807 | 92.8% resolution rate |
| Broken targets | 296 | 7.2% unresolved |
| Files containing wikilinks | 1,201 | 18.0% of corpus |
| Compiled .yaml artifacts | 91 | 7.3% of nuclei artifacts |

**Wikilink resolution: 92.8%** -- up from estimated 87-93% in v2.0. Strong signal: most [[]] references resolve correctly via frontmatter id matching.

---

## Broken Links -- Top 20 (Live Data)

| Rank | Target | Refs | Source File | Root Cause |
|------|--------|------|-------------|------------|
| 1 | CLAUDE | 12 | N00_genesis/P01_knowledge/README.md | Refers to CLAUDE.md -- no id field in rules file |
| 2 | [\[LLM_PIPELINE\]] | 12 | N00_genesis/P01_knowledge/README.md | Placeholder ID never instantiated as artifact |
| 3 | [\[CEX_ARCHITECTURE_MAP\]] | 12 | N00_genesis/P01_knowledge/README.md | Planned artifact not yet created |
| 4 | [\[N00_genesis\]] | 12 | N00_genesis/P01_knowledge/README.md | Directory name, not artifact id |
| 5 | n07-orchestrator | 11 | N00_genesis/P02_model/nucleus_def_n00.md | Rules file lacks id field |
| 6 | [\[P01_knowledge\]] | 8 | N00_genesis/README.md | Pillar directory name, not artifact id |
| 7 | [\[P02_model\]] | 8 | N00_genesis/README.md | Pillar directory name, not artifact id |
| 8 | [\[P03_prompt\]] | 8 | N00_genesis/README.md | Pillar directory name, not artifact id |
| 9 | [\[P04_tools\]] | 8 | N00_genesis/README.md | Pillar directory name, not artifact id |
| 10 | [\[P05_output\]] | 8 | N00_genesis/README.md | Pillar directory name, not artifact id |
| 11 | [\[P06_schema\]] | 8 | N00_genesis/README.md | Pillar directory name, not artifact id |
| 12 | [\[P07_evals\]] | 8 | N00_genesis/README.md | Pillar directory name, not artifact id |
| 13 | [\[P08_architecture\]] | 8 | N00_genesis/README.md | Pillar directory name, not artifact id |
| 14 | [\[P09_config\]] | 8 | N00_genesis/README.md | Pillar directory name, not artifact id |
| 15 | [\[P10_memory\]] | 8 | N00_genesis/README.md | Pillar directory name, not artifact id |
| 16 | [\[P11_feedback\]] | 8 | N00_genesis/README.md | Pillar directory name, not artifact id |
| 17 | [\[P12_orchestration\]] | 8 | N00_genesis/README.md | Pillar directory name, not artifact id |
| 18 | [\[doctor\]] | 7 | N04_knowledge/P11_feedback/regression_check_n04.md | cex_doctor tool -- no artifact id |
| 19 | [\[skill\]] | 6 | N04_knowledge/P01_knowledge/p01_gl_taxonomy.md | Generic term, no matching artifact |
| 20 | 8f-reasoning | 4 | N04_knowledge/P01_knowledge/kc_autonomous_orchestration.md | File exists (.claude/rules/8f-reasoning.md) but no frontmatter id |

**Pattern analysis of 296 broken targets:**
- **Directory-as-link** (P01_knowledge, N00_genesis etc.): ~80 refs -- systematic in README files
- **Rules files without id field** (n07-orchestrator, 8f-reasoning): ~15 refs -- fixable by adding id to frontmatter
- **Planned but uncreated artifacts** (LLM_PIPELINE, CEX_ARCHITECTURE_MAP): ~60 refs -- genuine gaps
- **Tool/command references** (doctor, skill): ~50 refs -- conceptual links, not artifact links

---

## Spot Verification (F7 GOVERN)

Three claimed broken links verified by file search:

1. **8f-reasoning** -- CONFIRMED BROKEN. File `.claude/rules/8f-reasoning.md` EXISTS but has no `id:` field in frontmatter. Fix: add `id: 8f-reasoning` to the file's YAML header.

2. **[\[doctor\]]** -- CONFIRMED BROKEN. No `.md` file found with `id: doctor`. The cex_doctor.py tool is referenced conceptually, not as an artifact. Fix: either create `kc_cex_doctor.md` with this id, or change references to `[\[kc_cex_doctor\]]`.

3. **[\[research_then_build\]]** -- CONFIRMED BROKEN. No file with this id exists anywhere in the repo. Referenced in `N04_knowledge/rules/n04-knowledge.md`. Fix: create the artifact or remove the wikilink.

---

## Orphan Artifacts (Zero Incoming References)

**Total orphans: 446** (vs. estimated 40-60 in v2.0 -- 10x higher than estimated)

**Category breakdown:**

| Category | Estimated Count | Example |
|----------|----------------|---------|
| Template stubs (tpl_*.md with placeholder ids) | ~120 | `"p01_fse_{{TOPIC_SLUG}}"` |
| N01 atlas fragments (atom_*.md) | ~80 | `atom_14_coze_xagent` |
| Action prompts / output files never linked | ~60 | `action_prompt_upsell` |
| Agent / nucleus artifacts not yet cross-linked | ~40 | `agent_n04` |
| KC files not listed in any index | ~50 | `kc_nixpacks_buildpacks` |
| API references and specs | ~20 | `api_reference_stripe` |
| Example artifacts (examples/ subdir) | ~76 | varied |

**Root cause**: Template files use placeholder ids (e.g. `"p01_fse_{{TOPIC_SLUG}}"`) that can never be referenced by wikilinks. Atlas atom files are standalone research fragments not yet integrated into KCs. These are not defects -- they are pre-integration material.

**Actionable orphans** (real artifacts with no incoming refs): ~200 out of 446.

---

## Recommendations (Priority Order)

### Wave 1 -- BLOCKING (immediate)

1. **Add id fields to .claude/rules/*.md files** (8f-reasoning, n07-orchestrator, composable-crew, etc.)
   - Impact: Fixes ~15 broken refs at zero content cost
   - Effort: 10 minutes -- add 1 YAML line per file

2. **Create [\[CEX_ARCHITECTURE_MAP\]]** knowledge_card
   - Referenced 12x from N00_genesis README; never created
   - Scope: overview diagram of 8 nuclei x 12 pillars x 125 kinds
   - Owner: N04, kind=knowledge_card, pillar=P01

3. **Create [\[LLM_PIPELINE\]]** knowledge_card
   - Referenced 12x; describes how LLM inference flows through CEX stack
   - Owner: N03 or N04, pillar=P01

### Wave 2 -- HIGH (this week)

4. **N07 vocabulary KC** (still missing from v2.0 recommendation)
   - `N07_admin/P01_knowledge/kc_orchestration_vocabulary.md` -- 0 KC for dispatch/wave/topology terms
   - 3 KCs total in N07 is the system's most critical documentation gap

5. **Add frontmatter ids to N00_genesis/README.md pillar links**
   - 12 broken refs all from one file; change [\[P01_knowledge\]] to [\[pillar_p01_knowledge_overview\]] or similar

6. **Link N01 atlas atoms into KCs**
   - 80+ atom fragments are orphaned; each should be cited in at least 1 KC
   - Creates knowledge graph from raw research material

### Wave 3 -- MEDIUM (next 2 weeks)

7. **Fix [\[doctor\]] and [\[skill\]]**: create `kc_cex_doctor.md` and `kc_cex_skills.md` or update references
8. **N03 engineering patterns KC**: factory, builder, observer, adapter patterns -- 8 KCs total is weakest engineering documentation
9. **Deepend P08 Architecture** (53 total, weakest functional pillar after P02): N01 and N02 have only 4 each

### Wave 4 -- ONGOING

10. **Orphan reduction**: target 100 orphan -> linked per sprint; run `cex_retriever.py --find-orphans`
11. **Compile sync**: 91/1,247 compiled (7.3%); target 15%+ for semantic query coverage
12. **Monthly audit**: re-run this stress test after each major grid wave to track resolution rate

---

## Structural Integrity Summary

| Gate | Status | Notes |
|------|--------|-------|
| Builder health (cex_doctor) | PASS (301/301) | Zero failures, zero warnings |
| YAML frontmatter validity | PASS | All nuclei artifacts valid |
| Wikilink resolution | PASS (92.8%) | Strong; 3,807 / 4,103 resolve |
| Broken link count | WARN (296) | 7.2%; fixable; top 20 above |
| Orphan artifact count | WARN (446) | 10x estimated; mostly templates+atlas |
| Compiled artifact sync | WARN (7.3%) | 91/1,247; low but not blocking |
| Retriever index coverage | PASS (94.0%) | 6,261/6,661 indexed |
| Fractal compliance (12P dirs per N) | PASS | All nuclei have 12 pillar dirs |
| N07 KC depth | FAIL (3 KCs) | Critical documentation gap |

---


### How to use

```text
You are the consuming agent that acts on this knowledge_card under F3 INJECT.
- Resolve the open slots (query_context, target_audience) from the caller request.
- Honor every constraint and field contract declared above.
- Emit the result in the shape this knowledge_card defines; never improvise the schema.
```

### Procedure

```text
1. Load this artifact and read its contract under F3 INJECT.
2. Bind query_context and target_audience from the incoming request.
3. Validate the inputs against the constraints declared above.
4. Execute the knowledge_card behavior; resolve each open slot at act-time.
5. Verify the output shape, then signal completion to the orchestrator.
```

## Related Artifacts

| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[bld_knowledge_nucleus_def]] | sibling | 0.31 |
| audit_self_review_n05 | downstream | 0.31 |
| p12_ct_cex_full_grid | downstream | 0.30 |
| audit_self_review_n01 | downstream | 0.30 |
| p07_bm_kind_gap_audit_m1 | downstream | 0.29 |
| [[kc_orchestration_vocabulary]] | sibling | 0.29 |
| audit_self_review_n03 | downstream | 0.29 |
| [[bld_architecture_default]] | downstream | 0.28 |
| p01_kc_cex_project_overview | sibling | 0.28 |
