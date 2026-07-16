---
kind: output_template
id: bld_output_template_sdk_example
pillar: P05
llm_function: PRODUCE
purpose: Template with vars for sdk_example production
quality: null
title: "Output Template Sdk Example"
version: "1.0.0"
author: wave1_builder_gen_v2
tags: [sdk_example, builder, output_template]
tldr: "Template with vars for sdk_example production"
domain: "sdk_example construction"
created: "2026-04-14"
updated: "2026-04-14"
8f: "F6_produce"
keywords: [sdk_example construction, output template sdk example, sdk_example, builder, output_template, example name, example usage, parameter table, sample response, client client]
density_score: 0.85
related:
  - kc_sdk_example
  - bld_config_sdk_example
  - bld_collaboration_sdk_example
  - n00_sdk_example_manifest
  - bld_schema_sdk_example
---
```yaml
---
id: p04_sdk_{{name}}.md
name: {{SDK Example Name}}
description: {{Brief description of the SDK example}}
quality: null
pillar: P04
category: sdk_example
---
```

<!-- Replace `{{SDK Example Name}}` with the specific SDK example name -->
<!-- Describe the purpose of this SDK example in 1-2 sentences -->
<!-- Ensure ID follows p04_sdk_[a-z][a-z0-9_]+.md pattern -->

### Example Usage
```python
from {{sdk_name}} import Client

client = Client(api_key="your_key")
response = client.get_data(endpoint="/v1/example")
print(response.json())
```

### Parameter Table
| Name      | Type   | Description                  |
|-----------|--------|------------------------------|
| api_key   | string | Authentication credential    |
| endpoint  | string | API endpoint path            |
| timeout   | int    | Request timeout in seconds   |

### Sample Response
```json
{
  "status": "success",
  "data": {"example_field": "value"}
}
```

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[kc_sdk_example]] | upstream | 0.41 |
| [[bld_config_sdk_example]] | downstream | 0.37 |
| [[bld_collaboration_sdk_example]] | downstream | 0.31 |
| [[n00_sdk_example_manifest]] | upstream | 0.28 |
| [[bld_schema_sdk_example]] | downstream | 0.28 |
