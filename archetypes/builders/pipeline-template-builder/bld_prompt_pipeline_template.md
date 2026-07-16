---
quality: 8.4
quality: 7.9
kind: instruction
id: bld_instruction_pipeline_template
pillar: P03
llm_function: REASON
purpose: Step-by-step production process for pipeline_template
title: "Instruction Pipeline Template"
version: "1.0.0"
author: n03_builder
tags: [pipeline_template, builder, instruction, scenario_indexed]
tldr: "Step-by-step production process for pipeline_template"
domain: "pipeline_template construction"
created: "2026-04-18"
updated: "2026-04-18"
8f: "F6_produce"
keywords: [pipeline_template construction, instruction pipeline template, pipeline_template, builder, instruction, scenario_indexed, "p12_pt_{{scenario}}.yaml", related artifacts, canonical values]
density_score: 0.87
related:
 - bld_schema_pipeline_template
 - pipeline-template-builder
 - n00_pipeline_template_manifest
 - p11_qg_pipeline_template
 - bld_output_template_pipeline_template
---
## Phase 1: RESEARCH
1. Identify target scenario from the 7 canonical values: new_feature, new_feature_security, bug_fix_unknown, bug_fix_known, refactoring, perf_opt, infra.
2. Load the canonical stage sequence for the scenario from bld_knowledge_card_pipeline_template.md.
3. Identify optional stages (e.g., researcher for new_feature_security, security for new_feature_security).
4. Determine model_tier per stage: xhigh for architect/planner; high for analyst/coder/optimizer/refactorer/devops; medium for finder/debugger/fixer/documenter/security; low for reviewer/tester.
5. Confirm revision_loop target (user for interactive, nucleus for autonomous).

## Phase 2: COMPOSE
1. Reference SCHEMA (bld_schema_pipeline_template.md) for required fields.
2. Set scenario to one of the 7 canonical values.
3. Populate stages array in execution order; mark optional stages.
4. Set model_tier for each stage per the tier mapping from Phase 1.
5. Configure revision_loop: max_iterations (default 3), escalation_target.
6. Set quality_gates: mandatory MUST include reviewer and tester; set priority_order.
7. Apply naming: `p12_pt_`{{scenario}}`.yaml` (yaml extension, not.md).
8. Set tags: [hermes_origin, pipeline, scenario_indexed] plus scenario-specific tags.
9. Proofread: stages in correct order, no missing mandatory gates, revision_loop valid.

## Phase 3: VALIDATE
-  scenario is one of the 7 canonical values.
-  stages array has >= 2 entries, all in execution order.
-  every stage has role and model_tier set.
-  quality_gates.mandatory includes reviewer and tester.
-  revision_loop.max_iterations between 1 and 5.
-  priority_order includes security for new_feature_security scenario.
-  File size <= 4096 bytes.

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[bld_schema_pipeline_template]] | downstream | 0.56 |
| [[pipeline-template-builder]] | downstream | 0.53 |
| [[n00_pipeline_template_manifest]] | downstream | 0.48 |
| [[p11_qg_pipeline_template]] | downstream | 0.48 |
| [[bld_output_template_pipeline_template]] | downstream | 0.46 |
