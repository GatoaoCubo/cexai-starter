---
kind: tools
id: bld_tools_lifecycle_rule
pillar: P04
llm_function: CALL
purpose: Tools available for lifecycle_rule production
quality: null
title: "Tools Lifecycle Rule"
version: "1.0.0"
author: n03_builder
tags: [lifecycle_rule, builder, examples]
tldr: "Golden and anti-examples for lifecycle rule construction, demonstrating ideal structure and common pitfalls."
domain: "lifecycle rule construction"
created: "2026-04-07"
updated: "2026-04-07"
8f: "F5_call"
keywords: [lifecycle rule construction, tools lifecycle rule, lifecycle_rule, builder, examples, production tools, data sources, quality gates, tool permissions, interim validation
manually]
density_score: 0.90
related:
  - bld_tools_golden_test
  - bld_tools_unit_eval
  - bld_tools_retriever_config
  - bld_tools_cli_tool
  - bld_tools_memory_scope
---

# Tools: lifecycle-rule-builder
## Production Tools
| Tool | Purpose | When | Status |
|------|---------|------|--------|
| brain_query [MCP] | Search existing lifecycle_rules | Phase 1 (check duplicates) | CONDITIONAL |
| validate_artifact.py | Validate any artifact kind | Phase 3 | [PLANNED] |
| cex_forge.py | Generate artifact from seeds | Alternative compose | [PLANNED] |
## Data Sources
| Source | Path/URL | Data |
|--------|----------|------|
| CEX Schema | P11_feedback/_schema.yaml | Field definitions for lifecycle_rule |
| CEX Examples | P11_feedback/examples/ | Existing lifecycle_rule artifacts |
| SEED_BANK | archetypes/SEED_BANK.yaml | P11_lifecycle_rule seeds |
| TAXONOMY_LAYERS | archetypes/TAXONOMY_LAYERS.yaml | Position and overlap info |
| Quality Gates | archetypes/builders/quality-gate-builder/ | Reference for gate integration |
## Tool Permissions

| Category | Tools | Status |
|----------|-------|--------|
| ALLOWED | Read, Write, Edit, Bash, Glob, Grep | Explicitly permitted |
| DENIED | (none) | Explicitly blocked |
| EFFECTIVE | Bash, Edit, Glob, Grep, Read, Write | ALLOWED minus DENIED |

## Interim Validation
Manually check each QUALITY_GATES.md gate against produced artifact.
1. [ ] YAML parses
2. [ ] id matches p11_lc_ prefix
3. [ ] freshness_days is positive integer
4. [ ] review_cycle in [weekly, monthly, quarterly, yearly]
5. [ ] States table >= 3 states
6. [ ] Transitions table >= 3 transitions
7. [ ] All triggers are measurable

## Metadata

```yaml
id: bld_tools_lifecycle_rule
pipeline: 8F
scoring: hybrid_3_layer
```

```bash
python _tools/cex_score.py --apply bld-tools-lifecycle-rule.md
```

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[bld_tools_golden_test]] | sibling | 0.56 |
| [[bld_tools_unit_eval]] | sibling | 0.55 |
| [[bld_tools_retriever_config]] | sibling | 0.55 |
| bld_tools_cli_tool | sibling | 0.55 |
| [[bld_tools_memory_scope]] | sibling | 0.55 |
