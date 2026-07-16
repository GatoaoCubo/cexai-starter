---
kind: tools
id: bld_tools_sdk_example
pillar: P04
llm_function: CALL
purpose: Tools available for sdk_example production
quality: null
title: "Tools Sdk Example"
version: "1.0.0"
author: wave1_builder_gen_v2
tags: [sdk_example, builder, tools]
tldr: "Tools available for sdk_example production"
domain: "sdk_example construction"
created: "2026-04-14"
updated: "2026-04-14"
8f: "F5_call"
keywords: [sdk_example construction, tools sdk example, sdk_example, builder, tools, production tools, validation tools, external references, twilio quickstart, google java style]
density_score: 0.85
related:
  - bld_tools_api_reference
  - bld_tools_quickstart_guide
  - bld_tools_changelog
  - bld_tools_github_issue_template
  - bld_tools_competitive_matrix
---
## Production Tools
| Tool | Purpose | When |
|------|---------|------|
| cex_compile.py | Compiles ISOs to deployable artifact | During build phase |
| cex_score.py | Scores quality via 3-layer rubric | Post-validation |
| cex_retriever.py | Finds related SDK artifacts via TF-IDF | Pre-runtime setup |
| cex_doctor.py | Diagnoses frontmatter and structure issues | On first run or deployment |

## Validation Tools
| Tool | Purpose | When |
|------|---------|------|
| cex_wave_validator.py | Validates frontmatter, ISO count, kind fields | Pre-commit |
| cex_hooks.py | Pre/post build validation hooks | On build events |
| cex_system_test.py | Full system validation (54 checks) | Release gate |

## External References
- Twilio Quickstart SDK style (auth + retry + pagination canonical patterns)
- GitHub idiomatic code examples (language-specific README conventions)
- PEP8 (Python) / Google Java Style / StandardJS (language style guides)

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[bld_tools_api_reference]] | sibling | 0.52 |
| [[bld_tools_quickstart_guide]] | sibling | 0.51 |
| [[bld_tools_changelog]] | sibling | 0.34 |
| [[bld_tools_github_issue_template]] | sibling | 0.32 |
| [[bld_tools_competitive_matrix]] | sibling | 0.32 |
