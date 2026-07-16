---
kind: output_template
id: bld_output_template_usage_report
pillar: P05
llm_function: PRODUCE
purpose: Template with vars for usage_report production
quality: null
title: "Output Template Usage Report"
version: "1.0.0"
author: wave1_builder_gen_v2
tags: [usage_report, builder, output_template]
tldr: "Template with vars for usage_report production"
domain: "usage_report construction"
created: "2026-04-14"
updated: "2026-04-14"
8f: "F6_produce"
keywords: [usage_report construction, output template usage report, usage_report, builder, output_template, <!-- insert code snippet here -->, total users, session count, peak load, code example]
density_score: 0.85
related:
  - bld_schema_usage_report
  - bld_architecture_usage_report
  - bld_architecture_eval_metric
---
```yaml
---
id: p07_ur_{{name}}.yaml
name: {{name}}
quality: null
pillars:
  - P07
description: {{description}}
<!-- Replace with report description -->
generated_at: {{generated_at}}
<!-- ISO 8601 date/time -->
data_source: {{data_source}}
<!-- e.g., "CEX API v2.1" -->
---
## Overview
| Metric         | Value       |
|----------------|-------------|
| Total Users    | {{user_count}} |
<!-- Number of active users -->
| Session Count  | {{session_count}} |
<!-- Total sessions recorded -->
| Peak Load      | {{peak_load}} |
<!-- Highest concurrent users -->

## Code Example
```python
def generate_report():
    # `{{code_example}}`
    # Sample logic for report generation
    return {"status": "success"}
```
<!-- Insert code snippet here -->
```

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[bld_output_template_playground_config]] | sibling | 0.20 |
| [[bld_schema_usage_report]] | downstream | 0.19 |
| [[bld_output_template_sales_playbook]] | sibling | 0.17 |
| [[bld_architecture_usage_report]] | downstream | 0.17 |
| [[bld_architecture_eval_metric]] | downstream | 0.17 |
