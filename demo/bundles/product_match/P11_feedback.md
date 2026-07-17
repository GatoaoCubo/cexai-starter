---
quality: null
id: p11_fb_product_match
kind: builder_default
pillar: P11
title: "Feedback: Product Match"
domain: product_match
version: 1.1.0
tags: [feedback, anti-patterns, P11, product_match]
8f: "F7_govern"
keywords: [product match, never rules, failure modes, step correction, feedback, anti-patterns, product_match, common failure modes, failure mode, correction protocol]
tldr: "Anti-patterns and correction protocol for product_match builders. 6 NEVER rules + 4 failure modes + 3-step correction."
author: builder
llm_function: GOVERN
density_score: 0.88
created: "2026-07-02"
updated: "2026-07-02"
---
# Feedback: Product Match

## Anti-Patterns (NEVER do)

| Rule | Violation | Gate |
|------|-----------|------|
| No self-score | Never assign quality score to own output | H01 |
| No hallucination | Never claim `reverse_image`/`embedding`/`manual` produce a real match today -- product_match.py has no implementation for any of the three | H03 |
| ASCII-only code | No emoji, no accented chars in .py/.ps1/.sh | H04 |
| No partial output | Complete artifact; no truncation, no "..." | H05 |
| No frontmatter omission | Every artifact starts with valid YAML frontmatter | H01 |
| No EAN/GTIN/barcode as join key | Structurally excluded by design (every reseller recodes them) | H10 |

## Common Failure Modes

| Failure Mode | Signal | Fix |
|-------------|--------|-----|
| Fabricated match confidence | A SIM/PARCIAL row with confidence > 0 while `match_engine=none` or no credential | Re-read `bld_knowledge_product_match.md` Match Engine Status Matrix; offline is ALWAYS NAO at 0.0 |
| Reordered or renamed output sections | Section titles/order diverge from Resultado do match -> Auditoria de catalogo -> Proveniencia -> Veredito | Re-read `bld_output_product_match.md`; the shape is frozen to `MOLD_PRODUCT_MATCH` |
| Missing `match_confiavel` gate | Veredito section present but no named boolean gate + blockers | Add `match_confiavel` row per `bld_schema_product_match.md` |
| Join key includes an excluded field | `match_join_keys` lists `ean`/`gtin`/`barcode` without acknowledging exclusion | Cross-check `_DEFAULT_EXCLUDE_KEYS` in `product_match.py`; document the exclusion explicitly |

## Correction Protocol

| Step | Action | Gate |
|------|--------|------|
| 1 | Identify which H01-H10 gate failed | F7 |
| 2 | Return to F6 PRODUCE with explicit fix instruction | F6 |
| 3 | Re-run F7 GOVERN | F7 |
| 4 | Max 2 retries before escalating to N07 | F8 |

## Key Behaviors

- Builder MUST load all 12 ISOs (1:1 with pillars) before producing any artifact
- Builder MUST run F7 GOVERN quality gate before saving output
- Builder MUST compile output via cex_compile.py after saving (F8 COLLABORATE)
- Builder MUST signal completion with quality score to N07 orchestrator
- Builder MUST NOT self-score: quality field is always null in own output
- Builder MUST ground every match_engine claim in `product_match.py`'s actual `build()` behavior,
  not the enum's aspirational vocabulary

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
gates_passed: 7/7
density: 0.85+
```

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| p11_fb_quality_gate | sibling | 0.76 |
