---
id: p11_fb_kind_manifest
kind: builder_default
pillar: P11
title: "Feedback: Kind Manifest"
domain: kind_manifest
version: 1.0.0
quality: null
tags: [feedback, anti-patterns, P11, kind_manifest]
8f: "F7_govern"
keywords: [kind manifest, never rules, failure modes, step correction, feedback, anti-patterns, kind_manifest, naming axis, fixed filename, common failure modes]
tldr: "Anti-patterns and correction protocol for kind_manifest builders. 6 NEVER rules + 4 failure modes + 3-step correction, centered on the fixed-filename axis and the honest builder-pointer discipline."
author: builder
llm_function: GOVERN
density_score: 0.86
created: "2026-07-10"
updated: "2026-07-10"
related:
  - p11_qg_kind_manifest
  - p11_fb_knowledge_card
  - p11_fb_kind
  - bld_schema_kind_manifest
  - p10_lr_kind_manifest_builder
---
# Feedback: Kind Manifest

## Anti-Patterns (NEVER do)

| Rule | Violation | Gate |
|------|-----------|------|
| No self-score | Never assign quality score to own output | H05 |
| No hallucination | Cite sources; no invented builder pointers, no fabricated wikilinks | H01 |
| ASCII-only code | No emoji, no accented chars in .py/.ps1/.sh (the artifact's own body may carry non-ASCII content freely -- only executable code is ASCII-restricted) | -- |
| No partial output | Complete artifact; all 10 body sections present, no truncation | -- |
| No frontmatter omission | Every artifact starts with valid YAML frontmatter | H01 |
| No filename/id renaming | Never rename the fixed `kind_manifest_n00.md` filename or an existing instance's `id:` -- that is a dedicated, out-of-scope reconciliation sweep | H07 |

## Common Failure Modes

| Failure Mode | Signal | Fix |
|-------------|--------|-----|
| Fabricated builder pointer | A `## Builder` section cites a path that does not exist on disk | Replace with the honest "Builder -- honest status (register row R-XXX, OPEN)" callout |
| Stale corpus statistic | A cited instance count (e.g. "294") is asserted without a fresh check | Re-Glob/re-count before publishing; a newly-registered kind changes the number immediately |
| Invented `depends_on` | An entry appears where kinds_meta.json fixes it to `[]` | Remove it; a real dependency requires a kinds_meta.json edit, out of scope for this builder |
| Filename/directory drift | The produced file is not literally named `kind_manifest_n00.md`, or lives outside `kind_{{kind}}/` | Revert to the fixed shape -- this is the one naming axis this kind never varies |

## Correction Protocol

| Step | Action | Gate |
|------|--------|------|
| 1 | Identify which H01-H07 gate failed | F7 |
| 2 | Return to F6 PRODUCE with explicit fix instruction | F6 |
| 3 | Re-run F7 GOVERN | F7 |
| 4 | Max 2 retries before escalating to N07 | F8 |

## Key Behaviors

- Builder MUST load all 12 ISOs (1:1 with pillars) before producing any artifact
- Builder MUST run F7 GOVERN quality gate before saving output
- Builder MUST compile output via cex_compile.py after saving (F8 COLLABORATE)
- Builder MUST signal completion with quality score to N07 orchestrator
- Builder MUST NOT self-score: quality field is always null in own output
- Builder MUST state a REAL builder path or an honest OPEN-status callout --
  never a fabricated pointer
- Builder MUST NOT retroactively rename any of the 294 pre-existing real
  instances' ids or filenames; the fixed-filename axis is forward-stable, not
  a retroactive gate

## Quality Thresholds

| Dimension | Weight | Target | Gate |
|-----------|--------|--------|------|
| Structural completeness | 30% | >= 8.0 | L1 |
| Rubric compliance | 30% | >= 8.0 | L2 |
| Semantic coherence | 40% | >= 8.5 | L3 |
| Density score | -- | >= 0.85 | S06 |
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
gates_passed: 7/7
density: 0.85+
```

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[p11_qg_kind_manifest]] | sibling | 0.80 |
| [[p11_fb_knowledge_card]] | sibling (former mis-type contrast) | 0.70 |
| [[p11_fb_kind]] | sibling (reflexive-case source) | 0.68 |
| [[bld_schema_kind_manifest]] | related | 0.60 |
| [[p10_lr_kind_manifest_builder]] | sibling | 0.55 |
