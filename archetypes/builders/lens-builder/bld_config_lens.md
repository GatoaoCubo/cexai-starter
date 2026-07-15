---
kind: config
id: bld_config_lens
pillar: P09
llm_function: CONSTRAIN
purpose: Naming conventions, file paths, size limits, operational constraints
pattern: CONFIG restricts SCHEMA, never contradicts it
effort: medium
max_turns: 25
disallowed_tools: []
fork_context: null
hooks:
  pre_build: null
  post_build: null
  on_error: null
  on_quality_fail: null
permission_scope: nucleus
quality: null
title: "Config Lens"
version: "1.0.0"
author: n03_builder
tags: [lens, builder, examples]
tldr: "Golden and anti-examples for lens construction, demonstrating ideal structure and common pitfalls."
domain: "lens construction"
created: "2026-04-07"
updated: "2026-04-07"
8f: "F1_constrain"
keywords: [naming conventions, file paths, size limits, operational constraints, lens construction, config lens, lens, builder, examples, "p02_lens_{perspective_slug}.yaml"]
density_score: 0.90
related:
  - p03_ins_lens
  - bld_collaboration_lens
  - bld_memory_lens
  - bld_architecture_lens
  - lens-builder
---
# Config: lens Production Rules
## Naming Convention
| Scope | Convention | Example |
|-------|-----------|---------|
| Artifact files | `p02_lens_{perspective_slug}.yaml` | `p02_lens_cost_efficiency.yaml` |
| Builder directory | kebab-case | `lens-builder/` |
| Frontmatter fields | snake_case | `applies_to`, `perspective` |
| Perspective slugs | snake_case, lowercase | `cost_efficiency`, `security_posture` |
Rule: id MUST equal filename stem.
## File Paths
1. Output: `cex/P02_model/examples/p02_lens_{perspective_slug}.yaml`
2. Compiled: `cex/P02_model/compiled/p02_lens_{perspective_slug}.yaml`
## Size Limits (aligned with SCHEMA)
1. Body: max 2048 bytes
2. Total: ~3000 bytes including frontmatter
3. Density: >= 0.80
## Perspective Rules
| Rule | Enforcement |
|------|-------------|
| Non-empty perspective | HARD (H07) |
| applies_to >= 1 kind | HARD (H08) |
| Concrete filters | SOFT (S04) |
| Declared bias | SOFT (S08) |
## Composition Rules
1. Multiple lenses can apply to the same artifact kind
2. Weight field (0.0-1.0) controls influence in multi-lens scenarios
3. Priority field (integer) controls evaluation order
4. Conflicting lenses: higher priority wins, equal priority uses weight

## Metadata

```yaml
id: bld_config_lens
pipeline: 8F
scoring: hybrid_3_layer
```

```bash
python _tools/cex_score.py --apply bld-config-lens.md
```

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[p03_ins_lens]] | upstream | 0.38 |
| [[bld_orchestration_lens]] | upstream | 0.37 |
| [[bld_memory_lens]] | downstream | 0.37 |
| [[bld_architecture_lens]] | upstream | 0.36 |
| [[lens-builder]] | upstream | 0.35 |
