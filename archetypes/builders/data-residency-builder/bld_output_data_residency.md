---
kind: output_template
id: bld_output_template_data_residency
pillar: P05
llm_function: PRODUCE
purpose: Template with vars for data_residency production
quality: null
title: "Output Template Data Residency"
version: "1.0.0"
author: wave1_builder_gen_v2
tags: [data_residency, builder, output_template]
tldr: "Template with vars for data_residency production"
domain: "data_residency construction"
created: "2026-04-14"
updated: "2026-04-14"
8f: "F6_produce"
keywords: [data_residency construction, output template data residency, data_residency, builder, output_template, audit logs, acme corp, related artifacts, regions compliance, gdpr ccpa]
density_score: 0.85
related:
  - p09_qg_data_residency
  - p01_kc_data_residency
  - bld_knowledge_card_data_residency
  - data-residency-builder
  - bld_instruction_data_residency
---
```yaml
---
id: p09_dr_{{name}}.md
name: {{name}}
description: {{description}}
regions: {{regions}}
compliance: {{compliance}}
data_ownership: {{data_ownership}}
encryption: {{encryption}}
audit_logs: {{audit_logs}}
quality: null
---
```

<!-- id: Generated filename following p09_dr_[a-z][a-z0-9_]+.yaml pattern -->
<!-- name: Short identifier for this data residency policy -->
<!-- description: Brief explanation of policy scope -->
<!-- regions: Array of ISO country codes where data resides -->
<!-- compliance: Array of regulatory standards (e.g., GDPR, CCPA) -->
<!-- data_ownership: Legal entity responsible for data -->
<!-- encryption: Boolean indicating if data is encrypted at rest -->
<!-- audit_logs: Boolean indicating if audit trails are enabled -->
<!-- quality: Always set to null -->

| Region | Compliance | Encryption | Audit Logs |
|--------|------------|------------|------------|
| EU     | GDPR       | true       | true       |
| US     | CCPA       | true       | false      |

```python
# Example data residency configuration
residency_config = {
    "regions": ["US", "EU"],
    "compliance": ["GDPR", "CCPA"],
    "data_ownership": "Acme Corp",
    "encryption": True,
    "audit_logs": False
}
```

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[p09_qg_data_residency]] | downstream | 0.42 |
| [[p01_kc_data_residency]] | downstream | 0.36 |
| [[bld_knowledge_card_data_residency]] | upstream | 0.34 |
| [[data-residency-builder]] | downstream | 0.34 |
| [[bld_instruction_data_residency]] | upstream | 0.32 |
