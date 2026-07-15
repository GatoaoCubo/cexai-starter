---
kind: quality_gate
id: p11_qg_lens
pillar: P11
llm_function: GOVERN
purpose: Golden and anti-examples of lens artifacts
pattern: few-shot learning — LLM reads these before producing
quality: null
title: "Gate: Lens"
version: "1.0.0"
author: builder_agent
tags:
  - "quality-gate"
  - "lens"
  - "perspective"
  - "P02"
  - "filter"
tldr: "Quality gate for lens artifacts: enforces declared bias, scoped focus, and explicit applies_to list."
domain: lens
created: "2026-03-27"
updated: "2026-03-27"
8f: "F7_govern"
keywords:
  - "enforces declared bias"
  - "scoped focus"
  - "and explicit applies_to list"
  - "quality-gate"
  - "lens"
  - "perspective"
  - "filter"
density_score: 0.85
related:
  - lens-builder
  - p03_ins_lens
  - bld_architecture_lens
  - bld_knowledge_card_lens
  - bld_schema_lens
---
## Quality Gate

# Gate: Lens
## Definition
A `lens` is a perspective filter applied to artifact evaluation or routing. It amplifies certain attributes and suppresses others without executing logic. Gates here prevent lenses from claiming capabilities (which belong to agents), enforce honest bias declaration, and require a concrete `applies_to` scope so the lens is never applied indiscriminately.
## HARD Gates
All HARD gates must pass. Any single failure sets score to 0 and blocks publish.
| ID  | Check | Failure consequence |
|-----|-------|---------------------|
| H01 | YAML frontmatter parses without error | Artifact unparseable by tooling |
| H02 | `id` matches `^p02_lens_[a-z][a-z0-9_]+$` | Namespace violation — not discoverable |
| H03 | `id` equals filename stem exactly | Brain search failure — id/file mismatch |
| H04 | `kind` == literal string `"lens"` | Type integrity failure |
| H05 | `quality` == `null` | Self-scoring violation — pool metric corruption |
| H06 | All required fields present and non-empty (`id`, `kind`, `pillar`, `version`, `created`, `updated`, `author`, `perspective`, `applies_to`, `bias`, `tags`, `tldr`) | Incomplete artifact |
## SOFT Scoring
Weights sum to 100%. Each dimension scores 0 or its full weight.
| ID  | Dimension | Weight | Criteria |
|-----|-----------|--------|----------|
| S01 | tldr quality | 1.0 | `tldr` <= 160 chars, states what the lens amplifies, not just its name |
| S02 | Focus narrowly scoped | 1.0 | Focus section targets one concern — not "quality in general" |
| S03 | Bias declaration honest | 1.0 | Bias names what the lens systematically over- or under-weights |
| S04 | `applies_to` types valid | 1.0 | Each item matches a known artifact `kind` in the registry |
| S05 | Interpretation criteria clear | 1.0 | Body defines what score high vs. low on this lens means |
| S06 | Weight or priority defined | 0.5 | `weight` or `priority` field present and numeric |
## Actions
| Score | Tier | Action |
|-------|------|--------|
| >= 9.5 | GOLDEN | Publish to pool + record in memory |
| >= 8.0 | PUBLISH | Commit to pool |
| >= 7.0 | REVIEW | Acceptable with documented improvement items |
| < 7.0 | REJECT | Revise and resubmit — do not publish |
| 0 (HARD fail) | REJECTED | Fix failing HARD gate(s) first |
## Bypass
Bypasses are logged and expire automatically.
| Field | Value |
|-------|-------|
| condition | Lens is experimental — `applies_to` scope cannot be confirmed until integration testing complete |
| approver | P02 domain owner |
| audit_log | Entry required in `records/governance/bypass_log.md` with gate ID, lens id, and test plan reference |
| expiry | 7 days — `applies_to` must be confirmed or lens moves to DRAFT state |
H01 and H05 cannot be bypassed under any condition.

## Examples

# Examples: lens-builder
## Golden Example
INPUT: "Create uma lens de cost para avaliar model_cards e embedding_configs"
OUTPUT:
```yaml
id: p02_lens_cost_efficiency
kind: lens
pillar: P02
version: "1.0.0"
created: "2026-03-26"
updated: "2026-03-26"
author: "builder_agent"
perspective: "cost_efficiency"
applies_to: [model_card, embedding_config, agent_card]
focus: "Pricing, token costs, and cost-per-task efficiency"
filters: [pricing, context_window, tokens_per_second, batch_size, dimensions]
bias: "Favors lower cost-per-output-token when quality is comparable"
interpretation: "Ranks artifacts by cost efficiency ratio: quality / cost. Higher = better."
weight: 0.8
priority: 1
scope: "LLM selection, agent_group model routing, embedding provider choice"
domain: "infrastructure-optimization"
quality: 8.8
tags: [lens, cost, efficiency, pricing, model-selection]
tldr: "Cost efficiency lens — evaluates artifacts by quality-to-cost ratio for infra decisions."
```
## Perspective
Evaluates artifacts through cost efficiency: what is the quality-per-dollar ratio?
Applies to model_cards (LLM pricing), embedding_configs (vector cost), agent_cards (model allocation).
## Filters
- **pricing**: input/output token costs, batch discounts, free tiers
- **context_window**: cost per context unit (larger window = fewer calls)
- **tokens_per_second**: throughput efficiency (faster = lower wall-clock cost)
- **batch_size**: bulk processing economics
## Application
1. Read the artifact's cost-related fields
2. Calculate quality-to-cost ratio where applicable
3. Compare against alternatives in the same kind
4. Flag artifacts where cost exceeds 2x the cheapest comparable option
## Limitations
- Does not evaluate quality directly (that is scoring_rubric P07)
- Ignores latency preferences (a speed lens would cover that)
- May undervalue high-cost options justified for critical tasks

### S_RELATED: Cross-Reference Check (SOFT)
- [ ] `related:` frontmatter field populated (3-15 entries)
- [ ] `## Related Artifacts` section present in artifact body
- [ ] At least 1 upstream and 1 downstream reference
- Penalty: -0.3 if empty (does not block, encourages wiring)
