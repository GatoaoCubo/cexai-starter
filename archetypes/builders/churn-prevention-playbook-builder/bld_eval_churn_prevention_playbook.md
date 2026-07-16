---
kind: quality_gate
id: p03_qg_churn_prevention_playbook
pillar: P11
llm_function: GOVERN
purpose: Quality gate with HARD and SOFT scoring for churn_prevention_playbook
quality: null
title: "Quality Gate Churn Prevention Playbook"
version: "1.0.0"
author: n05_wave6
tags: [churn_prevention_playbook, builder, quality_gate]
tldr: "Quality gate with HARD and SOFT scoring for churn_prevention_playbook"
domain: "churn_prevention_playbook construction"
created: "2026-04-14"
updated: "2026-04-14"
8f: "F7_govern"
keywords: [churn_prevention_playbook construction, churn_prevention_playbook, builder, quality_gate, '^p03_cpp_[a-z][a-z0-9_]+\.md$', quality gate, fail condition]
density_score: 0.85
related:
  - churn-prevention-playbook-builder
---
## Quality Gate

## Definition
| Metric                        | Threshold | Operator | Scope                              |
|-------------------------------|-----------|----------|------------------------------------|
| Gainsight/ChurnZero alignment | 100%      | equals   | All playbook artifacts             |
| Save script completeness      | 4 sections| min      | opening + discovery + objections + close |

## HARD Gates
| ID  | Check                                                       | Fail Condition                         |
|-----|-------------------------------------------------------------|----------------------------------------|
| H01 | YAML frontmatter valid                                      | Invalid YAML or missing required fields|
| H02 | ID matches `^p03_cpp_[a-z][a-z0-9_]+\.md$`                 | Pattern mismatch                       |
| H03 | kind = `churn_prevention_playbook`                         | Wrong or missing kind                  |
| H04 | health_score_model present with >= 3 components             | Incomplete health model                |
| H05 | intervention_triggers covers red-zone AND pre-renewal       | Missing trigger coverage               |
| H06 | Save script has opening, discovery, objections, close       | Incomplete script structure            |
| H07 | Win-back sequence has >= 3 touchpoints                      | Insufficient win-back coverage         |

## SOFT Scoring
| Dim | Dimension                                           | Weight | Scoring Guide                                                  |
|-----|-----------------------------------------------------|--------|----------------------------------------------------------------|
| D01 | Health score model completeness                     | 0.25   | 5 components (usage, NPS, support, engagement, contract) = 1.0, 3-4 = 0.7, <3 = 0.3 |
| D02 | Churn reason taxonomy coverage                      | 0.20   | All 4 reasons (product, budget, competitor, champion) = 1.0, 2-3 = 0.6, <2 = 0.2 |
| D03 | Objection handler specificity                       | 0.20   | Named objections with scripts = 1.0, generic = 0.5, absent = 0|
| D04 | Escalation path completeness                        | 0.15   | CSM -> VP CS -> exec = 1.0, CSM -> mgr only = 0.6, single hop = 0.2 |
| D05 | Win-back sequence quality                           | 0.20   | 3+ touchpoints + personalization hooks = 1.0, generic = 0.5, absent = 0 |

## Actions
| Score   | Threshold | Action                              |
|---------|-----------|-------------------------------------|
| GOLDEN  | >=9.5     | Auto-publish, no review             |
| PUBLISH | >=8.0     | Auto-publish after validation       |
| REVIEW  | >=7.0     | Require CS Director review          |
| REJECT  | <7.0      | Reject -- rebuild with save script  |

## Bypass
| Condition                  | Approver     | Audit Trail              |
|----------------------------|--------------|--------------------------|
| Emergency churn spike      | VP CS        | Incident log             |

## Examples

## Golden Example  
---
**Title**: Churn Prevention Playbook for SaaS Retention  
**Author**: Customer Success Team  
**Date**: 2023-10-05  
**Version**: 1.2  

### Signal Detection  
- **Tools**: Salesforce (custom fields for usage metrics), Mixpanel (behavioral analytics)  
- **Signals**: 30-day inactivity, 20% drop in feature usage, support tickets with "billing" in subject line  

### Intervention Triggers  
- **Rules**:  
  - If user has 2+ inactive licenses in Salesforce AND Mixpanel shows 0 logins in 14 days → Auto-assign to CS Rep  
  - If NPS score < 5 in SurveyMonkey → Trigger email from HubSpot with CSM  

### Save-the-Account Scripts  
- **Script 1**:  
  ```python  
  # HubSpot API call to send personalized email  
  payload = {  
    "email": "user@example.com",  
    "subject": "We noticed you're not using [Feature X] – let’s fix that!",  
    "body": "Hi [Name], we see you haven’t used [Feature X] recently. Our team can help you get more value from it. Schedule a call here: [link]."  
  }  
  ```  
- **Script 2**:  
  ```sql  
  -- Query to identify at-risk accounts in Salesforce  
  SELECT Name, AccountId, LastLoginDate, NumberOfLicenses  
  FROM User  
  WHERE LastLoginDate < DATEADD(day, -30, GETDATE()) AND NumberOfLicenses > 5;  
  ```  

## Anti-Example 1: Vague Tool References  
---
**Title**: Generic Churn Playbook  
**Author**: Unknown  
**Date**: 2023-01-01  
**Version**: 0.1  

### Signal Detection  
- **Tools**: "Some CRM", "Generic analytics tool"  
- **Signals**: "Low engagement", "High support requests"  

### Intervention Triggers  
- **Rules**:  
  - If "user is unhappy" → "Send email"  

### Save-the-Account Scripts  
- **Script**: "Use [tool] to contact user"  

## Why it fails  
Lacks specificity in tools (no real vendor names) and actionable steps. "Low engagement" and "user is unhappy" are too vague to trigger automated workflows.

### S_RELATED: Cross-Reference Check (SOFT)
- [ ] `related:` frontmatter field populated (3-15 entries)
- [ ] `## Related Artifacts` section present in artifact body
- [ ] At least 1 upstream and 1 downstream reference
- Penalty: -0.3 if empty (does not block, encourages wiring)
