---
quality: null
quality: null
id: bld_tools_domain_vocabulary
kind: knowledge_card
pillar: P01
title: "Domain Vocabulary Builder -- Tools"
version: 1.0.0
llm_function: CALL
tags: [builder, domain_vocabulary, tools]
author: builder
tldr: "Domain Vocabulary knowledge: tool integrations, CLI commands, and external capabilities"
8f: "F3_inject"
keywords: [domain vocabulary knowledge, tool integrations, cli commands, and external capabilities, builder, domain_vocabulary, tools, "cex_compile.py {path}", cex_doctor.py, "cex_retriever.py --query {intent}"]
density_score: 0.88
created: "2026-04-17"
updated: "2026-04-17"
related:
  - bld_tools_data_contract
  - bld_tools_value_object
  - bld_tools_bounded_context
  - bld_tools_domain_event
  - bld_tools_deployment_manifest
---
# Domain Vocabulary Builder -- Tools

Builder domain: ubiquitous language. Primary nucleus: N04.

## Runtime Tools

| Tool | Function | Stage |
|------|----------|-------|
| `cex_compile.py {path}` | Compile artifact to YAML | F8 COLLABORATE |
| `cex_doctor.py` | Validate builder integrity (13 ISOs present) | F7 GOVERN |
| `cex_retriever.py --query {intent}` | Find similar domain_vocabulary artifacts | F5 CALL |
| `cex_score.py {path}` | Peer-review quality scoring | F7 GOVERN |
| `cex_hooks.py validate {path}` | Frontmatter + field validation | F7 GOVERN |

## Context Sources

| Source | Content | Stage |
|--------|---------|-------|
| `N00_genesis/P01_knowledge/library/kind/kc_domain_vocabulary.md` | Primary domain KC | F3 INJECT |
| `.cex/kinds_meta.json` (key: `domain_vocabulary`) | Boundary, pillar, naming | F1 CONSTRAIN |
| `archetypes/builders/domain-vocabulary-builder/bld_examples_domain_vocabulary.md` | Reference examples | F3 INJECT |
| `archetypes/builders/domain-vocabulary-builder/bld_schema_domain_vocabulary.md` | Output schema | F2 BECOME |

## Discovery

```bash
# Find existing domain_vocabulary artifacts
python _tools/cex_retriever.py --query "Governed canonical term registry for a bounded context"

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
| [[bld_tools_data_contract]] | sibling | 0.62 |
| bld_tools_value_object | sibling | 0.61 |
| bld_tools_bounded_context | sibling | 0.60 |
| bld_tools_domain_event | sibling | 0.59 |
| bld_tools_deployment_manifest | sibling | 0.59 |
