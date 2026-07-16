---
kind: quality_gate
id: p11_qg_trace_config
pillar: P11
llm_function: GOVERN
purpose: Golden and anti-examples of trace_config artifacts
pattern: few-shot learning — LLM reads these before producing
quality: null
title: "Gate: trace_config"
version: "1.0.0"
author: "builder_agent"
tags: [quality-gate, trace-config, observability, tracing, P11]
tldr: "Gates for trace_config artifacts: validates exporter, sample rate, capture flags, span attributes, retention, and privacy controls."
domain: "trace_config — execution tracing specifications with exporters, sample rates, capture rules, and retention policies"
created: "2026-04-06"
updated: "2026-04-06"
8f: "F7_govern"
keywords: [sample rates, capture rules, and retention policies, gates for trace_config artifacts, validates exporter, sample rate, capture flags]
density_score: 0.91
related:
  - bld_schema_trace_config
  - bld_knowledge_card_trace_config
  - p10_lr_trace_config_builder
  - bld_output_template_trace_config
  - p11_qg_kind_builder
---
## Quality Gate

# Gate: trace_config
## Definition
| Field     | Value |
|-----------|-------|
| metric    | Composite score from SOFT dimensions + all HARD gates pass |
| threshold | >= 7.0 to publish; >= 9.5 golden |
| operator  | AND (all HARD) + weighted_sum (SOFT) |
| scope     | All artifacts where `kind: trace_config` |
## HARD Gates
All must pass. Any single failure = REJECT regardless of SOFT score.
| ID  | Check | Failure message |
|-----|-------|----------------|
| H01 | Frontmatter parses as valid YAML | "Frontmatter YAML syntax error" |
| H02 | `id` matches `^p07_tc_[a-z][a-z0-9_]+$` | "ID fails trace_config namespace regex" |
| H03 | `id` value equals filename stem | "ID does not match filename" |
| H04 | `kind` equals literal `"trace_config"` | "Kind is not 'trace_config'" |
| H05 | `quality` field is `null` | "Quality must be null at authoring time" |
| H06 | All required fields present: id, kind, pillar, enabled, sample_rate, export_format, export_path, capture_prompts, capture_responses, span_attributes, retention_days, version, created, author, tags | "Missing required field(s)" |
## SOFT Scoring
Dimensions sum to 100%. Score each 0.0-10.0; multiply by weight.
| Dimension | Weight | What to assess |
|-----------|--------|----------------|
| Exporter rationale | 1.0 | Why this exporter fits the target environment and infrastructure |
| Sample rate justification | 1.0 | Rate explained relative to request volume, storage budget, debugging needs |
| Capture rule clarity | 1.0 | Explicit rules for what is/isn't captured with privacy justification |
| Span attribute coverage | 1.0 | 8F function boundaries mapped to spans, token counts included |
| Retention tiering | 1.0 | Hot/warm/cold tiers with days per tier and cleanup strategy |
| Privacy controls | 1.0 | PII redaction, prompt capture policy, consent documentation |
Weight sum: 1.0+1.0+1.0+1.0+1.0+1.0+0.5+0.5+0.5+0.5+1.0+0.5 = 10.0 (100%)
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
| conditions | Development-only trace config where retention and privacy are not yet defined |
| approver | Security lead approval required (written) for any config with capture_prompts: true in production |

## Examples

# Examples: trace-config-builder
## Golden Example
INPUT: "Define a production trace config for CEX 8F pipeline with OTLP export"
OUTPUT:
```yaml
id: p07_tc_production_8f
kind: trace_config
pillar: P07
version: "1.0.0"
created: "2026-04-06"
updated: "2026-04-06"
author: "builder_agent"
enabled: true
```
## Tracing Specification
Production tracing at 10% sample rate via OTLP/gRPC to the configured collector endpoint.
Captures span metadata (nucleus, kind, model, tokens, latency) but NOT prompt or response
content — privacy by default. 10% sample provides statistically meaningful data for
~100 req/day while keeping storage under 500MB/month.
## Capture Rules
| Category | Captured | Rationale |
|----------|----------|-----------|
| Span metadata | YES | Nucleus, kind, function name — lightweight, no PII |
| Token counts | YES | Input/output/total — essential for cost tracking |
| Latency | YES | Per-function and total — performance debugging |
| Error codes | YES | Classified by type — incident response |
| Prompt content | NO | May contain user PII, proprietary data |
| Response content | NO | Large, expensive to store, privacy risk |
## Span Attributes
| Span | Attributes | 8F Mapping |
|------|-----------|-----------|
| `cex.pipeline` | nucleus, kind, intent | Root span — one per build request |
| `cex.8f.f1_constrain` | kind_resolved, pillar, schema_loaded | F1 CONSTRAIN |
| `cex.8f.f2_become` | builder_id, iso_count | F2 BECOME |
| `cex.8f.f3_inject` | knowledge_sources, template_match_pct | F3 INJECT |
| `cex.8f.f4_reason` | section_count, approach | F4 REASON |
| `cex.8f.f5_call` | tools_ready, similar_count | F5 CALL |
## Retention Policy
| Tier | Days | Storage | Query speed | Cleanup |
|------|------|---------|-------------|---------|
| Hot | 7 | Primary store | Fast (indexed) | Auto-rollover |
| Warm | 30 | Compressed | Moderate | Weekly compaction |
| Cold | 90 | Archive | Slow (on-demand) | Quarterly purge |
WHY THIS IS GOLDEN:
- quality: null (H05 pass)
- id matches p07_tc_ pattern (H02 pass)
- kind: trace_config (H04 pass)
- All 8 core fields present: enabled, sample_rate, export_format, export_path, capture_prompts, capture_responses, span_attributes, retention_days (H06 pass)

### S_RELATED: Cross-Reference Check (SOFT)
- [ ] `related:` frontmatter field populated (3-15 entries)
- [ ] `## Related Artifacts` section present in artifact body
- [ ] At least 1 upstream and 1 downstream reference
- Penalty: -0.3 if empty (does not block, encourages wiring)
