---
name: council-on-high-score
description: Auto-invoke a multi-provider council when within-model F7 score is suspiciously high to defend against single-model sycophancy.
when:
  - F7 GOVERN reports a within-model score of 9.5 or higher on any artifact.
  - Artifact frontmatter sets `requires_council: true`.
  - User explicitly passes the `--council` flag to a build or evaluation command.
kind: skill
pillar: P04
nucleus: all
quality: null
version: 1.0.0
created: 2026-04-27
updated: 2026-04-27
multi_runtime: true
runtimes: [claude, codex, gemini, ollama]
density_score: 0.87
tags: [skill, autofire, council, sycophancy, f7c, autowire, layer3]
related:
  - p12_ct_cross_provider_council
  - 8f-reasoning
---

> **[DISTILL ANNOTATION]** This file cites tool(s) not shipped in this tenant (Central-only): cex_council. Inline citations are marked `[NOT SHIPPED in this tenant -- Central-only tool]`.

# Council on High Score

## When this fires
- F7 GOVERN within-model scoring returns >= 9.5 (sycophancy heuristic).
- A frontmatter declares `requires_council: true` on the artifact being evaluated.
- The build was launched with the `--council` flag.

## What to do
1. Pause publication BEFORE F8 COLLABORATE writes the final artifact.
2. Run `python _tools/cex_council.py --auto --artifact <path>` to invoke the cross-provider council crew_template.  <!-- [NOT SHIPPED in this tenant -- Central-only tool] -->
3. The council runs the same scoring_rubric independently against N providers (default 3, premium 4) and returns `consensus_score`, `divergence_score`, and per-judge dissent rationales.
4. Block publication if `divergence_score > 0.3`. Surface the dissent rationales to the user; do NOT auto-suppress lone outliers (they may be the correct dissent).
5. If consensus passes, replace the within-model score with the consensus score in the frontmatter and proceed to F8.
6. Honor the artifact's `council_budget_tokens` cap; if missing, default budget is 3x the original judge token cost.

## Example
- N03 finishes a knowledge_card. F7 returns 9.7 (suspicious). Skill fires `cex_council --auto`. Three judges return 9.0 / 8.5 / 7.5; divergence is 0.61. Skill blocks publication, shows the 7.5 dissent (judge flagged factual gap), and N03 enters F6 again.

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| p12_ct_cross_provider_council | upstream | 0.85 |
| 8f-reasoning | upstream | 0.70 |
