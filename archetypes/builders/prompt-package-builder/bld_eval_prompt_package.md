---
id: p11_qg_prompt_package
kind: quality_gate
pillar: P11
llm_function: GOVERN
domain: prompt_package
version: 1.0.0
created: "2026-07-03"
updated: "2026-07-03"
author: builder
tags:
- eval
- P11
- quality_gate
- decompose
quality: null
title: 'Gate: Prompt Package'
tldr: Quality gate for the Stage 1 -> Stage 2 handoff artifact -- validates the 8 required fields, 4 body sections, and the fill-marker/max_bytes rules from p06_if_prompt_package.md.
8f: "F7_govern"
density_score: 0.85
related:
  - p11_qg_prompt_template
  - p03_ins_prompt_package
  - bld_knowledge_card_prompt_package
  - prompt-package-builder
  - bld_memory_prompt_package
---
## Quality Gate

## Definition

A prompt package is a frozen F1-F4 handoff: Stage 1 (Opus/Sonnet) writes it; Stage 2 (a cheap
model) reads it and executes F6 PRODUCE only. It carries `package_type: f6_prompt_package`,
resolves a real `target_kind`, and contains exactly 4 body sections in order (IDENTITY, CONTEXT,
PLAN, TEMPLATE). Scope: files with `kind: prompt_package`. Does not apply to `prompt_template`
(reusable, unfilled mold) or `system_prompt` (fixed identity, no Stage-1/Stage-2 handoff).

## HARD Gates

Failure on any single gate means REJECT -- Stage 2 MUST NOT consume the package.

| ID | Predicate | How to test |
|-----|-----------|-------------|
| H01 | Frontmatter parses as valid YAML | `yaml.safe_load(frontmatter)` raises no error |
| H02 | `package_type` equals literal `f6_prompt_package` | string equality check |
| H03 | `target_kind` resolves in `.cex/kinds_meta.json` | `target_kind in kinds_meta` |
| H04 | `kind` equals literal `prompt_package` | string equality check |
| H05 | All 4 body sections present, in order | regex match on `## IDENTITY`, `## CONTEXT`, `## PLAN`, `## TEMPLATE` headers |
| H06 | `## TEMPLATE` contains >= 1 fill marker | `{{...}}` OR `[FILL: ...]` present (both conventions attested -- see Boundary note below) |
| H07 | `max_bytes` is a positive integer <= 32768 AND <= the target kind's own registered cap | numeric + cross-check against `kinds_meta[target_kind]["max_bytes"]` |
| H08 | `quality` is null at authoring time | `quality is None` |

**Boundary note (H06)**: `p06_if_prompt_package.md` specifies `[FILL: ...]` as the marker
convention, but the real template (`tpl_prompt_package.md`) and the real writer
(`cex_8f_runner.py::_write_prompt_package`) both use Mustache `{{...}}`. This gate accepts
EITHER -- rejecting one in favor of the other would reject real, working artifacts.

## SOFT Scoring

Score each dimension 0 (absent or fails) to 1 (present and passes). Weights are 0.5 or 1.0.

| # | Dimension | Weight |
|----|-----------|--------|
| 1 | `density_target` field present and in [0.80, 1.00] | 1.0 |
| 2 | `## CONTEXT` carries pre-resolved facts, zero unexecuted MCP/retrieval calls | 1.0 |
| 3 | `## TEMPLATE` is the target kind's own `bld_output` ISO content (not a fresh guess) | 1.0 |
| 4 | `stage_2_model_hint` present (soft preference for the tier resolver) | 0.5 |
| 5 | `builder_isos_loaded` and `context_sources` are non-zero (manual/example authoring; may be legitimately 0 only for `mode: repair`/`mode: evolve` packages) | 0.5 |
| 6 | Tags list includes `prompt-package` | 0.5 |

**Formula**: `final_score = (sum of score_i * weight_i) / (sum of weight_i) * 10`
Weight total: 4.5. Score range: 0.0 to 10.0.

## Actions

| Tier | Threshold | Action |
|------|-----------|--------|
| GOLDEN | >= 9.5 | Publish to `N00_genesis/P03_prompt/examples/stress_decompose_packages/` as a new golden T-case |
| PUBLISH | >= 8.0 | Hand off to Stage 2 (`cex_decompose.py::stage_2`) |
| REVIEW | >= 7.0 | Return to Stage 1 with scored dimension feedback; one revision cycle |
| REJECT | < 7.0 | Block from Stage 2; Stage 1 must re-run F1-F4 harvesting |

## Bypass

| Field | Value |
|-------|-------|
| condition | `mode: repair` or `mode: evolve` package where `builder_isos_loaded: 0` / `context_sources` is intentionally minimal (T07/T08 real precedent) |
| approver | N07 orchestrator must confirm the mode is intentional, not a harvesting failure |
| audit_log | Record via `cex_cost_tracker`'s `CEX_COST_CONTEXT=decompose_stage_1` event, already emitted by `cex_decompose.py::stage_1` |
| expiry | N/A -- `mode: repair`/`evolve` is a standing, documented shape, not a time-boxed bypass |

## Examples

# Examples -- prompt-package-builder

## Golden Example

A complete, valid `prompt_package` (schema mirrors the real `pp_T05_pipeline_template.md`).
```yaml
id: pp_T05_pipeline_template
kind: prompt_package
pillar: P03
package_type: f6_prompt_package
task_id: T05
target_kind: pipeline_template
target_pillar: P12
target_nucleus: N03
target_path: N03_engineering/P12_orchestration/p12_pt_ci_cd_artifact_validation.md
builder_isos_loaded: 12
context_sources: 4
density_target: 0.87
max_bytes: 8192
quality: null
```
Body: `## IDENTITY` (pipeline_template-builder persona) -> `## CONTEXT` (4 injected sources) ->
`## PLAN` (section list + density target) -> `## TEMPLATE` (pipeline_template's own bld_output
ISO, fill markers intact).

### S_RELATED: Cross-Reference Check (SOFT)
- [ ] `related:` frontmatter field populated (3-15 entries)
- [ ] `## Related Artifacts` section present in artifact body
- [ ] At least 1 upstream and 1 downstream reference
- Penalty: -0.3 if empty (does not block, encourages wiring)

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[p11_qg_prompt_template]] | sibling | 0.60 |
| [[p03_ins_prompt_package]] | related | 0.52 |
| [[bld_knowledge_card_prompt_package]] | related | 0.48 |
| [[prompt-package-builder]] | upstream | 0.45 |
| [[bld_memory_prompt_package]] | related | 0.40 |
