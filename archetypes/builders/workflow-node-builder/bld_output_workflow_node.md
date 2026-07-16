---
kind: output_template
id: bld_output_template_workflow_node
pillar: P05
llm_function: PRODUCE
purpose: Template with vars for workflow_node production
quality: null
title: "Output Template Workflow Node"
version: "1.0.0"
author: wave1_builder_gen_v2
tags: [workflow_node, builder, output_template]
tldr: "Template with vars for workflow_node production"
domain: "workflow_node construction"
created: "2026-04-14"
updated: "2026-04-14"
8f: "F6_produce"
keywords: [workflow_node construction, output template workflow node, workflow_node, builder, output_template, configuration example, related artifacts, description description, status status, parameters param]
density_score: 0.85
related:
  - p04_function_def_NAME
  - p12_qg_workflow_node
  - bld_output_template_playground_config
  - bld_output_template_input_schema
  - bld_output_template_eval_metric
---
```yaml
---
id: {{id}} <!-- ^p12_wn_[a-z][a-z0-9_]+.md$ -->
name: {{name}} <!-- Node display name -->
description: {{description}} <!-- Purpose/behavior summary -->
type: {{type}} <!-- E.g., "data_transform", "validation" -->
inputs: {{inputs}} <!-- List of required input fields -->
outputs: {{outputs}} <!-- List of generated output fields -->
parameters: {{parameters}} <!-- Configurable options -->
quality: {{quality}} <!-- MUST be: null -->
status: {{status}} <!-- "draft", "review", "production" -->
---
```

**Description**  
`{{description}}` <!-- Explain node's role in workflow -->

**Inputs/Outputs**  
| Name      | Type   | Description                  |
|-----------|--------|------------------------------|
| `{{input1}}` | `{{type}}` | `{{purpose}}`                |
| `{{input2}}` | `{{type}}` | `{{purpose}}`                |

**Configuration Example**  
```yaml
parameters:
  {{param1}}: {{value}} <!-- {{comment}} -->
  {{param2}}: {{value}} <!-- {{comment}} -->
```

**Parameters**  
- `{{param1}}`: `{{description}}` <!-- Configurable setting -->
- `{{param2}}`: `{{description}}` <!-- Default: `{{default}}` -->

**Status**  
`{{status}}` <!-- Current lifecycle stage -->

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[p04_function_def_NAME]] | upstream | 0.27 |
| [[p12_qg_workflow_node]] | downstream | 0.27 |
| [[bld_output_template_playground_config]] | sibling | 0.26 |
| [[bld_output_template_input_schema]] | sibling | 0.23 |
| [[bld_output_template_eval_metric]] | sibling | 0.22 |
