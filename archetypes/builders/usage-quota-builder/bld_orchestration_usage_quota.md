---
kind: collaboration
id: bld_collaboration_usage_quota
pillar: P12
llm_function: COLLABORATE
purpose: How usage_quota-builder works in crews with other builders
quality: null
title: "Collaboration Usage Quota"
version: "1.0.0"
author: wave1_builder_gen_v2
tags: [usage_quota, builder, collaboration]
tldr: "How usage_quota-builder works in crews with other builders"
domain: "usage_quota construction"
created: "2026-04-14"
updated: "2026-04-14"
8f: "F8_collaborate"
keywords: [usage_quota construction, collaboration usage quota, usage_quota, builder, collaboration, rate limit builder, cost budget manager, crew role  
defines, receives from, quota policy validator]
density_score: 0.85
related:
  - usage-quota-builder
---
## Crew Role  
Defines and enforces usage quotas across services, ensuring compliance with predefined limits and policies.  

## Receives From  
| Builder         | What                  | Format  |  
|-----------------|-----------------------|---------|  
| Quota Policy Validator | Validated quota policies | JSON    |  
| Usage Tracker   | Real-time usage metrics | CSV     |  
| Config Manager  | Configuration updates | YAML    |  

## Produces For  
| Builder         | What                  | Format  |  
|-----------------|-----------------------|---------|  
| Quota Enforcer  | Enforceable quota specs | JSON    |  
| Usage Dashboard | Aggregated quota data | CSV     |  
| Audit Log       | Enforcement records   | JSON    |  

## Boundary  
Does NOT handle rate_limit_config (RPM) or cost_budget (dollars). Rate limits are managed by `Rate Limit Builder`; cost budgets by `Cost Budget Manager`. Does NOT enforce quotas directly—only generates specs for enforcers.

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[usage-quota-builder]] | upstream | 0.43 |
