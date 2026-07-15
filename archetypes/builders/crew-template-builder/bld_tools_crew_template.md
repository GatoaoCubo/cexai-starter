---
kind: tools
id: bld_tools_crew_template
pillar: P04
llm_function: CALL
purpose: Tools available for crew_template production
quality: null
title: "Tools Crew Template"
version: "1.0.0"
author: n03_wave8_builder
tags: [crew_template, builder, tools, composable, crewai]
tldr: "Tools available for crew_template production"
domain: "crew_template construction"
created: "2026-04-14"
updated: "2026-04-14"
8f: "F5_call"
keywords: [crew_template construction, tools crew template, crew_template, builder, tools, composable, crewai, crewai.process.process, production tools, validation tools]
density_score: 0.86
related:
  - bld_tools_role_assignment
  - bld_tools_pipeline_template
  - bld_knowledge_card_crew_template
  - bld_instruction_crew_template
  - bld_tools_discovery_questions
---
## Production Tools
| Tool              | Purpose                                  | When                      |
|-------------------|------------------------------------------|---------------------------|
| cex_compile.py    | Compile crew_template .md to .yaml blueprint | F8 COLLABORATE        |
| cex_retriever.py  | Find similar crew templates (reuse)      | F3 INJECT                 |
| cex_query.py      | Discover role_assignment refs            | F1 CONSTRAIN              |
| cex_doctor.py     | Validate all role refs resolve           | F7 GOVERN                 |
| cex_score.py      | Peer-review scoring (HARD + SOFT)        | F7 GOVERN                 |
| signal_writer.py  | Signal N07 on completion                 | F8 COLLABORATE            |

## Validation Tools
| Tool                  | Purpose                                    | When          |
|-----------------------|--------------------------------------------|---------------|
| cex_doctor.py  | Resolve p02_ra_* references                | Pre-commit    |
| cex_builder_linter.py   | Check topology vs dependency graph         | F7 GOVERN     |
| cex_retriever.py   | Flag over-shared memory_scope              | F7 GOVERN     |
| cex_builder_linter.py | Require measurable success_criteria       | F7 GOVERN     |

## External References
- CrewAI Process API docs (`crewai.process.Process`)
- Microsoft Agent Framework GroupChat patterns (MAF v1.0 preview)
- OpenAI Agents SDK v0.6+ handoff/transfer functions
- Google A2A v0.3.0 Task lifecycle specification
- LangGraph StateGraph conditional edges (consensus equivalent)

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[bld_tools_role_assignment]] | sibling | 0.40 |
| bld_tools_pipeline_template | sibling | 0.37 |
| [[bld_knowledge_card_crew_template]] | upstream | 0.32 |
| [[bld_instruction_crew_template]] | upstream | 0.28 |
| bld_tools_discovery_questions | sibling | 0.27 |
