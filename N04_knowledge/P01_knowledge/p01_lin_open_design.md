---
id: p01_lin_open_design
kind: lineage_record
pillar: P01
version: 1.0.0
target_artifact: N03_engineering/P06_schema/p06_ds_*.md (150 instances)
sources_count: 1
activities_count: 3
derivation_type: wasDerivedFrom
domain: knowledge-provenance
created: "2026-06-24"
updated: "2026-06-24"
author: lineage-record-builder
quality: null
tags: [lineage_record, knowledge-provenance, open-design, Apache-2.0, design-system, assimilation]
tldr: "Provenance for 150 design_system instances: clean-room concept extraction from nexu-io/open-design (Apache-2.0 v0.11.0)"
related:
  - p01_kc_gstack_attribution_ledger
  - p01_lin_graphify
---

# Lineage: design_system x150 (open-design)

## Canonical Provenance Frontmatter Schema

Derived artifacts MUST carry this block:

```yaml
provenance:
  source: "github.com/nexu-io/open-design"
  license: "Apache-2.0"
  lineage_record: "p01_lin_open_design"
  method: "clean_room_concept_extraction"
  derived: "2026-06-24"
```

## Entities

| ID | Type | Location | Retrieved |
|----|------|----------|-----------|
| open_design_src | prov:Entity | github.com/nexu-io/open-design v0.11.0 | 2026-06-15T00:00:00Z |

Source: nexu-io/open-design, Apache-2.0, v0.11.0. Method: concept-inspiration
only -- "0 external traces" (N07 DESIGN_ASSIM mission, 2026-06-15). 150 instances;
10 regenerated via the engine (spec 07, 2026-06-24); 140 provenance-retrofitted.

## Activities

| ID | Label | Used | Generated | Agent | Timestamp |
|----|-------|------|-----------|-------|-----------|
| act_extract | clean_room_concept_extraction | open_design_src | ds_concepts | N07 | 2026-06-15T00:00:00Z |
| act_build_150 | design_system_build_batch | ds_concepts | ds_instances_150 | N03 | 2026-06-15T00:00:00Z |
| act_retrofit_10 | engine_regen_10 | ds_concepts | ds_regen_10 | N03 | 2026-06-24T00:00:00Z |

## Agents

| ID | Type | Role |
|----|------|------|
| N07 | nucleus | orchestrator + concept extraction coordinator |
| N03 | nucleus | design_system artifact producer |

## Derivation Relations

- ds_instances_150 wasDerivedFrom open_design_src
- ds_instances_150 wasGeneratedBy act_build_150
- ds_instances_150 wasAttributedTo N03
- ds_regen_10 wasGeneratedBy act_retrofit_10
- ds_regen_10 wasAttributedTo N03

## Apache-2.0 NOTICE Attribution

```
This product includes design system concepts derived from open-design
(https://github.com/nexu-io/open-design), Copyright nexu-io contributors,
licensed under the Apache License, Version 2.0.
Original: nexu-io/open-design v0.11.0. Derivation: clean-room concept
extraction (no source code vendored).
```

## Related Artifacts

| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[p01_lin_graphify]] | sibling | 0.50 |
| [[p01_kc_gstack_attribution_ledger]] | sibling | 0.55 |
| p06_ds_001 | downstream | 0.80 |
