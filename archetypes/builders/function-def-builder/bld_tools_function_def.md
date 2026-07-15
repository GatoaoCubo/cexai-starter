---
kind: tools
id: bld_tools_function_def
pillar: P04
llm_function: CALL
purpose: Tools and APIs available for function_def production
quality: null
title: "Tools Function Def"
version: "1.0.0"
author: n03_builder
tags: [function_def, builder, examples]
tldr: "Golden and anti-examples for function def construction, demonstrating ideal structure and common pitfalls."
domain: "function def construction"
created: "2026-04-07"
updated: "2026-04-07"
8f: "F5_call"
keywords: [function def construction, tools function def, function_def, builder, examples, production tools, data sources, anthropic docs, tool permissions, interim validation
no]
density_score: 0.90
related:
  - bld_tools_search_tool
  - bld_tools_cli_tool
  - bld_tools_response_format
  - bld_tools_input_schema
  - bld_tools_mcp_server
---
# Tools: function-def-builder
## Production Tools
| Tool | Purpose | When | Status |
|------|---------|------|--------|
| brain_query [MCP] | Search existing function_def artifacts in pool | Phase 1 (check duplicates) | CONDITIONAL |
| validate_artifact.py | Generic artifact validator | Phase 3 | [PLANNED] |
| cex_forge.py | Generate artifact from seeds | Alternative compose | [PLANNED] |
| jsonschema_validate | Validate parameters against JSON Schema draft-07 | Phase 3 | [PLANNED] |
## Data Sources
| Source | Path/URL | Data |
|--------|----------|------|
| CEX Schema | P04_tools/_schema.yaml | Field definitions, function_def kind |
| CEX Examples | P04_tools/examples/ | Real function_def artifacts |
| SEED_BANK | archetypes/SEED_BANK.yaml | Seeds for P04_function_def |
| TAXONOMY | archetypes/TAXONOMY_LAYERS.yaml | Layer position, runtime layer |
| OpenAI Docs | platform.openai.com/docs/guides/function-calling | Provider reference |
| Anthropic Docs | docs.anthropic.com/en/docs/build-with-claude/tool-use | Provider reference |
## Tool Permissions

| Category | Tools | Status |
|----------|-------|--------|
| ALLOWED | Read, Write, Edit, Bash, Glob, Grep | Explicitly permitted |
| DENIED | (none) | Explicitly blocked |
| EFFECTIVE | Bash, Edit, Glob, Grep, Read, Write | ALLOWED minus DENIED |

## Interim Validation
No automated validator exists yet. Manually check each QUALITY_GATES.md gate against
the produced artifact. Key checks: YAML parses, id pattern, parameters is valid JSON Schema,
body <= 2048 bytes, quality == null, returns defined.

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[bld_tools_search_tool]] | sibling | 0.60 |
| bld_tools_cli_tool | sibling | 0.57 |
| [[bld_tools_response_format]] | sibling | 0.56 |
| [[bld_tools_input_schema]] | sibling | 0.56 |
| [[bld_tools_mcp_server]] | sibling | 0.56 |
