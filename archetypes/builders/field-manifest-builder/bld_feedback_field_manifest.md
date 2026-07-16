---
id: p11_fb_field_manifest
kind: builder_default
pillar: P11
title: "Feedback: Field Manifest"
domain: field_manifest
version: 1.0.0
quality: null
tags: [feedback, anti-patterns, P11, field_manifest]
8f: "F7_govern"
keywords: [field manifest, never rules, failure modes, step correction, feedback, anti-patterns, field_manifest, common failure modes, failure mode, correction protocol]
tldr: "Anti-patterns and correction protocol for field_manifest builders. 6 NEVER rules + 4 failure modes + 3-step correction."
author: builder
llm_function: GOVERN
density_score: 0.86
created: "2026-07-03"
updated: "2026-07-03"
related:
  - p11_qg_field_manifest
  - p11_fb_input_schema
  - p11_fb_type_def
  - bld_schema_field_manifest
  - p11_fb_kind
---
# Feedback: Field Manifest

## Anti-Patterns (NEVER do)

| Rule | Violation | Gate |
|------|-----------|------|
| No self-score | Never assign quality score to own output | H01 |
| No hallucination | Cite sources; no invented facts, metrics, refs, or FieldKind values outside the 14 closed set | H03 |
| ASCII-only code | No emoji, no accented chars in .py/.ps1/.sh (the manifest artifact's own body may carry PT-BR content -- only executable code is ASCII-restricted) | H04 |
| No partial output | Complete artifact; no truncation, no "..." in the fields list | H05 |
| No frontmatter omission | Every artifact starts with valid YAML frontmatter | H01 |
| No behavior leakage | Never describe app-logic (upload/autoCalc/aiAssist implementation) INSIDE the manifest -- document the NEED, route the HOW to HandlerRegistry | H07 |

## Common Failure Modes

| Failure Mode | Signal | Fix |
|-------------|--------|-----|
| Ungated publish-critical field | A field the business clearly requires before "published" carries no `publish` rule | Add the appropriate rule (minCount/minLength/present/positive) with a label |
| Silent multi-field gate | A `positive` gate spans multiple fields but only one is named | Add `companions` naming every other field the gate depends on |
| FieldKind drift | A field's `kind` is not one of the 14 closed values | Re-check against `types.ts`'s `FieldKind` union; extend the union in the SAME change if a new kind is truly needed, never leave it dangling |
| Missing section reference | `field.section` names an id not present in `sections` | Add the missing section or fix the typo; every field must resolve to a declared section |

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
- Builder MUST keep declarative field description (WHAT) separate from app-logic
  behavior (HOW) -- the latter belongs in a HandlerRegistry description, never
  inline in the manifest body

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
| [[p11_qg_field_manifest]] | sibling | 0.80 |
| [[p11_fb_input_schema]] | sibling | 0.72 |
| [[p11_fb_type_def]] | sibling | 0.70 |
| [[bld_schema_field_manifest]] | related | 0.60 |
| [[p11_fb_kind]] | sibling | 0.55 |
