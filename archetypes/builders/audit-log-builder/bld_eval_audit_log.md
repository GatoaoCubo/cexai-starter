---
kind: quality_gate
id: p11_qg_audit_log
pillar: P11
llm_function: GOVERN
purpose: Quality gate with HARD and SOFT scoring for audit_log
quality: null
title: "Quality Gate Audit Log"
version: "1.0.0"
author: wave1_builder_gen_v2
tags: [audit_log, builder, quality_gate]
tldr: "Quality gate with HARD and SOFT scoring for audit_log"
domain: "audit_log construction"
created: "2026-04-14"
updated: "2026-04-14"
8f: "F7_govern"
keywords: [audit_log construction, quality gate audit log, audit_log, builder, quality_gate, "## anti-example 1: missing immutability", quality gate, fail condition, scoring guide, data integrity]
density_score: 0.85
related:
  - audit-log-builder
---
## Quality Gate

## Definition
| metric | threshold | operator | scope |
|---|---|---|---|
| Audit log immutability | 100% | equals | All audit logs |

## HARD Gates
| ID | Check | Fail Condition |
|---|---|---|
| H01 | YAML frontmatter valid | Missing or invalid frontmatter |
| H02 | ID matches pattern ^p11_al_[a-z][a-z0-9_]+.md$ | ID format invalid |
| H03 | kind field matches 'audit_log' | kind field incorrect |
| H04 | Required field 'timestamp' exists | Missing 'timestamp' |
| H05 | Required field 'actor' exists | Missing 'actor' |
| H06 | Required field 'action' exists | Missing 'action' |
| H07 | Required field 'resource' exists | Missing 'resource' |
| H08 | Required field 'outcome' exists | Missing 'outcome' |

## SOFT Scoring
| Dim | Dimension | Weight | Scoring Guide |
|---|---|---|---|
| D1 | Data Integrity | 0.20 | 1.0 if immutable, 0.5 if partially mutable, 0.0 otherwise |
| D2 | Encryption | 0.15 | 1.0 if encrypted at rest, 0.5 if unencrypted |
| D3 | Retention | 0.15 | 1.0 if retention ≥ 180 days, 0.5 if < 180 days |
| D4 | Tamper Evidence | 0.15 | 1.0 if hash signatures present, 0.5 if absent |
| D5 | Field Completeness | 0.10 | 1.0 if all required fields present, 0.5 if missing |
| D6 | Access Controls | 0.10 | 1.0 if read-only access enforced, 0.5 if not |
| D7 | Audit Trail Completeness | 0.15 | 1.0 if full event context captured, 0.5 if partial |

## Actions
| Score | Action |
|---|---|
| GOLDEN (≥9.5) | Auto-approve and deploy |
| PUBLISH (≥8.0) | Publish with review |
| REVIEW (≥7.0) | Manual review required |
| REJECT (<7.0) | Block deployment |

## Bypass
| conditions | approver | audit trail |
|---|---|---|
| Emergency system fix | Security Officer | Log bypass request with justification |

## Examples

## Golden Example
```yaml
spec: audit_log
vendor: AWS
product: CloudTrail
version: 2.0
compliance: SOC2 Type II
---
log_retention: 730 days
encryption_at_rest: AES-256 (managed by AWS KMS)
access_controls: IAM roles with least privilege, multi-factor authentication required
immutability: Enabled via S3 versioning and CloudTrail log integrity checks
audit_coverage: All API calls, user activity, configuration changes
```

## Anti-Example 1: Missing Immutability
```yaml
spec: audit_log
vendor: Azure
product: Log Analytics
version: 1.5
compliance: SOC2 Type II
---
log_retention: 365 days
encryption_at_rest: AES-256
access_controls: RBAC with admin overrides
immutability: Not enforced
audit_coverage: System events only
```
## Why it fails
Lacks immutability guarantees required for SOC2. Logs can be modified or deleted by admins, violating integrity requirements.

## Anti-Example 2: Incomplete Retention
```yaml
spec: audit_log
vendor: Google Cloud
product: Cloud Audit Logs
version: 3.1
compliance: SOC2 Type II
---
log_retention: 90 days
encryption_at_rest: AES-256
access_controls: IAM with audit logging
immutability: Enabled
audit_coverage: All administrative actions
```
## Why it fails
Retention period (90 days) is insufficient for SOC2 compliance, which typically requires 3-5 years of log retention for audit trails.

### H_RELATED: Cross-Reference Check (HARD)
- [ ] `related:` frontmatter field populated (min 3 entries)
- [ ] `## Related Artifacts` section present in artifact body
- [ ] At least 1 upstream and 1 downstream or sibling reference
- Gate: REJECT if < 3 entries (auto-populated by cex_wikilink.py at F6.5)

### S_RELATED: Cross-Reference Check (SOFT)
- [ ] `related:` frontmatter field populated (3-15 entries)
- [ ] `## Related Artifacts` section present in artifact body
- [ ] At least 1 upstream and 1 downstream reference
- Penalty: -0.3 if empty (does not block, encourages wiring)
