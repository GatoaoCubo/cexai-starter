---
id: p11_fb_output_template
kind: builder_default
pillar: P11
title: "Feedback: Output Template"
domain: output_template
version: 1.0.0
quality: null
tags: [feedback, anti-patterns, P11, output_template]
8f: "F7_govern"
keywords: [output template, never rules, failure modes, step correction, feedback, anti-patterns, output_template, naming drift, reflexive usage, common failure modes]
tldr: "Anti-patterns and correction protocol for output_template builders. 6 NEVER rules + 4 failure modes + 3-step correction, centered on the reflexive-vs-broader split and the 3-way naming drift."
author: builder
llm_function: GOVERN
density_score: 0.86
created: "2026-07-07"
updated: "2026-07-07"
related:
  - bld_schema_output_template
---
# Feedback: Output Template

## Anti-Patterns (NEVER do)

| Rule | Violation | Gate |
|------|-----------|------|
| No self-score | Never assign quality score to own output | H05 |
| No hallucination | Cite sources; no invented naming conventions, no fabricated wikilinks | H01 |
| ASCII-only code | No emoji, no accented chars in .py/.ps1/.sh (the artifact's own body may carry PT-BR content -- only executable code is ASCII-restricted) | -- |
| No partial output | Complete artifact; no truncation, no "..." in the template body | -- |
| No frontmatter omission | Every artifact starts with valid YAML frontmatter | H01 |
| No silent drift-blessing | Never pick one of Convention A/B/C and present it as "the" standard without disclosure | H07/S02 |

## Common Failure Modes

| Failure Mode | Signal | Fix |
|-------------|--------|-----|
| Usage ambiguity | Reader cannot tell if this is a blank fill-in-the-blank scaffold or a completed report | State the usage (reflexive/broader) explicitly in the body, not just implied by tone |
| Invented `depends_on` | An entry appears in `depends_on` where kinds_meta.json fixes it to `[]` | Remove it; if a real dependency is needed, that is a kinds_meta.json edit, out of scope for this builder |
| Retroactive rename attempt | An existing one of the 18 real instances gets its id "corrected" to the canonical pattern | Revert -- that is a separate, deliberate reconciliation sweep (its own register row), never a side effect of authoring a NEW instance |
| Reflexive/broader shape mismatch | A reflexive ISO#9 template invents fields not present in the target kind's own `bld_schema_{{kind}}.md` | Re-derive every field from that schema; template derives, never invents |

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
- Builder MUST state explicitly which usage (reflexive ISO#9 vs broader recurring
  document) a produced instance serves -- the two are never interchangeable
- Builder MUST NOT retroactively rename any of the 18 pre-existing real instances;
  H02's canonical pattern is FORWARD-ONLY

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
| p11_fb_field_manifest | sibling | 0.72 |
| p11_fb_kind | sibling (reflexive-case source) | 0.70 |
| [[bld_schema_output_template]] | related | 0.60 |
