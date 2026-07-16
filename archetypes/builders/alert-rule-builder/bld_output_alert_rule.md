---
id: bld_output_alert_rule
kind: output_template
pillar: P05
llm_function: PRODUCE
version: 1.0.0
quality: null
tags: [alert_rule, template, output]
title: "Output Template: alert_rule"
author: builder
tldr: "Alert Rule prompt: output template, formatting rules, and structure"
8f: "F6_produce"
keywords: [output template, alert rule prompt, formatting rules, and structure, alert_rule, template, output, output template checklist, output pattern, related artifacts]
density_score: 0.88
created: "2026-04-17"
updated: "2026-04-17"
related:
  - alert-rule-builder
  - bld_schema_alert_rule
---
# Output Template: alert_rule
```markdown
---
id: ar_{{system_snake}}_{{metric_snake}}
kind: alert_rule
pillar: P09
title: "{{SystemName}} {{MetricName}} {{Condition}} Alert"
version: 1.0.0
quality: null
alert_name: {{PascalCaseAlertName}}
severity: {{critical|warning|info}}
for_duration: "{{ISO_duration}}"
metric_expression: "{{PromQL_or_logical_expression}}"
routing: "{{team_channel_or_policy}}"
tags: [{{system}}, {{metric}}, alert-rule]
---

# {{PascalCaseAlertName}}

## Condition
| Field | Value |
|-------|-------|
| metric | {{metric_name}} |
| expression | `{{metric_expression}}` |
| threshold | {{numeric_value}} {{unit}} |
| for_duration | {{ISO_duration}} |

## Severity & Routing
| Field | Value |
|-------|-------|
| severity | {{critical/warning/info}} |
| routing | {{target}} |
| on_call | {{team_or_person}} |

## Response
- **Automated**: {{auto_action or "none"}}
- **Runbook**: {{runbook_url or "TBD"}}
- **Remediation**: {{steps_or_link}}

## Labels (Prometheus)
```yaml
severity: `{{severity}}`
team: `{{team}}`
service: `{{service}}`
```

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
| [[alert-rule-builder]] | downstream | 0.40 |
| [[bld_schema_alert_rule]] | downstream | 0.36 |
