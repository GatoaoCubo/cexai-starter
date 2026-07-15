---
id: p11_fb_glossary_entry
kind: builder_default
pillar: P11
title: "Feedback: Glossary Entry"
domain: glossary_entry
quality: null
tags: [feedback, anti-patterns, P11, glossary_entry]
tldr: "Glossary Entry feedback: anti-patterns, regression signals, and quality improvement triggers"
8f: "F7_govern"
keywords: [glossary entry, glossary entry feedback, regression signals, and quality improvement triggers, feedback, anti-patterns, glossary_entry, common failure modes, correction protocol, key behaviors]
density_score: 1.0
updated: "2026-04-22"
related:
  - p11_fb_retriever
  - p11_fb_ab_test_config
  - p11_fb_handoff
  - p11_fb_research_pipeline
  - p11_fb_prompt_version
---
# Feedback: Glossary Entry

## Anti-Patterns (NEVER do)

- **No self-score**: never assign quality score to your own output
- **No hallucination**: cite sources; do not invent facts, metrics, or references
- **ASCII-only code**: no emoji, no accented chars in .py/.ps1/.sh output
- **No partial output**: produce complete artifact; no truncation, no "..." placeholders
- **No frontmatter omission**: every artifact must start with valid YAML frontmatter
- **No quality below 8.0**: re-draft before publishing if self-assessment < 8.0

## Common Failure Modes for Glossary Entry

- Vague identity section (no concrete capabilities, tools, or constraints)
- Missing required frontmatter fields (id, kind, pillar, version: 1.1.0
quality: null)
- Body prose only -- no tables, no structured data (density < 0.85)
- Output not matching the output template schema

## Correction Protocol

1. Identify which H01-H07 gate failed
2. Return to F6 PRODUCE with explicit fix instruction
3. Re-run F7 GOVERN
4. Maximum 2 retries before escalating to N07

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
| [[p11_fb_retriever]] | sibling | 0.77 |
| p11_fb_ab_test_config | sibling | 0.76 |
| p11_fb_handoff | sibling | 0.76 |
| [[p11_fb_research_pipeline]] | sibling | 0.76 |
| [[p11_fb_prompt_version]] | sibling | 0.76 |
