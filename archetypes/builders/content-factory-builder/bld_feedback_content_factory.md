---
quality: null
id: p11_fb_content_factory
kind: builder_default
pillar: P11
title: "Feedback: Content Factory"
domain: content_factory
version: 1.0.0
tags: [feedback, anti-patterns, P11, content_factory]
8f: "F7_govern"
keywords: [content factory, never rules, failure modes, step correction, feedback, anti-patterns, content_factory, common failure modes, failure mode, correction protocol]
tldr: "Anti-patterns and correction protocol for content_factory builders. 6 NEVER rules + 4 failure modes + 3-step correction."
author: builder
llm_function: GOVERN
density_score: 0.88
created: "2026-07-03"
updated: "2026-07-03"
related:
  - p11_fb_social_publisher
  - p11_qg_content_factory
  - bld_instruction_content_factory
  - p01_kc_content_factory
  - content-factory-builder
---
# Feedback: Content Factory

## Anti-Patterns (NEVER do)

| Rule | Violation | Gate |
|------|-----------|------|
| No self-score | Never assign quality score to own output | H01 |
| No hallucination | Cite sources; no invented facts, metrics, refs | H03 |
| ASCII-only code | No emoji, no accented chars in .py/.ps1/.sh | H04 |
| No partial output | Complete artifact; no truncation, no "..." | H05 |
| No frontmatter omission | Every artifact starts with valid YAML frontmatter | H01 |
| No quality below 8.0 | Re-draft before publishing if self-assessment < 8.0 | H07 |

## Common Failure Modes

| Failure Mode | Signal | Fix |
|-------------|--------|-----|
| System conflation | Artifact describes MoneyPrinterTurbo/Chatterbox video rendering instead of the brief -> N-row fan-out | Re-read `bld_knowledge_card_content_factory.md`'s Naming Collision table; ground in `_tools/cex_content_factory.py` |
| Pre-approved row | A row example ships with `approved=True` at production time | Every row is born `approved=False`/`publish_status=pending` -- fix per `bld_schema_content_factory.md` |
| Ungrounded caption | Caption asserts a fact not present in `source_facts`/topic | Route the claim through the grounding engine or OMIT it |
| Missing handoff | Artifact stops at the produced bundle, omits review/publish contracts | Add the Handoffs section per `bld_output_template_content_factory.md` |

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
| [[p11_fb_social_publisher]] | sibling | 0.78 |
| [[p11_qg_content_factory]] | sibling | 0.76 |
| [[bld_instruction_content_factory]] | sibling | 0.72 |
| [[p01_kc_content_factory]] | upstream | 0.68 |
| [[content-factory-builder]] | upstream | 0.65 |
