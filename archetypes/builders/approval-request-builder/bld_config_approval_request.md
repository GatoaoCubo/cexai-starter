---
kind: config
id: bld_config_approval_request
pillar: P09
llm_function: CONSTRAIN
purpose: Naming conventions, file paths, size limits, operational constraints
pattern: CONFIG restricts SCHEMA, never contradicts it
effort: low
max_turns: 15
disallowed_tools: []
fork_context: null
hooks:
  pre_build: null
  post_build: null
  on_error: null
  on_quality_fail: null
permission_scope: nucleus
quality: null
title: "Config Approval Request"
version: "1.0.0"
author: n03_builder
tags: [approval_request, builder, config, P09]
tldr: "Naming, paths, size limits, and enum constraints for approval_request production: p11_ar_{name}.yaml, body <= 2048B, status/scope enums."
domain: "approval_request construction"
created: "2026-07-03"
updated: "2026-07-03"
8f: "F1_constrain"
keywords: [naming conventions, file paths, size limits, operational constraints, approval_request construction, config approval request, status scope enums, approval_request, builder, config]
density_score: 0.90
related:
  - bld_knowledge_card_approval_request
  - bld_instruction_approval_request
  - p10_lr_approval_request_builder
  - bld_config_hitl_config
  - bld_schema_approval_request
---
# Config: approval_request Production Rules
## Naming Convention
| Scope | Convention | Example |
|-------|-----------|---------|
| Artifact files | `p11_ar_{name}.yaml` (compiled); author `.md` | `p11_ar_prod_migration_deploy_0091.yaml` |
| Builder directory | kebab-case | `approval-request-builder/` |
| Frontmatter fields | snake_case | `request_id`, `emitting_policy` |
| Name slug | snake_case, lowercase, no hyphens | `content_review_0042`, `prod_migration_deploy_0091` |
| Requester identity | snake_case, nucleus/agent id | `n02_marketing`, `n05_operations` |
Rule: id MUST equal filename stem. Hyphens in id = HARD FAIL.
## File Paths
1. Output: `P11_feedback/examples/p11_ar_{name}.md`
2. Compiled: `P11_feedback/compiled/p11_ar_{name}.yaml`
3. FORBIDDEN: `.cexai/approvals/**` -- the live runtime watch-file path is Python-owned
   (`cexai.governance.hitl.file_gate.FileApprovalGate`); this builder NEVER writes there
## Size Limits (aligned with SCHEMA)
1. Body: max 2048 bytes -- SMALLER than hitl_config's 3072 (an instance is small; kinds_meta.json
   + `adr_v03_governance_taxonomy.md` both record this)
2. Total (frontmatter + body): ~3200 bytes
3. Density: >= 0.85 (no filler) -- with only 2048B of body budget, tables over prose is mandatory
## Enum Values (HARD constraints -- no other values accepted)
### status
| Value | Meaning | Terminal? |
|-------|---------|-----------|
| pending | Awaiting a human verdict | NO -- the only non-terminal state |
| approved | Human approved; operation proceeds | YES |
| denied | Human denied; step marked `denied_by_human` | YES |
| timeout | Deadline passed with no verdict; step marked `approval_timeout` | YES |
### scope (unique to this kind -- see bld_schema H07)
| Value | Meaning | Use When |
|-------|---------|---------|
| fixture | Authored fresh, no live watch file backs it | Demo tenant seed, regression-test fixture |
| audit_transcription | Copied from a real, already-resolved live watch file | Durable post-hoc audit record |
## M-of-N Policy Defaults
| Field | Default | Notes |
|-------|---------|-------|
| approvers_required | 1 | Omit from frontmatter when using the default (matches `ApprovalPolicy(1, 1)`) |
| approvers_total | 1 | Omit from frontmatter when using the default |
| approvers_roster | none | Only document when the real gate was configured with one (R-202) |
## Timeout Reference (informational -- mirrors the real gate's defaults)
| Context | Production default | Source |
|---------|--------------------|--------|
| `FileApprovalGate` deadline | 86400s (24h) | `cexai/cexai/governance/hitl/file_gate.py:114-116` |
| Poll interval (runtime only, never authored) | 1.0s | `cexai/cexai/governance/hitl/file_gate.py:118-120` |

## Metadata

```yaml
id: bld_config_approval_request
pipeline: 8F
scoring: hybrid_3_layer
```

```bash
python _tools/cex_score.py --apply bld-config-approval-request.md
```

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[bld_knowledge_card_approval_request]] | upstream | 0.36 |
| [[bld_instruction_approval_request]] | upstream | 0.36 |
| [[p10_lr_approval_request_builder]] | downstream | 0.33 |
| [[bld_config_hitl_config]] | sibling (emitting-policy config) | 0.33 |
| [[bld_schema_approval_request]] | sibling | 0.32 |
