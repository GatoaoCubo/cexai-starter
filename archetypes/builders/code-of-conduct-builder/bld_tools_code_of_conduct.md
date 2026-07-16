---
kind: tools
id: bld_tools_code_of_conduct
pillar: P04
llm_function: CALL
purpose: Tools available for code_of_conduct production
quality: null
title: "Tools Code of Conduct"
version: "1.0.0"
author: n04_knowledge
tags: [code_of_conduct, builder, tools]
tldr: "Tools available for code_of_conduct production"
domain: "code_of_conduct construction"
created: "2026-04-14"
updated: "2026-04-14"
8f: "F5_call"
keywords: [code_of_conduct construction, tools code of conduct, code_of_conduct, builder, tools, production tools, validation tools, external references, contributor covenant, tools tool]
density_score: 0.87
related:
  - bld_tools_github_issue_template
  - bld_tools_app_directory_entry
  - bld_tools_customer_segment
  - bld_tools_white_label_config
  - bld_tools_playground_config
---

## Production Tools
| Tool                  | Purpose                               | When                          |
|-----------------------|---------------------------------------|-------------------------------|
| cex_compile.py        | Compile .md builder ISOs to .yaml     | After each ISO write          |
| cex_score.py          | Score artifact quality (5D + H gates) | Post-validation phase         |
| cex_retriever.py      | TF-IDF similarity search on artifacts | Finding similar CoC patterns  |
| cex_doctor.py         | Builder health check (118 assertions) | Pre-deployment verification   |
| cex_wave_validator.py | Validate all ISOs in a builder dir    | After completing all 13 ISOs  |
| cex_hygiene.py        | Artifact CRUD + 8 hygiene rules       | Cleanup and consistency pass  |

## Validation Tools
| Tool                  | Purpose                               | When                          |
|-----------------------|---------------------------------------|-------------------------------|
| cex_hooks.py          | Pre-commit validation + ASCII check   | On git commit                 |
| cex_sanitize.py       | Detect and fix non-ASCII in code files| Before committing .py/.ps1    |
| cex_schema_hydrate.py | Hydrate ISOs with universal patterns  | After schema changes          |

## External References
- Contributor Covenant v2.1: https://www.contributor-covenant.org/version/2/1/code_of_conduct/
- Mozilla Community Participation Guidelines: https://www.mozilla.org/en-US/about/governance/policies/participation/
- CNCF Code of Conduct: https://github.com/cncf/foundation/blob/main/code-of-conduct.md

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[bld_tools_github_issue_template]] | sibling | 0.54 |
| [[bld_tools_app_directory_entry]] | sibling | 0.46 |
| [[bld_tools_customer_segment]] | sibling | 0.36 |
| [[bld_tools_white_label_config]] | sibling | 0.35 |
| [[bld_tools_playground_config]] | sibling | 0.33 |
