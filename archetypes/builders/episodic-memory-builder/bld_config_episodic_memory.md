---
quality: null
quality: null
kind: config
id: bld_config_episodic_memory
pillar: P09
llm_function: CONSTRAIN
purpose: Naming, paths, size limits for episodic_memory production
effort: medium
max_turns: 20
title: "Config Episodic Memory"
version: "1.0.0"
author: n03_builder
tags: [episodic_memory, builder, config]
tldr: "Naming, paths, size limits, and enum constraints for episodic_memory production."
domain: "episodic memory construction"
created: "2026-04-17"
updated: "2026-04-17"
8f: "F1_constrain"
keywords: [episodic memory construction, config episodic memory, size limits, episodic_memory, builder, config, "p10_ep_{scope}.md", p10_ep_n07_orchestration.md, episodic-memory-builder/, episode_schema]
density_score: 0.90
related:
  - bld_config_working_memory
  - bld_config_prospective_memory
  - bld_config_memory_scope
  - bld_config_retriever_config
  - bld_config_pipeline_template
---
# Config: episodic_memory Production Rules

## Naming Convention
| Scope | Convention | Example |
|-------|-----------|---------|
| Artifact files | `p10_ep_{scope}.md` | `p10_ep_n07_orchestration.md` |
| Builder directory | kebab-case | `episodic-memory-builder/` |
| Frontmatter fields | snake_case | `episode_schema`, `retrieval_method`, `decay_policy` |
| Store slug | snake_case, lowercase | `n07_orchestration`, `n01_research` |

Rule: id MUST equal filename stem.

## File Paths
- Output: `N0x_{domain}/P10_memory/p10_ep_{scope}.md`
- Compiled: `N0x_{domain}/P10_memory/compiled/p10_ep_{scope}.yaml`

## Size Limits
- Body: max 4096 bytes
- Density: >= 0.80

## Retrieval Method Enum
| Value | Mechanism |
|-------|-----------|
| recency | Most recent N episodes |
| relevance | Embedding similarity search |
| hybrid | Recency score + relevance score fusion |

## Decay Policy Methods
| Method | When to use |
|--------|-------------|
| time | Age-based: purge after N days |
| count | Size-based: remove oldest when > max |
| relevance | Utility-based: remove never-retrieved episodes |
| hybrid | Time + relevance combined |

## Episode Count Guidelines
| Agent Type | Recommended Count |
|-----------|------------------|
| Single-task agent | 50-100 |
| Multi-domain agent | 100-500 |
| Long-running orchestrator | 200-1000 |
| Never | unlimited (null) |

## Configuration Checklist

- Verify all required fields are present in frontmatter before saving
- Validate config values against schema constraints (type, range, enum)
- Cross-reference with related configs to avoid contradictions
- Test config loading in target runtime before committing

## Validation

```yaml
# Required config validation
fields_present: true
types_valid: true
ranges_checked: true
cross_refs_verified: true
```

```bash
python _tools/cex_compile.py {FILE}
python _tools/cex_doctor.py --scope {BUILDER}
```

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| bld_config_working_memory | sibling | 0.42 |
| bld_config_prospective_memory | sibling | 0.41 |
| [[bld_config_memory_scope]] | sibling | 0.32 |
| [[bld_config_retriever_config]] | sibling | 0.29 |
| bld_config_pipeline_template | sibling | 0.29 |
