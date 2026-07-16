---
kind: quality_gate
id: p11_qg_pipeline_template
pillar: P11
llm_function: GOVERN
purpose: Quality gate with HARD and SOFT scoring for pipeline_template
quality: null
title: "Quality Gate Pipeline Template"
version: "1.0.0"
author: n03_builder
tags: [pipeline_template, builder, quality_gate, scenario_indexed]
tldr: "Quality gate with HARD and SOFT scoring for pipeline_template"
domain: "pipeline_template construction"
created: "2026-04-18"
updated: "2026-04-18"
8f: "F7_govern"
keywords: [pipeline_template construction, quality gate pipeline template, pipeline_template, builder, quality_gate, scenario_indexed]
density_score: 0.88
related:
 - pipeline-template-builder
 - bld_schema_pipeline_template
---
## Quality Gate

## Definition
| Metric | Threshold | Operator | Scope |
|--------|-----------|----------|-------|
| Stage sequence completeness | 100% | equals | All pipeline_templates |
| Mandatory gate coverage | 100% | equals | reviewer + tester present |

## HARD Gates
| ID | Check | Fail Condition |
|-----|-------|----------------|
| H01 | YAML frontmatter valid | Invalid YAML syntax or missing required fields |
| H02 | ID matches ^p12_pt_[a-z][a-z0-9_]+$ | ID pattern mismatch |
| H03 | kind field == 'pipeline_template' | Kind field incorrect or missing |
| H04 | scenario in {new_feature, new_feature_security, bug_fix_unknown, bug_fix_known, refactoring, perf_opt, infra} | Invalid scenario value |
| H05 | stages array has >= 2 entries | Empty or single-stage pipeline |
| H06 | every stage has role + model_tier | Missing role or model_tier in any stage |
| H07 | quality_gates.mandatory includes reviewer AND tester | Missing mandatory gate |
| H08 | revision_loop.max_iterations between 1 and 5 | Out-of-range iteration count |

## SOFT Scoring
| Dim | Dimension | Weight | Scoring Guide |
|-----|-----------|--------|---------------|
| D01 | Stage sequence fidelity (matches multi-agent catalog) | 0.30 | Exact match = 1.0, minor variant = 0.5, diverged = 0 |
| D02 | Model-tier assignment accuracy (cognitive load mapping) | 0.20 | All correct = 1.0, 1-2 off = 0.5, systemic wrong = 0 |
| D03 | Revision loop completeness (iterations + escalation) | 0.20 | Both set = 1.0, one missing = 0.5, absent = 0 |
| D04 | Quality gate specificity (priority_order + mandatory) | 0.15 | Security-first + both gates = 1.0, partial = 0.5, vague = 0 |
| D05 | Instantiation example clarity | 0.15 | Runnable example = 1.0, pseudo-code = 0.5, absent = 0 |

## Actions
| Score | Action |
|-------|--------|
| GOLDEN >= 9.5 | Auto-register as canonical scenario pipeline |
| PUBLISH >= 8.0 | Publish to pipeline-template library |
| REVIEW >= 7.0 | Request peer review from N03 |
| REJECT < 7.0 | Rebuild per 8F F6 |

## Bypass
| Conditions | Approver | Audit Trail |
|------------|----------|-------------|
| Experimental scenario (non-canonical) | N07 lead |.cex/experiments/results.tsv |

## Examples

## Golden Example: bug_fix_unknown
```yaml
---
id: p12_pt_bug_fix_unknown
kind: pipeline_template
pillar: P12
title: "Pipeline: Bug Fix (Unknown Cause)"
scenario: bug_fix_unknown
stages:
 - role: finder
 model_tier: medium
 optional: false
 - role: debugger
 model_tier: high
 optional: false
 - role: fixer
 model_tier: high
 optional: false
 - role: reviewer
 model_tier: medium
 optional: false
 - role: tester
 model_tier: low
 optional: false
revision_loop:
 max_iterations: 3
 escalation_target: user
quality_gates:
 mandatory: [reviewer, tester]
 priority_order: [quality, implementation]
version: 1.0.0
quality: null
tags: [hermes_origin, pipeline, scenario_indexed, bug_fix_unknown]
---

## Scenario
Use when a bug has been reported but the root cause is unknown.
finder locates likely candidates; debugger traces execution to confirm cause;
fixer implements the patch; reviewer validates code quality; tester runs regression suite.

## Stage Sequence
| Order | Role | Model Tier | Optional | Notes |
|-------|------|-----------|----------|-------|
| 1 | finder | medium | No | Locate bug candidates in codebase |
| 2 | debugger | high | No | Trace root cause via logs/state |
| 3 | fixer | high | No | Apply minimal targeted patch |
| 4 | reviewer | medium | No | Validate code quality + diff |
| 5 | tester | low | No | Run regression suite |

## Quality Gates
Mandatory: reviewer + tester. Priority: quality > implementation.
Gate failure at reviewer routes back to fixer (max 3 loops), then escalates to user.
```

## Anti-Example 1: Missing mandatory gate
```yaml
---
id: p12_pt_refactoring
kind: pipeline_template
scenario: refactoring
stages:
 - role: finder
 model_tier: medium
 optional: false
 - role: refactorer
 model_tier: high
 optional: false
quality_gates:
 mandatory: [reviewer]
 priority_order: [quality]
---
```
**Why it fails:** quality_gates.mandatory missing `tester` (H07). Even refactoring pipelines need regression testing to verify behavior is preserved. Both reviewer AND tester are non-negotiable per canonical rules.

### S_RELATED: Cross-Reference Check (SOFT)
-  `related:` frontmatter field populated (3-15 entries)
-  `## Related Artifacts` section present in artifact body
-  At least 1 upstream and 1 downstream reference
- Penalty: -0.3 if empty (does not block, encourages wiring)
