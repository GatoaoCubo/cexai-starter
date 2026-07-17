---
id: bld_orchestration_brandbook
kind: workflow
pillar: P12
builder: brandbook-builder
version: 1.0.0
quality: null
title: Orchestration -- brandbook
author: n06_commercial
tags: [workflow, brandbook, P12]
llm_function: COLLABORATE
created: 2026-06-22
updated: 2026-06-22
---

## Orchestration: brandbook

### Solo Build (single generator)
```bash
python _tools/cex_8f_runner.py "build brandbook for {brand_name}" \
  --kind brandbook --nucleus n06 --execute
```

### Crew Build (3-role sequential)
```bash
python _tools/cex_crew.py run brand_discovery \
  --charter N06_commercial/P12_orchestration/crews/team_charter_brand_default.md \
  --execute
```

### Wave Placement in Grid
brandbook is built in Wave 2 (after brand discovery crew, before content factory):
```
Wave 1: N01 brand research (competitive intelligence, positioning)
Wave 2: N06 brand_discovery crew -> brandbook-builder
Wave 3: N02 content factory (uses brandbook as context)
Wave 4: N03 landing page / design_system (uses brandbook tokens)
```

### Downstream Consumers
| Artifact | How it uses brandbook |
|----------|-----------------------|
| landing_page (P05) | Injects palette + typography + headline copy |
| design_system (P06) | Consumes palette + typography for tokens |
| white_label_config (P09) | Consumes palette hex -> HSL 24-token format |
| content calendar (N02) | Injects brand persona voice + messaging framework |
| ad_copy (N02) | Injects copy samples as copy seeds |
