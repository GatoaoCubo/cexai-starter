---
kind: architecture
id: bld_architecture_fabrication_manifest
pillar: P08
llm_function: CONSTRAIN
purpose: Component map of fabrication_manifest -- inventory, dependencies
quality: null
title: "Architecture Fabrication Manifest"
version: "1.0.0"
author: n03_engineering
tags: [fabrication_manifest, builder, architecture, orchestration]
tldr: "Component map of fabrication_manifest -- inventory, dependencies"
domain: "fabrication_manifest construction"
created: "2026-07-03"
updated: "2026-07-03"
8f: "F1_constrain"
keywords: [fabrication_manifest construction, architecture fabrication manifest, fabrication_manifest, builder, architecture, component inventory, data flow, bootstrap orchestrator]
density_score: 0.85
related:
  - bld_architecture_team_charter
  - bld_architecture_deployment_manifest
  - kc_fabrication_manifest
  - fabrication-manifest-builder
  - bld_tools_fabrication_manifest
---
## Component Inventory
| ISO File | Role | Pillar | Status |
|----------|------|--------|--------|
| bld_model_fabrication_manifest | Builder identity + routing (constrained scribe, not free author) | P12 | Active |
| bld_prompt_fabrication_manifest | Step-by-step preview/explain process | P03 | Active |
| bld_knowledge_fabrication_manifest | Domain knowledge (A/B/C/D pipeline, deprecation status) | P01 | Active |
| bld_tools_fabrication_manifest | Real CLI + test + validation tools | P04 | Active |
| bld_output_fabrication_manifest | Starter-shape template + pipeline-only block reference | P05 | Active |
| bld_schema_fabrication_manifest | SSOT field definitions + documented discrepancies | P06 | Active |
| bld_eval_fabrication_manifest | HARD/SOFT gates + golden/anti-examples | P11 | Active |
| bld_architecture_fabrication_manifest | This component map | P08 | Active |
| bld_config_fabrication_manifest | Naming, paths, limits | P09 | Active |
| bld_memory_fabrication_manifest | Learned patterns + pitfalls | P10 | Active |
| bld_feedback_fabrication_manifest | NEVER rules + failure modes | P11 | Active |
| bld_orchestration_fabrication_manifest | Crew coordination + boundary vs sibling kinds | P12 | Active |

## Dependencies (real, from kinds_meta.json + code)
| From | To | Type |
|------|-----|------|
| fabrication_manifest | white_label_config | depends_on (brand_config_ref points here) |
| fabrication_manifest | capability_registry | depends_on (chosen_capabilities validated against this) |
| bld_schema_fabrication_manifest | `new_manifest()` (cex_bootstrap_orchestrator.py:278) | ground-truth reference |
| bld_tools_fabrication_manifest | cex_tenant_onboard.onboard() | integration (Stage B reuses) |
| bld_tools_fabrication_manifest | cex_tenant_paths (resolve_tenant_path, deny_cross_tenant) | integration (path guard + isolation) |
| bld_tools_fabrication_manifest | cex_capability_registry (attach gate) | integration (Stage C3) |
| bld_tools_fabrication_manifest | cex_distill.py | successor pointer (does NOT share this kind) |

## Architectural Position
`fabrication_manifest` occupies the CLI-owned STATE layer of P12 (Orchestration) -- distinct from
the builder-authored governance layer where `team_charter` and `deployment_manifest` live. Those
two are `.md` + frontmatter documents an LLM hand-composes and `cex_compile.py` compiles.
`fabrication_manifest` is a bare, gitignored YAML the ORCHESTRATOR CODE itself writes
(`new_manifest`/`save_manifest`), read back by its own `status` subcommand. This builder sits
ABOVE that code only as an INTERPRETER: it helps N07/a nucleus reason about a manifest's shape
and stage progress without ever becoming the write path. The real write path is, in order of
recency: `_tools/cex_bootstrap_orchestrator.py` (current code, deprecated as of 2026-07-02) ->
`_tools/cex_distill.py` (founder-designated successor, does not use this kind).

## Data Flow (real, from the module's own docstring + code)
```
BrandBook  --[A INGEST]-->  brand config overlay  --[B PROVISION]-->  per-tenant surface + RLS binding
                                                                              |
                                                            [C FABRICATE: C_admin + C_brain + C_site]
                                                                              |
                                                                     [D WIRE: flywheel-closes assert]
                                                                              |
                                                        fabrication_manifest.yaml (stage_status all done)
                                                                              |
                                                    read back by: status <tid> / this builder's preview
```

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[bld_architecture_team_charter]] | sibling | 0.55 |
| [[bld_architecture_deployment_manifest]] | sibling | 0.53 |
| [[kc_fabrication_manifest]] | upstream | 0.48 |
| [[fabrication-manifest-builder]] | downstream | 0.42 |
| [[bld_tools_fabrication_manifest]] | related | 0.38 |
