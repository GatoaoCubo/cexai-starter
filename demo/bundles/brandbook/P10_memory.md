---
id: bld_memory_brandbook
kind: memory_scope
pillar: P10
builder: brandbook-builder
version: 1.0.0
quality: null
title: Memory Scope -- brandbook
author: n06_commercial
tags: [memory_scope, brandbook, P10]
llm_function: INJECT
created: 2026-06-22
updated: 2026-06-22
---

## Memory Scope

| Scope | What | Retention | Owner |
|-------|------|-----------|-------|
| tenant-persistent | brand_config.yaml (13 required fields) | permanent | N06 brand tools |
| tenant-persistent | Produced brandbook artifacts p05_bb_*.md | permanent | brandbook-builder |
| per-session | Extracted palette colors from logo | session | Cell A |
| per-session | Extracted text from materials PDF/URL | session | Cell A |
| cross-nucleus | brand_propagate.py propagates to all 7 nuclei | on demand | brand_propagate.py |

## Persistence Path
Brandbooks persist tenant-scoped per the dual-output machine face:
  `.cex/runtime/capabilities/{tenant_id}/brandbook_{brand_slug}/`

## Related Memory Artifacts
- `N06_commercial/P10_memory/brand_decisions_memory.md` -- brand decision log
- `N06_commercial/P10_memory/pricing_optimization_memory.md` -- pricing experiments
- `.cex/brand/brand_config.yaml` -- the authoritative brand identity record
