---
id: p12_ct_cross_provider_council
kind: crew_template
pillar: P12
title: "Cross-Provider Judging Council"
version: 1.0.0
created: 2026-04-27
quality: null
density_score: 0.92
tags: [crew, consensus, multi_provider, anti_sycophancy, council, F7c]
related:
  - llm-judge-builder
  - judge-config-builder
  - scoring-rubric-builder
  - red-team-eval-builder
  - p12_ct_product_launch
process: consensus
roles_count: 4
crew_name: cross_provider_council
purpose: "Run N independent judges (each on a different LLM provider) against the same scoring_rubric, then compute consensus_score + divergence_score to detect sycophancy and hallucination"
crewai_equivalent: "Process.parallel + VotingAggregator"
autogen_equivalent: "GroupChat.parallel_vote"
swarm_equivalent: "judge_claude | judge_gemini | judge_gpt | judge_ollama -> aggregator"
handoff_protocol_id: a2a-task-consensus
---

## Overview

Instantiate when an artifact needs cross-provider validation to guard against
single-model sycophancy or hallucination. The council runs 4 judges in
parallel, each bound to a different LLM provider via `provider_override`
in their `judge_config` instance. All judges share the same `scoring_rubric`.

Triggers (F7c COUNCIL): artifact frontmatter `requires_council: true`,
CLI `--council` flag, or within-model score >= 9.5 (sycophancy heuristic).

## Roles

| Role | Role Assignment ID | Provider | Reason |
|------|---------------------|----------|--------|
| judge_claude | p02_ra_council_judges (role: judge_claude) | claude | Primary model -- high reasoning, potential self-bias |
| judge_gemini | p02_ra_council_judges (role: judge_gemini) | gemini | Cross-family diversity -- different training data |
| judge_gpt | p02_ra_council_judges (role: judge_gpt) | gpt | Cross-family diversity -- independent alignment |
| judge_ollama | p02_ra_council_judges (role: judge_ollama) | ollama | Local model -- no API dependency, different scale |

## Process

Topology: `consensus`. Rationale: judges MUST NOT see each other's scores
before producing their own -- independence is the entire value proposition.
Sequential would introduce anchoring bias. Hierarchical would create a
single point of sycophancy.

## Aggregation

```
consensus_score = mean(judge_scores)
divergence_score = stddev(judge_scores)
dissent_rationales = [r for r in rationales if |score - consensus| > 0.3]
```

Decision rules:
- `divergence_score <= 0.3`: PASS -- publish with consensus_score
- `divergence_score > 0.3`: FAIL -- surface dissent_rationales, block publication
- Lone outlier: do NOT auto-suppress -- the outlier may be the only honest judge

## Memory Scope

| Role | Scope | Retention |
|------|-------|-----------|
| judge_claude | isolated | per-council-instance |
| judge_gemini | isolated | per-council-instance |
| judge_gpt | isolated | per-council-instance |
| judge_ollama | isolated | per-council-instance |

Isolation is mandatory -- shared memory would allow anchoring.

## Handoff Protocol

`a2a-task-consensus` -- all 4 judges run in parallel. Each writes a
completion signal with `score` + `rationale`. Aggregator collects all 4
before computing consensus.

## Success Criteria

- [ ] All 4 judges produced independent scores
- [ ] No judge saw another judge's output before scoring
- [ ] divergence_score computed correctly (stddev, not range)
- [ ] Dissent rationales surfaced when divergence > 0.3
- [ ] Council result attached to artifact as `council_trace`

## Instantiation

```bash
python _tools/cex_council.py --artifact path/to/artifact.md \
  --rubric path/to/rubric.md \
  --providers claude,gemini,ollama
```

Or via crew CLI:
```bash
python _tools/cex_crew.py run cross_provider_council \
  --charter path/to/charter.md --execute
```

## Related Artifacts

| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[p12_ct_product_launch]] | sibling | 0.50 |
| [[p02_ra_council_judges]] | child | 0.90 |
| [[llm-judge-builder]] | upstream | 0.60 |
| [[judge-config-builder]] | upstream | 0.55 |
