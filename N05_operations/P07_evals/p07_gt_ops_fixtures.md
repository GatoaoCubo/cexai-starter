---
id: p07_gt_ops_fixtures
kind: golden_test
8f: F7_govern
pillar: P07
title: "Golden: N05 Operations Reference Fixtures"
version: "1.0.0"
created: "2026-07-20"
updated: "2026-07-20"
author: golden-test-builder
target_kind: "operations_fixture"
input: "Reference input/output pairs defining correct behavior for N05 critical operations: compile, signal, doctor, sanitize, wikilink resolution."
golden_output_ref: "inline"
quality_threshold: 9.5
rationale: "6 fixtures cover the N05 ops surface every artifact passes through before it can ship: compile, signal, doctor, sanitize (pass + fail), wikilink resolution. Each specifies comparison_method for deterministic assertion."
edge_case: true
reviewer: "n07_orchestrator"
approval_date: "2026-07-20"
domain: "operations"
quality: null
tags: [golden-test, n05-operations, compile, signal, sanitize, doctor, wikilink, P07]
tldr: "6 N05 ops golden fixtures: compile->yaml, signal->json, doctor healthy, sanitize pass/fail, wikilink resolve."
keywords: [operations reference fixtures, golden fixtures, doctor healthy, sanitize pass, sanitize fail, wikilink resolve, golden_test]
density_score: 0.91
related:
  - golden-test-builder
  - p07_bm_ops_pipeline
  - p07_rc_ops
  - nucleus_def_n05
---

## Input Scenario

Six deterministic reference cases for N05 operations. Each case is a triple: (test_id,
input_fixture, expected_output, comparison_method). Gating Wrath lens: no ambiguity
tolerated -- every case has an exact pass/fail assertion, no fuzzy matches.

## Golden Output

### golden_compile

```yaml
test_id: golden_compile
description: "cex_compile.py converts a minimal valid .md to .yaml"
input_fixture: |
  ---
  id: p01_kc_test
  kind: knowledge_card
  pillar: P01
  version: "1.0.0"
  created: "2026-07-20"
  updated: "2026-07-20"
  author: "test"
  domain: "test"
  quality: null
  tags: [test, compile, validation]
  tldr: "Minimal KC for compile golden test"
  ---
  ## Body
  Content here.
expected_output:
  file_created: true
  yaml_fields_present: [id, kind, pillar, version, created, updated, author, domain, quality, tags, tldr]
  exit_code: 0
comparison_method: json_match
```

### golden_signal

```yaml
test_id: golden_signal
description: "signal_writer.write_signal produces a valid JSON signal file"
input_fixture: "write_signal('n05', 'complete', 9.0)"
expected_output:
  file_pattern: ".cex/runtime/signals/signal_n05_complete_*.json"
  required_fields: [nucleus, event_type, score, timestamp]
  field_values:
    nucleus: "n05"
    event_type: "complete"
    score: 9.0
  timestamp_format: "ISO8601"
  exit_code: 0
comparison_method: json_match
```

### golden_doctor_healthy

```yaml
test_id: golden_doctor_healthy
description: "cex_doctor.py reports 0 failures on a clean repo state"
input_fixture: "clean_repo_state"
expected_output:
  stdout_contains: "0 failures"
  exit_code: 0
comparison_method: contains
```

### golden_sanitize_clean

```yaml
test_id: golden_sanitize_clean
description: "cex_sanitize.py --check passes on an ASCII-only .py file"
input_fixture: |
  # ASCII-only Python file
  def hello():
      print("[OK] all good")
expected_output:
  exit_code: 0
  stdout_contains: "clean"
comparison_method: contains
```

### golden_sanitize_dirty

```yaml
test_id: golden_sanitize_dirty
description: "cex_sanitize.py --check fails on a .py containing an em-dash (U+2014)"
input_fixture: |
  # Python file with em-dash violation
  # line 2: result -- value
  x = 1
expected_output:
  exit_code: 1
  stdout_pattern: "line [0-9]+"
  violation_char: "U+2014"
comparison_method: regex
```

### golden_wikilink_resolve

```yaml
test_id: golden_wikilink_resolve
description: "cex_wikilink_gate.py exits 0 when every double-bracket target reference in the body resolves to a real id: declaration; exits 1 on a fabricated target"
input_fixture: "artifact body containing one real-id reference (nucleus_def_n05) and one fabricated reference (a made-up id with no matching declaration anywhere in the repo)"
expected_output:
  exit_code: 1
  fabricated_targets: ["the made-up id"]
comparison_method: contains
```

## Rationale

- H01: frontmatter parses as valid YAML (gate: H01 pass)
- H02: id=p07_gt_ops_fixtures matches the golden_test id pattern (H02 pass)
- H03: id equals filename stem `p07_gt_ops_fixtures` (H03 pass)
- H04: kind == golden_test (H04 pass)
- H05: quality == null (H05 pass)
- H06: all required fields present (H06 pass)
- H07: quality_threshold=9.5 >= 9.5 (H07 pass)
- H08: target_kind=operations_fixture, not golden_test (H08 pass)
- H09: Golden Output section present with 6 complete fixtures (H09 pass)
- H10: Input Scenario section present and non-empty (H10 pass)

S03: 6 fixtures map to distinct ops gate paths (compile / signal / doctor / sanitize / wikilink).
S04: Every fixture is copy-pasteable as a real test assertion against the tools it names.
S05: golden_sanitize_dirty and golden_wikilink_resolve are edge/failure cases.
S06: This is not a `few_shot_example` (teaches format) -- it evaluates correct ops behavior.
S07: This is not a `unit_eval` -- it is a 9.5+ reference fixture set, not a threshold assertion.
S08: Reviewer: n07_orchestrator, approval_date: 2026-07-20.

## Evaluation Criteria

- [ ] golden_compile: yaml file created with all frontmatter fields, exit 0
- [ ] golden_signal: JSON file matches schema (nucleus/event_type/score/timestamp), exit 0
- [ ] golden_doctor_healthy: stdout contains "0 failures", exit 0
- [ ] golden_sanitize_clean: exit 0, stdout contains "clean"
- [ ] golden_sanitize_dirty: exit 1, stdout matches "line [0-9]+" regex
- [ ] golden_wikilink_resolve: exit 1, fabricated target named in output
- [ ] All 6 test_ids are unique
- [ ] All comparison_method values are one of: exact/contains/regex/json_match
- [ ] No real user data in any fixture (synthetic only)

## References

1. `_tools/cex_compile.py` -- compile .md to .yaml
2. `_tools/signal_writer.py` -- write_signal(nucleus, event_type, score)
3. `_tools/cex_doctor.py` -- repo health check
4. `_tools/cex_sanitize.py` -- ASCII-only enforcement
5. `_tools/cex_wikilink_gate.py` -- mechanical wikilink resolution gate
6. `.claude/rules/ascii-code-rule.md` -- U+2014 violation spec

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[golden-test-builder]] | upstream | 0.30 |
| [[p07_bm_ops_pipeline]] | sibling | 0.28 |
| [[p07_rc_ops]] | sibling | 0.26 |
| [[nucleus_def_n05]] | upstream | 0.22 |
