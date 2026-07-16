---
kind: collaboration
id: bld_collaboration_memory_benchmark
pillar: P12
llm_function: COLLABORATE
purpose: How memory_benchmark-builder works in crews with other builders
quality: null
title: "Collaboration Memory Benchmark"
version: "1.0.0"
author: wave1_builder_gen_v2
tags: [memory_benchmark, builder, collaboration]
tldr: "How memory_benchmark-builder works in crews with other builders"
domain: "memory_benchmark construction"
created: "2026-04-14"
updated: "2026-04-14"
8f: "F8_collaborate"
keywords: [memory_benchmark construction, collaboration memory benchmark, memory_benchmark, builder, collaboration, crew role  
generates, receives from, produces for, boundary  
does, related artifacts]
density_score: 0.85
related:
  - bld_collaboration_memory_scope
  - bld_collaboration_benchmark_suite
  - bld_collaboration_memory_type
  - bld_output_template_memory_benchmark
  - n00_memory_benchmark_manifest
---
## Crew Role  
Generates and validates memory-specific benchmark tests, ensuring alignment with evaluation criteria and data integrity.  

## Receives From  
| Builder       | What                  | Format  |  
|---------------|-----------------------|---------|  
| scenario_gen | Test scenarios        | JSON    |  
| config_mgr    | Memory config params  | YAML    |  
| data_prov     | Synthetic memory data | CSV     |  

## Produces For  
| Builder       | What                  | Format      |  
|---------------|-----------------------|-------------|  
| eval_suite    | Memory benchmark suite| JSON        |  
| report_gen    | Evaluation report     | Markdown    |  
| metrics_agg   | Performance metrics   | Parquet     |  

## Boundary  
Does NOT handle system architecture design (memory_architecture) or general-purpose benchmarks (benchmark_suite).

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[bld_collaboration_memory_scope]] | sibling | 0.38 |
| [[bld_collaboration_benchmark_suite]] | sibling | 0.34 |
| [[bld_collaboration_memory_type]] | sibling | 0.34 |
| [[bld_output_template_memory_benchmark]] | upstream | 0.30 |
| [[n00_memory_benchmark_manifest]] | upstream | 0.30 |
