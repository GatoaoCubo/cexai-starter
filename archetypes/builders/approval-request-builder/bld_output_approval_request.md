---
kind: output_template
id: bld_output_template_approval_request
pillar: P05
llm_function: PRODUCE
purpose: Template with {{vars}} that the LLM fills to produce an approval_request artifact
pattern: every field here exists in SCHEMA.md -- template derives, never invents
quality: null
title: "Output Template Approval Request"
version: "1.0.0"
author: n03_builder
tags:
  - "approval_request"
  - "builder"
  - "output_template"
  - "P11"
tldr: "Fill-in template for approval_request: frontmatter + 4 body sections covering request detail, approval context, lifecycle, and scope disclaimer."
domain: "approval_request construction"
created: "2026-07-03"
updated: "2026-07-03"
8f: "F6_produce"
keywords:
  - "template with"
  - "approval_request construction"
  - "output template approval request"
  - "fill-in template for approval_request"
  - "body sections covering request detail"
  - "approval_request"
  - "builder"
  - "output_template"
  - "## overview"
  - "## request detail"
density_score: 0.90
related:
  - bld_schema_approval_request
  - bld_architecture_approval_request
---
# Output Template: approval_request
```yaml
id: p11_ar_{{name}}
kind: approval_request
pillar: P11
version: "1.0.0"
created: "{{YYYY-MM-DD}}"
updated: "{{YYYY-MM-DD}}"
author: "{{who_produced}}"
request_id: "{{appr-hex12_or_same_slug_as_id_if_fresh_fixture}}"
operation: "{{gated_action_e.g._publish_to_social_media}}"
requester: "{{nucleus_or_agent_that_attempted_it}}"
expires_at: "{{ISO-8601_deadline}}"
status: "{{pending|approved|denied|timeout}}"
emitting_policy: "{{hitl_config_id_that_would_emit_this_or_omit}}"
quality: null
tags: [approval_request, {{tag_2}}, {{tag_3}}]
tldr: "{{dense_summary_max_160ch}}"
description: "{{what_operation_and_why_it_was_gated_max_200ch}}"
scope: "{{fixture|audit_transcription}}"
approvers_required: {{integer_or_omit_if_1of1_default}}
approvers_total: {{integer_or_omit_if_1of1_default}}
```
## Overview
`{{which_operation_is_gated_1_sentence}}`
`{{why_human_judgment_was_required_1_sentence}}`
`{{who_requested_it_and_who_or_what_consumes_the_verdict}}`
## Request Detail
| Field | Value |
|-------|-------|
| request_id | `{{request_id}}` |
| operation | `{{operation}}` |
| requester | `{{requester}}` |
| expires_at | `{{expires_at}}` |
| status | `{{pending|approved|denied|timeout}}` |
## Approval Context
Emitting policy: `{{hitl_config_id}}` (workflow: `{{workflow_name}}`).
| Field | Value | Notes |
|-------|-------|-------|
| approvers_required (M) | `{{integer}}` | Omit table if 1-of-1 default |
| approvers_total (N) | `{{integer}}` | |
| recorded verdicts | `{{approver: verdict, ... or "none yet"}}` | Only for resolved/terminal instances |
## Lifecycle
Current state: **`{{pending|approved|denied|timeout}}`**.
| Transition | Downstream Effect |
|-----------|-------------------|
| -> approved | `{{operation_proceeds}}` |
| -> denied | Step marked `denied_by_human` |
| -> timeout | Step marked `approval_timeout` |
## Scope Disclaimer
This artifact is a **`{{fixture|audit_transcription}}`**. It is NOT the live runtime watch file
(`.cexai/approvals/{{request_id}}.json`), which is owned exclusively by
`cexai.governance.hitl.file_gate.FileApprovalGate`. `{{if_audit_transcription: "Transcribed from
the live watch file on {{date}}; fields verified to match exactly." | if_fixture: "Authored fresh
for {{test|demo|seed}} purposes; no live watch file backs this instance."}}`
## References
- `{{reference_1_e.g._the_emitting_hitl_config_artifact_path}}`
- `{{reference_2_e.g._the_live_watch_file_path_if_audit_transcription}}`

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[bld_schema_approval_request]] | downstream | 0.39 |
| [[bld_architecture_approval_request]] | downstream | 0.34 |
