---
id: bld_tools_brandbook
kind: toolkit
pillar: P04
builder: brandbook-builder
version: 1.0.0
quality: null
title: Tools -- brandbook
author: n06_commercial
tags: [toolkit, brandbook, P04]
llm_function: CALL
created: 2026-06-22
updated: 2026-06-22
---

## Tools Available to brandbook-builder

### From N06 (brand infrastructure)
| Tool | Purpose |
|------|---------|
| `brand_audit.py` | Score brand consistency across 6 dimensions |
| `brand_ingest.py` | Scan user's messy folder -> extract brand signals |
| `brand_inject.py` | Replace `{{BRAND_*}}` tokens in templates |
| `brand_propagate.py` | Push brand context to all 7 nuclei |
| `brand_validate.py` | Validate brand_config.yaml (13 required fields) |

### From System
| Tool | Purpose |
|------|---------|
| `cex_compile.py` | Compile .md to .yaml |
| `cex_doctor.py` | Quality gate check |
| `cex_crew.py run brand_discovery` | Spawn the 3-role brand crew |

### MCP (pre-compiled by N07 via preflight)
| MCP | Purpose |
|-----|---------|
| `fetch` | Scrape brand's site URL for materials |
| `markitdown` | Convert PDF/brand doc to markdown |
| `canva` | Export visual brand assets |

### Media Pipeline (dual-output)
| Hook | Purpose |
|------|---------|
| `media_requests(inputs)` | Declare logo + palette + cover image slots |
| `produced_media(inputs)` | Map uploaded logo data-uri to logo_primary slot |
