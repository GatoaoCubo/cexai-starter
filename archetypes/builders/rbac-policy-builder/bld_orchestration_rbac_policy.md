---
kind: collaboration
id: bld_collaboration_rbac_policy
pillar: P12
llm_function: COLLABORATE
purpose: How rbac_policy-builder works in crews with other builders
quality: null
title: "Collaboration Rbac Policy"
version: "1.0.0"
author: wave1_builder_gen_v2
tags: [rbac_policy, builder, collaboration]
tldr: "How rbac_policy-builder works in crews with other builders"
domain: "rbac_policy construction"
created: "2026-04-14"
updated: "2026-04-14"
8f: "F8_collaborate"
keywords: [rbac_policy construction, collaboration rbac policy, rbac_policy, builder, collaboration, crew role  
designs, based access control, receives from, produces for, boundary  
does]
density_score: 0.85
related:
  - rbac-policy-builder
---
## Crew Role  
Designs, validates, and maintains Role-Based Access Control (RBAC) policies to enforce least-privilege access models across systems.  

## Receives From  
| Builder                    | What                              | Format  |  
|----------------------------|-----------------------------------|---------|  
| permission-builder         | Permission definitions + scopes   | YAML    |  
| guardrail-builder          | Safety boundaries + deny rules    | YAML    |  
| env-config-builder         | Environment and tenant context    | YAML    |  

## Produces For  
| Builder                    | What                              | Format  |  
|----------------------------|-----------------------------------|---------|  
| agent-profile-builder      | Role bindings for agent personas  | YAML    |  
| sandbox-config-builder     | Sandbox access control rules      | YAML    |  
| compliance-framework-builder | RBAC policy compliance mapping  | YAML    |  

## Boundary  
Does NOT handle secret storage (secret-config-builder), SSO federation (sso-config-builder), or authentication flows. Policy enforcement integration is handled downstream by the agent runtime.

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[bld_orchestration_permission]] | sibling | 0.30 |
| [[bld_orchestration_secret_config]] | sibling | 0.28 |
| [[rbac-policy-builder]] | upstream | 0.25 |
| bld_collaboration_agent_computer_interface | sibling | 0.23 |
| [[bld_orchestration_path_config]] | sibling | 0.23 |
