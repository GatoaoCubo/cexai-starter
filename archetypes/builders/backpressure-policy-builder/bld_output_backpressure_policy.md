---
quality: null
quality: null
kind: output_template
id: bld_output_template_backpressure_policy
pillar: P05
llm_function: PRODUCE
purpose: Template with {{vars}} that the LLM fills to produce a backpressure_policy artifact
pattern: every field here exists in SCHEMA.md -- template derives, never invents
title: "Output Template Backpressure Policy"
version: "1.0.0"
author: n03_builder
tags: [backpressure_policy, builder, output_template]
tldr: "Fill-in template for backpressure_policy: overflow strategy, buffer, shed threshold, watermarks, batch size."
domain: "backpressure policy construction"
created: "2026-04-17"
updated: "2026-04-17"
8f: "F6_produce"
keywords: [template with, backpressure policy construction, output template backpressure policy, fill-in template for backpressure_policy, overflow strategy, shed threshold, batch size, backpressure_policy, builder, output_template]
density_score: 0.90
related:
  - p11_qg_backpressure_policy
  - bld_instruction_backpressure_policy
  - bld_schema_backpressure_policy
  - bld_architecture_backpressure_policy
  - backpressure-policy-builder
---
# Output Template: backpressure_policy

```yaml
id: p09_bp_{{scope_slug}}
kind: backpressure_policy
pillar: P09
version: "1.0.0"
created: "{{YYYY-MM-DD}}"
updated: "{{YYYY-MM-DD}}"
author: "{{who_produced}}"
overflow_strategy: "{{DROP_LATEST|DROP_OLDEST|BUFFER|THROTTLE|ERROR}}"
buffer_size: {{positive_integer}}
shed_threshold: {{float_0_to_1}}
high_watermark: {{integer_lte_buffer_size}}
low_watermark: {{integer_lt_high_watermark}}
request_batch_size: {{positive_integer}}
monitored_queue: "{{queue_or_channel_name}}"
quality: null
tags: [backpressure_policy, {{scope_slug}}, {{tag_3}}]
tldr: "{{dense_summary_max_160ch}}"
```

## Overview
`{{producer_consumer_context_why_backpressure_needed_1_to_2_sentences}}`

## Strategy
**Overflow strategy**: `{{overflow_strategy}}`
Rationale: `{{why_this_strategy_fits_this_use_case}}`

| Strategy | Behavior | Data loss risk |
|----------|----------|---------------|
| `{{overflow_strategy}}` | `{{what_happens_when_applied}}` | `{{loss_risk_level}}` |

## Thresholds
- Buffer capacity: `{{buffer_size}}` items
- Shedding begins at: `{{shed_threshold * 100}}`% (`{{buffer_size * shed_threshold}}` items)
- Active backpressure (high watermark): `{{high_watermark}}` items
- Normal flow resumes (low watermark): `{{low_watermark}}` items

## Flow
- Demand signal batch size: `{{request_batch_size}}` items per request
- Protocol: `{{Reactive Streams|polling|push-pull}}`
- Queue monitored: `{{monitored_queue}}`
- Consumer lag SLA: `{{acceptable_lag_description}}`

## Output Template Checklist

- Verify output format matches target kind schema
- Validate all frontmatter fields are present in template
- Cross-reference with eval gate for completeness
- Test template rendering with sample data before publishing

## Output Pattern

```yaml
# Output validation
format_match: true
frontmatter_complete: true
eval_gate_aligned: true
sample_rendered: true
```

```bash
python _tools/cex_compile.py {FILE}
python _tools/cex_doctor.py --scope {BUILDER}
```

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[p11_qg_backpressure_policy]] | downstream | 0.52 |
| [[bld_instruction_backpressure_policy]] | upstream | 0.46 |
| [[bld_schema_backpressure_policy]] | downstream | 0.46 |
| [[bld_architecture_backpressure_policy]] | downstream | 0.44 |
| [[backpressure-policy-builder]] | downstream | 0.41 |
