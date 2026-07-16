---
kind: quality_gate
id: p05_qg_onboarding_flow
pillar: P11
llm_function: GOVERN
purpose: Quality gate with HARD and SOFT scoring for onboarding_flow
quality: null
title: "Quality Gate Onboarding Flow"
version: "1.0.0"
author: wave1_builder_gen_v2
tags: [onboarding_flow, builder, quality_gate]
tldr: "Quality gate with HARD and SOFT scoring for onboarding_flow"
domain: "onboarding_flow construction"
created: "2026-04-14"
updated: "2026-04-14"
8f: "F7_govern"
keywords: [onboarding_flow construction, quality gate onboarding flow, onboarding_flow, builder, quality_gate, quality gate, fail condition]
density_score: 0.85
related:
  - onboarding-flow-builder
---
## Quality Gate

## Definition
| metric                | threshold | operator | scope         |
|-----------------------|-----------|----------|---------------|
| User activation rate  | 85%       | >=       | All users     |

## HARD Gates
| ID  | Check                          | Fail Condition                                    |
|-----|--------------------------------|---------------------------------------------------|
| H01 | YAML frontmatter valid         | Invalid or missing YAML frontmatter               |
| H02 | ID matches pattern             | ID does not match ^p05_of_[a-z][a-z0-9_]+.md$    |
| H03 | Onboarding completion rate     | < 80% completion rate                             |
| H04 | Aha-moment defined             | No aha-moment trigger specified                   |
| H05 | Error rate during onboarding   | > 5% error rate                                   |
| H06 | Time to first value            | > 10 minutes                                      |
| H07 | Invite/share hook present      | No viral hook defined in flow                     |

## SOFT Scoring
| Dim | Dimension               | Weight | Scoring Guide                                         |
|-----|-------------------------|--------|-------------------------------------------------------|
| D01 | Completion rate         | 0.20   | 1.00 (85%+), 0.50 (70-84%), 0.00 (<70%)              |
| D02 | Aha-moment engagement   | 0.20   | 1.00 (70%+), 0.50 (50-69%), 0.00 (<50%)              |
| D03 | Time to first value     | 0.15   | 1.00 (<=5 min), 0.50 (5-10 min), 0.00 (>10 min)     |
| D04 | Milestone clarity       | 0.15   | 1.00 (explicit+measurable), 0.50 (vague), 0.00 (missing) |
| D05 | Error rate              | 0.10   | 1.00 (<=2%), 0.50 (2-5%), 0.00 (>5%)                |
| D06 | UX feedback score       | 0.10   | 1.00 (4.5/5+), 0.50 (3.5-4.4), 0.00 (<=3.4)        |
| D07 | Invite/share hook       | 0.10   | 1.00 (at aha-moment), 0.50 (post-flow), 0.00 (absent) |

## Actions
| Score   | Action                                 |
|---------|----------------------------------------|
| GOLDEN  | No action required                     |
| PUBLISH | Publish with notes                     |
| REVIEW  | Review with engineering                |
| REJECT  | Reject and fix before resubmission     |

## Bypass
| conditions                          | approver | audit trail        |
|-------------------------------------|----------|--------------------|
| Critical bug fix with CTO approval  | CTO      | Ticket #PROD-12345 |

## Examples

## Golden Example  
**Title**: Notion Onboarding Flow -- "Create Your First Page" Aha-Moment  
**Kind**: onboarding_flow  
**Description**: A 4-step PLG activation flow that engineers the aha-moment at the first collaborative doc creation, driving team invites and habit formation.  
**Boundary**: Account creation -> first shared workspace (activation, not retention).  

**Steps**:  
1. **Sign-up**: Email or Google SSO. Single screen, no password confirmation required. Time-to-screen: <30s.  
2. **Use-case selection**: "What will you use Notion for?" (3 choices: Personal, Team, Work). Pre-populates workspace template. Reduces blank-canvas paralysis.  
3. **First page creation**: Pre-filled template based on use-case. User edits one field. Aha-moment trigger: real-time collaborative cursor appears after 10s, showing "You could invite your team here."  
4. **Invite hook**: "Notion is better with your team -- add 2 colleagues to unlock 1,000 AI credits." Double reward: social proof + tangible value.  

**Aha-Moment Design**:  
- Trigger: first edit saved (Sean Ellis activation event).  
- Signal: empty-state replaced with a filled page + teammate ghost cursor.  
- CTA: "Share this page" appears above fold, no scroll required.  
- Time-to-aha target: <2 minutes from sign-up.  

**Why it works**:  
- Mirrors Reforge activation framework: reduce friction, deliver value before asking for commitment.  
- Invite hook at aha-moment maximizes k-factor (viral coefficient).  
- Progress bar (3 of 4 steps complete) reduces abandonment via Zeigarnik effect.  

## Anti-Example 1: Missing Aha-Moment (Slack circa 2018)  
**Title**: Slack Onboarding -- Team-First Dead-End  
**Kind**: onboarding_flow  
**Description**: Flow that gates all value behind team setup, leaving solo sign-ups with an empty workspace and no activation path.  
**Boundary**: Activation flow.  

**Steps**:  
1. Sign-up with email.  
2. Create workspace name.  
3. Invite teammates (mandatory, 3 email fields).  
4. End flow -- empty #general channel.  

**Why it fails**:  
- Solo users who skip step 3 land on an empty channel with zero value. No aha-moment, no product tour, no template.  
- Mandatory invite field blocks 40%+ of sign-ups who don’t have emails ready.  
- No progress indicator -- users don’t know how close they are to finishing.

### S_RELATED: Cross-Reference Check (SOFT)
- [ ] `related:` frontmatter field populated (3-15 entries)
- [ ] `## Related Artifacts` section present in artifact body
- [ ] At least 1 upstream and 1 downstream reference
- Penalty: -0.3 if empty (does not block, encourages wiring)
