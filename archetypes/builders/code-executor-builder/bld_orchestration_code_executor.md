---
kind: collaboration
id: bld_collaboration_code_executor
pillar: P12
llm_function: COLLABORATE
purpose: How code-executor-builder works in crews with other builders
pattern: each builder must know its ROLE in a team, what it RECEIVES and PRODUCES
quality: null
title: "Collaboration Code Executor"
version: "1.0.0"
author: n03_builder
tags: [code_executor, builder, examples]
tldr: "Golden and anti-examples for code executor construction, demonstrating ideal structure and common pitfalls."
domain: "code executor construction"
created: "2026-04-07"
updated: "2026-04-07"
8f: "F8_collaborate"
keywords: [code executor construction, collaboration code executor, code_executor, builder, examples, "### crew: agent runtime", my role, crew compositions, code execution pipeline, agent runtime]
density_score: 0.90
related:
  - bld_collaboration_function_def
  - code-executor-builder
  - p01_kc_code_executor
  - bld_collaboration_cli_tool
  - bld_collaboration_handoff_protocol
---
# Collaboration: code-executor-builder
## My Role in Crews
I am a SPECIALIST. I answer ONE question: "what languages can run here, how is it isolated, and what are the limits?"
I do not build CLI commands. I do not define protocol servers.
I specify sandboxed execution environments so agents can safely run LLM-generated code.
## Crew Compositions
### Crew: "Code Execution Pipeline"
```
  1. function-def-builder -> "function interface (what to call)"
  2. code-executor-builder -> "execution environment (where it runs)"
  3. retriever-builder -> "data access (what data is available)"
```
### Crew: "Agent Runtime"
```
  1. code-executor-builder -> "sandboxed code execution"
  2. cli-tool-builder -> "terminal command execution"
  3. daemon-builder -> "persistent background processes"
```
## Handoff Protocol
### I Receive
- seeds: execution use case, language requirements, isolation needs
- optional: resource limits, network policy, session model
### I Produce
- code_executor artifact (.md + .yaml compiled)
- committed to: `cex/P04_tools/examples/p04_exec_{runtime}.md`
### I Signal
- signal: complete (with quality score from QUALITY_GATES)
- if quality < 8.0: signal retry with failure reasons
## Builders I Depend On
None — independent builder (layer 0). Code executors are self-contained environment specs.
## Builders That Depend On Me
| Builder | Why |
|---------|-----|
| agent-builder | Agents reference code executors for running generated code |
| function-def-builder | Functions may specify code_executor as their runtime |
| mcp-server-builder | MCP servers may use code executors for dynamic operations |

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[bld_collaboration_function_def]] | sibling | 0.36 |
| [[code-executor-builder]] | upstream | 0.35 |
| [[p01_kc_code_executor]] | upstream | 0.30 |
| bld_collaboration_cli_tool | sibling | 0.27 |
| [[bld_collaboration_handoff_protocol]] | sibling | 0.26 |
