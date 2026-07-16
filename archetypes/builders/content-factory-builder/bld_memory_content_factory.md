---
id: p10_lr_content-factory-builder
kind: learning_record
pillar: P10
version: 1.0.0
created: 2026-07-03
updated: 2026-07-03
author: n03_engineering
observation: "This kind's own name collides with two unrelated systems (a MoneyPrinterTurbo+Chatterbox short-social VIDEO package in cexai/cexai/content_factory/, and an N06 content_monetization spec). The triage evidence trail (docs/DECISION_BUILDERLESS_KINDS_2026_07_03.md) cited BOTH systems as SCAFFOLD evidence for this ONE kind -- reading only the summary table would have grounded this builder in the WRONG system's mechanics."
pattern: "Before grounding a builder in cited evidence, cross-check the kind's own `depends_on` in kinds_meta.json against each evidence bullet's actual module. This kind's depends_on=[social_publisher, supabase_data_layer] only matches `_tools/cex_content_factory.py` (the produce->review->publish trio) -- not the video package (which reuses workflow/tts_provider, per its own ADR titled 'ZERO new kinds')."
evidence: "docs/DECISION_BUILDERLESS_KINDS_2026_07_03.md Sec 2.3 lists 8 evidence bullets; re-reading each file showed bullets 2,3,6,7 (OSS spec vertical, 5-module package, R-241 bugfix, ADR v0.6) describe cexai/cexai/content_factory/ (the VIDEO package), while only bullets 1,4,5-partial,8 (kind-KC, _tools/cex_content_factory.py, tests/test_content_fabric.py, Wave-3 promotion record) describe THIS kind. tests/test_content_fabric.py re-run live: 14/14 passed."
confidence: 0.9
outcome: SUCCESS
domain: content_factory
tags: [content-factory, naming-collision, grounding-discipline, depends_on-crosscheck, evidence-triage]
tldr: "A shared name across 3 systems means evidence bullets must be individually verified against depends_on, not accepted as a block. 4 of 8 cited bullets belonged to a sibling system."
impact_score: 8.5
decay_rate: 0.05
keywords: [content-factory, naming-collision, grounding, depends_on, evidence-verification, test_content_fabric]
memory_scope: project
observation_types: [project, reference]
quality: null
title: "Memory Content Factory"
8f: "F7_govern"
density_score: 0.90
llm_function: INJECT
related:
  - content-factory-builder
  - bld_architecture_content_factory
  - bld_eval_content_factory
---
# Learning: content_factory

## Key Insight
When a kind's NAME is reused by an unrelated system elsewhere in the repo, the evidence
trail supporting its SCAFFOLD verdict can silently conflate the two. The fix is mechanical:
cross-check every cited evidence bullet's module path against the kind's own `depends_on`
in `kinds_meta.json`. A module that does not touch either dependency is evidence for a
DIFFERENT system wearing the same name.

## Evidence from this build
| Evidence bullet (decision doc Sec 2.3) | Module | Matches depends_on? | System |
|------------------------------------------|--------|----------------------|--------|
| 1. Kind-KC exists | `kc_content_factory.md` | N/A (definitional) | THIS kind |
| 2. OSS spec vertical | `cexai-specs/20_content_factory/` | NO (sources: MoneyPrinterTurbo/Chatterbox) | video package |
| 3. 5-module package | `cexai/cexai/content_factory/*` | NO (reuses workflow/tts_provider) | video package |
| 4. Dedicated central tool | `_tools/cex_content_factory.py` | YES (calls into social_publisher + content_library shapes) | THIS kind |
| 5. Tests (2 suites) | `cexai/tests/.../test_content_factory.py` (23) + `tests/test_content_fabric.py` (14) | Only the 2nd | split evidence |
| 6. Shipped bugfix R-241 | `cexai/cexai/content_factory/tts.py` | NO | video package |
| 7. ADR v0.6 | "ZERO new kinds" (titled explicitly) | NO -- this ADR argues AGAINST new kinds for the video pkg | video package |
| 8. Wave-3 promotion record | `SPEC_central_backlog_2026_06_23.md:42-46` | YES (content_fabric, produce->review->publish) | THIS kind |

## Lessons Learned
1. **A SCAFFOLD verdict can still survive evidence correction** -- bullets 1, 4, 5-partial,
   8 alone remain >= 2 independent real sites; the verdict holds even after removing the
   4 misattributed bullets.
2. **`depends_on` is the fastest disambiguation lens** -- `social_publisher` +
   `supabase_data_layer` only make sense for the produce->review->publish trio.
3. **An ADR titled "ZERO new kinds" is a red flag when cited as kind-registration
   evidence** -- read the title literally before citing it as proof a kind is real.
4. **Live test re-run beats trusting a cited pass-count** -- `tests/test_content_fabric.py`
   was re-run in this session (14/14 passed) rather than trusted from the decision doc.

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[content-factory-builder]] | upstream | 0.32 |
| [[bld_architecture_content_factory]] | related | 0.28 |
| [[bld_eval_content_factory]] | related | 0.25 |
