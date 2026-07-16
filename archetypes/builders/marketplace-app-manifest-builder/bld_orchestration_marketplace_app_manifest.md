---
kind: collaboration
id: bld_collaboration_marketplace_app_manifest
pillar: P12
llm_function: COLLABORATE
purpose: How marketplace_app_manifest-builder works in crews with other builders
quality: null
title: "Collaboration Marketplace App Manifest"
version: "1.0.0"
author: wave1_builder_gen_v2
tags: [marketplace_app_manifest, builder, collaboration]
tldr: "How marketplace_app_manifest-builder works in crews with other builders"
domain: "marketplace_app_manifest construction"
created: "2026-04-14"
updated: "2026-04-14"
8f: "F8_collaborate"
keywords: [marketplace_app_manifest construction, collaboration marketplace app manifest, marketplace_app_manifest, builder, collaboration, plugin_loader, app_directory_manager, crew role  
generates, receives from  
builder, app developer]
density_score: 0.85
related:
  - bld_collaboration_app_directory_entry
  - marketplace-app-manifest-builder
  - kc_marketplace_app_manifest
  - kc_app_directory_entry
  - app-directory-entry-builder
---
## Crew Role  
Generates and validates marketplace app manifests, ensuring compliance with marketplace schema and metadata requirements.  

## Receives From  
Builder | What | Format  
--- | --- | ---  
App Developer | App metadata | JSON  
Config Manager | Marketplace schema | YAML  
Dependency Tracker | External service references | CSV  

## Produces For  
Builder | What | Format  
--- | --- | ---  
Marketplace Validator | Parsed manifest | JSON  
Documentation Team | Manifest summary | Markdown  
Deployment System | Validated manifest | XML  

## Boundary  
Does NOT handle plugin loading or app directory entries. Plugin loading is managed by `plugin_loader`, and app directory entries are handled by `app_directory_manager`.

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[bld_collaboration_app_directory_entry]] | sibling | 0.57 |
| [[marketplace-app-manifest-builder]] | upstream | 0.42 |
| [[kc_marketplace_app_manifest]] | upstream | 0.39 |
| [[kc_app_directory_entry]] | upstream | 0.37 |
| [[app-directory-entry-builder]] | upstream | 0.34 |
