---
kind: quality_gate
id: p11_qg_permission
pillar: P11
llm_function: GOVERN
purpose: Golden and anti-examples of permission artifacts
pattern: few-shot learning — LLM reads these before producing
quality: null
title: "Gate: permission"
version: "1.0.0"
author: "builder_agent"
tags:
  - "quality-gate"
  - "permission"
  - "P11"
  - "P09"
  - "governance"
  - "access-control"
  - "security"
tldr: "Gates for permission artifacts — roles, operations, deny-by-default, audit trail, and escalation path defined."
domain: permission
created: "2026-03-27"
updated: "2026-03-27"
8f: "F7_govern"
keywords:
  - "gates for permission artifacts"
  - "audit trail"
  - "and escalation path defined"
  - "quality-gate"
  - "permission"
  - "governance"
  - "access-control"
density_score: 0.85
related:
  - bld_architecture_permission
  - permission-builder
  - n00_permission_manifest
  - p09_perm_{{SCOPE_SLUG}}
  - bld_collaboration_permission
---
## Quality Gate

# Gate: permission
## Definition
| Field     | Value                                              |
|-----------|----------------------------------------------------|
| metric    | role coverage completeness + deny-by-default enforcement |
| threshold | 8.0                                                |
| operator  | >=                                                 |
| scope     | all permission artifacts (P09)                     |
## HARD Gates
All must pass. Failure on any = final score 0.
| Gate | Check | Why |
|------|-------|-----|
| H01 | YAML frontmatter parses valid YAML | Broken YAML = permission silently open |
| H02 | id matches `^p09_perm_[a-z][a-z0-9_]+$` | Namespace compliance |
| H03 | id == filename stem | Brain search relies on this |
| H04 | kind == "permission" | Type integrity |
| H05 | quality == null | Never self-score |
| H06 | All required fields present: id, kind, pillar, version, created, updated, author, domain, quality, tags, tldr | Completeness |
## SOFT Scoring
| Gate | Check | Weight |
|------|-------|--------|
| S01 | tldr <= 160 chars, non-empty | 1.0 |
| S02 | tags is list, len >= 3, includes "permission" | 0.5 |
| S03 | density_score >= 0.80 | 0.5 |
| S04 | role_hierarchy block documents which roles inherit from which | 1.0 |
| S05 | allow_deny_precedence field states whether deny overrides allow or vice versa | 1.0 |
| S06 | inheritance_rules block explains how child resources derive permissions from parent | 0.5 |
Weights sum: 9.0. Normalize: divide each by 9.0 before scoring.
## Actions
| Score | Action |
|-------|--------|
| >= 9.5 | GOLDEN — pool as referencand access control spec for this resource class |
| >= 8.0 | PUBLISH — enforce in runtime and register in security index |
| >= 7.0 | REVIEW — complete audit trail, escalation path, or role hierarchy |
| < 7.0  | REJECT — rework default_access and operations contract |
## Bypass
| Field | Value |
|-------|-------|
| conditions | Incident response requiring emergency access grant with no time for full review |
| approver | p09-chief |
| audit_trail | Log in records/audits/ with grantee, resource, duration, and incident reference |
| expiry | 24h — emergency grant expires automatically; permanent change requires full gate pass |
| never_bypass | H01 (YAML), H05 (quality null) |

## Examples

# Examples: permission-builder
## Golden Example
INPUT: "Create permission para controlar access de agents ao pool de knowledge cards"
OUTPUT:
```yaml
id: p09_perm_pool_access
kind: permission
pillar: P09
title: "Permission: Pool Access"
version: "1.0.0"
created: "2026-03-26"
updated: "2026-03-26"
author: "builder"
```
WHY THIS IS GOLDEN:
- quality: null (H06 pass)
- id matches p09_perm_ pattern (H02 pass)
- kind: permission (H04 pass)
- 19 frontmatter fields present (H08 pass)
## Anti-Example
INPUT: "Set up access rules"
BAD OUTPUT:
```yaml
id: access_rules
kind: permission
title: "Access"
quality: 7.5
roles: admin
read: yes
write: yes

### S_RELATED: Cross-Reference Check (SOFT)
- [ ] `related:` frontmatter field populated (3-15 entries)
- [ ] `## Related Artifacts` section present in artifact body
- [ ] At least 1 upstream and 1 downstream reference
- Penalty: -0.3 if empty (does not block, encourages wiring)
