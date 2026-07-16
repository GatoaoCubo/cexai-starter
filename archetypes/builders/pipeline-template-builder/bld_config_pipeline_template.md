---
kind: config
id: bld_config_pipeline_template
pillar: P09
llm_function: CONSTRAIN
purpose: Naming, paths, limits for pipeline_template production
quality: null
title: "Config Pipeline Template"
version: "1.0.0"
author: n03_builder
tags: [pipeline_template, builder, config, scenario_indexed]
tldr: "Naming, paths, limits for pipeline_template production"
domain: "pipeline_template construction"
created: "2026-04-18"
updated: "2026-04-18"
8f: "F1_constrain"
keywords: [limits for pipeline_template production, pipeline_template construction, config pipeline template, pipeline_template, builder, config, scenario_indexed, "p12_pt_{{scenario}}.yaml", p12_pt_new_feature.yaml]
density_score: 0.86
related:
 - bld_config_ab_test_config
 - bld_config_prospective_memory
 - bld_config_working_memory
 - bld_config_transport_config
 - bld_config_episodic_memory
---

## Naming Convention
Pattern: `p12_pt_`{{scenario}}`.yaml`
Examples: `p12_pt_new_feature.yaml`, `p12_pt_bug_fix_unknown.yaml`, `p12_pt_refactoring.yaml`
Note: file extension is `.yaml` (not `.md`); pipeline_templates are data artifacts.

## Paths
Artifacts stored in: `P12_orchestration/pipelines/p12_pt_`{{scenario}}`.yaml`
Compiled JSON: `P12_orchestration/pipelines/compiled/p12_pt_`{{scenario}}`.json`
Index entry: `.cex/indices/pipelines.json`

## Limits
max_bytes: 4096
max_turns: 3
effort_level: 2
max_stages_per_pipeline: 10
max_revision_iterations: 5
canonical_scenarios: 7

## Hooks
pre_build: validate_scenario_in_canonical_enum
post_build: compile_to_json
on_error: null
on_quality_fail: rebuild_with_canonical_catalog

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
| [[bld_config_ab_test_config]] | sibling | 0.30 |
| [[bld_config_prospective_memory]] | sibling | 0.28 |
| [[bld_config_working_memory]] | sibling | 0.28 |
| [[bld_config_transport_config]] | sibling | 0.27 |
| [[bld_config_episodic_memory]] | sibling | 0.26 |
