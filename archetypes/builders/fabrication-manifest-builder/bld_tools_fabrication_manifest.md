---
kind: tools
id: bld_tools_fabrication_manifest
pillar: P04
llm_function: CALL
purpose: Tools available for fabrication_manifest production
quality: null
title: "Tools Fabrication Manifest"
version: "1.0.0"
author: n03_engineering
tags: [fabrication_manifest, builder, tools, orchestration]
tldr: "Tools available for fabrication_manifest production"
domain: "fabrication_manifest construction"
created: "2026-07-03"
updated: "2026-07-03"
8f: "F5_call"
keywords: [fabrication_manifest construction, tools fabrication manifest, fabrication_manifest, builder, tools, bootstrap orchestrator, cex_distill, production tools, validation tools]
density_score: 0.85
related:
  - fabrication-manifest-builder
  - bld_knowledge_card_fabrication_manifest
  - kc_fabrication_manifest
  - bld_collaboration_fabrication_manifest
  - p11_fb_fabrication_manifest
---
## Production Tools (real, verified this build)
| Tool | Purpose | When |
|------|---------|------|
| `_tools/cex_bootstrap_orchestrator.py ingest <tid>` | Stage A: BrandBook -> brand config overlay | Tenant has a raw BrandBook input |
| `_tools/cex_bootstrap_orchestrator.py provision <tid>` | Stage B: mint per-tenant surface idempotently | Manifest needs a surface before Stage C |
| `_tools/cex_bootstrap_orchestrator.py fabricate <tid>` | THE KEYSTONE: A->B->C->D, resumable via stage_status | Full or resumed fabrication run |
| `_tools/cex_bootstrap_orchestrator.py status <tid> [--json]` | Read a tenant's manifest + per-stage progress | Diagnostic / resume check (read-only) |
| `_tools/cex_bootstrap_orchestrator.py --self-test` | DB-free correctness check (A-D + idempotency + isolation) | Regression check after any edit to the module |

**DEPRECATION NOTICE (grounded, verified this build):** every invocation of the module above
prints `[DEPRECATED] cex_bootstrap_orchestrator.py is superseded by _tools/cex_distill.py
(docs/SPEC_TENANT_BRAIN_RUNNABLE.md P4) -- use cex_distill.py for tenant fabrication.` to stderr
(`main()`, non-blocking -- it still executes the command). `_tools/cex_distill.py` is the
CANONICAL path for new tenant work (`python _tools/cex_distill.py --tenant-id <slug> --execute`)
but grep confirms it does NOT reference `fabrication_manifest`/`MANIFEST_KIND` anywhere -- it is a
structurally separate pipeline, not a drop-in replacement for THIS kind's shape. When asked to
fabricate a NEW tenant, surface both facts: the deprecated engine still works and is what this
kind's mechanics describe, but the founder-designated successor tool does not use this kind.

## Validation Tools
| Tool | Purpose | When |
|------|---------|------|
| `python -m pytest _tools/tests/test_bootstrap_orchestrator.py -q` | Re-run the 24-case integration suite | Before trusting any manifest-shape claim (24 passed, ~52s, re-verified this build) |
| `_tools/tests/test_bootstrap_orchestrator_ingest_wire.py` | Companion suite (Stage A + Stage D coverage) | Ingest/wire-specific regressions |
| `python _tools/cex_doctor.py` | Validate THIS builder's 12 ISOs (naming/density/size/frontmatter/related) | After any ISO edit |
| `yaml.safe_load(text)` (stdlib PyYAML) | Parse an on-disk manifest instance directly | Reading `.cex/tenants/<tid>/runtime/fabrication_manifest.yaml` |

## External References
- `_tools/cex_tenant_onboard.py` -- `onboard()`, the idempotent tenant-surface mint Stage B reuses.
- `_tools/cex_tenant_paths.py` -- `resolve_tenant_path`, `deny_cross_tenant`, `active_tenant_id`
  (the fail-closed path guard + cross-tenant isolation invariant Stage B asserts).
- `_tools/cex_capability_registry.py` -- the attach-gate Stage C3 (fabricate_admin) reuses to set
  the tenant dashboard's enabled-capability allowlist.
- `_tools/cex_tenant_knowledge.py` / `_tools/cex_runtime_sync.py` -- the write-leg/return-leg pair
  Stage D (`wire_flywheel`) asserts closes.
- `docs/specs/04_bootstrap_orchestrator/spec.md` -- the spec proposing this kind (status: Draft).

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[fabrication-manifest-builder]] | downstream | 0.45 |
| [[bld_knowledge_card_fabrication_manifest]] | upstream | 0.43 |
| [[kc_fabrication_manifest]] | upstream | 0.42 |
| [[bld_collaboration_fabrication_manifest]] | downstream | 0.38 |
| [[p11_fb_fabrication_manifest]] | downstream | 0.33 |
