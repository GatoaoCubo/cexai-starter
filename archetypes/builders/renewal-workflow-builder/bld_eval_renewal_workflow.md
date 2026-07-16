---
kind: quality_gate
id: p12_qg_renewal_workflow
pillar: P11
llm_function: GOVERN
purpose: Quality gate with HARD and SOFT scoring for renewal_workflow
quality: null
title: "Quality Gate Renewal Workflow"
version: "1.0.0"
author: wave6_n06
tags: [renewal_workflow, builder, quality_gate, GRR, renewal, Gainsight]
tldr: "Quality gate with HARD and SOFT scoring for renewal_workflow"
domain: "renewal_workflow construction"
created: "2026-04-14"
updated: "2026-04-14"
8f: "F7_govern"
keywords: [renewal_workflow construction, quality gate renewal workflow, renewal_workflow, builder, quality_gate, renewal, gainsight]
density_score: 0.85
related:
  - bld_schema_renewal_workflow
---
## Quality Gate

## Definition
| Metric                      | Threshold | Operator | Scope                          |
|-----------------------------|-----------|----------|--------------------------------|
| Stage owner assignment      | 100%      | equals   | All 3 stages have named owners |
| GRR scenario coverage       | 100%      | equals   | Full + contraction + churn     |

## HARD Gates
| ID  | Check                                               | Fail Condition                                          |
|-----|-----------------------------------------------------|---------------------------------------------------------|
| H01 | YAML frontmatter valid                              | Invalid YAML syntax or missing required fields          |
| H02 | ID matches pattern ^p12_rw_[a-z][a-z0-9_]+\.yaml$ | ID format mismatch                                      |
| H03 | kind field = "renewal_workflow"                     | Kind field incorrect or missing                         |
| H04 | renewal_stage field present and valid enum          | Missing or invalid (must be 90_day/60_day/30_day/closed)|
| H05 | days_to_renewal field present and positive integer  | Missing or negative/zero value                          |
| H06 | GRR_impact field present and valid enum             | Missing or invalid (must be full/contraction_*/churn)   |

## SOFT Scoring
| Dim | Dimension                                              | Weight | Scoring Guide                                                              |
|-----|--------------------------------------------------------|--------|----------------------------------------------------------------------------|
| D01 | Stage completeness (owner + tasks + automation trigger)| 0.25   | All 3 elements per stage = 1.0, 2 = 0.5, <2 = 0                          |
| D02 | Price-increase playbook specificity                    | 0.25   | % range + timing + objections + discount authority = 1.0, 2-3 = 0.5, <2 = 0|
| D03 | Multi-year incentive structure                         | 0.20   | Discount range + approval authority = 1.0, one only = 0.5, missing = 0   |
| D04 | GRR model completeness (3 scenarios)                   | 0.15   | All 3 modeled with ARR impact = 1.0, 2 = 0.5, <2 = 0                     |
| D05 | Compliance accuracy (jurisdiction-specific notices)    | 0.15   | Named jurisdictions with specific days = 1.0, partial = 0.5, generic = 0  |

## Actions
| Level  | Score  | Action                                            |
|--------|--------|---------------------------------------------------|
| GOLDEN | >=9.5  | Auto-publish; used as golden example              |
| PUBLISH| >=8.0  | Auto-publish after RevOps + Legal review          |
| REVIEW | >=7.0  | Require CS VP and Legal manual review             |
| REJECT | <7.0   | Reject; return to builder for rework              |

## Bypass
| Conditions                          | Approver           | Audit Trail               |
|-------------------------------------|--------------------|---------------------------|
| Contract end < 14 days emergency    | VP CS + CFO        | Escalation log in Gainsight|

## Examples

## Golden Example
```yaml
---
id: p12_rw_acme_corp_2026.yaml
kind: renewal_workflow
pillar: P12
title: "Acme Corp Renewal Workflow -- 2026-06-30"
contract_id: "SF-OPP-2024-0892"
renewal_stage: 90_day
days_to_renewal: 91
```

## Anti-Example 1: Missing Escalation Triggers
```yaml
---
kind: renewal_workflow
renewal_stage: 90_day
---
# Stages
90-day: Send email, check in with customer
60-day: Send proposal
30-day: Try to close
Escalation: Escalate if needed
```
**Why it fails**: "If needed" is not an escalation trigger. There is no health score threshold, no named escalation owner, no SLA. CSMs will not know when or to whom to escalate. High-risk renewals will slip through without executive involvement.

## Anti-Example 2: Generic Compliance Language
```yaml
auto_renewal: true
notice_period_days: 30
```
Without specifying jurisdiction, "30 days" may be non-compliant. California requires 30 days for auto-renewal. EU GDPR may require different notice. Australia has its own consumer law requirements. Generic notice periods create legal exposure.

## Anti-Example 3: Expansion Play Misclassified as Renewal
```yaml
---
kind: renewal_workflow
title: "Acme Corp Renewal and Upsell"
---
# Renewal
Renew the current contract AND add 20 seats at renewal.
```
**Why it fails**: Seat upsell is an expansion_play, not a renewal_workflow. Renewal workflows protect existing ARR (GRR). Expansion plays grow net-new ARR within existing accounts (NRR > 100%). Conflating the two creates accountability confusion between CS (owns renewal) and AE (owns expansion).

### S_RELATED: Cross-Reference Check (SOFT)
- [ ] `related:` frontmatter field populated (3-15 entries)
- [ ] `## Related Artifacts` section present in artifact body
- [ ] At least 1 upstream and 1 downstream reference
- Penalty: -0.3 if empty (does not block, encourages wiring)
