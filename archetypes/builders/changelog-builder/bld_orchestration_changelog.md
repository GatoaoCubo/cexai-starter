---
kind: collaboration
id: bld_collaboration_changelog
pillar: P12
llm_function: COLLABORATE
purpose: How changelog-builder works in crews with other builders
quality: null
title: "Collaboration Changelog"
version: "1.0.0"
author: wave1_builder_gen_v2
tags: [changelog, builder, collaboration]
tldr: "How changelog-builder works in crews with other builders"
domain: "changelog construction"
created: "2026-04-14"
updated: "2026-04-14"
8f: "F8_collaborate"
keywords: [changelog construction, collaboration changelog, changelog, builder, collaboration, crew role  
automates, receives from, version control system, issue tracker, produces for]
density_score: 0.85
related:
  - bld_collaboration_response_format
  - bld_memory_response_format
  - bld_tools_edit_format
  - bld_collaboration_edit_format
  - bld_tools_changelog
---
## Crew Role  
Automates generation of structured changelogs by aggregating atomic changes from version-controlled repositories and CI/CD pipelines.  

## Receives From  
| Builder       | What              | Format              |  
|---------------|-------------------|---------------------|  
| Version Control System | Commit messages   | Git commit log format |  
| CI/CD Pipeline  | Deployment events | JSON payload        |  
| Issue Tracker   | Issue resolutions | Jira API format     |  

## Produces For  
| Builder       | What              | Format              |  
|---------------|-------------------|---------------------|  
| Release Management Tool | Change summary  | YAML format         |  
| Documentation System    | Versioned history | HTML format         |  
| Artifact Repository     | Changelog file    | Markdown format     |  

## Boundary  
Does NOT write prose or rationale (handled by release_notes/decision_record). Does NOT resolve merge conflicts (handled by Release Manager).

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[bld_collaboration_response_format]] | sibling | 0.32 |
| [[bld_memory_response_format]] | upstream | 0.28 |
| [[bld_tools_edit_format]] | upstream | 0.28 |
| [[bld_collaboration_edit_format]] | sibling | 0.23 |
| [[bld_tools_changelog]] | upstream | 0.22 |
