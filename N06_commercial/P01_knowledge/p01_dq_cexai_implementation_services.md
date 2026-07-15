---
id: p01_dq_cexai_implementation_services
kind: discovery_questions
pillar: P01
nucleus: n06
title: "Discovery Questions -- CEXAI Implementation Services (MEDDIC)"
version: 1.0.0
created: "2026-06-11"
updated: "2026-06-11"
author: n06_commercial
domain: enterprise-sales
quality: null
tags: [discovery_questions, meddic, enterprise, implementation_services, cexai]
tldr: "MEDDIC discovery bank for CEXAI implementation deals. 3 personas x 6 dimensions = 18 questions. Qualify or disqualify in 30 minutes."
question_type: "open-ended"
target_audience: "enterprise economic buyers (CTO, CEO, VP Engineering) + champion"
sensitivity_level: "low"
related:
  - sales_playbook_n06
  - p01_cm_cexai_vs_ai_frameworks
  - enterprise_sla_cex_platform
---

# Discovery Questions -- CEXAI Implementation Services (MEDDIC)

## Purpose

Qualify enterprise prospects for CEXAI implementation services. Surface pain, confirm budget authority, identify champion. 30-minute discovery call.

## Scope

In: Enterprises evaluating AI orchestration + knowledge governance (target deal $50K-$500K).
Out: SMB self-serve, course buyers, OSS-only adoption.

## Questions by Persona

### Persona A: CTO / VP Engineering

| MEDDIC | # | Question |
|---|---|---|
| Metrics | 1 | "How do you measure AI output quality today? What breaks down when outputs aren't governed?" |
| Metrics | 2 | "What's your estimate for hours lost per week re-creating context that AI systems forget?" |
| Econ Buyer | 3 | "Who owns AI tooling budget? Does it cross into platform or data budgets?" |
| Econ Buyer | 4 | "What's the approval process for an engagement in the $50K-$250K range?" |
| Criteria | 5 | "What matters most: sovereign data, multi-runtime, quality governance, or deployment speed?" |
| Criteria | 6 | "What's your dealbreaker -- what would make you not move forward?" |

### Persona B: CEO / Founder

| MEDDIC | # | Question |
|---|---|---|
| Decision Process | 7 | "How have you evaluated AI vendors before? What stalled the last evaluation?" |
| Decision Process | 8 | "What does your board expect from AI capability in the next 12 months?" |
| Pain | 9 | "What's the most painful thing about how your team uses AI today?" |
| Pain | 10 | "Are you worried that AI work is evaporating -- no lasting asset to show investors or auditors?" |
| Champion | 11 | "Who on your team would own this technically?" |
| Champion | 12 | "If we moved forward, who would you want at the kickoff?" |

### Persona C: Lead Engineer (Champion)

| MEDDIC | # | Question |
|---|---|---|
| Metrics | 13 | "How many times per week does your team rebuild context that AI forgot?" |
| Pain | 14 | "What's your current stack? Where does it break at scale (>10 concurrent agents)?" |
| Pain | 15 | "Have you tried LangChain or CrewAI? What worked and what frustrated you?" |
| Champion | 16 | "Would you run a 2-week pilot -- 3 artifacts through 8F? Fastest proof of value." |
| Champion | 17 | "What would you need to see to recommend CEXAI to your CTO?" |

## Qualification Gate

| MEDDIC | Qualified | Disqualify |
|---|---|---|
| Metrics | Measurable AI quality problem | "AI is a nice-to-have" |
| Econ Buyer | Identified + access confirmed | "I'd have to escalate" (no path) |
| Criteria | 2+ criteria CEXAI wins | "We only care about price" |
| Process | Clear timeline + steps | "Nothing this quarter" |
| Pain | Governance / permanence pain | Task automation only (LangChain wins) |
| Champion | Willing to run a pilot | "I'll pass this along" |

Rule: 5+ dimensions GREEN -> pilot proposal. 3+ RED -> disqualify; offer OSS self-serve.

## Review Process

1. Rep uses 6-question set per persona in 30-min call.
2. Score MEDDIC post-call; flag RED dimensions.
3. After 5 uses: peer review with N06 team; update based on objection patterns.

## Related Artifacts
| Artifact | Relationship | Score |
|---|---|---|
| sales_playbook_n06 | upstream | 0.85 |
| [[p01_cm_cexai_vs_ai_frameworks]] | related | 0.70 |
| enterprise_sla_cex_platform | downstream | 0.60 |
