---
kind: tools
id: bld_tools_glossary_entry
pillar: P04
llm_function: CALL
purpose: Tools and APIs available for glossary_entry production
quality: null
title: "Tools Glossary Entry"
version: "1.0.0"
author: n03_builder
tags: [glossary_entry, builder, examples]
tldr: "Golden and anti-examples for glossary entry construction, demonstrating ideal structure and common pitfalls."
domain: "glossary entry construction"
created: "2026-04-07"
updated: "2026-04-07"
8f: "F5_call"
keywords: [glossary entry construction, tools glossary entry, glossary_entry, builder, examples, production tools, data sources, tool permissions, interim validation
no, related artifacts]
density_score: 0.90
related:
  - bld_tools_retriever_config
  - bld_tools_validator
  - bld_tools_lens
  - bld_tools_input_schema
  - bld_tools_cli_tool
---

# Tools: glossary-entry-builder
## Production Tools
| Tool | Purpose | When | Status |
|------|---------|------|--------|
| brain_query [MCP] | Search existing glossary entries in pool | Phase 1 (check duplicates) | CONDITIONAL |
| validate_artifact.py | Generic artifact validator | Phase 3 | [PLANNED] |
| cex_forge.py | Generate artifact from seeds | Alternative compose | [PLANNED] |
## Data Sources
| Source | Path/URL | Data |
|--------|----------|------|
| CEX Schema | P01_knowledge/_schema.yaml | Field definitions for glossary_entry |
| CEX Examples | P01_knowledge/examples/ | Real glossary_entry artifacts |
| SEED_BANK | archetypes/SEED_BANK.yaml | P01_glossary_entry seeds |
| TAXONOMY | archetypes/TAXONOMY_LAYERS.yaml | Layer position, overlaps |
| Existing pool | pool/ (brain_query) | Existing term definitions |
## Tool Permissions

| Category | Tools | Status |
|----------|-------|--------|
| ALLOWED | Read, Write, Edit, Bash, Glob, Grep | Explicitly permitted |
| DENIED | (none) | Explicitly blocked |
| EFFECTIVE | Bash, Edit, Glob, Grep, Read, Write | ALLOWED minus DENIED |

## Interim Validation
No automated validator exists yet for glossary entries.
Manually check each QUALITY_GATES.md gate against produced artifact:
1. [ ] YAML parses without error
2. [ ] id matches p01_gl_ prefix
3. [ ] definition is <= 3 lines
4. [ ] synonyms list is non-empty
5. [ ] quality is null
6. [ ] term is non-empty string

## Metadata

```yaml
id: bld_tools_glossary_entry
pipeline: 8F
scoring: hybrid_3_layer
```

```bash
python _tools/cex_score.py --apply bld-tools-glossary-entry.md
```

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[bld_tools_retriever_config]] | sibling | 0.60 |
| [[bld_tools_validator]] | sibling | 0.60 |
| [[bld_tools_lens]] | sibling | 0.60 |
| [[bld_tools_input_schema]] | sibling | 0.59 |
| bld_tools_cli_tool | sibling | 0.58 |
