---
id: bld_config_brandbook
kind: env_config
pillar: P09
builder: brandbook-builder
version: 1.0.0
quality: null
title: Config -- brandbook
author: n06_commercial
tags: [env_config, brandbook, P09]
llm_function: CONSTRAIN
created: 2026-06-22
updated: 2026-06-22
---

## Runtime Configuration

```yaml
brandbook_generator:
  version: "1.0.0"
  max_palette_colors: 5       # roles: primary, secondary, accent, neutral, background
  max_sections: 8             # frozen output contract
  max_bytes: 8192             # P05 pillar cap
  quality_floor: 7.0          # commercial foundation -- below 7.0 = rework
  placeholder_prefix: "[fornecer:"
  placeholder_suffix: "]"

# Media slots (for cex_dual_output)
media_slots:
  - key: logo_primary
    kind: image
    required: false
  - key: logo_dark
    kind: image
    required: false
  - key: brand_cover
    kind: image
    required: false
  - key: palette_visual
    kind: image
    required: false

# Cell A input pre-processing keys
cell_a_keys:
  palette: brand_materials_palette
  text: brand_materials_text
  data_uri: brand_materials_data_uri
```
