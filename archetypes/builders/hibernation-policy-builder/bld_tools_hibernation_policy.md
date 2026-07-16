---
kind: toolkit
id: bld_tools_hibernation_policy
pillar: P04
llm_function: CALL
purpose: P04 tools used by hibernation_policy builder
quality: null
title: "Tools: hibernation_policy Builder"
version: "1.0.0"
author: n03_engineering
tags: [hibernation_policy, builder, tools]
tldr: "P04 tools used by hibernation_policy builder"
domain: "hibernation_policy construction"
created: "2026-04-18"
updated: "2026-04-18"
8f: "F5_call"
keywords: [hibernation_policy construction, hibernation_policy builder, hibernation_policy, builder, tools, cex_compile.py, cex_doctor.py, python -m json.tool, cex_retriever.py, cex_8f_runner.py]
density_score: 0.90
related:
  - bld_tools_messaging_gateway
  - bld_tools_personality
  - bld_tools_terminal_backend
  - bld_tools_data_contract
  - bld_tools_deployment_manifest
---
## Tools Used in F5 CALL

| Tool | Purpose | When |
|------|---------|------|
| `cex_compile.py` | Compile .md -> .yaml | F8 COLLABORATE -- after save |
| `cex_doctor.py` | Health check artifact structure | F7 GOVERN -- validate before commit |
| `python -m json.tool` | Validate kinds_meta.json | F8 -- after patching kinds_meta |
| `cex_retriever.py` | Find similar existing hibernation_policy artifacts | F3 INJECT -- avoid duplication |
| `cex_8f_runner.py` | Execute full 8F pipeline for this kind | F1 entry point |

## External APIs (optional -- for validation only)

| API | Purpose | Required |
|-----|---------|----------|
| Daytona API | Validate workspace pause/resume endpoint exists | No -- design-time only |
| Modal API | Validate container scaling-to-zero config | No -- design-time only |

## No External Calls During Build
hibernation_policy is a pure config artifact. The builder does NOT make live API calls to backends during construction. Configuration is validated syntactically (schema + gates), not by hitting live endpoints.

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[bld_tools_messaging_gateway]] | related | 0.26 |
| [[bld_tools_personality]] | related | 0.25 |
| [[bld_tools_terminal_backend]] | related | 0.25 |
| [[bld_tools_data_contract]] | downstream | 0.24 |
| [[bld_tools_deployment_manifest]] | downstream | 0.24 |
