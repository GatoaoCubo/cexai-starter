---
kind: output_template
id: bld_output_template_legal_vertical
pillar: P05
llm_function: PRODUCE
purpose: Template with vars for legal_vertical production
quality: null
title: "Output Template Legal Vertical"
version: "1.0.0"
author: wave1_builder_gen_v2
tags: [legal_vertical, builder, output_template]
tldr: "Template with vars for legal_vertical production"
domain: "legal_vertical construction"
created: "2026-04-14"
updated: "2026-04-14"
8f: "F6_produce"
keywords: [legal_vertical construction, output template legal vertical, legal_vertical, builder, output_template, legal vertical compliance framework, key requirements, regulatory body, required documentation, sample legal clause]
density_score: 0.85
related:
  - n00_legal_vertical_manifest
  - bld_schema_legal_vertical
  - n00_compliance_framework_manifest
  - bld_config_legal_vertical
  - bld_output_template_govtech_vertical
---
```markdown
---
id: p01_lv_{{legal_entity}}.md
pillar: P01
type: legal_vertical
quality: null
naming: p01_lv_{{legal_entity}}
required_fields:
  - compliance_framework
  - jurisdiction
  - regulatory_body
  - documentation_template
---
## Legal Vertical Compliance Framework

### Key Requirements
| Jurisdiction | Regulatory Body       | Required Documentation         |
|--------------|-----------------------|--------------------------------|
| {{jurisdiction}} | {{regulatory_body}} | {{documentation_template}}   |

### Sample Legal Clause
```yaml
compliance_framework:
  name: "`{{compliance_framework}}`"
  scope: "covers `{{jurisdiction}}` regulations"
  enforcement: "`{{regulatory_body}}` audits required"
```

<!-- jurisdiction: e.g., "EU", "US", "APAC" -->
<!-- regulatory_body: e.g., "ESMA", "SEC", "FCA" -->
<!-- documentation_template: e.g., "KYC Form v2.1", "AML Policy 2023" -->
<!-- compliance_framework: e.g., "MiFID II", "Dodd-Frank", "MAS 6" -->
```

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[n00_legal_vertical_manifest]] | upstream | 0.34 |
| [[bld_schema_legal_vertical]] | downstream | 0.31 |
| [[n00_compliance_framework_manifest]] | downstream | 0.29 |
| [[bld_config_legal_vertical]] | downstream | 0.25 |
| [[bld_output_template_govtech_vertical]] | sibling | 0.24 |
