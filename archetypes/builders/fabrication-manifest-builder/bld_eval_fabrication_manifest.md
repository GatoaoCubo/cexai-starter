---
kind: quality_gate
id: p12_qg_fabrication_manifest
pillar: P11
llm_function: GOVERN
purpose: Quality gate with HARD and SOFT scoring for fabrication_manifest
quality: null
title: "Quality Gate Fabrication Manifest"
version: "1.0.0"
author: n03_engineering
tags: [fabrication_manifest, builder, quality_gate, orchestration]
tldr: "Quality gate with HARD and SOFT scoring for fabrication_manifest"
domain: "fabrication_manifest construction"
created: "2026-07-03"
updated: "2026-07-03"
8f: "F7_govern"
keywords: [fabrication_manifest construction, quality gate fabrication manifest, fabrication_manifest, builder, quality_gate, stage_status, hosting_target, brand_config_ref]
density_score: 0.85
related:
  - bld_schema_fabrication_manifest
  - fabrication-manifest-builder
---
## Definition
| Metric | Threshold | Operator | Scope |
|--------|-----------|----------|-------|
| Manifest shape fidelity to `new_manifest()` | 100% required fields present | equals | Any preview/draft this builder produces |

## HARD Gates
| ID | Check | Fail Condition |
|----|-------|----------------|
| H01 | `schema` == `cex.fabrication_manifest/1` and `kind` == `fabrication_manifest` | Either field wrong or missing |
| H02 | `tenant_id` passes the sanitize contract | Traversal chars, empty, or > 64 chars |
| H03 | `brand_config_ref` is a reference (string/null), never inline brand values | Literal `{{brand_*}}`-shaped values present |
| H04 | `stage_status` has all 7 keys, each in `pending\|done\|skipped\|error` | Missing key or invalid value |
| H05 | `hosting_target` is a registered id (`cex_managed`\|`sovereign`) | Unknown target string |
| H06 | No `provision`/`fabricate`/`ingest`/`wire` block hand-fabricated in a PREVIEW | Any pipeline-only block populated without a cited real run |

## SOFT Scoring
| Dim | Dimension | Weight | Scoring Guide |
|-----|-----------|--------|---------------|
| D01 | Field completeness vs `new_manifest()` shape | 0.30 | All 12 top-level keys present = 1.0, 1 missing = 0.6, 2+ = 0 |
| D02 | `stage_status.C` roll-up correctness (matches `_roll_up_stage_c` logic) | 0.25 | Correct derivation = 1.0, plausible-but-unchecked = 0.5, contradicts sub-keys = 0 |
| D03 | Honesty about deprecation (module status disclosed when relevant) | 0.20 | Disclosed unprompted = 1.0, disclosed on ask = 0.6, omitted = 0 |
| D04 | Naming/max_bytes discrepancies acknowledged (not silently "corrected") | 0.15 | Both flagged = 1.0, one flagged = 0.5, neither = 0 |
| D05 | No invented capability slugs / hosting targets | 0.10 | All real = 1.0, any invented = 0 |

## Actions
| Label | Score | Action |
|-------|-------|--------|
| GOLDEN | >= 9.5 | Archive as gold example |
| PUBLISH | >= 8.0 | Authorize as reference material for N07 dispatch |
| REVIEW | >= 7.0 | Require N07 manual review before dispatch |
| REJECT | < 7.0 | Reject; rebuild from `bld_output_template_fabrication_manifest.md` |

## Bypass
| Condition | Approver | Audit Trail |
|-----------|----------|--------------|
| Founder explicitly asks for a hypothetical "what would stage C look like" illustration | User explicit request | Output labeled HYPOTHETICAL, not a real manifest state |

## Golden Example (REAL data, read from disk this build -- not invented)
```yaml
schema: cex.fabrication_manifest/1
kind: fabrication_manifest
tenant_id: petlux_showcase
brand_config_ref: .cex/runtime/moldgen/petlux_showcase/brand.config.ts
chosen_capabilities: [landing, ads]
hosting_target: cex_managed
status: fabricated
stage_status: {A: done, B: done, C: done, D: done, C_admin: done, C_brain: done, C_site: done}
```
Source: `.cex/tenants/petlux_showcase/runtime/fabrication_manifest.yaml` (gitignored, read
directly). All 7 stage_status keys terminal, `wire.closed: true` with a real
`run_to_readback` (1 row written, 1 read back, artifact matched) -- this is what a COMPLETE,
trustworthy manifest looks like.

## Anti-Example 1: Hand-Fabricated Progress
```yaml
schema: cex.fabrication_manifest/1
kind: fabrication_manifest
tenant_id: acme
stage_status: {A: done, B: done, C: done, D: done, C_admin: done, C_site: done, C_brain: done}
provision: {tenant_root: "/fake/path"}
```
## Why it fails:
No real `provision_tenant()`/`fabricate_layers()`/`wire_flywheel()` call produced this --
`stage_status` and `provision` were typed by hand. This corrupts the resume anchor: a real
`fabricate <tid>` run would now skip stages that never actually executed (constitution 4 violated).

## Anti-Example 2: Kind Conflated with `team_charter`
```yaml
---
id: p12_fm_acme.md
kind: fabrication_manifest
title: "Fabrication Manifest: Acme"
quality: null
---
## Mission Statement
This tenant will be fabricated by Friday.
```
## Why it fails:
`fabrication_manifest` has NO `.md` frontmatter, NO `title`, NO `id` field, and is never a
mission-statement document -- that shape belongs to `team_charter`. Conflating the two kinds
produces a file the real CLI cannot parse as its own state.

### S_RELATED: Cross-Reference Check (SOFT)
- [ ] `related:` frontmatter field populated (3-15 entries)
- [ ] `## Related Artifacts` section present in artifact body
- [ ] At least 1 upstream and 1 downstream reference
- Penalty: -0.3 if empty (does not block, encourages wiring)

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[bld_schema_fabrication_manifest]] | upstream | 0.40 |
| [[fabrication-manifest-builder]] | related | 0.36 |
