---
id: bld_quality_gate_deployment_manifest
kind: quality_gate
pillar: P07
title: "Gate: deployment_manifest"
version: "1.0.0"
created: "2026-04-17"
updated: "2026-04-17"
author: builder
domain: deployment_manifest
quality: null
tags:
  - "quality_gate"
  - "deployment_manifest"
  - "P09"
llm_function: GOVERN
tldr: "Validates deployment manifests for artifact pinning, rollback strategy, secrets handling, and environment targeting."
8f: "F7_govern"
keywords:
  - "rollback strategy"
  - "secrets handling"
  - "and environment targeting"
  - "quality_gate"
  - "deployment_manifest"
  - "^p09_dm_[a-z][a-z0-9_]+$"
  - "quality"
density_score: null
---
## Quality Gate

## Definition
A deployment_manifest specifies what artifacts to deploy, to which environment, with what config, and how to roll back. This gate ensures every manifest is safe to hand to an automated deployment pipeline without human interpretation.

## HARD Gates
Failure on any HARD gate causes immediate REJECT.

| ID  | Check | Rule |
|-----|-------|------|
| H01 | Frontmatter parses | YAML frontmatter is valid with no syntax errors |
| H02 | ID matches namespace | `id` matches pattern `^p09_dm_[a-z][a-z0-9_]+$` |
| H03 | Kind matches literal | `kind` is exactly `deployment_manifest` |
| H04 | No inline secrets | No plaintext secret values in frontmatter or body |
| H05 | Quality is null | `quality` field is `null` |
| H06 | Artifacts list non-empty | At least 1 artifact with name + version |

## SOFT Scoring
| Dimension | Weight | Pass Condition |
|-----------|--------|----------------|
| Artifacts have checksums | 1.0 | SHA256 present per artifact |
| Target environment fully specified | 1.0 | namespace + region + cluster all present |
| Health check endpoint present | 1.0 | health_check_endpoint is non-empty |
| Config overrides documented | 0.5 | env_vars table present (even if empty) |
| Auto-rollback flag set | 0.5 | auto_rollback: true or false (not missing) |
| Tags include deployment_manifest | 0.5 | tags contains "deployment_manifest" |
| tldr <= 160 chars | 0.5 | Concise summary |

Sum of weights: 5.0. `soft_score = sum(weight * gate_score) / 5.0 * 10`

## Actions
| Score | Action |
|-------|--------|
| >= 9.0 | PUBLISH -- safe for automated pipeline |
| >= 7.0 | REVIEW -- deploy with manual approval |
| < 7.0 | REJECT -- incomplete; do not deploy |

## Examples

# Examples: deployment_manifest

## Golden Example 1 -- CEX API Production Deploy
INPUT: "Deploy cex-api 2.1.0 and worker to production with rollback plan"
OUTPUT:
```yaml
---
id: p09_dm_cex_api_v210_prod
kind: deployment_manifest
pillar: P09
version: 1.0.0
created: "2026-04-17"
updated: "2026-04-17"
manifest_name: "CEX API v2.1.0 Production Deploy"
```
WHY THIS IS GOLDEN:
- Artifact checksums (SHA256) -- reproducible, tamper-evident
- Secrets as vault refs, not inline values (H04 security gate)
- Exact rollback_to version (not "previous")
- Config overrides table documents WHY each value differs from default

## Golden Example 2 -- SaaS Checkout Hotfix Deploy
INPUT: "Emergency hotfix for checkout service -- payment bug in 1.4.2, deploy 1.4.3 to production NOW"
OUTPUT:
```yaml
---
id: p09_dm_checkout_hotfix_v143
kind: deployment_manifest
pillar: P09
version: 1.0.0
created: "2026-04-18"
updated: "2026-04-18"
manifest_name: "Checkout Service Hotfix v1.4.3 -- Payment Bug Fix"
```
WHY THIS IS GOLDEN:
- deploy_type: hotfix encodes urgency context
- Skips 1.4.2 in rollback chain (explicitly notes bugged version)
- Revenue-alert integration (RevOps notification)
- 60s readiness timeout (tighter than standard 120s -- hotfix speed)

## Anti-Example 1: Inline Secret (REJECTED)
```yaml
# FAIL: plaintext credentials in manifest
DATABASE_URL: postgres://admin:SECRET123@prod-db.company.io/checkout
STRIPE_SECRET: sk_live_REAL_SECRET_KEY_HERE
image: checkout:latest  # FAIL: "latest" is non-reproducible
```
WHY REJECTED: Inline secrets in a deployment manifest will be committed to git, exposed in CI logs, and readable by anyone with repo access. Use vault paths or k8s secret refs. "latest" means each deploy may pull a different image -- breaks reproducibility and rollback.

## Anti-Example 2: Missing Rollback Target (REJECTED)
```yaml
target_env: production
artifacts:
  - name: api
    version: 3.0.0
# FAIL: no rollback_to
# FAIL: no health_check
# FAIL: no rollback trigger
rollback: true  # FAIL: "true" with no target or trigger is useless
```
WHY REJECTED: `rollback: true` with no `rollback_to`, no health check, and no trigger means the system knows rollback is desired but has zero information to execute it. On deploy failure, engineers must manually find the previous version, health check URL, and criteria -- all while the revenue impact clock is running.

### S_RELATED: Cross-Reference Check (SOFT)
- [ ] `related:` frontmatter field populated (3-15 entries)
- [ ] `## Related Artifacts` section present in artifact body
- [ ] At least 1 upstream and 1 downstream reference
- Penalty: -0.3 if empty (does not block, encourages wiring)
