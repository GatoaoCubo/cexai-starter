---
id: bld_architecture_brandbook
kind: diagram
pillar: P08
builder: brandbook-builder
version: 1.0.0
quality: null
title: Architecture -- brandbook
author: n06_commercial
tags: [diagram, brandbook, P08]
llm_function: CONSTRAIN
created: 2026-06-22
updated: 2026-06-22
---

## Brandbook Data Flow

```
INPUTS                          GENERATOR                       OUTPUTS
------                          ---------                       -------
brand_name (required)
brand_essence (optional)        brandbook.build(inputs)
brand_materials (file/url/text) --->                            8 output_sections
  |                                                             (frozen shape)
  v (Cell A pre-processes)
brand_materials_text            F1 CONSTRAIN                   StructuredOutput
brand_materials_palette    ---> F3 INJECT (palette, text)      + artifact JSON
brand_materials_data_uri        F6 PRODUCE (8 sections)        + notes
                                F7 GOVERN (gate + score)
                                      |
                                      v
                                cex_dual_output.to_dual_output
                                      |
                          +-----------+-----------+
                          |                       |
                     MACHINE face            HUMAN face
                   .md + YAML frontmatter   HTML audiovisual
                   (id/brand/sections)      (sections + media slots)
                   persisted tenant-scoped  logo + palette + cover
```

## Brand CREW Integration

```
brand_discovery crew (sequential, 3 roles)
  |
  +-- Brand Strategist  --> positioning_brief (knowledge_card)
        |
        +-- Persona Architect --> personality + tagline artifacts
              |
              +-- Visual Packager --> design_system + white_label_config
                    |
                    +-- brandbook-builder consumes all 3 artifacts
                          |
                          v
                    p05_bb_{brand}.md (final brandbook)
```

## Composition Map
| Kind composed | Where used | Builder |
|---------------|------------|---------|
| personality (P02) | Section 4 Persona | personality-builder |
| design_system (P06) | Sections 2+3 | design-system-builder |
| white_label_config (P09) | Sections 2+3 (24 HSL tokens) | white-label-config-builder |
| tagline (P03) | Section 1 Identidade | tagline-builder |
