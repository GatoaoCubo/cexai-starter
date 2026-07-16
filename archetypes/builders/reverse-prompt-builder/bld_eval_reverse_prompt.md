---
id: p11_qg_reverse_prompt
kind: quality_gate
pillar: P11
llm_function: GOVERN
domain: reverse_prompt
version: 1.0.0
created: '2026-07-03'
updated: '2026-07-03'
author: builder
tags:
- eval
- P11
- quality_gate
- examples
quality: null
title: 'Gate: Reverse Prompt'
tldr: Structural gate (H01-H10) plus the real cross-runtime equivalence rubric
  (C1-C5) for reverse_prompt artifacts, distinguishing canonical synthesizer
  output from builder-authored drafts.
8f: "F7_govern"
density_score: 0.87
related:
  - reverse-prompt-builder
  - bld_feedback_reverse_prompt
---
## Quality Gate

## Definition
A `reverse_prompt` is a filled, frozen repo-reconstruction prompt instance. This gate validates BOTH structural conformance (H01-H10) and, when the artifact represents or is compared against a real repo synthesis, semantic equivalence (rubric C1-C5, `rubric_reverse_prompt_equivalence.md`). Scope: files with `kind: reverse_prompt`. Does not apply to `prompt_template` (unfilled molds) or `knowledge_card` (factual notes).
## HARD Gates
Failure on any single gate means REJECT regardless of soft score.
| ID | Predicate | How to test |
|-----|-----------|-------------|
| H01 | Frontmatter parses as valid YAML | `yaml.safe_load(frontmatter)` raises no error |
| H02 | `id` matches `^p03_rp_[a-z][a-z0-9_]+$` | regex match |
| H03 | `kind` equals literal `reverse_prompt` | string equality |
| H04 | `quality` is null at authoring time | `quality is None` |
| H05 | All 3 open_vars declared with resolved `filled_vars` | keys present: target_audience, target_runtime, complexity_level |
| H06 | Enum validity | `target_runtime` in {claude-code,codex,gemini,ollama}; `complexity_level` in {introductory,intermediate,advanced} |
| H07 | `source_url` normalized | matches `https://{github\|gitlab\|bitbucket}.com/<owner>/<repo>` |
| H08 | License disclosed | `upstream_license` present OR `derived_from_unlicensed_source: true` |
| H09 | `## Provenance` section present, mode declared, non-determinism disclosed unless mode==repair | manual read |
| H10 | Size <= 8192 bytes; path is NOT `.cex/runtime/artifacts/reverse_prompts/` | `len(bytes) <= 8192` + path check |
## SOFT Scoring
Score each dimension 0 (absent/fails) to 1 (present/passes).
| # | Dimension | Weight |
|----|-----------|--------|
| 1 | `density_score` present and >= 0.80 | 1.0 |
| 2 | Repo Extract Summary populated (primary_language, description, entry files) | 1.0 |
| 3 | Equivalence rubric C1-C5 satisfied vs. a comparison instance (when applicable) | 1.0 |
| 4 | Complete filled Example section present | 1.0 |
| 5 | Tags include `reverse_prompt` | 0.5 |
| 6 | `related` >= 3 entries | 0.5 |
**Formula**: `final_score = (sum of score_i * weight_i) / (sum of weight_i) * 10`. Weight total: 5.0.
## Equivalence Sub-Check (C1-C5, from rubric_reverse_prompt_equivalence.md)
| # | Check | Required when |
|---|-------|---------------|
| C1 | Same primary purpose / domain | Comparing 2 instances of the SAME repo |
| C2 | Same top-level architectural components (reasonable variance) | Same as C1 |
| C3 | Same entry-point files, or >60% overlapping subset | Same as C1 |
| C4 | Compatible technology stack | Same as C1 |
| C5 | Same `target_audience` calibration | Same as C1 |
Binary verdict: EQUIVALENT (all 5 substantially met) or NOT-EQUIVALENT (>=1 material failure). Judge kappa target >= 0.70 (ADR 011).
## Actions
| Tier | Threshold | Action |
|------|-----------|--------|
| GOLDEN | >= 9.5 | Publish as a golden calibration example |
| PUBLISH | >= 8.0 | Publish to pool; production-ready draft |
| REVIEW | >= 7.0 | Return with scored dimension feedback; one revision cycle |
| REJECT | < 7.0 | Block from pool; full rewrite required |
## Bypass
| Field | Value |
|-------|-------|
| condition | A `repair` of a real synthesizer artifact where only a truncation/typo is patched (source_url, tree_sha, license fields untouched) |
| approver | Domain lead (N03) must approve in writing |
| audit_log | `records/pool/audits/bypasses.md` with date, approver, reason |
| expiry | 30 days from bypass grant |

## Examples

# Examples -- reverse-prompt-builder
## Golden Example (dry_run mode, documentation purpose)
```yaml
id: p03_rp_example_repo_dry_run
kind: reverse_prompt
pillar: P03
title: "Reverse Prompt: example/todo-app (dry_run)"
source_url: "https://github.com/example/todo-app"
tree_sha: "dry_run-no_extraction"
open_vars: [target_audience, target_runtime, complexity_level]
filled_vars: {target_audience: "junior python dev", target_runtime: "claude-code", complexity_level: "intermediate"}
quality: null
```
Body opens with `## Provenance` disclosing `mode: dry_run`, `byte-deterministic: false`, and `derived_from_unlicensed_source: true` if no LICENSE was verifiable -- never silently omitted.

### S_RELATED: Cross-Reference Check (SOFT)
- [ ] `related:` frontmatter field populated (3-15 entries)
- [ ] `## Related Artifacts` section present in artifact body
- [ ] At least 1 upstream and 1 downstream reference
- Penalty: -0.3 if empty (does not block, encourages wiring)

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[reverse-prompt-builder]] | upstream | 0.50 |
| [[bld_feedback_reverse_prompt]] | downstream | 0.46 |
