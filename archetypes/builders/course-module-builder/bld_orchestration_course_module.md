---
kind: collaboration
id: bld_collaboration_course_module
pillar: P12
llm_function: COLLABORATE
purpose: How course_module-builder works in crews with other builders
quality: null
title: "Collaboration Course Module"
version: "1.0.0"
author: wave1_builder_gen_v2
tags: [course_module, builder, collaboration]
tldr: "How course_module-builder works in crews with other builders"
domain: "course_module construction"
created: "2026-04-14"
updated: "2026-04-14"
8f: "F8_collaborate"
keywords: [course_module construction, collaboration course module, course_module, builder, collaboration, crew role  
coordinates, receives from, content curator, assessment builder, media collector]
density_score: 0.85
related:
  - course-module-builder
  - bld_tools_course_module
  - bld_instruction_course_module
  - p01_kc_course_module
  - bld_config_course_module
---
## Crew Role  
Coordinates creation of structured course modules, integrating content, assessments, and media into cohesive learning units.  

## Receives From  
| Builder         | What                  | Format      |  
|-----------------|-----------------------|-------------|  
| Content Curator | Learning objectives   | Text        |  
| Assessment Builder | Quizzes/exercises   | JSON        |  
| Media Collector | Video/illustration links | URLs        |  

## Produces For  
| Builder           | What                  | Format      |  
|-------------------|-----------------------|-------------|  
| Content Reviewer  | Draft module          | Markdown    |  
| LMS Integrator    | Configured module     | YAML        |  
| Analytics Tracker | Usage metrics         | CSV         |  

## Boundary  
Does NOT handle user authentication, enrollment management, or prompt/knowledge card creation. These are managed by LMS, enrollment_system, and prompt_template/knowledge_card builders respectively.

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[course-module-builder]] | upstream | 0.28 |
| [[bld_tools_course_module]] | upstream | 0.27 |
| [[bld_instruction_course_module]] | upstream | 0.25 |
| [[p01_kc_course_module]] | upstream | 0.23 |
| [[bld_config_course_module]] | upstream | 0.22 |
