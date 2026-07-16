---
kind: config
id: bld_config_kind_manifest
pillar: P09
llm_function: CONSTRAIN
purpose: "Naming conventions, file paths, size limits, operational constraints"
pattern: "CONFIG restricts SCHEMA, never contradicts it"
effort: low
max_turns: 15
disallowed_tools: []
fork_context: null
hooks:
  pre_build: null
  post_build: null
  on_error: null
  on_quality_fail: null
permission_scope: nucleus
quality: null
title: "Config Kind Manifest"
version: "1.0.0"
author: n03_builder
tags: [kind_manifest, builder, examples]
tldr: "Golden and anti-examples for kind_manifest construction: the fixed-filename/varying-directory naming axis and the clean, drift-free id pattern."
domain: "kind_manifest construction"
created: "2026-07-10"
updated: "2026-07-10"
8f: "F1_constrain"
keywords: [naming conventions, file paths, size limits, operational constraints, kind_manifest construction, config kind manifest, kind_manifest, builder, examples, "n00_{{kind}}_manifest"]
density_score: 0.87
related:
  - bld_schema_kind_manifest
  - bld_config_kind
  - bld_config_knowledge_card
  - bld_output_template_kind_manifest
  - bld_config_output_template
---
# Config: kind_manifest Production Rules
## Naming Convention
| Scope | Convention | Example | Status |
|-------|-----------|---------|--------|
| Artifact id | `n00_{{kind}}_manifest` | `n00_agent_manifest` | CANONICAL -- 294/294 real instances match, ZERO drift |
| Artifact filename | `kind_manifest_n00.md` | `kind_manifest_n00.md` | INVARIANT -- identical across all 294 real instances |
| Artifact directory | `kind_{{kind}}/` | `kind_agent/` | The ONE path segment that varies with the target kind |
| Builder directory | kebab-case | `kind-manifest-builder/` | this scaffold |
| Frontmatter fields | snake_case | `depends_on`, `density_score` | universal |
Rule: id MUST equal `n00_{{kind}}_manifest`, but filename is INVARIANT rather than derived from id -- the OPPOSITE convention from most kinds (which template the FILENAME and hold the id fixed or freely chosen). This is a deliberate, corpus-wide convention (`.cex/kinds_meta.json`'s own `naming: "kind_{{kind}}/kind_manifest_n00.md"` registers exactly this shape), not a drift needing reconciliation.
## File Paths
1. Real instance: `N00_genesis/P0X_{{pillar_domain}}/kind_{{kind}}/kind_manifest_n00.md` (X = the DOCUMENTED kind's own pillar number, 01-12)
2. Compiled: `N00_genesis/P0X_{{pillar_domain}}/compiled/kind_manifest_n00.yaml` (via `cex_compile.py`)
3. Builder ISOs (this family): `archetypes/builders/kind-manifest-builder/bld_{{role}}_kind_manifest.md`
4. Reference corpus (read-only grounding, not an output path): `.cex/kinds_meta.json`'s `kind_manifest` entry
## Size Limits (aligned with SCHEMA -- per kinds_meta.json)
1. Whole file: max 8192 bytes; real corpus observed 3,256-6,352B (p95 4,635B)
2. Density: >= 0.75 (doctor floor); reference corpus self-reports ~1.0 (near-zero blank lines)
## depends_on (fixed by kinds_meta.json -- do not vary per-instance)
`[]` -- EMPTY. A kind_manifest instance may CITE any kind by name in its "Related kinds" prose section, but declares no formal `depends_on` edge -- a manifest is a reference document, not a build-time dependency of the kind it documents.
## Fixed Per-Instance Values (never vary, per the real 294-instance corpus)
| Field | Value | Source |
|-------|-------|--------|
| `8f` | `F3_inject` | 294/294 real instances |
| `nucleus` | `n00` (lowercase) | 294/294 real instances -- distinct from kinds_meta.json's owning-nucleus field (`N03`) |
| `density_score` | `1.0` | 294/294 real instances hard-code this exactly |
| `quality` | `null` | never self-scored, same as every other CEX kind |
## Builder-Pointer Policy (this kind's own operational quirk)
1. If `archetypes/builders/{{kind}}-builder/` exists on disk, cite its REAL path plus a `cex_8f_runner.py` invocation example
2. If it does NOT exist, write "## Builder -- honest status (register row R-XXX, OPEN)" naming the real register row -- never fabricate a path
3. When a builder that was previously OPEN later lands, update the manifest to the standard pointer -- this is a maintenance duty of whichever nucleus scaffolds the builder, not this builder's own job to police retroactively

## Metadata

```yaml
id: bld_config_kind_manifest
pipeline: 8F
scoring: hybrid_3_layer
```

```bash
python _tools/cex_score.py --apply bld-config-kind-manifest.md
```

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[bld_schema_kind_manifest]] | upstream | 0.42 |
| [[bld_config_kind]] | sibling (reflexive-case source) | 0.38 |
| [[bld_config_knowledge_card]] | sibling (former mis-type contrast) | 0.36 |
| [[bld_output_template_kind_manifest]] | upstream | 0.33 |
| [[bld_config_output_template]] | sibling | 0.30 |
