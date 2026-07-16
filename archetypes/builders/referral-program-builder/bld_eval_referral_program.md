---
kind: quality_gate
id: p11_qg_referral_program
pillar: P11
llm_function: GOVERN
purpose: Quality gate with HARD and SOFT scoring for referral_program
quality: null
title: "Quality Gate Referral Program"
version: "1.0.0"
author: wave1_builder_gen_v2
tags: [referral_program, builder, quality_gate]
tldr: "Quality gate with HARD and SOFT scoring for referral_program"
domain: "referral_program construction"
created: "2026-04-14"
updated: "2026-04-14"
8f: "F7_govern"
keywords: [referral_program construction, quality gate referral program, referral_program, builder, quality_gate, "## anti-example 1: missing viral coefficient", quality gate]
density_score: 0.85
related:
  - referral-program-builder
---
## Quality Gate

## Definition
(Table: metric, threshold, operator, scope)
| Metric | Threshold | Operator | Scope |
|---|---|---|---|
| Viral coefficient | ≥1.5 | ≥ | Program design |
| Reward conversion rate | ≥10% | ≥ | User engagement |

## HARD Gates
(Table: ID | Check | Fail Condition)
| ID | Check | Fail Condition |
|---|---|---|
| H01 | YAML frontmatter valid | Invalid or missing YAML metadata |
| H02 | ID matches pattern ^p11_rp_[a-z][a-z0-9_]+.yaml$ | ID format mismatch |
| H03 | kind field matches 'referral_program' | Kind field incorrect |
| H04 | Referral link uniqueness enforced | Duplicate referral links allowed |
| H05 | Reward cap per user defined | No maximum reward limit |
| H06 | Program cooldown period ≥7 days | Cooldown period <7 days |
| H07 | Referral tracking system implemented | No tracking mechanism |
| H08 | Terms of use compliance checked | Missing legal compliance checks |

## SOFT Scoring
(Table: Dim | Dimension | Weight | Scoring Guide)
| Dim | Dimension | Weight | Scoring Guide |
|---|---|---|---|
| D1 | Viral coefficient design | 0.20 | 1.0-1.5 (1.0), 0.5-1.0 (0.5), <0.5 (0) |
| D2 | Reward clarity | 0.15 | Clear (1.0), Ambiguous (0.5), Missing (0) |
| D3 | User experience | 0.15 | Seamless (1.0), Moderate (0.5), Poor (0) |
| D4 | Legal compliance | 0.15 | Fully compliant (1.0), Partial (0.5), Non-compliant (0) |
| D5 | Scalability | 0.10 | Scalable (1.0), Limited (0.5), Non-scalable (0) |
| D6 | Conversion rate | 0.10 | >=10% (1.0), 5-10% (0.5), <5% (0) |
| D7 | Tracking accuracy | 0.15 | 100% (1.0), 75-99% (0.5), <75% (0) |

## Actions
(Table: Score | Action)
| Score | Action |
|---|---|
| ≥9.5 | GOLDEN: Deploy immediately |
| ≥8.0 | PUBLISH: Launch with monitoring |
| ≥7.0 | REVIEW: Fix minor issues |
| <7.0 | REJECT: Revise and resubmit |

## Bypass
(Table: conditions, approver, audit trail)
| Conditions | Approver | Audit Trail |
|---|---|---|
| Urgent business need | CTO | Documented approval + timestamp |

## Examples

## Golden Example  
```yaml  
kind: referral_program  
name: "Dropbox Referral Program"  
vendor: Dropbox Inc.  
description: "Incentivizes users to invite peers via tiered rewards and viral sharing mechanics."  
spec:  
  viral_coefficient: 2.5  
  reward_structure:  
    - level: 1  
      condition: "Invite 1 user"  
      reward: "5GB of storage"  
    - level: 5  
      condition: "Invite 5 users"  
      reward: "100GB of storage + $10 credit"  
  tracking:  
    - method: "Unique referral links with UTM parameters"  
    - attribution: "First-click model for credit assignment"  
  metrics:  
    - "Referral conversion rate"  
    - "Average number of referrals per user"  
```  

## Anti-Example 1: Missing Viral Coefficient  
```yaml  
kind: referral_program  
name: "FakeApp Referral Program"  
vendor: FakeApp LLC.  
description: "Users earn points for referrals, but no clear viral mechanics."  
spec:  
  reward_structure:  
    - level: 1  
      condition: "Invite 1 user"  
      reward: "10 points"  
  tracking:  
    - method: "Email-based referral codes"  
```  
## Why it fails  
No viral coefficient defined; users have no incentive to share beyond minimal rewards. Points system lacks scalability or urgency, leading to low participation.  

## Anti-Example 2: Unaligned Reward Structure  
```yaml  
kind: referral_program  
name: "BrokenReferral Program"  
vendor: BrokenCo Inc.  
description: "Rewards are given only after 100 referrals, deterring early engagement."  
spec:  
  viral_coefficient: 1.2  
  reward_structure:  
    - level: 100  
      condition: "Invite 100 users"  
      reward: "Free premium subscription"  
```  
## Why it fails  
Reward structure is too distant (100 invites) to motivate participation. High threshold creates friction, making the program ineffective for viral growth.

### S_RELATED: Cross-Reference Check (SOFT)
- [ ] `related:` frontmatter field populated (3-15 entries)
- [ ] `## Related Artifacts` section present in artifact body
- [ ] At least 1 upstream and 1 downstream reference
- Penalty: -0.3 if empty (does not block, encourages wiring)
