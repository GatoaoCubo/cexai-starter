---
kind: output_template
id: bld_output_template_eval_metric
pillar: P05
llm_function: PRODUCE
purpose: Template with vars for eval_metric production
quality: null
title: "Output Template Eval Metric"
version: "1.0.0"
author: wave1_builder_gen_v2
tags: [eval_metric, builder, output_template]
tldr: "Template with vars for eval_metric production"
domain: "eval_metric construction"
created: "2026-04-14"
updated: "2026-04-14"
8f: "F6_produce"
keywords: [eval_metric construction, output template eval metric, eval_metric, builder, output_template, related artifacts, param description, description, sibling, param]
density_score: 0.85
related:
  - bld_config_eval_metric
---
```yaml
---
id: p07_em_{{metric_name}}.md
name: {{metric_name}}
description: {{brief_description_of_metric}}
type: eval_metric
quality: null
parameters:
  - name: {{param1}}
    description: {{param1_description}}
examples:
  - {{example_usage}}
---
```

<!-- metric_name: Replace with lowercase alphanumeric name (e.g., 'accuracy') -->
<!-- brief_description_of_metric: 1-2 sentence summary of metric purpose -->
<!-- param1: First parameter name (e.g., 'threshold') -->
<!-- param1_description: Explanation of parameter's role -->
<!-- example_usage: Code snippet showing metric application -->

| Metric         | Description                  | Type      |
|----------------|------------------------------|-----------|
| p07_em_accuracy | Measures classification correctness | eval_metric |

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| bld_output_template_workflow_node | sibling | 0.31 |
| bld_output_template_playground_config | sibling | 0.27 |
| [[bld_config_eval_metric]] | downstream | 0.26 |
| bld_output_template_sandbox_spec | sibling | 0.21 |
| bld_output_template_judge_config | sibling | 0.21 |
