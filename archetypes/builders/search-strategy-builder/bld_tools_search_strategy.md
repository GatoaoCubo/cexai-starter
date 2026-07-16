---
kind: tools
id: bld_tools_search_strategy
pillar: P04
llm_function: CALL
purpose: Tools available for search_strategy production
quality: null
title: "Tools Search Strategy"
version: "1.0.0"
author: wave1_builder_gen
tags: [search_strategy, builder, tools]
tldr: "Tools available for search_strategy production"
domain: "search_strategy construction"
created: "2026-04-13"
updated: "2026-04-13"
8f: "F5_call"
keywords: [search_strategy construction, tools search strategy, search_strategy, builder, tools, production tools, validation tools, external references, related artifacts, tools tool]
density_score: 0.85
related:
  - bld_tools_reasoning_strategy
  - bld_tools_planning_strategy
  - bld_tools_vad_config
  - bld_tools_edit_format
  - bld_tools_transport_config
---

## Production Tools
| Tool | Purpose | When |
|---|---|---|
| cex_compile.py | Compiles search strategies into executable code | During strategy development |
| cex_score.py | Evaluates strategy effectiveness using metrics | After strategy execution |
| cex_retriever.py | Fetches data from external sources | During query processing |
| cex_doctor.py | Diagnoses strategy errors and inefficiencies | During testing/iteration |
| cex_evolve.py | Refines strategies for performance | Post-initial deployment |
| cex_8f_runner.py | Runs compiled strategies in production | In live search operations |

## Validation Tools
| Tool | Purpose | When |
|---|---|---|
| val_checker.py | Validates strategy syntax and logic | Pre-deployment |
| val_simulator.py | Simulates strategy behavior under stress | During QA |
| val_analyzer.py | Compares strategy outputs against benchmarks | Post-execution |
| val_reporter.py | Generates validation summary reports | After testing |

## External References
- Elasticsearch: Full-text search and analytics engine
- LangChain: Framework for building LLM-powered search pipelines
- Pandas: Data manipulation for strategy input/output processing

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[bld_tools_reasoning_strategy]] | sibling | 0.51 |
| [[bld_tools_planning_strategy]] | sibling | 0.38 |
| [[bld_tools_vad_config]] | sibling | 0.35 |
| [[bld_tools_edit_format]] | sibling | 0.30 |
| [[bld_tools_transport_config]] | sibling | 0.29 |
