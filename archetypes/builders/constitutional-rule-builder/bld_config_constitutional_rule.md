---
id: bld_context_sources_constitutional_rule
kind: knowledge_card
pillar: P11
title: "Constitutional Rule Builder -- Context Sources"
version: 1.0.0
quality: null
tags: [builder, constitutional_rule, context]
llm_function: CONSTRAIN
author: builder
tldr: "Constitutional Rule feedback: naming conventions, output paths, and production limits"
8f: "F3_inject"
keywords: [constitutional rule feedback, naming conventions, output paths, and production limits, builder, constitutional_rule, context, context sources, mandatory loads, related kind]
density_score: 0.88
created: "2026-04-17"
updated: "2026-04-17"
related:
  - bld_tools_constitutional_rule
  - bld_context_sources_deployment_manifest
  - bld_context_sources_value_object
  - bld_context_sources_canary_config
  - bld_context_sources_slo_definition
---
# Context Sources: constitutional_rule
## Mandatory Loads (F3 INJECT)
| Source | Path | Purpose |
|--------|------|---------|
| Kind KC | N00_genesis/P01_knowledge/library/kind/kc_constitutional_rule.md | Primary definition |
| Schema | archetypes/builders/constitutional-rule-builder/bld_schema_constitutional_rule.md | Field constraints |
| Template | archetypes/builders/constitutional-rule-builder/bld_output_template_constitutional_rule.md | Structure |
| Examples | archetypes/builders/constitutional-rule-builder/bld_examples_constitutional_rule.md | Golden patterns |
| Guardrail builder | archetypes/builders/guardrail-builder/ | Contrast: soft vs absolute |
| Pillar schema | N00_genesis/P11_feedback/_schema.yaml | Pillar constraints |
## Related Kind KCs
| KC | Relationship |
|----|-------------|
| kc_guardrail.md | soft constraint with bypass (the adjacent kind; know the difference) |
| kc_quality_gate.md | output quality enforcement (not behavioral) |
## External References
| Source | Relevance |
|--------|----------|
| Bai et al. Constitutional AI (2022) | Original CAI paper defining constitutional principles |
| Anthropic Usage Policy | Hardcoded behaviors that cannot be unlocked by operators |
| NIST AI RMF | Trustworthiness dimensions including safety and explainability |
| EU AI Act Art. 5 | Prohibited AI practices (maps to harm_prevention basis) |

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
| [[bld_tools_constitutional_rule]] | sibling | 0.40 |
| bld_context_sources_deployment_manifest | sibling | 0.40 |
| bld_context_sources_value_object | sibling | 0.38 |
| bld_context_sources_canary_config | sibling | 0.38 |
| bld_context_sources_slo_definition | sibling | 0.38 |
