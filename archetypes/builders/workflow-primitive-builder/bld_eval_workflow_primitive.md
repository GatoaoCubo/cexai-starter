---
kind: quality_gate
id: p11_qg_workflow_primitive
pillar: P11
llm_function: GOVERN
purpose: Golden and anti-examples of workflow_primitive artifacts
pattern: few-shot learning for atomic orchestration building blocks
quality: null
title: 'Gate: Workflow Primitive'
version: 1.0.0
author: builder
tags:
- eval
- P11
- quality_gate
- examples
tldr: Gates ensuring workflow primitives define typed I/O, enforce composition rules
  (parallel-merge, loop max_iter, gate threshold), and contain no full workflow graphs
  or DAG edges.
domain: workflow_primitive
created: '2026-04-06'
updated: '2026-04-06'
8f: "F7_govern"
keywords:
  - "workflow primitive"
  - "enforce composition rules"
  - "p12_wp_{type}"
  - "p12_wp_{type}_{name}"
  - "workflow_primitive"
  - "quality"
  - "inputs"
density_score: 0.85
related:
  - p03_ins_workflow_primitive_builder
  - bld_knowledge_card_workflow_primitive
  - bld_output_template_workflow_primitive
  - workflow-primitive-builder
  - bld_config_workflow_primitive
---
## Quality Gate

## Definition
A workflow_primitive is an atomic orchestration building block — one of seven types (step, condition, loop, parallel, router, gate, merge) with typed inputs and outputs. It passes this gate when its type is valid, inputs and outputs are typed, type-specific guards are present (max_iter for loops, threshold for gates, merge_ref for parallel), and the primitive contains no full workflow graphs or DAG edges.
## HARD Gates
Failure on any HARD gate = immediate REJECT regardless of score.
| ID  | Check | Rationale |
|-----|-------|-----------|
| H01 | Frontmatter parses as valid YAML with no syntax errors | Unparseable file cannot be indexed or validated |
| H02 | `id` matches pattern `p12_wp_{type}` or `p12_wp_{type}_{name}` | Mismatched IDs cause routing failures |
| H03 | `kind` is exactly `workflow_primitive` (literal match) | Kind drives the loader; wrong literal silently misroutes |
| H04 | `quality` field is `null` (not filled by author) | Quality is assigned by this gate, not self-reported |
| H05 | `type` is one of: step, condition, loop, parallel, router, gate, merge | Unknown types break primitive resolution |
| H06 | `inputs` is a non-empty list with typed entries (name + type + required) | Untyped inputs break composition |
## SOFT Scoring
Dimensions are weighted; total normalized weight = 100%.
| # | Dimension | Weight | 1 (Poor) | 5 (Good) | 10 (Excellent) |
|---|-----------|--------|----------|----------|----------------|
| 1 | density >= 0.80 (content per token ratio) | 1.0 | Padded with filler | Mostly substantive | No filler; every line carries information |
| 2 | I/O typing precision (types match domain expectations, descriptions present) | 1.5 | Types are all "string" | Most types correct | Every type precisely matches the data it carries |
| 3 | Guard clause completeness (type-specific guards present and reasonable) | 1.5 | Missing required guards | Guards present but values questionable | Guards present with well-justified values |
| 4 | Composition metadata (composable_after/before lists match type semantics) | 1.0 | No composition metadata | Partial metadata | Complete composition rules for this type |
| 5 | Description clarity (one-line, actionable, matches what the primitive does) | 0.5 | Vague or missing | Present but generic | Precise one-line description of the operation |
| 6 | Error handling (on_error or retry_count defined where apownte) | 0.5 | No error handling | retry_count set | on_error with fallback primitive reference |

## Examples

# Examples: workflow-primitive-builder
## Golden Example: Step
INPUT: "Create a research step primitive that takes a query and returns findings"
OUTPUT (`p12_wp_step.yaml`):
```yaml
type: step
description: Execute research query against knowledge base and return ranked findings
inputs:
  - name: query
    type: string
    required: true
    description: Natural language research question
  - name: max_results
```
WHY THIS IS GOLDEN:
- filename follows `p12_wp_{type}.yaml`
- type is valid enum value
- inputs and outputs are fully typed with names, types, required flags
- descriptions are concise one-liners
## Golden Example: Loop with Guard
OUTPUT (`p12_wp_loop_retry_build.yaml`):
```yaml
type: loop
description: Retry artifact build with quality feedback until passing score or max attempts
inputs:
  - name: build_intent
    type: string
    required: true
    description: Original build instruction
  - name: feedback
```
WHY THIS PASSES:
- max_iter = 3 (within 1-100 range) — loop has termination guard
- break_condition provides early exit when quality is sufficient
- feedback_input connects loop iterations to quality gate output
- typed I/O enables composition with upstream step and downstream gate
## Golden Example: Parallel + Merge Pair
OUTPUT (`p12_wp_parallel_research.yaml`):
```yaml
type: parallel
description: Fan out research to N01 and N04 simultaneously
inputs:
  - name: research_query
    type: string
    required: true
outputs:
  - name: branch_results
```
OUTPUT (`p12_wp_merge_research_collect.yaml`):
```yaml
type: merge
description: Collect and deduplicate parallel research results from N01 and N04
inputs:
  - name: branch_results
    type: list
    required: true
    description: Results from parallel research branches
outputs:
```
WHY THIS PAIR PASSES:
- parallel has `merge_ref` pointing to the merge primitive
- merge has `source_refs` pointing back to the parallel
- parallel has `timeout_s` to kill stalled branches
- merge `strategy: all` waits for both branches

### S_RELATED: Cross-Reference Check (SOFT)
- [ ] `related:` frontmatter field populated (3-15 entries)
- [ ] `## Related Artifacts` section present in artifact body
- [ ] At least 1 upstream and 1 downstream reference
- Penalty: -0.3 if empty (does not block, encourages wiring)
