---
id: bld_output_template_value_object
kind: output_template
pillar: P06
title: "Value Object Builder -- Output Template"
version: 1.0.0
quality: null
tags:
  - "builder"
  - "value_object"
  - "template"
llm_function: PRODUCE
author: builder
8f: "F1_constrain"
keywords:
  - "builder"
  - "value_object"
  - "template"
  - "-> new"
  - "with {changed attribute}:"
  - "output template"
  - "value object"
  - "valid example"
  - "invalid example"
  - "equality two"
density_score: 0.88
created: "2026-04-17"
updated: "2026-04-17"
related:
  - bld_instruction_value_object
  - bld_schema_value_object
  - bld_manifest_value_object
  - bld_quality_gate_value_object
  - kc_value_object
---
# Output Template: value_object
```yaml
---
id: p06_vo_{slug}
kind: value_object
pillar: P06
title: "Value Object: {Name}"
version: 0.1.0
attributes:
  - name: "{attr1}"
    type: "{Type}"
    constraint: "{rule}"
  - name: "{attr2}"
    type: "{Type}"
    constraint: "{rule}"
equality: structural
used_in:
  - "{AggregateRoot or Entity name}"
transformations:
  - "{methodName}({param}: {Type}) -> {Name}: returns new instance with {change}"
hashable: true
quality: null
tags: [value_object, {domain_slug}, P06]
tldr: "{Name}: immutable value defined by {N} attributes, structural equality, used in {context}"
---

## Attributes
| Attribute | Type | Constraint | Valid Example | Invalid Example |
|-----------|------|-----------|---------------|-----------------|
| {attr1} | {Type} | {rule} | {ok} | {bad} |
| {attr2} | {Type} | {rule} | {ok} | {bad} |

## Equality
Two `{Name}` instances are equal if and only if all attributes are equal.
No identity field. Reference equality is NOT domain equality.

## Validation
**Valid**: {example of valid instance}
**Invalid**: {example 1 -- which constraint violated}
**Invalid**: {example 2 -- which constraint violated}

## Transformations
- `{methodName}({param})` -> new `{Name}` with {changed attribute}: `{example}`

## Usage
Used as attribute in: {AggregateRoot.fieldName}, {Entity.fieldName}
```

## Output Template Checklist

- Verify output format matches target kind schema
- Validate all frontmatter fields are present in template
- Cross-reference with eval gate for completeness
- Test template rendering with sample data before publishing

## Output Pattern

```yaml
# Output validation
format_match: true
frontmatter_complete: true
eval_gate_aligned: true
sample_rendered: true
```

```bash
python _tools/cex_compile.py {FILE}
python _tools/cex_doctor.py --scope {BUILDER}
```

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[bld_instruction_value_object]] | related | 0.41 |
| [[bld_schema_value_object]] | related | 0.40 |
| [[bld_manifest_value_object]] | related | 0.35 |
| [[bld_quality_gate_value_object]] | related | 0.31 |
| [[kc_value_object]] | upstream | 0.28 |
