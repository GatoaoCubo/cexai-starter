---
kind: collaboration
id: bld_collaboration_fabrication_manifest
pillar: P12
llm_function: COLLABORATE
purpose: How fabrication-manifest-builder works in crews with other builders
quality: null
title: "Collaboration Fabrication Manifest"
version: "1.0.0"
author: n03_engineering
tags: [fabrication_manifest, builder, collaboration, orchestration]
tldr: "How fabrication-manifest-builder works in crews with other builders"
domain: "fabrication_manifest construction"
created: "2026-07-03"
updated: "2026-07-03"
8f: "F8_collaborate"
keywords: [fabrication_manifest construction, collaboration fabrication manifest, fabrication_manifest, builder, collaboration, team_charter, deployment_manifest, white_label_config, bootstrap orchestrator]
density_score: 0.85
related:
  - fabrication-manifest-builder
  - kc_orchestration_vocabulary
  - bld_architecture_fabrication_manifest
  - bld_tools_fabrication_manifest
---
## Crew Role
Interprets and previews the bootstrap-orchestrator's own per-tenant state kind so N07 (or a
nucleus) can reason about a fabrication run WITHOUT hand-editing the live gitignored file or
inventing pipeline progress. Acts as the read-mostly bridge between "a tenant needs fabricating"
(intent) and "the real CLI that owns this state" (execution).

## Receives From
| Source | What | Format |
|--------|------|--------|
| GDP decision / user | `tenant_id`, `chosen_capabilities`, `hosting_target` choice | plain text / decision manifest |
| `white_label_config` | The brand config THIS manifest's `brand_config_ref` points at | moldgen `.ts` overlay or brand-spec YAML/JSON |
| `capability_registry` | The declared-capability universe `chosen_capabilities` is validated against | `capability_registry.json` |
| An existing on-disk manifest | Real stage progress (if resuming) | bare YAML, `.cex/tenants/<tid>/runtime/` |

## Produces For
| Consumer | What | Format |
|----------|------|--------|
| N07 orchestrator | A preview/explanation of what `fabricate <tid>` would do or has done | Markdown/table summary |
| The operator running the CLI | A sanity-checked starter shape (tenant_id, brand_config_ref, chosen_capabilities) | YAML preview (Section A only) |
| Diagnostic requests | A read-only explanation of `stage_status` and what remains `pending` | Markdown |

## Boundary (explicit -- per the kind's own boundary text)
Does NOT produce `team_charter` (a crew MISSION CONTRACT with budget/deadline/quality_gate,
N roles -- handled by `team-charter-builder`). Does NOT produce `deployment_manifest` (WHAT
deploys WHERE + rollback -- handled by `deployment-manifest-builder`). Does NOT produce
`white_label_config` (the brand spec this manifest only REFERENCES via `brand_config_ref`). Does
NOT run the real pipeline stages itself -- that is `_tools/cex_bootstrap_orchestrator.py`'s CLI
(or its successor `_tools/cex_distill.py`) job, invoked as a TOOL, not reimplemented in-context.

## Collaboration Pattern
1. N07 (or the operator) decides a tenant needs fabricating -- `tenant_id` + chosen capabilities
   + a brand reference are the inputs.
2. This builder checks `load_manifest(tenant_id)` (conceptually) -- if a manifest already exists,
   the correct action is RESUME (`fabricate <tid>` re-runs only non-`done` stages), not restart.
3. If no manifest exists, this builder drafts a STARTER preview (Section A of the output
   template) for review -- it does NOT write the file itself.
4. The operator/N05 runs the real CLI (`provision`/`fabricate`) OR the successor
   (`cex_distill.py`) to perform the actual write.
5. This builder can be asked again, post-run, to EXPLAIN the resulting `stage_status` and any
   `provision`/`fabricate`/`wire` blocks -- read-only, never edited.
6. Nothing is archived by this builder -- the manifest's own gitignored runtime location IS its
   permanent (per-tenant) record; there is no `.cex/runtime/decisions/archive/` step like
   `team_charter` has.

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[fabrication-manifest-builder]] | related | 0.46 |
| [[kc_orchestration_vocabulary]] | upstream | 0.35 |
| [[bld_architecture_fabrication_manifest]] | upstream | 0.32 |
| [[bld_tools_fabrication_manifest]] | upstream | 0.31 |
