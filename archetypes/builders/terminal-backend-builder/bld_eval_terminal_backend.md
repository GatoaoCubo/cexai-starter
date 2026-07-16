---
kind: quality_gate
id: p09_qg_terminal_backend
pillar: P11
llm_function: GOVERN
purpose: Quality gate with HARD and SOFT scoring for terminal_backend
quality: null
title: "Quality Gate Terminal Backend"
version: "1.0.0"
author: n03_engineering
tags:
  - "terminal_backend"
  - "builder"
  - "quality_gate"
tldr: "Quality gate for terminal_backend: 5 HARD gates (backend_type, timeout, auth, serverless-flag, ID pattern), 5D SOFT scoring"
domain: "terminal_backend construction"
created: "2026-04-18"
updated: "2026-04-18"
8f: "F7_govern"
keywords:
  - "terminal_backend construction"
  - "quality gate terminal backend"
  - "quality gate for terminal_backend"
  - "hard gates"
  - "id pattern"
  - "d soft scoring"
  - "terminal_backend"
density_score: 0.92
related:
  - bld_schema_terminal_backend
  - terminal-backend-builder
---
## Quality Gate
## Definition
| metric | threshold | operator | scope |
|--------|-----------|----------|-------|
| Backend Type Valid | one of 6 | required | backend_type field |
| Timeout Defined | > 0 | required | limits.timeout_seconds |
| Quality Score | 8.0 | >= | Publish threshold |

## HARD Gates
| ID | Check | Fail Condition |
|----|-------|---------------|
| H01 | YAML valid | Invalid YAML syntax in artifact |
| H02 | ID matches pattern | ID does not match `^p09_tb_[a-z0-9_-]+$` |
| H03 | backend_type valid | backend_type not in {local, docker, ssh, daytona, modal, singularity} |
| H04 | timeout_seconds set | limits.timeout_seconds is null or missing |
| H05 | auth consistency | auth.method != none but auth.secret_ref is null |

## SOFT Scoring
| Dim | Dimension | Weight | Scoring Guide |
|-----|-----------|--------|---------------|
| D1 | Schema Completeness | 0.25 | All required fields present+typed=1.0; missing 1=0.7; missing 2+=0.3 |
| D2 | Backend Specificity | 0.25 | Connection block + backend-specific fields=1.0; generic only=0.6; empty=0.2 |
| D3 | Auth Correctness | 0.20 | Method matches backend type + secret_ref set=1.0; method set but no ref=0.6; none for auth-required=0.0 |
| D4 | Cost Model Accuracy | 0.15 | billing + estimated_usd_per_hour both set=1.0; billing only=0.7; neither=0.3 |
| D5 | Serverless Flags | 0.15 | serverless+hibernation_capable match backend capabilities=1.0; one wrong=0.5; both wrong=0.0 |

**Weight sum: 0.25+0.25+0.20+0.15+0.15 = 1.00**

## Actions
| Score | Action |
|-------|--------|
| GOLDEN >=9.5 | Auto-approve, ready for nucleus deployment |
| PUBLISH >=8.0 | Manual review, staging allowed |
| REVIEW >=7.0 | Peer review required, no deployment |
| REJECT <7.0 | Block deployment, fix required |

## Bypass
| conditions | approver | audit trail |
|------------|----------|-------------|
| Emergency backend switch with compensating documentation | N05 Lead | Incident ticket |
| New backend type not in supported list | Architecture review | ADR required |
| auth.method=none on ssh in air-gapped network with compensating network controls | Security Lead | Security exception ticket + 30-day expiry |

## Backend Capability Matrix
| Backend | serverless | hibernation | auth | billing |
|---------|-----------|-------------|------|---------|
| local | false | false | none | free |
| docker | false | false | none | free |
| ssh | false | false | ssh_key | free |
| daytona | true | true | api_token | per_task |
| modal | true | false | api_token | per_invocation |
| singularity | false | false | ssh_key | site_license |

### S_RELATED: Cross-Reference Check (SOFT)
- [ ] `related:` frontmatter field populated (3-15 entries)
- [ ] `## Related Artifacts` section present in artifact body
- [ ] At least 1 upstream and 1 downstream reference
- Penalty: -0.3 if empty (does not block, encourages wiring)
