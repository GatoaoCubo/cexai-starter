---
kind: collaboration
id: bld_collaboration_eval_metric
pillar: P12
llm_function: COLLABORATE
purpose: How eval_metric-builder works in crews with other builders
quality: null
title: "Collaboration Eval Metric"
version: "1.0.0"
author: wave1_builder_gen_v2
tags: [eval_metric, builder, collaboration]
tldr: "How eval_metric-builder works in crews with other builders"
domain: "eval_metric construction"
created: "2026-04-14"
updated: "2026-04-14"
8f: "F8_collaborate"
keywords: [eval_metric construction, collaboration eval metric, eval_metric, builder, collaboration, crew role  
defines, receives from, data provider, metric specifier, domain expert]
density_score: 0.85
related:
  - bld_collaboration_reranker_config
  - bld_collaboration_reward_model
  - bld_collaboration_cohort_analysis
  - bld_collaboration_ab_test_config
  - bld_collaboration_white_label_config
---
## Crew Role  
Defines and structures individual evaluation metrics, specifying calculation logic, input requirements, and output formats for quantitative assessment.  

## Receives From  
| Builder        | What                  | Format         |  
|----------------|-----------------------|----------------|  
| Data Provider  | Dataset samples       | Parquet/CSV    |  
| Metric Specifier | Metric configuration | JSON schema    |  
| Domain Expert  | Business rules        | Natural language |  

## Produces For  
| Builder        | What                  | Format         |  
|----------------|-----------------------|----------------|  
| Metric Validator | Metric definition   | JSON/YAML      |  
| Calculation Engine | Script            | Python         |  
| Documentation Team | Technical spec    | Markdown       |  
| Validation Team | Test cases          | CSV/JSON       |  

## Boundary  
Does NOT handle composite metrics (benchmark_suite builder), qualitative rubrics (scoring_rubric builder), or data collection (data_provider).

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| bld_collaboration_reranker_config | sibling | 0.31 |
| bld_collaboration_reward_model | sibling | 0.29 |
| bld_collaboration_cohort_analysis | sibling | 0.29 |
| bld_collaboration_ab_test_config | sibling | 0.29 |
| [[bld_orchestration_white_label_config]] | sibling | 0.27 |
