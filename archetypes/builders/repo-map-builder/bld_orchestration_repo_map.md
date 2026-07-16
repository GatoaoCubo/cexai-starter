---
kind: collaboration
id: bld_collaboration_repo_map
pillar: P12
llm_function: COLLABORATE
purpose: How repo_map-builder works in crews with other builders
quality: null
title: "Collaboration Repo Map"
version: "1.0.0"
author: wave1_builder_gen
tags: [repo_map, builder, collaboration]
tldr: "How repo_map-builder works in crews with other builders"
domain: "repo_map construction"
created: "2026-04-13"
updated: "2026-04-13"
8f: "F8_collaborate"
keywords: [repo_map construction, collaboration repo map, repo_map, builder, collaboration, crew role  
creates, receives from, produces for, boundary  
does, related artifacts]
density_score: 0.85
related:
  - bld_config_repo_map
  - p11_fb_repo_map
  - ctx_n03
  - bld_collaboration_component_map
  - p12_wf_code_review
---
## Crew Role  
Creates and maintains a consistent, cross-repo context map for navigation and dependency tracking. Ensures alignment between repo structures, ownership, and purpose.  

## Receives From  
| Builder | What | Format |  
|---|---|---|  
| Repo configurer | Repo metadata (name, owner, purpose) | YAML |  
| Dependency tracker | Cross-repo dependency graph | JSON |  
| CI/CD system | Repo event triggers (create, delete) | Webhook |  

## Produces For  
| Builder | What | Format |  
|---|---|---|  
| Repo navigator | Visual repo map (graph, hierarchy) | JSON |  
| Documentation team | Repo context summary | Markdown |  
| Dependency analyzer | Normalized dependency graph | DOT |  

## Boundary  
Does NOT handle system architecture (component_map-builder), search index (knowledge_index-builder), or CI/CD pipeline orchestration (CI/CD team).

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[bld_config_repo_map]] | upstream | 0.36 |
| [[p11_fb_repo_map]] | upstream | 0.31 |
| [[ctx_n03]] | upstream | 0.20 |
| [[bld_collaboration_component_map]] | sibling | 0.18 |
| [[p12_wf_code_review]] | related | 0.18 |
