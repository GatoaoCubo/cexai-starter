---
kind: quality_gate
id: p03_qg_expansion_play
pillar: P11
llm_function: GOVERN
purpose: Quality gate with HARD and SOFT scoring for expansion_play
quality: null
title: "Quality Gate Expansion Play"
version: "1.0.0"
author: wave6_n06
tags: [expansion_play, builder, quality_gate, NRR, upsell, land-and-expand]
tldr: "Quality gate with HARD and SOFT scoring for expansion_play"
domain: "expansion_play construction"
created: "2026-04-14"
updated: "2026-04-14"
8f: "F7_govern"
keywords: [expansion_play construction, quality gate expansion play, expansion_play, builder, quality_gate, upsell, land-and-expand]
density_score: 0.85
related:
  - bld_schema_expansion_play
  - expansion-play-builder
  - bld_instruction_expansion_play
  - bld_knowledge_card_expansion_play
  - p12_qg_renewal_workflow
---
## Quality Gate

## Definition
| Metric                        | Threshold | Operator | Scope                        |
|-------------------------------|-----------|----------|------------------------------|
| Expansion trigger specificity | 100%      | equals   | All quantified, time-bounded |
| NRR model completeness        | 100%      | equals   | Expansion + contraction + churn |

## HARD Gates
| ID  | Check                                              | Fail Condition                                          |
|-----|----------------------------------------------------|---------------------------------------------------------|
| H01 | YAML frontmatter valid                             | Invalid YAML syntax or missing required fields          |
| H02 | ID matches pattern ^p03_ep_[a-z][a-z0-9_]+\.md$  | ID format mismatch                                      |
| H03 | kind field = "expansion_play"                      | Kind field incorrect or missing                         |
| H04 | expansion_type field present and valid enum        | Missing or invalid (must be seat_upsell/tier_upgrade/cross_sell/usage_ramp) |
| H05 | trigger_type field present and valid enum          | Missing or invalid trigger type                         |
| H06 | NRR_target field present and numeric              | Missing or non-numeric (e.g., "good NRR" fails)         |

## SOFT Scoring
| Dim | Dimension                                            | Weight | Scoring Guide                                                           |
|-----|------------------------------------------------------|--------|-------------------------------------------------------------------------|
| D01 | Trigger quantification (specific threshold + window) | 0.25   | Specific % + time window = 1.0, one dimension only = 0.5, vague = 0   |
| D02 | NRR model accuracy (all 3 components present)        | 0.25   | All 3 (expansion, contraction, churn) = 1.0, 2 = 0.5, <2 = 0          |
| D03 | Talk track quality (hook-value-case-ask-next)        | 0.20   | All 5 sections = 1.0, 3-4 = 0.5, <3 = 0                               |
| D04 | Account map depth (buyer + champion + blocker)       | 0.15   | 3+ stakeholders = 1.0, 2 = 0.5, 1 = 0                                 |
| D05 | QBR alignment (customer metrics, not internal)       | 0.15   | Customer-facing metrics only = 1.0, mixed = 0.5, internal only = 0    |

## Actions
| Level  | Score  | Action                                      |
|--------|--------|---------------------------------------------|
| GOLDEN | >=9.5  | Auto-publish; used as golden example        |
| PUBLISH| >=8.0  | Auto-publish after AE/CSM lead review       |
| REVIEW | >=7.0  | Require RevOps or CS lead manual review     |
| REJECT | <7.0   | Reject; return to builder for rework        |

## Bypass
| Conditions                     | Approver        | Audit Trail              |
|--------------------------------|-----------------|--------------------------|
| Emergency QBR prep (<48h)      | VP CS or VP Sales| Escalation log in CRM   |

## Examples

## Golden Example
```markdown
---
id: p03_ep_acme_seat_upsell_q2.md
kind: expansion_play
pillar: P03
title: "Acme Corp -- Seat Upsell Expansion Play Q2 2026"
account_segment: ENT
expansion_type: seat_upsell
trigger_type: usage_threshold
```

## Anti-Example 1: Vague Triggers
```markdown
---
kind: expansion_play
title: Acme Upsell Play
---
## Trigger
The account seems to be using the product heavily and the team is growing.
Consider reaching out when the timing feels right.
```
**Why it fails**: "Seems to be using heavily" and "when timing feels right" are not quantified triggers. There is no threshold, no time window, no owner. This cannot be automated or measured. The play will never fire reliably.

## Anti-Example 2: Missing NRR Model
```markdown
---
kind: expansion_play
NRR_target: "good"
---
## Expansion
Adding 20 seats will increase revenue and help us hit NRR targets.
```
**Why it fails**: "Good" is not a numeric NRR target. No beginning ARR, no expansion ARR, no contraction risk modeled. RevOps cannot forecast from this. The play provides zero commercial accountability.

## Anti-Example 3: Churn Play Misclassified as Expansion
```markdown
---
kind: expansion_play
title: "Acme Retention Play"
expansion_type: seat_upsell
---
## Trigger
Account health score dropped to 45. We need to save this account.
```
**Why it fails**: Health score 45 is a churn risk signal, not an expansion trigger. This belongs in churn_prevention_playbook, not expansion_play. Expansion plays require positive usage signals -- seats being consumed, adoption growing, value being realized.

### S_RELATED: Cross-Reference Check (SOFT)
- [ ] `related:` frontmatter field populated (3-15 entries)
- [ ] `## Related Artifacts` section present in artifact body
- [ ] At least 1 upstream and 1 downstream reference
- Penalty: -0.3 if empty (does not block, encourages wiring)
