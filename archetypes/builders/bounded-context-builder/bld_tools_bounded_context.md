---
quality: null
quality: null
id: bld_tools_bounded_context
kind: knowledge_card
pillar: P08
title: "Bounded Context Builder -- Tools"
version: 1.0.0
llm_function: CALL
tags: [builder, bounded_context, tools]
author: builder
tldr: "Bounded Context architecture: tool integrations, CLI commands, and external capabilities"
8f: "F3_inject"
keywords: [bounded context architecture, tool integrations, cli commands, and external capabilities, builder, bounded_context, tools, "cex_compile.py {path}", cex_doctor.py, "cex_retriever.py --query {intent}"]
density_score: 0.88
created: "2026-04-17"
updated: "2026-04-17"
related:
  - bld_tools_domain_event
  - bld_tools_data_contract
  - bld_tools_deployment_manifest
  - bld_tools_value_object
  - bld_tools_domain_vocabulary
---
# Bounded Context Builder -- Tools

Builder domain: domain architecture. Primary nucleus: N03.

## Runtime Tools

| Tool | Function | Stage |
|------|----------|-------|
| `cex_compile.py {path}` | Compile artifact to YAML | F8 COLLABORATE |
| `cex_doctor.py` | Validate builder integrity (13 ISOs present) | F7 GOVERN |
| `cex_retriever.py --query {intent}` | Find similar bounded_context artifacts | F5 CALL |
| `cex_score.py {path}` | Peer-review quality scoring | F7 GOVERN |
| `cex_hooks.py validate {path}` | Frontmatter + field validation | F7 GOVERN |

## Context Sources

| Source | Content | Stage |
|--------|---------|-------|
| `N00_genesis/P01_knowledge/library/kind/kc_bounded_context.md` | Primary domain KC | F3 INJECT |
| `.cex/kinds_meta.json` (key: `bounded_context`) | Boundary, pillar, naming | F1 CONSTRAIN |
| `archetypes/builders/bounded-context-builder/bld_examples_bounded_context.md` | Reference examples | F3 INJECT |
| `archetypes/builders/bounded-context-builder/bld_schema_bounded_context.md` | Output schema | F2 BECOME |

## Discovery

```bash
# Find existing bounded_context artifacts
python _tools/cex_retriever.py --query "Explicit DDD boundary where a model applies"

# Validate a new artifact
python _tools/cex_hooks.py validate path/to/artifact.md

# Compile after writing
python _tools/cex_compile.py path/to/artifact.md
```

## Tool Integration Checklist

- Verify tool name follows snake_case convention
- Validate input/output schema matches interface contract
- Cross-reference with capability_registry for discoverability
- Test tool invocation in sandbox before production use

## Invocation Pattern

```yaml
# Tool invocation contract
name: tool_name
input_schema: validated
output_schema: validated
error_handling: defined
timeout: configured
```

```bash
python _tools/cex_compile.py {FILE}
python _tools/cex_doctor.py --scope {BUILDER}
```

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[bld_tools_domain_event]] | sibling | 0.67 |
| [[bld_tools_data_contract]] | sibling | 0.67 |
| [[bld_tools_deployment_manifest]] | sibling | 0.65 |
| [[bld_tools_value_object]] | sibling | 0.65 |
| [[bld_tools_domain_vocabulary]] | sibling | 0.64 |
