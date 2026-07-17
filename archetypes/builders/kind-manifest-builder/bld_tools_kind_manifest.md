---
kind: tools
id: bld_tools_kind_manifest
pillar: P04
llm_function: CALL
purpose: "Tools and APIs available for kind_manifest production"
quality: null
title: "Tools Kind Manifest"
version: "1.0.0"
author: n03_builder
tags: [kind_manifest, builder, examples]
tldr: "Golden and anti-examples for kind_manifest construction: the real 5-tool bucket, the naming-validator skip-list, and the per-pillar directory counter."
domain: "kind_manifest construction"
created: "2026-07-10"
updated: "2026-07-10"
8f: "F5_call"
keywords: [kind_manifest construction, tools kind manifest, kind_manifest, builder, examples, production tools, data sources, tool permissions, interim validation, related artifacts]
density_score: 0.87
related:
  - bld_tools_kind
  - bld_tools_output_template
  - bld_tools_knowledge_card
  - bld_schema_kind_manifest
---
# Tools: kind-manifest-builder
## Production Tools
| Tool | Purpose | When | Status |
|------|---------|------|--------|
| Grep / Glob | Search `N00_genesis/P0X_*/kind_{{kind}}/` for an existing manifest, or a sibling to confirm the current body-shape convention | Phase 1 (check duplicates) | ACTIVE |
| brain_query [MCP] | Search existing kind_manifest instances in pool | Phase 1 | CONDITIONAL |
| cex_compile.py | .md -> .yaml compilation of the produced artifact | F8 COLLABORATE | REGISTERED (`.cex/kind_tool_supplement.json`) |
| cex_retriever.py | TF-IDF similarity check against the corpus before publishing | Phase 1/F7 | REGISTERED (same bucket) |
| cex_memory_select.py | Pulls relevant learning_record/memory context at F3 INJECT | F3 | REGISTERED (same bucket) |
| cex_query.py | General artifact query interface | Phase 1 | REGISTERED (same bucket) |
| cex_fts5_search.py | Full-text search across the corpus | Phase 1 | REGISTERED (same bucket) |
## Real Implementation Touchpoints (grounding, not production tools)
These are the REAL files a kind_manifest artifact's own SCHEMA/CONFIG describe -- read them to verify naming/count claims before producing, but do not treat them as CLI tools this builder invokes:
| Module | Role |
|--------|------|
| `.cex/kinds_meta.json` (`kind_manifest` entry) | boundary, pillar (P01), nucleus (N03), max_bytes, depends_on=[], core=false, registered 2026-07-10 |
| `.cex/kind_tool_supplement.json` (`kind_manifest` key) | The REAL 5-tool bucket this ISO documents above -- a kind-SPECIFIC bucket, not a generic shared one |
| `_tools/cex_naming_validator.py` (lines ~80-81, ~119) | Explicitly SKIPs any filename starting with `kind_manifest_` from the generic `p{{nn}}_{{kind}}_{{descriptor}}_n{{nn}}.ext` convention -- confirmed by direct read |
| `_tools/cex_stats.py` (`count_kind_manifests_by_pillar()`, ~line 148) | Counts `kind_*` DIRECTORIES per pillar directly on disk -- a directory count, not a `kind:`-field count, so it was unaffected by the R-310 re-typing |
| `archetypes/builders/kind-manifest-builder/bld_schema_kind_manifest.md` | This family's own schema -- read FIRST, always |
## Data Sources
| Source | Path/URL | Data |
|--------|----------|------|
| CEX Schema | `N00_genesis/P01_knowledge/_schema.yaml` (pillar schemas) | Field definitions for kind_manifest |
| kinds_meta.json | `.cex/kinds_meta.json` (`kind_manifest` entry) | boundary, naming, max_bytes, depends_on, core, nucleus, pillar |
| kind_tool_supplement.json | `.cex/kind_tool_supplement.json` | `kind_to_tools["kind_manifest"]` = 5 tools (see table above) |
| Real corpus | `N00_genesis/P0[1-9]_*/kind_*/kind_manifest_n00.md`, `N00_genesis/P1[0-2]_*/kind_*/kind_manifest_n00.md` | 294 real instances across all 12 pillar directories |
| Register history | `docs/PROJECT_BACKLOG.md` R-077, R-298, R-307, R-310 | The lineage this kind's own scaffold traces |
## Tool Permissions

| Category | Tools | Status |
|----------|-------|--------|
| ALLOWED | Read, Write, Edit, Bash, Glob, Grep | Explicitly permitted |
| DENIED | (none) | Explicitly blocked |
| EFFECTIVE | Bash, Edit, Glob, Grep, Read, Write | ALLOWED minus DENIED |

## Interim Validation
No dedicated automated validator exists yet for kind_manifest beyond the generic 7-check `cex_wave_validator.py` (ISO-level) and `cex_8f_runner.py`'s H01-H0N gates (artifact-level, per `bld_eval_kind_manifest.md`). Manually check each gate:
1. [ ] YAML parses without error
2. [ ] `kind` == `kind_manifest`, `nucleus` == `n00`, `8f` == `F3_inject`
3. [ ] `depends_on` == `[]` (never populated)
4. [ ] `quality` is `null`
5. [ ] `id` matches `^n00_[a-z][a-z0-9_]+_manifest$`
6. [ ] filename == `kind_manifest_n00.md` (invariant), directory == `kind_{{kind}}/`
7. [ ] the Builder section states a REAL path or an honest OPEN callout -- never fabricated

## Metadata

```yaml
id: bld_tools_kind_manifest
pipeline: 8F
scoring: hybrid_3_layer
```

```bash
python _tools/cex_score.py --apply bld-tools-kind-manifest.md
```

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[bld_tools_kind]] | sibling (reflexive-case source) | 0.50 |
| [[bld_tools_output_template]] | related (same resolution shape) | 0.40 |
| [[bld_tools_knowledge_card]] | related (former mis-type contrast) | 0.36 |
| [[bld_schema_kind_manifest]] | upstream | 0.33 |
