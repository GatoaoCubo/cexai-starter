---
quality: null
quality: null
id: bld_output_template_lineage_record
kind: knowledge_card
pillar: P05
title: "Output Template: lineage_record"
version: 1.0.0
created: "2026-04-17"
updated: "2026-04-17"
author: builder
domain: lineage_record
tags:
  - "output_template"
  - "lineage_record"
  - "P01"
llm_function: PRODUCE
tldr: "Canonical output template for lineage_record artifacts."
8f: "F3_inject"
keywords:
  - "output template"
  - "output_template"
  - "lineage_record"
  - "## body template"
  - "frontmatter template"
  - "body template"
  - "derivation relations"
  - "related artifacts"
  - "target_artifact_id sources_count"
  - "target_artifact_id"
density_score: null
related:
  - bld_schema_lineage_record
  - kc_lineage_record
  - bld_quality_gate_lineage_record
  - bld_instruction_lineage_record
  - bld_rules_lineage_record
---
# Output Template: lineage_record

## Frontmatter Template
```yaml
---
id: p01_lin_{{name_slug}}
kind: lineage_record
pillar: P01
version: 1.0.0
target_artifact: "{{target_artifact_id}}"
sources_count: {{sources_count}}
activities_count: {{activities_count}}
derivation_type: {{derivation_type}}
domain: "{{domain}}"
created: "{{date}}"
updated: "{{date}}"
author: "{{author}}"
quality: null
tags: [lineage_record, {{domain}}]
tldr: "Provenance chain for {{target_artifact_id}}: {{sources_count}} sources, {{activities_count}} activities"
---
```

## Body Template
```markdown
# Lineage: {{target_artifact_id}}

## Entities
| ID | Type | Location | Retrieved |
|----|------|----------|-----------|
| {{entity_id}} | {{type}} | {{path_or_url}} | {{iso_timestamp}} |

## Activities
| ID | Label | Used | Generated | Agent | Timestamp |
|----|-------|------|-----------|-------|-----------|
| {{activity_id}} | {{label}} | {{entity_ids}} | {{output_id}} | {{agent_id}} | {{iso_timestamp}} |

## Agents
| ID | Type | Role |
|----|------|------|
| {{agent_id}} | {{nucleus|tool|human}} | {{role}} |

## Derivation Relations
- {{target_artifact_id}} {{derivation_type}} {{source_entity_id}}
- {{target_artifact_id}} wasGeneratedBy {{primary_activity_id}}
- {{target_artifact_id}} wasAttributedTo {{primary_agent_id}}
```

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[bld_schema_lineage_record]] | downstream | 0.43 |
| [[kc_lineage_record]] | sibling | 0.36 |
| [[bld_quality_gate_lineage_record]] | downstream | 0.36 |
| [[bld_instruction_lineage_record]] | upstream | 0.33 |
| [[bld_rules_lineage_record]] | sibling | 0.33 |
