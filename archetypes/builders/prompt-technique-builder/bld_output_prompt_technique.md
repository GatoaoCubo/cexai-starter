---
kind: output_template
id: bld_output_template_prompt_technique
pillar: P05
llm_function: PRODUCE
purpose: Template with vars for prompt_technique production
quality: null
title: "Output Template Prompt Technique"
version: "1.0.0"
author: wave1_builder_gen_v2
tags: [prompt_technique, builder, output_template]
tldr: "Template with vars for prompt_technique production"
domain: "prompt_technique construction"
created: "2026-04-14"
updated: "2026-04-14"
8f: "F6_produce"
keywords: [prompt_technique construction, output template prompt technique, prompt_technique, builder, output_template, prompt engineering, instruction tuning, related artifacts, downstream, upstream]
density_score: 0.85
related:
  - tpl_instruction
  - p01_kc_prompt_engineering_best_practices
  - p03_ch_{{PIPELINE_SLUG}}
  - bld_architecture_chain
  - p12_wf_builder_8f_pipeline
---
```yaml
---
id: p03_pt_{{name}}.md
name: {{technique_name}}
quality: null
description: {{brief_description}}
category: {{prompt_type}}
example: {{usage_example}}
---
```

<!-- id: Unique identifier following p03_pt_[a-z][a-z0-9_]+.md pattern -->
<!-- name: Technique name (e.g., "Prompt Engineering") -->
<!-- description: 1-2 sentence explanation -->
<!-- category: Type of prompt (e.g., "Instruction Tuning") -->
<!-- example: Sample input/output pair -->

| Technique       | Description                  | Example                      |
|-----------------|------------------------------|------------------------------|
| Chain-of-Thought| Encourages step-by-step reasoning | "Explain how to solve this math problem step by step" |

```python
def apply_prompt_technique(input_text):
    # Apply specific formatting rules
    return f"[\[{input_text}\]]"
```

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[tpl_instruction]] | upstream | 0.26 |
| [[p01_kc_prompt_engineering_best_practices]] | upstream | 0.26 |
| [\[p03_ch_`{{PIPELINE_SLUG}}`\]] | upstream | 0.23 |
| [[bld_architecture_chain]] | downstream | 0.23 |
| [[p12_wf_builder_8f_pipeline]] | downstream | 0.22 |
