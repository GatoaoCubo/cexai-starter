---
kind: tools
id: bld_tools_interface
pillar: P04
llm_function: CALL
purpose: Tools and APIs available for interface production
quality: null
title: "Tools Interface"
version: "1.0.0"
author: n03_builder
tags: [interface, builder, examples]
tldr: "Golden and anti-examples for interface construction, demonstrating ideal structure and common pitfalls."
domain: "interface construction"
created: "2026-04-07"
updated: "2026-04-07"
8f: "F5_call"
keywords: [interface construction, tools interface, interface, builder, examples, production tools, data sources, tool permissions, interim validation
no, related artifacts]
density_score: 0.90
related:
  - bld_tools_input_schema
  - bld_tools_validator
  - bld_tools_retriever_config
  - bld_tools_cli_tool
  - bld_tools_memory_scope
---

# Tools: interface-builder
## Production Tools
| Tool | Purpose | When | Status |
|------|---------|------|--------|
| brain_query [MCP] | Search existing interfaces in pool | Phase 1 (check duplicates) | CONDITIONAL |
| validate_artifact.py | Generic artifact validator | Phase 3 | [PLANNED] |
| cex_forge.py | Generate artifact from seeds | Alternative compose | [PLANNED] |
## Data Sources
| Source | Path/URL | Data |
|--------|----------|------|
| CEX Schema | P06_schema/_schema.yaml | Field definitions for interface |
| CEX Examples | P06_schema/examples/ | Real interface artifacts |
| SEED_BANK | archetypes/SEED_BANK.yaml | P06_interface seeds |
| TAXONOMY | archetypes/TAXONOMY_LAYERS.yaml | Layer position, overlaps |
| OpenAPI Spec | https://spec.openapis.org/oas/latest.html | Method/contract patterns |
## Tool Permissions

| Category | Tools | Status |
|----------|-------|--------|
| ALLOWED | Read, Write, Edit, Bash, Glob, Grep | Explicitly permitted |
| DENIED | (none) | Explicitly blocked |
| EFFECTIVE | Bash, Edit, Glob, Grep, Read, Write | ALLOWED minus DENIED |

## Interim Validation
No automated validator exists yet for interfaces.
Manually check each QUALITY_GATES.md gate against produced artifact:
1. [ ] YAML parses without error
2. [ ] id matches p06_iface_ prefix
3. [ ] methods list is non-empty
4. [ ] each method has name, input, output
5. [ ] quality is null
6. [ ] backward_compatible is boolean

## Metadata

```yaml
id: bld_tools_interface
pipeline: 8F
scoring: hybrid_3_layer
```

```bash
python _tools/cex_score.py --apply bld-tools-interface.md
```

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[bld_tools_input_schema]] | sibling | 0.64 |
| [[bld_tools_validator]] | sibling | 0.63 |
| [[bld_tools_retriever_config]] | sibling | 0.58 |
| [[bld_tools_cli_tool]] | sibling | 0.58 |
| [[bld_tools_memory_scope]] | sibling | 0.58 |
