---
kind: collaboration
id: bld_collaboration_usage_report
pillar: P12
llm_function: COLLABORATE
purpose: How usage_report-builder works in crews with other builders
quality: null
title: "Collaboration Usage Report"
version: "1.0.0"
author: wave1_builder_gen_v2
tags: [usage_report, builder, collaboration]
tldr: "How usage_report-builder works in crews with other builders"
domain: "usage_report construction"
created: "2026-04-14"
updated: "2026-04-14"
8f: "F8_collaborate"
keywords: [usage_report construction, collaboration usage report, usage_report, builder, collaboration, crew role  
aggregates, receives from, data collector, produces for, alert system]
density_score: 0.85
related:
  - bld_config_usage_report
  - usage-report-builder
---
## Crew Role  
Aggregates, normalizes, and formats usage analytics data into actionable reports for stakeholders. Focuses on query patterns, resource consumption, and user activity metrics.  

## Receives From  
| Builder       | What                  | Format      |  
|---------------|-----------------------|-------------|  
| Data Collector| Raw usage logs        | JSON        |  
| API Gateway   | Request metadata      | Protobuf    |  
| Analytics DB  | Pre-aggregated metrics| Parquet     |  

## Produces For  
| Builder       | What                  | Format      |  
|---------------|-----------------------|-------------|  
| Dashboard     | Interactive reports   | HTML/JS     |  
| BI Tool       | Exported datasets     | CSV         |  
| Alert System  | Anomaly summaries     | JSON        |  

## Boundary  
Does NOT enforce cost limits (handled by cost_analyzer) or configure telemetry (handled by trace_collector). Excludes infrastructure health or error tracking.

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[bld_config_usage_report]] | upstream | 0.28 |
| [[usage-report-builder]] | upstream | 0.27 |
