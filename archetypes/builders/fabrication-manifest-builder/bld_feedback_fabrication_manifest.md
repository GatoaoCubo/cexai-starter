---
quality: null
id: p11_fb_fabrication_manifest
kind: builder_default
pillar: P11
title: "Feedback: Fabrication Manifest"
domain: fabrication_manifest
version: "1.0.0"
tags: [feedback, anti-patterns, P11, fabrication_manifest]
8f: "F7_govern"
keywords: [fabrication manifest, never rules, failure modes, step correction, feedback, anti-patterns, fabrication_manifest, stage_status, hand-fabrication, deprecation disclosure]
tldr: "Anti-patterns and correction protocol for fabrication_manifest builders. 6 NEVER rules + 4 failure modes + 3-step correction."
author: n03_engineering
llm_function: GOVERN
density_score: 0.85
created: "2026-07-03"
updated: "2026-07-03"
related:
  - bld_eval_fabrication_manifest
  - fabrication-manifest-builder
---
# Feedback: Fabrication Manifest

## Anti-Patterns (NEVER do)
| Rule | Violation | Gate |
|------|-----------|------|
| No self-score | Never assign quality score to own output | H01 |
| No hand-fabricated progress | Never write `stage_status: done` without a real pipeline run | H04 |
| No inline brand values | `brand_config_ref` is a REFERENCE only, never resolved `{{brand_*}}` | H03 |
| No invented capability slugs | `chosen_capabilities` entries must be real, registry-declared | D05 |
| No silent naming/max_bytes "fixes" | Surface the `p12_fm_{{tenant}}` vs real-filename gap; don't paper over it | D04 |
| No hidden deprecation | Disclose `cex_bootstrap_orchestrator.py`'s 2026-07-02 deprecation banner when relevant | D03 |

## Common Failure Modes
| Failure Mode | Signal | Fix |
|--------------|--------|-----|
| Treated like a `.md` artifact | Output has `title:`/`version:` frontmatter fields | Re-read `bld_schema_fabrication_manifest.md` -- this kind self-stamps only `schema:`+`kind:` |
| `stage_status.C` set without checking sub-keys | `C: done` while a `C_*` key is `pending`/`error` | Apply `_roll_up_stage_c` logic before asserting `C` |
| Presents deprecated module as current best practice | No mention of `cex_distill.py` | Re-read `bld_tools_fabrication_manifest.md` deprecation section |
| Duplicates brand values inline | Manifest carries literal brand name/palette instead of a ref | Replace with `brand_config_ref` pointer only |

## Correction Protocol
| Step | Action | Gate |
|------|--------|------|
| 1 | Identify which HARD gate (H01-H06, `bld_eval_fabrication_manifest.md`) failed | F7 |
| 2 | Return to F6 PRODUCE with the explicit fix (re-derive from `new_manifest()` shape) | F6 |
| 3 | Re-run F7 GOVERN | F7 |
| 4 | Max 2 retries before escalating to N07 | F8 |

## Key Behaviors
- Builder MUST load all 12 ISOs (1:1 with pillars) before producing any artifact.
- Builder MUST treat `_tools/cex_bootstrap_orchestrator.py` as the ground-truth shape source, not
  its own imagination.
- Builder MUST disclose the deprecation banner + `cex_distill.py` gap when discussing NEW work.
- Builder MUST NOT self-score: `quality` field is always `null` in own output.
- Builder MUST NOT hand-edit an existing gitignored tenant runtime file.

## Quality Thresholds
| Dimension | Weight | Target | Gate |
|-----------|--------|--------|------|
| Structural completeness | 30% | >= 8.0 | L1 |
| Rubric compliance | 30% | >= 8.0 | L2 |
| Semantic coherence | 40% | >= 8.5 | L3 |
| Density score | -- | >= 0.85 | S09 |
| Tables present | -- | >= 1 | S05 |

## Gate Check
```bash
python _tools/cex_score.py {FILE} --layer structural
python _tools/cex_score.py {FILE} --layer rubric
```
```yaml
# Expected output structure
structural: 8.5+
rubric: 7.5+
average: 8.0+
gates_passed: 6/6
density: 0.85+
```

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[bld_eval_fabrication_manifest]] | related | 0.55 |
| [[fabrication-manifest-builder]] | related | 0.50 |
