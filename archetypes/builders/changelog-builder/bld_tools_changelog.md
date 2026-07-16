---
kind: tools
id: bld_tools_changelog
pillar: P04
llm_function: CALL
purpose: Tools available for changelog production
quality: null
title: "Tools Changelog"
version: "1.1.0"
author: wave1_builder_gen_v2
tags: [changelog, builder, tools]
tldr: "CEX tools available for changelog production and validation"
domain: "changelog construction"
created: "2026-04-14"
updated: "2026-04-14"
8f: "F5_call"
keywords: [changelog construction, tools changelog, changelog, builder, tools, production tools, validation tools, external references, hub releases, related artifacts]
density_score: 0.85
related:
  - bld_tools_competitive_matrix
  - bld_tools_api_reference
  - bld_tools_case_study
  - bld_tools_nps_survey
  - bld_tools_quickstart_guide
---

## Production Tools
| Tool | Purpose | When |
|------|---------|------|
| cex_compile.py | Compile .md artifact to .yaml sidecar | After write |
| cex_score.py | Score changelog artifact against quality gate | Pre-publish |
| cex_retriever.py | Find similar changelogs for cross-reference | During research |
| cex_doctor.py | Validate frontmatter, kind, ID pattern compliance | Pre-publish |

## Validation Tools
| Tool | Purpose | When |
|------|---------|------|
| cex_wave_validator.py | Check all builder ISOs for schema compliance | Post-build |
| cex_hooks.py | Pre-commit YAML validation and quality gate | On git commit |

## External References
- keepachangelog.com (format specification)
- semver.org (version numbering specification)
- Git log (source of commit entries for changelog generation)
- GitHub Releases API (structured versioned release format)

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[bld_tools_competitive_matrix]] | sibling | 0.44 |
| [[bld_tools_api_reference]] | sibling | 0.40 |
| [[bld_tools_case_study]] | sibling | 0.40 |
| [[bld_tools_nps_survey]] | sibling | 0.37 |
| [[bld_tools_quickstart_guide]] | sibling | 0.36 |
