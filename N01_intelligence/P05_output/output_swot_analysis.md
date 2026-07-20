---
id: output_swot_analysis
kind: analyst_briefing
pillar: P05
nucleus: n01
title: "Output: SWOT Analysis (with Cited Evidence Per Quadrant)"
version: 1.0.0
created: 2026-07-20
author: n01_intelligence
domain: research-intelligence
quality: null
tags: [analyst_briefing, n01, swot, strategic, analysis, evidence-grading]
tldr: "4-quadrant SWOT with mandatory evidence grading per item, source citation, and cross-quadrant strategic implications (SO/WO/ST/WT). Adapted from Weihrich (1982) TOWS Matrix."
when_to_use: "Use at F6 PRODUCE to format a strategic SWOT briefing -- fill the fenced template per entity, grade each item, and derive the TOWS cross-strategies the decision needs."
keywords: [swot analysis, strengths, weaknesses, opportunities, threats, strategic implications, tows matrix, evidence grading, analyst_briefing]
long_tails:
  - "how do I produce a cited TOWS-matrix SWOT briefing in N01"
  - "what evidence grading and cross-quadrant strategies does an N01 SWOT require"
density_score: 0.93
related:
  - p05_parser_data_extractor_n01
  - api_reference_research_apis
  - p06_is_n01
  - benchmark_suite_n01
  - reasoning_strategy_n01
---

# Output: SWOT Analysis

## Origin

SWOT (Strengths, Weaknesses, Opportunities, Threats) was formalized by Albert Humphrey (Stanford Research Institute, 1960s) and operationalized as the TOWS Matrix by Heinz Weihrich (1982), which adds the cross-quadrant strategy derivation step that distinguishes a useful SWOT from a list of bullets. N01 templates ALWAYS use the TOWS variant -- a raw SWOT without cross-strategies is treated as an incomplete briefing.

## Template

```markdown
# SWOT: {{ENTITY}} in {{CATEGORY}}
**Date**: {{DATE}} | **Sources**: {{COUNT}} | **Analyst**: N01

## Matrix

|  | Helpful | Harmful |
|---|---------|---------|
| **Internal (controllable)** | **Strengths** | **Weaknesses** |
|  | S1: {{ITEM}} [grade: A1] [src: {{N}}] | W1: {{ITEM}} [grade: B2] [src: {{N}}] |
|  | S2: {{ITEM}} [grade: B2] [src: {{N}}] | W2: {{ITEM}} [grade: A1] [src: {{N}}] |
|  | S3: {{ITEM}} [grade: A1] [src: {{N}}] | W3: {{ITEM}} [grade: C3] [src: {{N}}] |
| **External (uncontrollable)** | **Opportunities** | **Threats** |
|  | O1: {{ITEM}} [grade: B2] [src: {{N}}] | T1: {{ITEM}} [grade: A1] [src: {{N}}] |
|  | O2: {{ITEM}} [grade: B2] [src: {{N}}] | T2: {{ITEM}} [grade: B2] [src: {{N}}] |
|  | O3: {{ITEM}} [grade: C3] [src: {{N}}] | T3: {{ITEM}} [grade: B2] [src: {{N}}] |

## TOWS Strategy Matrix (cross-quadrant -- mandatory)

| | O (External Opportunities) | T (External Threats) |
|---|----------------------------|----------------------|
| **S (Internal Strengths)** | **SO**: aggressive growth strategy | **ST**: defensive strategy |
| **W (Internal Weaknesses)** | **WO**: turnaround / acquire strategy | **WT**: retreat / divest strategy |

## Strategic Implications (per cell, with confidence)

- **SO** (use strengths for opportunities): {{STRATEGY}} (confidence: {{1-5}}, payoff window: {{months}})
- **WO** (fix weaknesses to capture opportunities): {{STRATEGY}} (confidence: {{1-5}}, investment: {{$/effort}})
- **ST** (use strengths to counter threats): {{STRATEGY}} (confidence: {{1-5}}, time-to-deploy: {{weeks}})
- **WT** (minimize weaknesses, avoid threats): {{STRATEGY}} (confidence: {{1-5}}, opportunity cost: {{$/lost}})

## Sources
{{ENUMERATED_CITATIONS_WITH_GRADES}}
```

## Worked Example (illustrative -- fictional entity, fictional data)

```markdown
# SWOT: NimbusCRM in Small-Business CRM Software
**Date**: 2026-06-15 | **Sources**: 6 | **Analyst**: N01

## Matrix

|  | Helpful | Harmful |
|---|---------|---------|
| **Internal** | **Strengths** | **Weaknesses** |
|  | S1: Sub-5-minute onboarding, no-code setup [A1] [src: 1] | W1: No native mobile app (web-only) [A1] [src: internal] |
|  | S2: Flat pricing, no per-seat fees [A1] [src: 2] | W2: Limited third-party integrations (12 vs category avg 40+) [B2] [src: 3] |
|  | S3: 24h median support response time [B2] [src: 4] | W3: No enterprise SSO / SCIM support [A1] [src: internal] |
| **External** | **Opportunities** | **Threats** |
|  | O1: Category incumbents raising prices 15-20% this cycle [A1] [src: 5] | T1: Two well-funded entrants launched in the last 12 months [A1] [src: 6] |
|  | O2: Growing demand for AI-assisted data entry in this category [B2] [src: 3] | T2: Platform vendors bundling basic CRM into adjacent suites for free [B2] [src: 5] |
|  | O3: Underserved solo-founder / micro-business segment [C3] [src: internal] | T3: Category consolidation reducing number of viable channel partners [B2] [src: 6] |

## TOWS Strategy Matrix

| | O | T |
|---|---|---|
| **S** | **SO**: Lead with flat pricing against incumbents' price hikes; target price-sensitive switchers | **ST**: Double down on onboarding speed as the anti-bundling wedge -- fast setup beats "free but buried" |
| **W** | **WO**: Ship 3-5 highest-demand integrations before the AI-data-entry wave peaks | **WT**: Avoid competing on integration breadth; position as the simple alternative, not the complete one |

## Strategic Implications

- **SO**: Publish a pricing-comparison page against the two incumbents that just raised prices (confidence: 4/5, payoff window: 1-3 months)
- **WO**: Ship top-5 requested integrations from support tickets (confidence: 3/5, investment: ~6 engineer-weeks)
- **ST**: Author a "why simple beats bundled" positioning piece for the solo-founder segment (confidence: 3/5, time-to-deploy: 2 weeks)
- **WT**: Defer enterprise SSO/SCIM investment; that buyer is not this product's ICP yet (confidence: 4/5, opportunity cost: low)

## Sources

[1] Onboarding time study, internal product analytics, 2026-06. Reliability: A/1.
[2] Public pricing pages, 3 named incumbents, accessed 2026-06-15. Reliability: A/1.
[3] Support ticket integration-request tally, internal, 2026 Q2. Reliability: B/2.
[4] Support SLA dashboard, internal, 2026 Q2. Reliability: B/2.
[5] Category pricing-change announcements, incumbent blogs, 2026 Q1-Q2. Reliability: A/2.
[6] New-entrant funding announcements, industry press, 2026 Q1-Q2. Reliability: B/2.
```

## Usage Guidelines

| Use When | Don't Use When |
|----------|----------------|
| Strategic positioning decisions | Tactical / operational decisions |
| Investor / board presentations | Daily standup |
| Annual planning cycles | Sprint planning |
| Competitive entry/exit decisions | Bug-fix prioritization |

## Anti-Patterns

| Anti-Pattern | Why It Fails | Correction |
|-------------|--------------|------------|
| SWOT without TOWS | Lists become inert; no decision derived | ALWAYS include cross-quadrant strategy table |
| Internal/external confusion (e.g., listing competitors as Weakness) | Categorical error | Internal = controllable; External = market-determined |
| Unsourced bullets | Cannot defend in review | Require evidence grading per item |
| 10+ items per quadrant | Cognitive overload | Cap at 5 per quadrant; rank-order |
| Symmetric SWOT (3 of each just because) | Implies false balance | Quadrants need NOT be equal -- some entities are S-heavy |

## Sources

- Humphrey, Albert (1960s, SRI International) -- original SWOT framework
- Weihrich, Heinz (1982), "The TOWS Matrix: A Tool for Situational Analysis," Long Range Planning, vol. 15 issue 2, pp. 54-66
- Helms & Nixon (2010), "Exploring SWOT analysis -- where are we now?", Journal of Strategy and Management, 3(3), pp. 215-251

### Procedure

```text
1. Fill the Matrix: <=5 items per quadrant; tag each [grade: IC-code] [src: N].
2. Separate Internal (controllable) from External (market-determined); fix mis-files.
3. Derive the TOWS cross-strategies (SO/WO/ST/WT) -- this step is mandatory.
4. For each strategy, attach confidence (1-5) + a payoff/cost/time window.
5. Enumerate the cited sources with reliability grades.
6. Gate: reject the briefing if any quadrant item is ungraded or TOWS is missing.
```

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[p05_parser_data_extractor_n01]] | sibling | 0.28 |
| [[api_reference_research_apis]] | upstream | 0.26 |
| [[p06_is_n01]] | upstream | 0.25 |
| [[benchmark_suite_n01]] | downstream | 0.24 |
| [[reasoning_strategy_n01]] | related | 0.23 |
