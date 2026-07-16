---
kind: output_template
id: bld_output_template_conformity_assessment
pillar: P05
llm_function: PRODUCE
purpose: Fill-in-the-blanks template for producing a complete Annex-IV conformity assessment artifact
quality: null
title: "Conformity Assessment Builder -- Output Template"
version: "1.0.0"
author: wave7_n05
tags: [conformity_assessment, builder, output_template]
tldr: "Annex-IV structured template with all 7 required categories and EU-AI-Act citations"
domain: "conformity_assessment construction"
created: "2026-04-14"
updated: "2026-04-14"
8f: "F6_produce"
keywords: [conformity_assessment construction, conformity_assessment, builder, output_template, conformity assessment builder, output template, usage
copy, flag aug, conformity assessment, aug- deadline]
density_score: 0.85
related:
  - bld_config_conformity_assessment
  - bld_collaboration_conformity_assessment
  - bld_quality_gate_conformity_assessment
  - bld_collaboration_prompt_template
  - bld_memory_conformity_assessment
---
# Conformity Assessment Builder -- Output Template
## Usage
Copy from "BEGIN ARTIFACT TEMPLATE" to "END ARTIFACT TEMPLATE".
Replace every `{{PLACEHOLDER}}` with actual content.
Do NOT leave any `{{PLACEHOLDER}}` unfilled in the final artifact.
Flag Aug-2026 deadline items with [AUG-2026-DEADLINE].
---
## BEGIN ARTIFACT TEMPLATE
```markdown
---
kind: conformity_assessment
id: p11_ca_{{SYSTEM_SLUG}}
pillar: P11
title: "Conformity Assessment -- {{SYSTEM_NAME}}"
system_name: "{{SYSTEM_NAME}}"
system_version: "{{SYSTEM_VERSION}}"
provider_name: "{{PROVIDER_NAME}}"
```
## END ARTIFACT TEMPLATE
---

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[bld_config_conformity_assessment]] | downstream | 0.24 |
| [[bld_collaboration_conformity_assessment]] | downstream | 0.24 |
| [[bld_quality_gate_conformity_assessment]] | downstream | 0.20 |
| [[bld_collaboration_prompt_template]] | upstream | 0.20 |
| [[bld_memory_conformity_assessment]] | downstream | 0.20 |
