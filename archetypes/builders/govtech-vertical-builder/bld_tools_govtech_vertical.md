---
kind: tools
id: bld_tools_govtech_vertical
pillar: P04
llm_function: CALL
purpose: Tools available for govtech_vertical production
quality: null
title: "Tools Govtech Vertical"
version: "1.0.0"
author: wave1_builder_gen_v2
tags: [govtech_vertical, builder, tools]
tldr: "Tools available for govtech_vertical production"
domain: "govtech_vertical construction"
created: "2026-04-14"
updated: "2026-04-14"
8f: "F5_call"
keywords: [govtech_vertical construction, tools govtech vertical, govtech_vertical, builder, tools, production tools, external references, security policy, award management, authorized products list]
density_score: 0.85
related:
  - p10_mem_govtech_vertical_builder
  - bld_instruction_govtech_vertical
  - bld_knowledge_card_govtech_vertical
  - govtech-vertical-builder
  - govtech_vertical_digital_services
---
## Production Tools
| Tool | Purpose | When |
|------|---------|------|
| cex_compile.py | Compile govtech_vertical YAML/MD artifacts to registry | After artifact generation |
| cex_score.py | Score artifact quality (5D rubric) against quality gate | Post-generation quality check |
| cex_retriever.py | Fetch similar govtech artifacts for reference | During F3 INJECT phase |
| cex_doctor.py | Diagnose schema compliance and frontmatter issues | Pre-validation checks |
| cex_wave_validator.py | Validate builder ISO set completeness and D01-D15 defects | Builder audit cycle |

## External References
- FedRAMP Marketplace (marketplace.fedramp.gov): authorized cloud services registry
- NIST SP 800-53 Rev. 5: security and privacy control catalog
- CJIS Security Policy v5.9.1 (SP 20-01): law enforcement data protection
- GSA System for Award Management (sam.gov): vendor registration and contract data
- StateRAMP Authorized Products List: state-level FedRAMP equivalent

## Domain Scope
These tools support govtech vertical artifact production, including FedRAMP authorization validation, CJIS compliance checks, and GSA-approved template management specific to govtech use cases.

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[p10_mem_govtech_vertical_builder]] | downstream | 0.39 |
| [[bld_instruction_govtech_vertical]] | upstream | 0.37 |
| [[bld_knowledge_card_govtech_vertical]] | upstream | 0.37 |
| [[govtech-vertical-builder]] | upstream | 0.36 |
| [[govtech_vertical_digital_services]] | upstream | 0.31 |
