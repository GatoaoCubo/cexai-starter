---
kind: tools
id: bld_tools_agent_profile
pillar: P04
llm_function: CALL
purpose: Tools available for agent_profile production
quality: null
title: "Tools Agent Profile"
version: "1.0.0"
author: wave1_builder_gen
tags: [agent_profile, builder, tools]
tldr: "Tools available for agent_profile production"
domain: "agent_profile construction"
created: "2026-04-13"
updated: "2026-04-13"
8f: "F5_call"
keywords: [agent_profile construction, tools agent profile, agent_profile, builder, tools, production tools, validation tools, external references, hugging face transformers, related artifacts]
density_score: 0.85
related:
  - bld_collaboration_agent
  - p01_kc_agent
  - bld_architecture_agent
  - bld_knowledge_card_agent
  - agent-profile-builder
---
## Production Tools
| Tool              | Purpose                          | When                          |
|-------------------|----------------------------------|-------------------------------|
| cex_compile.py    | Compile agent profiles into code | Deploying agent systems       |
| cex_score.py      | Evaluate profile quality         | Validating agent performance  |
| cex_retriever.py  | Fetch external data sources      | Building knowledge base       |
| cex_doctor.py     | Diagnose profile inconsistencies | Debugging agent behavior      |
| cex_retriever.py   | Deep profile analysis            | Optimizing agent parameters   |
| cex_evolve.py  | Tune agent configuration         | Refining system performance   |

## Validation Tools
| Tool              | Purpose                          | When                          |
|-------------------|----------------------------------|-------------------------------|
| val_check.py      | Validate syntax and structure    | Initial profile creation      |
| val_compare.py    | Compare profile versions         | Version control               |
| val_audit.py      | Ensure compliance with standards | Regulatory checks             |

## External References
- LangChain (agent orchestration framework)
- Hugging Face Transformers (NLP models)
- Neo4j (knowledge graph storage)

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[bld_orchestration_agent]] | downstream | 0.39 |
| [[kc_agent]] | upstream | 0.38 |
| [[bld_architecture_agent]] | downstream | 0.33 |
| [[bld_knowledge_agent]] | upstream | 0.32 |
| [[agent-profile-builder]] | upstream | 0.28 |
