---
kind: quality_gate
id: p11_qg_incident_report
pillar: P11
llm_function: GOVERN
purpose: Quality gate with HARD and SOFT scoring for incident_report
quality: null
title: "Quality Gate Incident Report"
version: "1.1.0"
author: n05_ops
tags: [incident_report, builder, quality_gate]
tldr: "Quality gate with HARD and SOFT scoring for incident_report"
domain: "incident_report construction"
created: "2026-04-13"
updated: "2026-04-13"
8f: "F7_govern"
keywords: [incident_report construction, quality gate incident report, incident_report, builder, quality_gate, 'inc-\d{4}-\d{2}-\d{2}', summary]
density_score: 0.85
related:
  - incident-report-builder
---
## Quality Gate

## Definition
(Table: metric, threshold, operator, scope)
| metric                | threshold | operator | scope               |
|-----------------------|-----------|----------|---------------------|
| Incident report completeness | 100%      | =        | All incident reports |

## HARD Gates
(Table: ID | Check | Fail Condition)
| ID   | Check                  | Fail Condition                                      |
|------|------------------------|-----------------------------------------------------|
| H01  | YAML valid             | Invalid YAML syntax                                 |
| H02  | ID matches pattern     | ID does not match `INC-\d{4}-\d{2}-\d{2}`          |
| H03  | kind matches           | `kind` ≠ `incident_report`                          |
| H04  | Required fields present| Missing `summary`, `root_cause`, `action_items`     |
| H05  | Timeline details       | Timeline lacks timestamps or responsible parties    |
| H06  | Root cause analysis    | Analysis insufficient or lacks technical depth      |

## SOFT Scoring
(Table: Dim | Dimension | Weight | Scoring Guide)
| Dim | Dimension               | Weight | Scoring Guide                                      |
|-----|-------------------------|--------|----------------------------------------------------|
| D1  | Completeness            | 0.15   | All required sections present = 1.0 |
| D2  | Root cause analysis     | 0.25   | 5-Whys complete, contributing factors mapped = 1.0 |
| D3  | Action items            | 0.20   | Specific, owned, and dated items = 1.0 |
| D4  | Timeline accuracy       | 0.15   | All NIST SP 800-61 phases with timestamps = 1.0 |
| D5  | Stakeholder impact      | 0.10   | Quantified user + business impact = 1.0 |
| D6  | Lessons learned         | 0.10   | Systemic gaps identified and linked to actions = 1.0 |
| D7  | Sign-off validity       | 0.05   | All required roles signed = 1.0 |

## Actions
(Table: Score | Action)
| Score     | Action                                      |
|-----------|---------------------------------------------|
| GOLDEN    | >=9.5: Automatically publish and notify stakeholders |
| PUBLISH   | >=8.0: Publish after minimal review           |
| REVIEW    | >=7.0: Require team review and revisions      |
| REJECT    | <7.0: Reject, resubmission required           |

## Bypass
(Table: conditions, approver, audit trail)
| conditions                | approver | audit trail                                |
|---------------------------|----------|--------------------------------------------|
| Emergency bypass          | CTO      | Log bypass reason, approver, timestamp     |
| Regulatory override       | CRO      | Document legal justification, approver     |
| System failure            | CTO      | Include system state, approver, timestamp  |

## Examples

## Golden Example
```markdown
---
title: "Data Corruption Incident in AI Training Pipeline"
date: 2023-10-15
team: AI Infrastructure
severity: High
---

**Summary**
A data corruption incident occurred during batch processing of training data, leading to 32% of models failing validation. Root cause: faulty checksum validation in data ingestion.

**Timeline**
- 2023-10-14 10:00: Ingestion job initiated
- 2023-10-14 11:30: Anomalies detected in validation metrics
- 2023-10-14 14:00: Incident declared; rollback to previous version
- 2023-10-15 09:00: Root cause identified; hotfix deployed

**Root Cause**
Missing checksum validation in data ingestion code allowed corrupted files to pass undetected. Code merged without peer review due to CI/CD pipeline misconfiguration.

**Impact**
- 12 models invalidated
- 48 hours of retraining required
- $12k in compute costs

**Mitigation**
- Implemented mandatory checksum validation
- Enforced peer review for critical code paths
- Added data integrity monitoring dashboard

**Lessons Learned**
- CI/CD pipeline requires stricter gatekeeping
- Data validation should be redundant across layers
- Incident response plan executed successfully
```

## Anti-Example 1: Missing Root Cause Analysis
```markdown
---
title: "Training Delay Incident"
date: 2023-10-15
team: AI Training
severity: Medium
---

**Summary**
Training job took 2 hours longer than expected. No further details.

**Timeline**
- 2023-10-14 10:00: Job started
- 2023-10-14 12:30: Job completed

**Impact**
- Minor delay in model deployment
- No financial impact

**Mitigation**
- "Improved monitoring" (no specifics)
```
## Why it fails
Lacks detailed root cause, actionable lessons, and quantified impact. Summary is vague, timeline provides no context, and mitigation is non-specific.

## Anti-Example 2: Overly Technical Without Context
```markdown
---
title: "GPU Memory Leak in Inference Engine"
date: 2023-10-15
team: Inference
severity: Critical
---

**Summary**
Memory leak detected in PyTorch 2.1.3 when using mixed-precision training with FSDP. Leak rate: 2.3MB/epoch.

**Timeline**
- 2023-10-14 10:00: Job started
- 2023-10-14 12:30: OOM error encountered

**Root Cause**
Incorrect tensor pinning in `torch.distributed` caused memory fragmentation.

**Mitigation**
- Upgraded to PyTorch 2.2
- Added `torch.cuda.empty_cache()` calls
```

### S_RELATED
-0.3 if `related:` < 3 or body lacks Related Artifacts

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[incident-report-builder]] | related | 0.28 |
