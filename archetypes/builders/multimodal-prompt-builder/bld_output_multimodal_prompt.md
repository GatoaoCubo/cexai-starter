---
kind: output_template
id: bld_output_template_multimodal_prompt
pillar: P05
llm_function: PRODUCE
purpose: Template with vars for multimodal_prompt production
quality: null
title: "Output Template Multimodal Prompt"
version: "1.0.0"
author: wave1_builder_gen_v2
tags: [multimodal_prompt, builder, output_template]
tldr: "Template with vars for multimodal_prompt production"
domain: "multimodal_prompt construction"
created: "2026-04-14"
updated: "2026-04-14"
8f: "F6_produce"
keywords: [multimodal_prompt construction, output template multimodal prompt, multimodal_prompt, builder, output_template, related artifacts, image image_url, replace, upstream, image]
density_score: 0.85
related:
  - kc_multimodal_prompt
---
```yaml
---
id: p03_mmp_{{name}}.md
name: {{name}}
kind: multimodal_prompt
pillar: P03
quality: null
description: {{description}}
content:
  - type: {{media_type}}
    data: {{data}}
---
```

<!-- Replace with prompt name -->
<!-- Replace with descriptive title -->
<!-- Replace with media type (text/image/audio) -->
<!-- Replace with raw data or reference -->

| Type   | Data                              |
|--------|-----------------------------------|
| text   | `{{text_content}}`                 |
| image  | `{{image_url}}`                    |
| code   | `{{code_snippet}}`                 |

```json
{
  "prompt": "{{name}}",
  "elements": [
    {"type": "text", "content": "{{text_content}}"},
    {"type": "image", "url": "{{image_url}}"}
  ]
}
```

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[kc_multimodal_prompt]] | upstream | 0.23 |
| bld_output_template_playground_config | sibling | 0.22 |
| n00_multimodal_prompt_manifest | upstream | 0.22 |
| bld_output_template_onboarding_flow | sibling | 0.21 |
| bld_knowledge_card_multi_modal_config | upstream | 0.18 |
