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
related:
  - bld_architecture_kind
  - p06_is_env_contract_n05
  - p06_td_cex_artifact_type_n03
  - bld_schema_brandbook
  - bld_instruction_kind
  - cybersec_performing_container_image_hardening_p03_chain
  - cybersec_performing_container_image_hardening_p07_red_team_eval
  - bld_schema_kind
---

## Configuração de Runtime

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

## Related Artifacts

| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[bld_architecture_kind]] | upstream | 0.23 |
| [[p06_is_env_contract_n05]] | upstream | 0.22 |
| [[p06_td_cex_artifact_type_n03]] | upstream | 0.20 |
| [[bld_schema_brandbook]] | upstream | 0.20 |
| [[bld_instruction_kind]] | upstream | 0.17 |
| [[cybersec_performing_container_image_hardening_p03_chain]] | upstream | 0.17 |
| [[cybersec_performing_container_image_hardening_p07_red_team_eval]] | upstream | 0.16 |
| [[bld_schema_kind]] | upstream | 0.15 |
