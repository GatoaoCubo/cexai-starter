---
kind: tools
id: bld_tools_marketplace_app_manifest
pillar: P04
llm_function: CALL
purpose: Tools available for marketplace_app_manifest production
quality: null
title: "Tools Marketplace App Manifest"
version: "1.0.0"
author: wave1_builder_gen_v2
tags: [marketplace_app_manifest, builder, tools]
tldr: "Tools available for marketplace_app_manifest production"
domain: "marketplace_app_manifest construction"
created: "2026-04-14"
updated: "2026-04-14"
8f: "F5_call"
keywords: [marketplace_app_manifest construction, tools marketplace app manifest, marketplace_app_manifest, builder, tools, production tools, validation tools, external references, related artifacts, tools tool]
density_score: 0.85
related:
  - bld_tools_vad_config
  - bld_tools_api_reference
  - bld_tools_faq_entry
  - bld_config_marketplace_app_manifest
  - bld_tools_quickstart_guide
---
## Production Tools
| Tool | Purpose | When |
|------|---------|------|
| cex_compile.py | Compiles app manifest from source files | During build process |
| cex_score.py | Evaluates manifest compliance with marketplace rules | Pre-deployment validation |
| cex_retriever.py | Fetches external dependencies for manifest | When resolving third-party assets |
| cex_doctor.py | Diagnoses manifest errors and suggests fixes | Post-validation troubleshooting |

## Validation Tools
| Tool | Purpose | When |
|------|---------|------|
| validate_manifest.py | Checks manifest syntax and structure | Pre-submission |
| schema_checker.py | Ensures adherence to marketplace schema | During development |
| linter_manifest.py | Enforces coding standards in manifest files | Continuous integration |

## External References
- JSON Schema (for manifest structure validation)
- PyYAML (for parsing manifest metadata)
- Marketplace API v2.1 (for runtime compliance checks)

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[bld_tools_vad_config]] | sibling | 0.33 |
| [[bld_tools_api_reference]] | sibling | 0.32 |
| [[bld_tools_faq_entry]] | sibling | 0.32 |
| [[bld_config_marketplace_app_manifest]] | downstream | 0.31 |
| [[bld_tools_quickstart_guide]] | sibling | 0.31 |
