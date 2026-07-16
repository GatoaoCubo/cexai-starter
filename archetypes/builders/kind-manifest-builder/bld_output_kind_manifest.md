---
kind: output_template
id: bld_output_template_kind_manifest
pillar: P05
llm_function: PRODUCE
purpose: "Template with {{vars}} that the LLM fills to produce a kind_manifest artifact"
pattern: "every field here exists in SCHEMA.md -- template derives, never invents"
quality: null
title: "Output Template Kind Manifest"
version: "1.0.0"
author: n03_builder
tags:
  - "kind_manifest"
  - "builder"
  - "examples"
tldr: "Fill-in-the-blank shape for kind_manifest instances: the fixed 10-section body, the n00_{{kind}}_manifest id pattern, and the honest Builder-pointer-or-OPEN-callout choice."
domain: "kind_manifest construction"
created: "2026-07-10"
updated: "2026-07-10"
8f: "F6_produce"
keywords:
  - "template with"
  - "kind manifest construction"
  - "output template kind manifest"
  - "kind_manifest"
  - "builder"
  - "examples"
  - "n00_{{kind}}_manifest"
  - "fixed filename varying directory"
density_score: 0.88
related:
  - bld_schema_kind_manifest
---
# Output Template: kind_manifest
This is the fill-in-the-blank shape a producing nucleus fills when documenting a NEWLY-registered kind. Every field traces to `bld_schema_kind_manifest.md` -- this template derives, never invents.

## Frontmatter
```yaml
id: n00_{{kind}}_manifest
kind: kind_manifest
8f: F3_inject
pillar: "{{target_kind_own_pillar}}"
nucleus: n00
title: "{{Kind Title Case}} -- Canonical Manifest"
version: 1.0
quality: null
tags: [manifest, "{{kind}}", "{{pillar_lower}}", n00, archetype, template]
density_score: 1.0
related:
  - "{{sibling_manifest_id_1}}"
  - "{{sibling_manifest_id_2}}"
updated: "{{YYYY-MM-DD}}"
```

## Body (the fixed 10-section order -- never reorder, never merge, never skip)
```text
<!-- 8F: F1=knowledge_card {{pillar}} F2=knowledge-card-builder F3=kinds_meta+builder-manifest F4=plan F5=scan F6=produce F7=gate F8=save -->

## Purpose
{{one_paragraph -- what this kind IS, in the taxonomy's own terms}}

## Pillar
{{P0X}} -- {{pillar_name}}

## Schema (key fields)
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| {{field_1}} | {{type}} | {{yes/no}} | {{description}} |

## When to use
- {{bullet_1}}
- {{bullet_2}}

## Builder
`archetypes/builders/{{kind}}-builder/`

Run: `python _tools/cex_8f_runner.py "your intent" --kind {{kind}} --execute`

(If no builder exists yet: "## Builder -- honest status (register row R-XXX, OPEN)"
naming the real register row -- never a fabricated path.)

## Template variables (open for instantiation)
- `{{VAR_1}}` -- {{what_it_resolves_to}}

## Example (minimal)
[fenced yaml -- a minimal real-shaped instance of the DOCUMENTED kind]

## Related kinds
- `{{sibling_kind}}` ({{pillar}}) -- {{one_line_contrast}}

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[{{ref}}]] | related | {{score}} |
```

## Naming Axis (fill exactly, never invent a variant)
| Slot | Rule |
|------|------|
| Filename | ALWAYS `kind_manifest_n00.md` -- invariant across all 294 real instances |
| Directory | `kind_{{kind}}/` -- the ONE part of the path that varies with the target kind |
| id | `n00_{{kind}}_manifest` -- 294/294 real instances match this pattern exactly |
| pillar (frontmatter) | The DOCUMENTED kind's OWN registered pillar -- NOT kind_manifest's own P01 |
| nucleus (frontmatter) | Always `n00`, lowercase -- distinct from kinds_meta.json's owning-nucleus field |

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[bld_schema_kind_manifest]] | upstream | 0.42 |
