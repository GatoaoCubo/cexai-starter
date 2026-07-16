---
kind: tools
id: bld_tools_edtech_vertical
pillar: P04
llm_function: CALL
purpose: Tools available for edtech_vertical production
quality: null
title: "Tools Edtech Vertical"
version: "1.0.0"
author: wave1_builder_gen_v2
tags: [edtech_vertical, builder, tools]
tldr: "Tools available for edtech_vertical production"
domain: "edtech_vertical construction"
created: "2026-04-14"
updated: "2026-04-14"
8f: "F5_call"
keywords: [edtech_vertical construction, tools edtech vertical, edtech_vertical, builder, tools, production tools, external references, developer keys, moodle external tool, domain scope
these]
density_score: 0.85
related:
  - edtech-vertical-builder
  - p10_mem_edtech_vertical_builder
  - bld_instruction_edtech_vertical
  - p01_qg_edtech_vertical
  - bld_output_template_edtech_vertical
---
## Production Tools
| Tool | Purpose | When |
|------|---------|------|
| cex_compile.py | Compile edtech_vertical YAML/MD artifacts to registry | After artifact generation |
| cex_score.py | Score artifact quality (5D rubric) against quality gate | Post-generation quality check |
| cex_retriever.py | Fetch similar edtech artifacts for reference | During F3 INJECT phase |
| cex_doctor.py | Diagnose schema compliance and frontmatter issues | Pre-validation checks |
| cex_wave_validator.py | Validate builder ISO set completeness and D01-D15 defects | Builder audit cycle |

## External References
- IMS Global LTI 1.3 specification (imsglobal.org/spec/lti/v1p3): LMS integration standard
- 1EdTech xAPI (Experience API) specification: learning activity tracking
- FERPA guidance (studentprivacy.ed.gov): educational record privacy
- COPPA FTC guidelines (ftc.gov/coppa): under-13 data collection rules
- Canvas LTI Developer Keys + Moodle External Tool documentation: LMS integration guides

## Domain Scope
These tools support edtech vertical artifact production, including LMS integration testing, accessibility compliance checks, and student data anonymization workflows specific to edtech use cases.

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[edtech-vertical-builder]] | upstream | 0.47 |
| [[p10_mem_edtech_vertical_builder]] | downstream | 0.47 |
| [[bld_instruction_edtech_vertical]] | upstream | 0.42 |
| [[p01_qg_edtech_vertical]] | downstream | 0.39 |
| [[bld_output_template_edtech_vertical]] | downstream | 0.36 |
