---
id: p01_lin_check_registry
kind: lineage_record
pillar: P01
nucleus: n01
version: 1.0.0
target_artifact: "_tools/cex_check_registry.py + _tools/tests/test_cex_check_registry.py"
sources_count: 3
activities_count: 4
derivation_type: wasDerivedFrom
domain: knowledge-provenance
created: "2026-07-03"
updated: "2026-07-03"
author: "n01_intelligence"
quality: null
tags: [lineage_record, knowledge-provenance, ruff, pre-commit, great-expectations, MIT, Apache-2.0, r162, check_registry, d3_wave]
tldr: "Provenance for _tools/cex_check_registry.py (R-162's first typed pluggable-check slice): clean-room mechanic transplant from 3 sources (Ruff MIT, pre-commit MIT, Great Expectations Apache-2.0) -- concepts only, no source code copied, both licenses double-verified."
related:
  - kc_oss_ruff
  - kc_oss_pre_commit
  - kc_oss_great_expectations
  - improvement_register
---

> **[DISTILL ANNOTATION]** This file cites tool(s) not shipped in this tenant (Central-only): cex_distill. Inline citations are marked `[NOT SHIPPED in this tenant -- Central-only tool]`.

# Lineage: `_tools/cex_check_registry.py` (Ruff + pre-commit + Great Expectations)

## Canonical Provenance Frontmatter Schema

Derived artifacts MUST carry this block:

```yaml
provenance:
  sources:
    - source: "github.com/astral-sh/ruff"
      license: "MIT"
    - source: "github.com/pre-commit/pre-commit"
      license: "MIT"
    - source: "github.com/great-expectations/great_expectations"
      license: "Apache-2.0"
  lineage_record: "p01_lin_check_registry"
  method: "clean_room_concept_extraction"
  derived: "2026-07-03"
```

## Entities

| ID | Type | Location | Retrieved |
|----|------|----------|-----------|
| ruff_src | prov:Entity | github.com/astral-sh/ruff (main branch) | 2026-07-03T00:00:00Z |
| precommit_src | prov:Entity | github.com/pre-commit/pre-commit (main branch) | 2026-07-03T00:00:00Z |
| ge_src | prov:Entity | github.com/great-expectations/great_expectations (develop branch) | 2026-07-03T00:00:00Z |
| improvement_register_r162 | prov:Entity | docs/IMPROVEMENT_REGISTER.md (row R-162) | 2026-07-03T00:00:00Z |
| carry_registry_precedent | prov:Entity | _tools/cex_distill.py (CarryEntry frozen-dataclass table, R-164) | 2026-07-03T00:00:00Z |  <!-- [NOT SHIPPED in this tenant -- Central-only tool] -->

Method for all 3 external sources: clean-room CONCEPT extraction only -- no source code
reproduced (Ruff is Rust, pre-commit and Great Expectations are Python, but in all 3 cases the
transplant re-derives a SHAPE -- a typed rule/hook/result contract -- in fresh CEXAI-native Python,
not a translation or copy of the originals' implementation). All 3 licenses independently
double-verified (LICENSE file + a second package-metadata file per target); full evidence and
citations live in the 3 companion `kc_oss_*` dossiers.

## Activities

| ID | Label | Used | Generated | Agent | Timestamp |
|----|-------|------|-----------|-------|-----------|
| act_license_gate | license_verification_3x_double_sourced | ruff_src, precommit_src, ge_src | license_gate_pass | N01 | 2026-07-03T00:00:00Z |
| act_extract_mechanics | clean_room_concept_extraction | ruff_src, precommit_src, ge_src | mechanic_concepts (rule-registry+fix-tiers, hook-manifest-contract, result+aggregate) | N01 | 2026-07-03T00:00:00Z |
| act_dossier | kc_oss_dossier_authoring | mechanic_concepts | kc_oss_ruff, kc_oss_pre_commit, kc_oss_great_expectations | N01 | 2026-07-03T00:00:00Z |
| act_build_registry | typed_registry_build_plus_tests | mechanic_concepts, improvement_register_r162, carry_registry_precedent | cex_check_registry_py, test_cex_check_registry_py | N03 | 2026-07-03T00:00:00Z |

## Agents

| ID | Type | Role |
|----|------|------|
| N01 | nucleus | research cell -- license gate, mechanic extraction, dossier authoring |
| N03 | nucleus | engineering cell -- typed registry build + 2 real plugins + pytest suite |

## Derivation Relations

- cex_check_registry_py wasDerivedFrom ruff_src (fix-applicability tier concept: `fix_hint` pinned
  to the "Display" tier, no autofix)
- cex_check_registry_py wasDerivedFrom precommit_src (required-vs-optional-with-defaults contract
  shape: `CheckPlugin`'s required id/severity/description/run vs optional fix_hint/selector)
- cex_check_registry_py wasDerivedFrom ge_src (per-check-result + suite-aggregate shape:
  `CheckFinding` + `summarize()`)
- cex_check_registry_py wasDerivedFrom carry_registry_precedent (house style: frozen-dataclass
  entry + tuple registry + engine-loop pattern, matching R-164's `CarryEntry`/`run_carries`)
- cex_check_registry_py wasGeneratedBy act_build_registry
- cex_check_registry_py wasAttributedTo N03
- kc_oss_ruff wasGeneratedBy act_dossier
- kc_oss_pre_commit wasGeneratedBy act_dossier
- kc_oss_great_expectations wasGeneratedBy act_dossier

## License Attribution (MIT x2 + Apache-2.0 x1)

```
This product includes mechanic concepts derived from:
  - Ruff (https://github.com/astral-sh/ruff), Copyright Charles Marsh / Astral Software Inc.,
    licensed under the MIT License.
  - pre-commit (https://github.com/pre-commit/pre-commit), Copyright pre-commit dev team
    (Anthony Sottile, Ken Struys), licensed under the MIT License.
  - Great Expectations (https://github.com/great-expectations/great_expectations), Copyright
    Great Expectations, Inc., licensed under the Apache License, Version 2.0.
No source code from any of the three projects is reproduced in this product; the derivation is
clean-room concept extraction (typed contract shapes only), documented in kc_oss_ruff.md,
kc_oss_pre_commit.md, and kc_oss_great_expectations.md.
```

## Boundary Note (what this transplant did NOT touch)

`_tools/cex_doctor.py`, `_tools/cex_score.py`, and `_tools/cex_distill.py` are UNCHANGED by this  <!-- [NOT SHIPPED in this tenant -- Central-only tool] -->
transplant -- `cex_check_registry.py` is new, additive, read-only infrastructure. Wiring it into
`cex_doctor.py` as a live plugin-discovery pass is R-162's stated next step, left to a future,
separately-scoped `/mission` per this task's own instructions.

## Related Artifacts

| Artifact | Relationship | Score |
|----------|-------------|-------|
| kc_oss_ruff | sibling | 0.55 |
| kc_oss_pre_commit | sibling | 0.55 |
| kc_oss_great_expectations | sibling | 0.55 |
| improvement_register | upstream | 0.45 |
