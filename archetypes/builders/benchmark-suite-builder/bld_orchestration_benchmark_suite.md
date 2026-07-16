---
kind: collaboration
id: bld_collaboration_benchmark_suite
pillar: P12
llm_function: COLLABORATE
purpose: How benchmark_suite-builder works in crews with other builders
quality: null
title: "Collaboration Benchmark Suite"
version: "1.0.0"
author: wave1_builder_gen_v2
tags: [benchmark_suite, builder, collaboration]
tldr: "How benchmark_suite-builder works in crews with other builders"
domain: "benchmark_suite construction"
created: "2026-04-14"
updated: "2026-04-14"
8f: "F8_collaborate"
keywords: [benchmark_suite construction, collaboration benchmark suite, benchmark_suite, builder, collaboration, crew role  
coordinates, receives from, benchmark author, config manager, data provider]
density_score: 0.85
related:
  - bld_collaboration_memory_benchmark
  - bld_collaboration_eval_framework
  - bld_config_benchmark_suite
  - bld_collaboration_eval_metric
  - bld_collaboration_cohort_analysis
---
## Crew Role  
Coordinates integration of multiple benchmarks into cohesive suites, ensuring consistency, versioning, and dependency management across components.  

## Receives From  
| Builder | What | Format |  
|---|---|---|  
| Benchmark Author | Individual benchmarks | YAML |  
| Config Manager | Configuration parameters | JSON |  
| Data Provider | Datasets | CSV |  

## Produces For  
| Builder | What | Format |  
|---|---|---|  
| Suite Validator | Benchmark suite | JSON |  
| QA Team | Validation report | Markdown |  
| Dev Team | Dependency graph | DOT |  

## Boundary  
Does NOT execute benchmarks (Benchmark Runner handles execution), analyze results (Eval Framework handles analysis), or manage user requests (User Interface handles direct interactions).

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[bld_collaboration_memory_benchmark]] | sibling | 0.36 |
| [[bld_collaboration_eval_framework]] | sibling | 0.35 |
| [[bld_config_benchmark_suite]] | upstream | 0.30 |
| [[bld_collaboration_eval_metric]] | sibling | 0.29 |
| [[bld_collaboration_cohort_analysis]] | sibling | 0.28 |
