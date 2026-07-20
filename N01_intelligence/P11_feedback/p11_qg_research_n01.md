---
id: p11_qg_research_n01
kind: quality_gate
pillar: P11
nucleus: n01
title: "N01 Quality Gate -- Research Output Validation"
version: 1.0.0
created: 2026-03-31
updated: 2026-03-31
author: n01_intelligence
domain: research-intelligence
quality: null
when_to_use: "Run at F7 GOVERN before any N01 artifact ships; consult for which hard gates a research output must pass."
tags: [quality_gate, n01, research, triangulation, freshness, source_grading]
tldr: "10 hard + 5 scoring checks for N01 research output. Triangulation (>=3 sources), freshness (<= 90 days), evidence grading, confidence scoring (1-5), and brand alignment. Every check has a measurable pass criterion."
keywords: [triangulation, confidence score, source diversity, actionable insights, evidence grading, competitive grid]
density_score: 0.95
related:
  - p03_pt_research_brief
  - p03_ch_research_pipeline_n01
  - p07_bm_research_quality
  - p01_kc_research_bias_taxonomy
  - p12_wf_intelligence
---

# N01 Quality Gate

## Hard Gates (FAIL = REJECT, no exceptions)

| ID | Check | Pass Criterion | Rationale |
|----|-------|---------------|-----------|
| H01 | Source triangulation per major claim | >= 3 independent sources cited | Single-source claims fail dossier review |
| H02 | Source URL + access date | 100% of citations have URL + ISO-8601 access date | Unverifiable sources = un-auditable findings |
| H03 | Confidence score on key findings | Every key finding has score 1-5 | Reader must know certainty level |
| H04 | Freshness flag | No undated source > 90 days without `[STALE]` tag | Stale data misleads |
| H05 | Template compliance | Output matches assigned schema (P06) | Consistency enables downstream pipelines |
| H06 | Source diversity | >= 2 source types (e.g., academic + industry, not all blogs) | Single-type sources = single-perspective bias |
| H07 | Evidence grading | Every source tagged with a reliability grade | Grade signals how much weight a claim can bear |
| H08 | No fabricated quotes | Every direct quote traceable to source | hallucination_rate gate |
| H09 | Reproducible search | Search strategy + queries logged | Peer can re-run and verify |
| H10 | Brand context alignment | Output references brand_config audience/tone | Generic research = wasted dispatch |

## Soft Scoring (Weighted, target >= 8.0)

| # | Dimension | Weight | 1 (Poor) | 5 (Adequate) | 10 (Excellent) |
|---|-----------|--------|----------|--------------|----------------|
| 1 | Source diversity (web + academic + industry + primary) | 1.0 | All from 1 type | 2 types covered | 4+ types with >=2 each |
| 2 | Actionable insights ("so what" per finding) | 1.0 | Raw data dump | Some implications drawn | Every finding has explicit decision implication |
| 3 | Competitive grid completeness | 0.8 | Missing competitors | Top 3 covered | All major players + dimensions |
| 4 | Visual structure (tables, grids, comparison matrices) | 0.6 | Wall of text | Some tables | Tables dominate; prose minimal |
| 5 | Brand context alignment depth | 0.6 | Generic research | Brand mentioned | Through-lens of user's market position |

## Source Reliability Scale (5-point)

| Grade | Meaning | Example |
|-------|---------|---------|
| A | Completely reliable | Published peer-review, .gov filings, official financial filings |
| B | Usually reliable | Major news outlets, reputable industry analysts |
| C | Fairly reliable | Trade publications, vendor blogs (with named author) |
| D | Not usually reliable | Anonymous blogs, social media accounts, unverified forum posts |
| E | Unreliable | Known-biased sources, marketing material disguised as research |

## Information Confidence Scale (1-6)

| Grade | Meaning |
|-------|---------|
| 1-2 | Confirmed / probably true, consistent with logic |
| 3-4 | Possibly true but unconfirmed / doubtful |
| 5-6 | Improbable / cannot be judged |

Combined grade format: `B2` (usually reliable + probably true), `A1` (gold standard), `D5` (skip).

## Application Guide

| Stage | Action | Example |
|-------|--------|---------|
| Pre-research | Define confidence thresholds + diversity targets | "High confidence" = 3+ A/B-grade sources agree |
| Post-research | Validate each claim against H01-H10 | "Market size $50B" -> 3 A/B sources + score 1-2 |
| Before delivery | Run final gate + soft-score check | All hard gates PASS, soft score >= 8.0 |

## Anti-Patterns (Common Failures)

| Anti-Pattern | Mitigation |
|-------------|-----------|
| Single source syndrome | H01 enforcement at F7 |
| Stale data masquerading | H04 `[STALE]` tag requirement |
| Confidence inflation | H03 + reliability scale enforcement |
| Cherry-picked sources (selection bias) | H06 source diversity check |

## Outcomes

- **`REJECT` (Hard Gate Fail)**: Artifact is returned to N01 with the failed Gate ID and a directive to fix it.
- **`FLAG_FOR_REVIEW` (Soft Gate Score < 8.0)**: Artifact is accepted but flagged for human oversight.
- **`ACCEPT` (Soft Gate Score >= 8.0)**: Artifact is accepted and a `validation_complete` signal is propagated.

## Actions

| Score | Tier | Action |
|-------|------|--------|
| >= 9.5 | GOLDEN | Publish as exemplar |
| >= 8.0 | PUBLISH | Ready for runtime |
| >= 7.0 | REVIEW | Flag for review |
| < 7.0  | REJECT | Rework required |

## Bypass

| Field | Value |
|-------|-------|
| conditions | Experimental artifact under active A/B testing; approver + audit_trail required |
| expiry | 48h -- must pass all gates before expiry |
| never_bypass | H01 (source triangulation), H03 (confidence score) |

### How to use

```text
ROLE: You are the F7 GOVERN gate for N01 outputs.
ACT:
  - Check every HARD gate (H01..H10) in order; a single fail blocks publication.
  - On fail, return the artifact to F6 with the failing gate annotated.
  - Only pass artifacts that clear all gates AND the score floor.
OUTPUT: PASS, or a blocked result naming the failed gate.
```

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[p03_pt_research_brief]] | upstream | 0.35 |
| [[p03_ch_research_pipeline_n01]] | upstream | 0.34 |
| [[p07_bm_research_quality]] | sibling | 0.32 |
| [[p01_kc_research_bias_taxonomy]] | upstream | 0.28 |
| [[p12_wf_intelligence]] | downstream | 0.25 |
