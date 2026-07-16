---
kind: tools
id: bld_tools_trajectory_eval
pillar: P04
llm_function: CALL
purpose: Tools available for trajectory_eval production
quality: null
title: "Tools Trajectory Eval"
version: "1.1.0"
author: n01_hybrid_review4
tags: [trajectory_eval, builder, tools]
tldr: "Real CEX tools for producing trajectory_eval artifacts."
domain: "trajectory_eval construction"
created: "2026-04-14"
updated: "2026-04-14"
8f: "F5_call"
keywords: [trajectory_eval construction, tools trajectory eval, trajectory_eval, builder, tools, production tools, validation tools, external references, related artifacts, tools tool]
density_score: 0.85
related:
  - bld_tools_github_issue_template
  - bld_knowledge_card_trajectory_eval
  - bld_tools_pricing_page
  - bld_tools_prompt_technique
  - bld_tools_self_improvement_loop
---
## Production Tools
| Tool | Purpose | When |
|------|---------|------|
| cex_compile.py | Compile .md artifact to .yaml | After saving |
| cex_score.py | Apply peer-review quality score | Post-production |
| cex_retriever.py | Find similar trajectory_eval artifacts for reference | Before composing |
| cex_doctor.py | Validate artifact health (frontmatter, kind, pillar) | During validation |

## Validation Tools
| Tool | Purpose | When |
|------|---------|------|
| cex_wave_validator.py | Structural checks: domain keywords, required fields | Pre-commit |
| cex_hygiene.py | Artifact CRUD hygiene: naming, orphan detection | Post-production |

## External References
- AgentBench: github.com/THUDM/AgentBench (step-level LLM agent evaluation framework)
- WebArena: github.com/web-arena-x/webarena (web navigation trajectory benchmark)
- SWE-bench: github.com/princeton-nlp/SWE-bench (software engineering agent benchmark)
- tau-bench: github.com/sierra-research/tau-bench (tool-agent-user trajectory evaluation)

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[bld_tools_github_issue_template]] | sibling | 0.33 |
| [[bld_knowledge_card_trajectory_eval]] | upstream | 0.33 |
| [[bld_tools_pricing_page]] | sibling | 0.29 |
| [[bld_tools_prompt_technique]] | sibling | 0.29 |
| [[bld_tools_self_improvement_loop]] | sibling | 0.29 |
