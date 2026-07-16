---
id: p01_kc_a2a_council_pattern
kind: knowledge_card
kc_type: meta_kc
pillar: P01
nucleus: N04
title: "A2A Council Pattern -- Independent Adversarial Multi-Agent Review"
version: "1.0.0"
created: "2026-06-13"
updated: "2026-06-13"
author: "n04_knowledge"
domain: "multi-agent orchestration, anti-sycophancy, adversarial council, consensus topology"
quality: null
tags:
  - council
  - anti_sycophancy
  - a2a
  - adversarial_review
  - consensus_topology
  - F7c
  - multi_agent
tldr: "N agents on distinct adversarial lenses judge in parallel; consensus=mean(scores), divergence=stddev; block publish if divergence>0.3; outliers never suppressed."
when_to_use: "High-stakes or load-bearing design decisions; when solo model may self-validate its own design; when doc-read assumptions need on-disk proof."
keywords:
  - council pattern
  - adversarial agents
  - consensus topology
  - anti-sycophancy
  - divergence score
  - F7c COUNCIL
long_tails:
  - "how to avoid LLM sycophancy in architecture decisions CEX"
  - "multi-agent council pattern for design review"
  - "when to use council vs single model judge"
axioms:
  - "ALWAYS assign DISTINCT adversarial lenses -- shared lens = shared blind spot."
  - "NEVER auto-suppress lone outliers -- outlier may be the only honest judge."
  - "IF divergence_score > 0.3 THEN block publish; surface all dissent rationales."
  - "IF on-disk probe contradicts doc-read THEN trust on-disk."
linked_artifacts:
  primary: p12_ct_cross_provider_council
  related:
    - p01_kc_autonomous_orchestration
    - 8f-reasoning
density_score: 0.88
data_source: "p12_ct_cross_provider_council; examples/09_council_review/council_trace.md; .claude/rules/composable-crew.md; https://arxiv.org/abs/2310.01848"
related:
  - bld_architecture_lens
  - lens-builder
  - bld_memory_lens
---

> **[DISTILL ANNOTATION]** This file cites tool(s) not shipped in this tenant (Central-only): cex_council. Inline citations are marked `[NOT SHIPPED in this tenant -- Central-only tool]`.

# A2A Council Pattern -- Independent Adversarial Multi-Agent Review

## Executive Summary

The A2A council pattern spawns N advisory agents, each assigned a **distinct
adversarial lens**, to evaluate a candidate design in parallel with no
inter-agent visibility. N07 synthesizes: `consensus_score = mean(scores)`,
`divergence_score = stddev(scores)`. High divergence signals genuine conflict;
lone dissenters are never auto-suppressed. The pattern is the anti-sycophancy
core of F7c COUNCIL (see 8f-reasoning) and is the mechanism by which a
within-session architectural decision can overturn its own doc-read assumption
when an on-disk probe returns contradicting evidence.

## Spec Table

| Parameter | Value | Notes |
|-----------|-------|-------|
| Topology | `consensus` | Judges isolated; no inter-agent visibility |
| Agent count | N >= 2; typically 3 | Each on a distinct lens |
| Aggregation | mean(scores), stddev(scores) | `cex_council.py` |
| Block threshold | `divergence_score > 0.3` | Configurable per-artifact |
| Outlier policy | NEVER suppressed | Surface rationale; human resolves |
| Memory scope | isolated per agent | Shared memory = anchoring bias |
| F7c trigger | within-model score >= 9.5 | Sycophancy heuristic |
| F7c trigger alt | `requires_council: true` in frontmatter | Explicit opt-in |
| Cost | N x token_budget | `council_budget_tokens` caps |
| Implementation | p12_ct_cross_provider_council | `cex_crew.py run cross_provider_council` |

## Patterns

### P1: Lens Independence (the mechanism)
Each agent receives only its own lens mandate and the candidate. No agent
is shown what other lenses will examine. This isolation is the entire value
proposition; parallel agents with identical mandates produce correlated
scores and understate real divergence.

Lenses used in THIN_BOOT architecture council (2026-06-13):
- `reliability` -- does thin boot omit context builders actually need?
- `efficiency` -- how many context KB does full boot load per spawn?
- `native-correctness` -- does `claudeMdExcludes` actually gate rule files?

### P2: On-Disk Verification as a Lens
One lens must carry a verify-on-disk mandate. The `native-correctness`
lens ran a spawn probe and compared byte-identical output -- it did NOT
rely on doc-read. Probe result **overturned the initial doc-read assumption**
that the flag might not scope `.claude/rules/*.md`. This is Commandment I
(ground claims in evidence) operationalized at the agent level.

### P3: Council vs Solo-Judge Decision Matrix

| Dimension | Solo Judge | A2A Council (3 lenses) |
|-----------|-----------|------------------------|
| Sycophancy risk | HIGH | LOW (adversarial mandate) |
| Groupthink risk | HIGH | LOW (lens diversity) |
| Cost | 1x budget | ~3x budget (parallel) |
| Wall-clock time | Fastest | ~same as single lens |
| Decision quality | Good for low-stakes | Required for high-stakes |

### P4: Council vs Cross-Provider Council (F7c)
This session used a **lens-based council** (same provider, distinct mandates).
F7c COUNCIL uses a **provider-based council** (different LLM families,
same rubric -- see p12_ct_cross_provider_council). Both are instances
of `process: consensus`. Composition rule: run lens-based first; escalate
to provider-based only when divergence_score > 0.3 persists after a second
lens-based pass.

## Anti-Patterns

- **Same lens twice** -- correlated scores; divergence_score misleads.
- **Sequential reveal** -- judge_1 output visible to judge_2 = anchoring.
- **Auto-suppressing outliers** -- outlier may be the sole correct dissent.
- **Council on trivial decisions** -- 3x token cost with no quality gain.
- **Doc-read lenses only** -- at least one lens must verify on disk.

## Application: THIN_BOOT Architecture Decision (2026-06-13)

N07 ran a 3-lens council before dispatching N03 (Phase A) and N04 (canary).

| Lens | Finding | Verdict |
|------|---------|---------|
| reliability | Builder ISOs + 8F + constitution intact under thin | PASS |
| efficiency | 10.2 KB excluded per spawn via claudeMdExcludes | PASS |
| native-correctness | Spawn probe: byte-identical builder context | PASS |

Unanimous verdict: `divergence_score = 0` -- publication not blocked.
N07 committed Phase A (8f2c2a30f5) and dispatched N04 for canary v2.

This artifact (`kc_a2a_council_pattern`) is the canary artifact: a full-quality
KC produced by N04 under `CEX_THIN_BOOT=1` to confirm thin boot does not
degrade builder output.

## CANARY VERDICT

CLEAN -- nothing missing under thin boot. Shared core (8F + constitution +
ascii + ubiquitous-language + guided-decisions) and N04 rules were fully
available. No MISSING CONTEXT flags raised.

## References

- p12_ct_cross_provider_council -- crew_template; consensus topology spec
- [[p01_kc_autonomous_orchestration]] -- Section 9: F7c auto-trigger at >= 9.5
- 8f-reasoning -- F7c COUNCIL sub-step; triggers + budget guardrail
- `.claude/rules/composable-crew.md` -- topology comparison table
- `examples/09_council_review/council_trace.md` -- worked FAIL example:
  divergence=1.96; lone GPT outlier (9.0/10) surfaces, not suppressed
- `_tools/cex_council.py` -- `--providers claude,gemini,ollama` flag  <!-- [NOT SHIPPED in this tenant -- Central-only tool] -->
- Sycophancy in LLMs (external): https://arxiv.org/abs/2310.01848


## Related Artifacts

| Artifact | Relationship | Score |
|----------|-------------|-------|
| p12_ct_cross_provider_council | downstream | 0.38 |
| [[bld_architecture_lens]] | downstream | 0.37 |
| [[lens-builder]] | downstream | 0.35 |
| [[bld_memory_lens]] | downstream | 0.35 |
| p11_cr_convene_council | downstream | 0.35 |
| p01_kc_cex_lens_concept | sibling | 0.34 |
| [[bld_orchestration_lens]] | downstream | 0.33 |
| [[kc_lens]] | sibling | 0.33 |
| n00_lens_manifest | sibling | 0.30 |
