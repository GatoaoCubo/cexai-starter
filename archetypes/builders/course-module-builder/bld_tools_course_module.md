---
kind: tools
id: bld_tools_course_module
pillar: P04
llm_function: CALL
purpose: Tools available for course_module production
quality: null
title: "Tools Course Module"
version: "1.0.0"
author: wave1_builder_gen_v2
tags: [course_module, builder, tools]
tldr: "Tools available for course_module production"
domain: "course_module construction"
created: "2026-04-14"
updated: "2026-04-14"
8f: "F5_call"
keywords: [course_module construction, tools course module, course_module, builder, tools, production tools, validation tools, external references, related artifacts, tools tool]
density_score: 0.85
related:
  - bld_tools_prosody_config
  - bld_tools_ab_test_config
  - bld_tools_vad_config
  - bld_config_course_module
  - bld_tools_faq_entry
---

## Production Tools
| Tool | Purpose | When |
|------|---------|------|
| cex_compile.py | Compiles course modules into executable formats | Pre-deployment |
| cex_score.py | Automates scoring of learner submissions | Post-activity |
| cex_retriever.py | Fetches external content for module integration | Content assembly |
| cex_doctor.py | Diagnoses module errors and suggests fixes | Debugging |
| cex_8f_runner.py | Creates boilerplate module structures | Initial setup |
| cex_doctor.py | Ensures compliance with course standards | Quality checks |

## Validation Tools
| Tool | Purpose | When |
|------|---------|------|
| mod_check.py | Verifies module consistency across versions | Updates |
| linter_mod.py | Enforces code style and syntax rules | Development |
| test_sim.py | Simulates learner interactions for edge cases | Testing |

## External References
- LMS API (for integration with learning management systems)
- Markdownlint (for content formatting validation)
- H5P (for interactive content authoring)

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[bld_tools_prosody_config]] | sibling | 0.33 |
| [[bld_tools_ab_test_config]] | sibling | 0.32 |
| [[bld_tools_vad_config]] | sibling | 0.31 |
| [[bld_config_course_module]] | downstream | 0.30 |
| [[bld_tools_faq_entry]] | sibling | 0.30 |
