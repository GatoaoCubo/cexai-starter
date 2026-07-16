---
id: p01_lin_eval_assertions_r173
kind: lineage_record
pillar: P01
nucleus: n01
version: 1.0.0
target_artifact: "_tools/cex_assertions.py + _tools/tests/test_cex_assertions.py"  <!-- [NOT SHIPPED in this tenant -- Central-only tool] -->
sources_count: 3
activities_count: 4
derivation_type: wasDerivedFrom
domain: knowledge-provenance
created: "2026-07-03"
updated: "2026-07-03"
author: "n01_intelligence"
quality: null
tags: [lineage_record, knowledge-provenance, guardrails_ai, promptfoo, deepeval, apache2, mit, r173, r174, r162, eval_assertions, d1_honesty]
tldr: "Provenance for _tools/cex_assertions.py (R-173's typed declarative assertion REGISTRY, fixing cex_score.py's prose-regex hard-gate parsing): clean-room mechanic transplant from 3 permissive sources (guardrails-ai Apache-2.0 register_validator dispatch, promptfoo MIT ASSERTION_HANDLERS dispatch, deepeval Apache-2.0 assert_test() re-execution discipline) -- concepts only, no source code copied, all 3 licenses double-verified in their own kc_oss_* dossiers."  <!-- [NOT SHIPPED in this tenant -- Central-only tool] -->
---

> **[DISTILL ANNOTATION]** This file cites tool(s) not shipped in this tenant (Central-only): cex_assertions, cex_council, cex_distill. Inline citations are marked `[NOT SHIPPED in this tenant -- Central-only tool]`.

# Lineage: `_tools/cex_assertions.py` (Guardrails AI + promptfoo + DeepEval)  <!-- [NOT SHIPPED in this tenant -- Central-only tool] -->

## Canonical Provenance Frontmatter Schema

Derived artifacts MUST carry this block:

```yaml
provenance:
  sources:
    - source: "github.com/guardrails-ai/guardrails"
      license: "Apache-2.0"
    - source: "github.com/promptfoo/promptfoo"
      license: "MIT"
    - source: "github.com/confident-ai/deepeval"
      license: "Apache-2.0"
  lineage_record: "p01_lin_eval_assertions_r173"
  method: "clean_room_concept_extraction"
  derived: "2026-07-03"
```

## Entities

| ID | Type | Location | Retrieved |
|----|------|----------|-----------|
| guardrails_src | prov:Entity | github.com/guardrails-ai/guardrails (main branch, `guardrails/validator_base.py` + `guardrails/types/on_fail.py`) | 2026-07-03T00:00:00Z |
| promptfoo_dossier | prov:Entity | N01_intelligence/P01_knowledge/kc_oss_promptfoo.md (prior-session dossier, license MIT verified 2x, ASSERTION_HANDLERS mechanic) | 2026-07-03T00:00:00Z |
| deepeval_dossier | prov:Entity | N01_intelligence/P01_knowledge/kc_oss_deepeval.md (prior-session dossier, license Apache-2.0 verified 2x, `assert_test()` re-execution mechanic) | 2026-07-03T00:00:00Z |
| improvement_register_r173 | prov:Entity | docs/IMPROVEMENT_REGISTER.md (row R-173, self-certification class shared with R-007/R-162/R-174) | 2026-07-03T00:00:00Z |
| cex_score_hard_gates | prov:Entity | _tools/cex_score.py `_parse_hard_gates` (line ~324, confirmed by direct Read) -- the artifact being fixed, UNCHANGED by this transplant | 2026-07-03T00:00:00Z |
| carry_registry_precedent | prov:Entity | _tools/cex_distill.py (`CarryEntry` frozen-dataclass + `CARRY_REGISTRY` tuple, R-164) -- house-style precedent for typed registry tables | 2026-07-03T00:00:00Z |  <!-- [NOT SHIPPED in this tenant -- Central-only tool] -->

Method: guardrails-ai was freshly license-gated and mechanic-extracted this session (2 live
fetches: LICENSE + pyproject.toml, cross-verified; full source read of `validator_base.py` in 3
chained fetches + `on_fail.py`). promptfoo and deepeval mechanics are REUSED from their own prior
`kc_oss_*` dossiers (both already license-gated PASS in earlier sessions) per the fit_rows this
spec named -- no re-fetch was needed since both licenses and mechanics were already independently
verified and cited in those dossiers. All 3 are clean-room CONCEPT extractions: a registry-decorator
dispatch table, a swappable action-vs-outcome contract, and a re-execution-not-trust discipline --
re-derived in fresh CEXAI-native Python, no source code from any of the 3 projects reproduced.

## Activities

| ID | Label | Used | Generated | Agent | Timestamp |
|----|-------|------|-----------|-------|-----------|
| act_license_gate | license_verification_guardrails_2x_double_sourced | guardrails_src | license_gate_pass (Apache-2.0) | N01 | 2026-07-03T00:00:00Z |
| act_extract_mechanics | clean_room_concept_extraction | guardrails_src, promptfoo_dossier, deepeval_dossier | mechanic_concepts (registry-decorator dispatch, ValidationResult/OnFailAction contract, Hub lazy-import) | N01 | 2026-07-03T00:00:00Z |
| act_dossier | kc_oss_dossier_authoring | mechanic_concepts | kc_oss_guardrails | N01 | 2026-07-03T00:00:00Z |
| act_build_engine | typed_registry_build_plus_tests | mechanic_concepts, improvement_register_r173, cex_score_hard_gates, carry_registry_precedent | cex_assertions_py, test_cex_assertions_py | N03 | 2026-07-03T00:00:00Z |

## Agents

| ID | Type | Role |
|----|------|------|
| N01 | nucleus | research cell -- license gate (guardrails-ai), mechanic extraction, dossier authoring |
| N03 | nucleus | engineering cell -- typed assertion registry build (8 assertion types) + 22-test pytest suite + live dogfood run |

## Derivation Relations

- cex_assertions_py wasDerivedFrom guardrails_src (`register_validator` decorator -> module-level
  lookup dict pattern; re-derived as `register_assertion` -> `ASSERTION_HANDLERS`)
- cex_assertions_py wasDerivedFrom promptfoo_dossier (`ASSERTION_HANDLERS` type->handler dispatch
  shape, cited concept-only via the prior kc_oss_promptfoo.md dossier -- no re-fetch this session)
- cex_assertions_py wasDerivedFrom deepeval_dossier (`assert_test()` re-execution-not-trust
  discipline: every handler is called against the REAL target content, never a cached/trusted
  status string, cited concept-only via the prior kc_oss_deepeval.md dossier)
- cex_assertions_py wasDerivedFrom cex_score_hard_gates (the `hard_gate_table` assertion type
  independently RE-IMPLEMENTS the `| H01 | check | fail_cond |` row-matching shape that
  `_parse_hard_gates()` targets, as a SEPARATE parser -- `cex_score.py` itself is untouched)
- cex_assertions_py wasDerivedFrom carry_registry_precedent (house style: module-level dict
  registry populated by a decorator, matching R-164's `CarryEntry`/`CARRY_REGISTRY` shape)
- cex_assertions_py wasGeneratedBy act_build_engine
- cex_assertions_py wasAttributedTo N03
- kc_oss_guardrails wasGeneratedBy act_dossier

## License Attribution (Apache-2.0 x2 + MIT x1)

```
This product includes mechanic concepts derived from:
  - Guardrails AI (https://github.com/guardrails-ai/guardrails), licensed under the
    Apache License, Version 2.0.
  - promptfoo (https://github.com/promptfoo/promptfoo), licensed under the MIT License.
  - DeepEval (https://github.com/confident-ai/deepeval), licensed under the
    Apache License, Version 2.0.
No source code from any of the three projects is reproduced in this product; the derivation is
clean-room concept extraction (typed registry-dispatch + pass/fail contract shapes only),
documented in kc_oss_guardrails.md (fresh this session) and kc_oss_promptfoo.md / kc_oss_deepeval.md
(reused prior-session dossiers, both already license-gated PASS).
```

## Boundary Note (what this transplant did NOT touch)

`_tools/cex_score.py`, `_tools/cex_doctor.py`, `_tools/cex_distill.py`, and `_tools/cex_council.py`  <!-- [NOT SHIPPED in this tenant -- Central-only tool] -->
are UNCHANGED by this transplant -- `cex_assertions.py` is new, additive, standalone infrastructure
with its own independent markdown/frontmatter loader (`load_markdown_context`, deliberately NOT
importing `cex_score.py`/`cex_shared.py`). Wiring `cex_assertions.py` INTO `cex_score.py`'s or
`cex_doctor.py`'s live gate-checking path is a follow-on register row, not this session's scope.

## Dogfood Evidence (live, this session)

`python _tools/cex_assertions.py --spec <spec.yaml> --target N05_operations/P11_feedback/quality_gate_operations.md --json`  <!-- [NOT SHIPPED in this tenant -- Central-only tool] -->
against a real, disk, hand-authored `quality_gate` artifact returned
`{"pass": true, "total": 4, "passed": 4, "failed": 0}` and independently re-derived
`gate_count: 9` (`H01`..`H09`) directly from the file's own markdown table -- a second,
independent parser agreeing with `cex_score.py`'s own `_parse_hard_gates()` count, without
importing or trusting that parser's output. 22/22 pytest tests pass
(`_tools/tests/test_cex_assertions.py`), including a negative-control dogfood test that
correctly FAILS an intentionally wrong assertion spec against the same real file (proves the
engine is not a rubber stamp).

## Related Artifacts

| Artifact | Relationship | Score |
|----------|-------------|-------|
| kc_oss_guardrails | sibling | 0.55 |
| kc_oss_promptfoo | sibling | 0.50 |
| kc_oss_deepeval | sibling | 0.50 |
| improvement_register | upstream | 0.45 |
