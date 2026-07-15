---
kind: tools
id: bld_tools_permission
pillar: P04
llm_function: CALL
purpose: Tools available for permission production
quality: null
title: "Tools Permission"
version: "1.0.0"
author: n03_builder
tags: [permission, builder, examples]
tldr: "Golden and anti-examples for permission construction, demonstrating ideal structure and common pitfalls."
domain: "permission construction"
created: "2026-04-07"
updated: "2026-04-07"
8f: "F5_call"
keywords: [permission construction, tools permission, permission, builder, examples, production tools, data sources, tool permissions, interim validation
manually, access matrix]
density_score: 0.90
related:
  - bld_tools_validation_schema
  - bld_tools_golden_test
  - bld_tools_response_format
  - bld_tools_path_config
  - bld_tools_retriever_config
---

# Tools: permission-builder
## Production Tools
| Tool | Purpose | When | Status |
|------|---------|------|--------|
| brain_query [MCP] | Search existing permissions | Phase 1 (check duplicates) | CONDITIONAL |
| validate_artifact.py | Validate any artifact kind | Phase 3 | [PLANNED] |
| cex_forge.py | Generate artifact from seeds | Alternative compose | [PLANNED] |
## Data Sources
| Source | Path/URL | Data |
|--------|----------|------|
| CEX Schema | P09_config/_schema.yaml | Field definitions for permission |
| CEX Examples | P09_config/examples/ | Existing permission artifacts |
| SEED_BANK | archetypes/SEED_BANK.yaml | P09_permission seeds |
| RBAC Patterns | NIST RBAC standard | Role hierarchy best forctices |
## Tool Permissions

| Category | Tools | Status |
|----------|-------|--------|
| ALLOWED | Read, Write, Edit, Bash, Glob, Grep | Explicitly permitted |
| DENIED | (none) | Explicitly blocked |
| EFFECTIVE | Bash, Edit, Glob, Grep, Read, Write | ALLOWED minus DENIED |

## Interim Validation
Manually check each QUALITY_GATES.md gate against produced artifact.
1. [ ] YAML parses
2. [ ] id matches p09_perm_ prefix
3. [ ] read/write/execute in [allow, deny, conditional]
4. [ ] roles is non-empty list
5. [ ] Access Matrix present with roles

## Metadata

```yaml
id: bld_tools_permission
pipeline: 8F
scoring: hybrid_3_layer
```

```bash
python _tools/cex_score.py --apply bld-tools-permission.md
```

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[bld_tools_validation_schema]] | sibling | 0.58 |
| [[bld_tools_golden_test]] | sibling | 0.56 |
| [[bld_tools_response_format]] | sibling | 0.55 |
| [[bld_tools_path_config]] | sibling | 0.55 |
| [[bld_tools_retriever_config]] | sibling | 0.54 |
