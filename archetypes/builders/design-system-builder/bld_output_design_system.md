---
id: bld_output_design_system
kind: response_format
pillar: P06
llm_function: PRODUCE
8f: F6_produce
version: 1.0.0
created: "2026-06-15"
updated: "2026-06-15"
author: n03_builder
title: "Template: design_system instance"
domain: design_system
quality: null
tags: [design_system, builder, template, output, P06]
tldr: "The exact shape a design_system instance fills: frontmatter (with leverage) + color/type/space/motion/form + components + usage + CEXAI Leverage section."
density_score: 0.88
related:
  - bld_schema_design_system
  - bld_prompt_design_system
---

# Template: design_system instance
Fill every placeholder; keep body <= 5120 bytes. Mirror p06_ds_ferro / p06_ds_sereno.
## Frontmatter
```yaml
id: p06_ds_{{name}}
kind: design_system
pillar: P06
title: "{{Name}} -- {{one-line stance}}"
version: 1.0.0
created: "{{date}}"
author: n03_builder
domain: design-systems
aesthetic: "{{one-line aesthetic stance}}"
density: {{comfortable|compact}}
quality: null
leverage:
  feeds_kinds: [landing_page, interactive_demo, product_tour, onboarding_flow, pitch_deck]
  inject_hook: "F3 INJECT: bind {{Name}} tokens as the sole palette/scale/motion source; compose only from the four recipes."
  brand_config_relation: "Realizes a {{identity}} brand_config identity into bindable tokens; brand_config selects {{Name}} as active."
  composes_with: [variant_shotgun_taste_loop, user_model, gdp]
  binds_8f: [F1_constrain, F3_inject]
tags: [design-system, tokens, {{trait_a}}, {{trait_b}}]
tldr: "{{dense one-line summary}}"
related: [p06_vs_design_system, p06_ds_ferro, p06_ds_sereno]
```
## Body sections (in order)
1. `# {{Name}}` + one paragraph stance (conforms to p06_vs_design_system).
2. `## color` -- role/value table (the nine roles).
3. `## type` -- faces, ratio, step ladder, weight, leading.
4. `## space` -- unit + s0..s7.
5. `## motion` -- dur, ease, move recipes.
6. `## form` -- radius, edge.width, shadow ladder.
7. `## components` -- surface/control/field/marker recipes.
8. `## usage` -- the four rules with concrete contrast numbers.
9. `## CEXAI Leverage` -- feeds, inject hook, brand_config relation, composes-with.
## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| p06_ds_ferro | example | 0.55 |
| p06_ds_sereno | example | 0.55 |
| [[bld_schema_design_system]] | upstream | 0.5 |
| [[bld_prompt_design_system]] | sibling | 0.42 |
| p06_vs_design_system | upstream | 0.42 |
