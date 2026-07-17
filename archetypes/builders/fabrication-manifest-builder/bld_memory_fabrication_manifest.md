---
kind: learning_record
id: p10_lr_fabrication_manifest_builder
pillar: P10
llm_function: INJECT
purpose: Learned patterns and pitfalls for fabrication_manifest construction
quality: null
title: "Learning Record Fabrication Manifest"
version: "1.0.0"
author: n03_engineering
tags: [fabrication_manifest, builder, learning_record, orchestration]
tldr: "Learned patterns and pitfalls for fabrication_manifest construction"
domain: "fabrication_manifest construction"
created: "2026-07-03"
updated: "2026-07-03"
8f: "F7_govern"
keywords: [fabrication_manifest construction, learning record fabrication manifest, fabrication_manifest, builder, learning_record, stage_status, deprecation, resumability]
density_score: 0.85
related:
  - fabrication-manifest-builder
  - bld_tools_fabrication_manifest
---
## Observation
This kind's triage (`docs/DECISION_BUILDERLESS_KINDS_2026_07_03.md` sec 2.5) verdict was SCAFFOLD
on 5 independent evidence sites, dated 2026-07-03. The central module it cites
(`_tools/cex_bootstrap_orchestrator.py`) carries its own DEPRECATED banner dated 2026-07-02 --
ONE DAY EARLIER -- pointing new tenant-fabrication work at `_tools/cex_distill.py`. The evidence
section that justified SCAFFOLD did not surface this banner. Both facts are independently true
and verified this build (re-ran the 24-case pytest suite: 24 passed; grepped `cex_distill.py` for
`fabrication_manifest`: zero matches). Lesson: "actively used" and "recommended for new work" are
different claims -- a kind can be real, load-bearing, and well-tested while its host module is
simultaneously superseded. A builder for a kind must ground BOTH facts, not just the one its
triage evidence happened to surface.

## Patterns (what works)
1. `load_manifest(tenant_id)` FIRST, always -- this kind's entire value proposition is
   resumability (constitution 4); treating every request as "start fresh" defeats the point.
2. Reading a REAL on-disk instance (`acme_demo`) before describing the shape in the
   abstract catches details a spec/KC summary can miss (e.g. the exact placeholder strings
   `__CEX_MANAGED_REPO__/...`, or that `wire.edit_to_reflect` carries a concrete `record_id`).
3. Checking `stage_status.C`'s roll-up rule (`_roll_up_stage_c`) BEFORE trusting a `C: done` value
   avoids treating a skipped `C_site` as a red flag when it is actually expected (Stage C2 SITE
   is intentionally a separate dispatch in the current phase).
4. Cross-checking the module's claimed successor (`cex_distill.py`) by grep, not by assumption --
   the assumption "the successor obviously reuses the same kind" was FALSE here.

## Evidence
Re-run this build: `python -m pytest _tools/tests/test_bootstrap_orchestrator.py -q` -> 24 passed
in 52.44s. Direct read of `.cex/tenants/acme_demo/runtime/fabrication_manifest.yaml`
confirmed all 7 `stage_status` keys `done`, `hosting_target: cex_managed`, and a real
`wire.run_to_readback` proof (1 row written, 1 read back, artifact matched).

## Anti-patterns (what breaks)
- Assuming the naming pattern in `kinds_meta.json` (`p12_fm_{{tenant}}.yaml`) is what's on disk --
  the real filename is fixed (`fabrication_manifest.yaml`), scoped by directory, not by name.
- Treating `max_bytes: 4096` as a hard ceiling the artifact always respects -- the real, complete
  instance already exceeds it (per the kind-KC), and that gap is pre-existing, not this cell's to
  silently "fix" by inventing a smaller shape.
- Presenting the deprecated module as the current best-practice path without disclosure -- the
  founder-visible successor tool exists and should be named alongside it.
- Hand-writing `provision`/`fabricate`/`wire` blocks to "complete" an example -- these are proof
  of a REAL run; fabricating them misrepresents what actually executed.

## Recommendations
- Template-first: start every preview from `bld_output_template_fabrication_manifest.md` Section A
  only; never draft Section B content.
- When in doubt about current recommended tooling for a kind whose central module looks old or
  authoritative, grep the SUCCESSOR file for the kind's own name before assuming continuity.
- Archive/read real gitignored instances directly when available -- they are better ground truth
  than any spec summary (specs describe intent; instances prove what actually ran).

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[fabrication-manifest-builder]] | downstream | 0.47 |
| [[bld_tools_fabrication_manifest]] | upstream | 0.31 |
