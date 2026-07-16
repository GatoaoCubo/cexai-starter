---
kind: quality_gate
id: p04_qg_diff_strategy
pillar: P11
llm_function: GOVERN
purpose: Quality gate with HARD and SOFT scoring for diff_strategy
quality: null
title: "Quality Gate Diff Strategy"
version: "1.1.0"
author: n06_audit_hybrid_review2
tags:
  - "diff_strategy"
  - "builder"
  - "quality_gate"
tldr: "Quality gate enforcing algorithm specificity, patch correctness, and edge-case coverage for code diff artifacts"
domain: "diff_strategy construction"
created: "2026-04-13"
updated: "2026-04-13"
8f: "F7_govern"
keywords:
  - "diff_strategy construction"
  - "quality gate diff strategy"
  - "patch correctness"
  - "diff_strategy"
  - "builder"
  - "quality_gate"
  - "p04_ds_[a-za-z0-9_-]+"
density_score: 0.90
related:
  - bld_knowledge_card_diff_strategy
  - bld_output_template_diff_strategy
  - bld_instruction_diff_strategy
  - diff-strategy-builder
  - bld_tools_diff_strategy
---
## Quality Gate

## Definition
| metric        | threshold | operator | scope                            |
|---------------|-----------|----------|----------------------------------|
| patch_accuracy| 99.0%     | >=       | Patch applies cleanly to target  |
| algorithm_named | true    | ==       | Named algorithm required         |
| edge_cases_min | 3        | >=       | Empty diff, binary, encoding     |

## HARD Gates
| ID  | Check                   | Fail Condition                                          |
|-----|-------------------------|---------------------------------------------------------|
| H01 | YAML valid              | Invalid YAML syntax                                     |
| H02 | ID matches pattern      | ID does not match `p04_ds_[a-zA-Z0-9_-]+`              |
| H03 | kind = diff_strategy    | kind field absent or wrong value                        |
| H04 | algorithm_type present  | Field missing or not in [Myers, LCS, patience, histogram, Ratcliff-Obershelp, custom] |
| H05 | granularity defined     | Field missing or not in [line, token, character, AST, semantic] |
| H06 | patch correctness test  | No test case demonstrating correct patch application    |
| H07 | edge cases documented   | Fewer than 3 edge cases (empty diff, binary file, encoding mismatch) |

## SOFT Scoring
| Dim | Dimension               | Weight | Scoring Guide                                             |
|-----|-------------------------|--------|-----------------------------------------------------------|
| D1  | Algorithm justification | 0.20   | 1.0 = named algo with complexity analysis; 0.0 = generic |
| D2  | Patch correctness       | 0.25   | 1.0 = idempotent, reversible patches; 0.0 = destructive  |
| D3  | Performance budget      | 0.15   | 1.0 = O(ND) or better cited; 0.0 = no complexity claim   |
| D4  | Edge case coverage      | 0.20   | 1.0 = 5+ named edge cases with handling; 0.0 = none      |
| D5  | Tool integration        | 0.20   | 1.0 = difflib/git-apply/patch cited; 0.0 = fictional tools|

## Score Thresholds
| Score  | Action                                                       |
|--------|--------------------------------------------------------------|
| >= 9.0 | GOLDEN -- publish to library                                 |
| 8.0-9.0| PUBLISH -- peer review before publish                        |
| 6.0-8.0| REVIEW -- fix algorithm gaps, resubmit                       |
| < 6.0  | REJECT -- rebuild; missing core algorithm or wrong domain    |

## Bypass
| Condition                          | Approver | Audit Trail                      |
|------------------------------------|----------|----------------------------------|
| Emergency patch rollback           | N07      | "Emergency patch rollback"       |

## Examples

## Golden Example -- Myers Line Diff (Aider udiff-simple format)
```yaml
---
kind: diff_strategy
id: p04_ds_myers_line_diff
algorithm_type: Myers
granularity: line
comparison_basis: edit_distance
performance_budget: O(ND) where N = sum of lengths, D = edit distance
---
```
```
## Overview
Myers greedy diff (1986): finds the shortest edit script (SES) by treating
diff as shortest-path search on an edit graph. Each diagonal k = x - y
represents balanced insertions/deletions. Runs in O(ND) time, O(D) space.

## Patch Format
Unified diff (POSIX): 3-line context window, @@ -L,S +L,S @@ hunk headers.
Applied via: `patch -p1 < file.diff` or `git apply --3way file.diff`
```

## Golden Example -- Patience Diff (structural)
```yaml
---
kind: diff_strategy
id: p04_ds_patience_structural
algorithm_type: patience
granularity: line
comparison_basis: unique_lines_LCS
---
```
```
## Overview
Patience diff (Bram Cohen, used in Bazaar/git): LCS only over unique lines.
Produces human-readable diffs for code refactors -- avoids matching braces/
blank lines that Myers would greedily consume. Git uses histogram diff as
refinement; libxdiff implements both.

## When to use
Prefer patience/histogram over Myers when:
```

## Anti-Example 1: edit_format (boundary violation)
```yaml
---
kind: edit_format   # WRONG -- this is format, not strategy
description: Aider SEARCH/REPLACE block syntax
---
```
**Why it fails**: edit_format specifies HOW changes are *serialized* (block
delimiters, line markers). diff_strategy specifies HOW changes are *computed*
(which algorithm finds the minimal edit script). These are downstream stages;
conflating them means the builder will mix syntax rules with algorithm selection.

### S_RELATED: Cross-Reference Check (SOFT)
- [ ] `related:` frontmatter field populated (3-15 entries)
- [ ] `## Related Artifacts` section present in artifact body
- [ ] At least 1 upstream and 1 downstream reference
- Penalty: -0.3 if empty (does not block, encourages wiring)
