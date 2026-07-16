---
kind: architecture
id: bld_architecture_partner_listing
pillar: P08
llm_function: CONSTRAIN
purpose: Component map of partner_listing -- inventory, dependencies
quality: null
title: "Architecture Partner Listing"
version: "1.0.0"
author: wave1_builder_gen_v2
tags: [partner_listing, builder, architecture]
tldr: "Component map of partner_listing -- inventory, dependencies"
domain: "partner_listing construction"
created: "2026-04-14"
updated: "2026-04-14"
8f: "F1_constrain"
keywords: [partner_listing construction, architecture partner listing, partner_listing, builder, architecture, component inventory, architectural position, related artifacts, definition active, bld_tools external]
density_score: 0.85
related:
  - bld_architecture_user_journey
  - bld_architecture_course_module
  - bld_architecture_integration_guide
  - bld_architecture_case_study
  - bld_architecture_app_directory_entry
---

## Component Inventory
| ISO Name              | Role                          | Pillar | Status  |
|-----------------------|-------------------------------|--------|---------|
| bld_manifest          | Core configuration            | P05    | Active  |
| bld_instruction       | Task definition               | P05    | Active  |
| bld_system_prompt     | LLM guidance                  | P05    | Active  |
| bld_schema            | Data structure definition     | P05    | Active  |
| bld_quality_gate      | Validation rules              | P05    | Active  |
| bld_output_template   | Formatting specification      | P05    | Active  |
| bld_examples          | Training samples              | P05    | Active  |
| bld_knowledge_card    | Partner metadata              | P05    | Active  |
| bld_architecture      | System blueprint              | P05    | Active  |
| bld_collaboration     | Workflow coordination         | P05    | Active  |
| bld_config            | Runtime parameters            | P05    | Active  |
| bld_memory            | Session persistence           | P05    | Active  |
| bld_tools             | External integration          | P05    | Active  |

## Dependencies
| From              | To                  | Type        |
|-------------------|---------------------|-------------|
| bld_manifest      | bld_config          | configuration|
| bld_instruction   | bld_system_prompt   | dependency  |
| bld_output_template | bld_schema        | dependency  |
| bld_quality_gate  | bld_examples        | validation  |
| bld_collaboration | bld_memory          | coordination|
| bld_tools         | external API        | integration |

## Architectural Position
partner_listing serves as the central coordination hub within CEX P05, enabling structured partner onboarding through standardized schema, quality validation, and collaborative workflow orchestration, ensuring alignment with ecosystem governance and operational excellence.

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[bld_architecture_user_journey]] | sibling | 0.81 |
| [[bld_architecture_course_module]] | sibling | 0.79 |
| [[bld_architecture_integration_guide]] | sibling | 0.79 |
| [[bld_architecture_case_study]] | sibling | 0.77 |
| [[bld_architecture_app_directory_entry]] | sibling | 0.62 |
