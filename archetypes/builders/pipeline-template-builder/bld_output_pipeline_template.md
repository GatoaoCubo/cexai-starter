---
kind: output_template
id: bld_output_template_pipeline_template
pillar: P05
llm_function: PRODUCE
purpose: Template with vars for pipeline_template production
quality: null
title: "Output Template Pipeline Template"
version: "1.0.0"
author: n03_builder
tags: [pipeline_template, builder, output_template, scenario_indexed]
tldr: "Template with vars for pipeline_template production"
domain: "pipeline_template construction"
created: "2026-04-18"
updated: "2026-04-18"
8f: "F6_produce"
keywords: [pipeline_template construction, output template pipeline template, pipeline_template, builder, output_template, scenario_indexed, stage sequence, model tier, revision loop
max]
density_score: 0.87
related:
 - pipeline-template-builder
---
```yaml
---
id: p12_pt_{{scenario}}
kind: pipeline_template
pillar: P12
title: "Pipeline: {{scenario_human}}"
scenario: {{scenario}} # new_feature|new_feature_security|bug_fix_unknown|bug_fix_known|refactoring|perf_opt|infra
stages:
 - role: {{role_1}} # canonical role name
 model_tier: {{tier_1}} # low|medium|high|xhigh
 optional: false
 - role: {{role_2}}
 model_tier: {{tier_2}}
 optional: {{optional_2}} # true for conditional stages
 #... additional stages in execution order
revision_loop:
 max_iterations: {{max_iter}} # 1-5, default 3
 escalation_target: {{target}} # user|nucleus|n07
quality_gates:
 mandatory: [reviewer, tester]
 priority_order: [{{p1}}, {{p2}}, {{p3}}] # security>quality>implementation
version: 1.0.0
quality: null
tags: [hermes_origin, pipeline, scenario_indexed, {{scenario}}]
---

## Scenario
{{scenario_description}} <!-- when to use this pipeline, what task type it covers -->

## Stage Sequence
| Order | Role | Model Tier | Optional | Notes |
|-------|------|-----------|----------|-------|
| 1 | {{role_1}} | {{tier_1}} | No | {{note_1}} |
| 2 | {{role_2}} | {{tier_2}} | {{optional_2}} | {{note_2}} |

## Revision Loop
Max iterations: {{max_iter}}. Triggered when quality gate fails. Escalates to {{target}} after max_iter exceeded.

## Quality Gates
Mandatory: reviewer (quality check) + tester (regression check).
Priority: {{p1}} > {{p2}} > {{p3}}.
Gate failure at reviewer: route back to coder/fixer (max {{max_iter}} loops).
Gate failure at tester: route back to previous stage (escalate after max_iter).

## Instantiation
```python
from cex_sdk.pipeline import Pipeline
pl = Pipeline.from_template('p12_pt_`{{scenario}}`.yaml')
result = pl.run(task='`{{task_description}}`', codebase='`{{repo_path}}`')
```

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[p11_qg_pipeline_template]] | downstream | 0.47 |
| [[pipeline-template-builder]] | downstream | 0.46 |
| [[bld_instruction_pipeline_template]] | upstream | 0.46 |
| [[n00_pipeline_template_manifest]] | downstream | 0.43 |
| [[kc_pipeline_template]] | upstream | 0.42 |
