---
id: p07_gt_n03
kind: golden_test
8f: F7_govern
pillar: P07
title: "Golden Tests -- N03 Builder Outputs"
version: 1.1.0
created: 2026-04-17
author: n03_engineering
domain: artifact-construction
quality: null
tags: [golden-test, N03, builder, expected-output, regression, 8F]
tldr: "Golden output tests for N03's primary builders. Each test case defines: input intent, expected kind, expected frontmatter fields, structural assertions, and forbidden patterns. Run before any builder ISO update."
keywords: [golden tests, builder iso, frontmatter, density_score, min_sections, must_contain, compile, exit_code, golden master testing, characterization test, snapshot testing]
density_score: 0.88
updated: "2026-07-17"
related:
  - bld_schema_kind
---

# Golden Tests: N03 Builder Outputs

## Purpose

Golden tests capture the EXPECTED output of N03's builders.
When a builder ISO is updated, golden tests detect unintended regressions.
These are NOT unit tests -- they test end-to-end builder output shape, not logic.

This is the industry **Golden Master Testing** pattern (a.k.a. *characterization
testing*, coined by Michael Feathers in *Working Effectively with Legacy Code*):
capture a system's actual observed behavior as a baseline, then flag any
deviation as a candidate regression. Because N03's builders emit LLM-authored
prose, not deterministic bytes, each case below asserts STRUCTURAL invariants
(frontmatter, headings, forbidden patterns) instead of one literal-text diff --
the same "assert shape, not the whole blob" discipline modern snapshot-testing
tooling recommends for large or semi-nondeterministic output (see: Jest --
Snapshot Testing).

## Test Execution

```bash
python _tools/cex_system_test.py --golden --nucleus n03
# Or specific kind:
python _tools/cex_system_test.py --golden --kind input_schema
```

**Pass condition:** all assertions match for every test case.
**Fail condition:** any assertion fails OR frontmatter field missing.
**Regression:** test that previously passed now fails.

## Golden Test Format

Each test case:
```yaml
test_id: gt_n03_{kind}_{variant}
kind: string                    # target kind
intent: string                  # input to builder
expected:
  frontmatter:
    kind: string                # must match exactly
    pillar: string               # must match exactly
    quality: null                # always null
    density_score: ">= 0.85"     # numeric assertion
  body:
    min_sections: integer        # H2 count minimum
    must_contain: string[]       # required strings in body
    must_not_contain: string[]   # forbidden patterns
    density_floor: 0.80
  compile:
    exit_code: 0                 # compile step must succeed
```

## Test Cases

### GT-N03-001: input_schema basic

```yaml
test_id: gt_n03_input_schema_basic
kind: input_schema
intent: "create an input schema for a build task"
expected:
  frontmatter:
    kind: input_schema
    pillar: P06
    quality: null
    density_score: ">= 0.85"
  body:
    min_sections: 3
    must_contain:
      - "## Fields"
      - "| Field |"
      - "| Type |"
      - "## Validation Rules"
      - "## Examples"
    must_not_contain:
      - "TODO"
      - "TBD"
      - "{{placeholder}}"
    density_floor: 0.82
  compile:
    exit_code: 0
```

### GT-N03-002: workflow with steps

```yaml
test_id: gt_n03_workflow_steps
kind: workflow
intent: "create a workflow for artifact build pipeline"
expected:
  frontmatter:
    kind: workflow
    pillar: P12
    quality: null
  body:
    min_sections: 3
    must_contain:
      - "## Steps"
      - "## Trigger"
    density_floor: 0.80
  compile:
    exit_code: 0
```

### GT-N03-003: scoring_rubric weight sum

```yaml
test_id: gt_n03_scoring_rubric_weights
kind: scoring_rubric
intent: "create a scoring rubric for artifact quality"
expected:
  frontmatter:
    kind: scoring_rubric
    pillar: P07
    quality: null
  body:
    min_sections: 3
    must_contain:
      - "| Weight |"
      - "100%"      # hard constraint: dimension weights MUST sum to exactly 100%
    density_floor: 0.82
  assertions:
    - type: weight_sum
      target: 100
      tolerance: 0
  compile:
    exit_code: 0
```

## Forbidden Pattern Library

These patterns, if found in any N03 output, fail the golden test:

| Pattern | Reason |
|---------|--------|
| `quality: [0-9]` | Self-scoring violation |
| `TODO` / `TBD` / `FIXME` | Placeholder in production output |
| `{{[a-zA-Z_]+}}` | Unresolved template variable |
| `research card` | Vocabulary drift (should be knowledge_card) |
| `N/A` as only content of a section | Empty section placeholder |
| Non-ASCII chars in .py/.ps1 code blocks | ASCII rule violation |

## Evaluation Criteria

| Layer | Mechanism | Source of the rule |
|-------|-----------|---------------------|
| Frontmatter contract | exact `kind`/`pillar`, `quality: null` | this file's `expected.frontmatter` |
| Structural shape | `min_sections`, `must_contain` | this file's `expected.body` |
| Negative space | `must_not_contain` | Forbidden Pattern Library above |
| Density | `density_floor` 0.80-0.82 | this file's `expected.body` |
| Domain invariant | `weight_sum == 100` (GT-N03-003 only) | scoring_rubric builder contract: "dimension weights MUST sum to exactly 100%" |
| Toolchain | `compile.exit_code == 0` | full compile of the produced artifact set |

A case fails if ANY layer fails -- no partial credit. A golden case that only
sometimes holds is not golden.

## Test Maintenance

- Run golden tests before ANY change to builder ISOs
- If output legitimately changes (spec update): update golden test first, then update ISO
- Golden tests are the CONTRACT between spec writers and builders
- Never delete a golden test without a spec change justifying the removal

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[bld_schema_kind]] | upstream | 0.25 |
