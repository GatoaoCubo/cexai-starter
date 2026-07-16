---
kind: tools
id: bld_tools_agents_md
pillar: P04
llm_function: CALL
purpose: Tools available for agents_md production
quality: null
title: "Tools Agents Md"
version: "1.0.0"
author: wave7_n03_dev_manifests
tags: [agents_md, builder, tools]
tldr: "Tools available for AGENTS.md production"
domain: "agents_md construction"
created: "2026-04-14"
updated: "2026-04-14"
8f: "F5_call"
keywords: [agents_md construction, tools agents md, tools available for agents, md production, agents_md, builder, tools, production tools, validation tools, detect claude]
density_score: 0.85
related:
  - bld_knowledge_card_agents_md
  - agents-md-builder
  - p10_lr_agents_md_builder
  - bld_collaboration_agents_md
  - bld_instruction_agents_md
---
## Production Tools
| Tool             | Purpose                                        | When                        |
|------------------|------------------------------------------------|-----------------------------|
| cex_compile.py   | Compile AGENTS.md source to project-root file  | After F6 PRODUCE            |
| cex_score.py     | Assign HARD/SOFT quality score                 | Post-validation phase       |
| cex_retriever.py | Fetch similar AGENTS.md from 60K corpus        | On-demand during F3 INJECT  |
| cex_doctor.py    | Diagnose missing command blocks                | Pre-validation checks       |
| codex            | OpenAI Codex CLI -- reference AAIF consumer    | Dry-run bootstrap test      |
| aider            | Aider coding-agent -- reference AAIF consumer  | Dry-run bootstrap test      |

## Validation Tools
| Tool              | Purpose                                     | When                    |
|-------------------|---------------------------------------------|-------------------------|
| agents_md_lint.py | Check spec conformance (AAIF schema)        | Pre-commit              |
| ci_mirror_check   | Verify command blocks match actual CI YAML  | Pre-publish             |
| vendor_scrub      | Detect Claude/Cursor-only directives leak   | Pre-publish             |
| shell_runnable    | Dry-run every fenced command in fresh shell | Release gate            |

## External References
- AGENTS.md spec: https://agents.md/ (AAIF governance, Dec 2025)
- OpenAI Codex CLI docs: reference parser implementation
- Block goose AGENTS.md guide: adoption patterns from 60K-projects corpus
- Conventional Commits 1.0.0: pr-format grammar source
- MCP (Model Context Protocol): complementary transport spec

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[bld_knowledge_card_agents_md]] | upstream | 0.52 |
| [[agents-md-builder]] | downstream | 0.42 |
| [[p10_lr_agents_md_builder]] | downstream | 0.34 |
| [[bld_collaboration_agents_md]] | downstream | 0.29 |
| [[bld_instruction_agents_md]] | upstream | 0.26 |
