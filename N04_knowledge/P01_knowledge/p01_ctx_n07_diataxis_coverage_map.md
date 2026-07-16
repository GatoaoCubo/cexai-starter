---
id: p01_ctx_n07_diataxis_coverage_map
kind: context_doc
8f: F3_inject
pillar: P01
version: 1.0.0
created: "2026-06-14"
updated: "2026-06-14"
author: n04_knowledge
domain: "N07 orchestration documentation"
scope: "Diataxis quadrant coverage analysis of N07 orchestration doc corpus -- gaps and prescriptions."
quality: null
tags: [context_doc, diataxis, coverage-map, N07, orchestration, P01]
source_attribution: "Pattern applied: p08_pat_diataxis_for_cex. Source methodology: gstack (garrytan/gstack, MIT, commit 14fc0866d9)."
---

> Coverage map via p08_pat_diataxis_for_cex. Attribution: gstack (garrytan/gstack, MIT, 14fc0866d9).

## Scope

IN: `.claude/rules/` (n07-orchestrator, 8f-reasoning, guided-decisions, dispatch-depth, composable-crew, system-overview, n07-input-transmutation, raci-matrix, ubiquitous-language) + `N07_admin/P01_knowledge/kc_orchestration_vocabulary.md` + `N07_admin/P12_orchestration/auto/wf_auto_*.md`.
OUT: `_tools/`, `.cex/runtime/`, schemas, handoffs, boot scripts.

## Coverage Map

| Doc | Kind | Quadrant |
|-----|------|----------|
| 8f-reasoning.md | context_doc | Explanation |
| n07-orchestrator.md | context_doc | How-to + Reference |
| system-overview.md | context_doc | Explanation + Reference |
| guided-decisions.md | context_doc | How-to |
| dispatch-depth.md | context_doc | Reference |
| composable-crew.md | context_doc | Explanation + How-to |
| n07-input-transmutation.md | context_doc | Reference |
| raci-matrix.md | context_doc | Reference |
| ubiquitous-language.md | context_doc | Explanation |
| kc_orchestration_vocabulary.md | knowledge_card | Reference |
| wf_auto_*.md (12 files) | workflow | Reference |

## Quadrant Tally

| Quadrant | Count | Status |
|----------|-------|--------|
| Tutorial | 0 | **MISSING** |
| How-to | 3 | THIN |
| Reference | 7 | COVERED |
| Explanation | 4 | COVERED |

## Gaps (Actionable)

| Gap | Quadrant | Kind to Create |
|-----|----------|---------------|
| No first-session walkthrough | Tutorial | `quickstart_guide` -- end-to-end `/mission` dispatch |
| No learn-by-doing dispatch guide | Tutorial | `course_module` -- 8F dispatch with worked example |
| Grid + worktree merge undocumented | How-to | `integration_guide` -- grid with `-w` and merge-all flow |

## Assumptions

- `workflow` artifacts count as Reference (lookup sequences, not tutorials).
- A doc spanning 2 quadrants is counted in both; a gap requires 0 in that quadrant.
- Corpus reflects `.claude/rules/` at 2026-06-14; map decays as rules evolve.
