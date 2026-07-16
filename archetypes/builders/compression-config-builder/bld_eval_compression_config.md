---
kind: quality_gate
id: p11_qg_compression_config
pillar: P11
llm_function: GOVERN
purpose: Golden and anti-examples of compression_config artifacts
pattern: few-shot learning — LLM reads these before producing
quality: null
title: "Gate: compression_config"
version: "1.0.0"
author: "builder_agent"
tags: [quality-gate, compression-config, context-window, token-reduction, P11]
tldr: "Gates for compression_config artifacts: validates strategy completeness, trigger ratio range, preserve types, decay weights, and pipeline ordering."
domain: "compression_config — context compression strategies with trigger ratios, preserve types, decay weights, and tiered pipelines"
created: "2026-04-06"
updated: "2026-04-06"
8f: "F7_govern"
keywords: [preserve types, decay weights, and tiered pipelines, gates for compression_config artifacts, validates strategy completeness, trigger ratio range, and pipeline ordering]
density_score: 0.90
related:
  - compression-config-builder
  - bld_knowledge_card_compression_config
  - p10_lr_compression_config_builder
  - bld_instruction_compression_config
  - bld_output_template_compression_config
---
## Quality Gate

# Gate: compression_config
## Definition
| Field     | Value |
|-----------|-------|
| metric    | Composite score from SOFT dimensions + all HARD gates pass |
| threshold | >= 7.0 to publish; >= 9.5 golden |
| operator  | AND (all HARD) + weighted_sum (SOFT) |
| scope     | All artifacts where `kind: compression_config` |
## HARD Gates
All must pass. Any single failure = REJECT regardless of SOFT score.
| ID  | Check | Failure message |
|-----|-------|----------------|
| H01 | Frontmatter parses as valid YAML | "Frontmatter YAML syntax error" |
| H02 | `id` matches `^p10_cc_[a-z][a-z0-9_]+$` | "ID fails compression_config namespace regex" |
| H03 | `id` value equals filename stem | "ID does not match filename" |
| H04 | `kind` equals literal `"compression_config"` | "Kind is not 'compression_config'" |
| H05 | `quality` field is `null` | "Quality must be null at authoring time" |
| H06 | All required fields present: id, kind, pillar, strategy, trigger_ratio, preserve_types, max_summary_tokens, min_context_tokens, decay_weights, version, created, author, tags | "Missing required field(s)" |
## SOFT Scoring
Dimensions sum to 100%. Score each 0.0-10.0; multiply by weight.
| Dimension | Weight | What to assess |
|-----------|--------|----------------|
| Strategy rationale | 1.0 | Why this strategy fits the target agent's workload |
| Preserve types completeness | 1.0 | All structural message types (system_prompt, tool_def, pinned) included |
| Decay weight coverage | 1.0 | Decay weights defined for all message types in the agent's vocabulary |
| Pipeline ordering | 1.0 | Stages ordered from least lossy to most lossy (summarize before drop) |
| Trigger ratio justification | 0.5 | Ratio explained relative to model context window and task length |
| Target ratio clarity | 0.5 | Post-compression target specified and achievable |
Weight sum: 1.0+1.0+1.0+1.0+0.5+0.5+1.0+1.0+0.5+1.0+0.5+0.5 = 10.0 (100%)
## Actions
| Score | Tier | Action |
|-------|------|--------|
| >= 9.5 | GOLDEN | Publish to pool as golden exemplar |
| >= 8.0 | PUBLISH | Publish to pool |
| >= 7.0 | REVIEW | Flag for human review before publish |
| < 7.0  | REJECT | Return to author with failure report |
## Bypass
| Field | Value |
|-------|-------|
| conditions | Experimental compression strategy being A/B tested where full decay weights are not yet calibrated |
| approver | Nucleus lead approval required (written); preserve_types never bypassed |

## Examples

# Examples: compression-config-builder
## Golden Example
INPUT: "Define a balanced compression strategy for a long-running research agent"
OUTPUT:
```yaml
id: p10_cc_balanced_research
kind: compression_config
pillar: P10
version: "1.0.0"
created: "2026-04-06"
updated: "2026-04-06"
author: "builder_agent"
strategy: tiered
```
## Strategy Specification
Tiered 3-stage compression for research agents that accumulate large context through
iterative tool calls. Triggers at 85% context utilization. Target: reduce to 60%.
Stage order: semantic dedup → summarize old assistant messages → truncate oldest observations.
## Preserve Types
- system_prompt: structural identity — never compressed
- tool_definition: function schemas required for tool calls — never compressed
- pinned: user-flagged messages with persistent relevance — never compressed
## Decay Weights
| Message Type | Base Priority | Age Decay (per 1K tokens of distance) | Rationale |
|-------------|--------------|---------------------------------------|-----------|
| system_prompt | 1.00 | 0.00 (no decay) | Structural — always relevant |
| tool_definition | 1.00 | 0.00 (no decay) | Required for function calling |
| pinned | 0.95 | 0.01 | User-flagged, slow decay |
| tool_result | 0.80 | 0.05 | Recent results critical, old results less so |
| user | 0.70 | 0.03 | User messages provide task context |
| assistant | 0.50 | 0.08 | Responses can be reconstructed from context |
| observation | 0.40 | 0.10 | Superseded by newer observations |
## Compression Pipeline
1. **Semantic Dedup** (target: -10%): remove near-duplicate assistant responses and repeated observations
2. **Summarize** (target: -15%): condense assistant messages older than 4K tokens into summaries (max 2048 tokens)
3. **Truncate Oldest** (target: remaining): drop lowest-priority messages by decay_weight * age_factor until target_ratio reached
WHY THIS IS GOLDEN:
- quality: null (H05 pass)
- id matches p10_cc_ pattern (H02 pass)
- kind: compression_config (H04 pass)
- All 6 core fields present: strategy, trigger_ratio, preserve_types, max_summary_tokens, min_context_tokens, decay_weights (H06 pass)

### S_RELATED: Cross-Reference Check (SOFT)
- [ ] `related:` frontmatter field populated (3-15 entries)
- [ ] `## Related Artifacts` section present in artifact body
- [ ] At least 1 upstream and 1 downstream reference
- Penalty: -0.3 if empty (does not block, encourages wiring)
