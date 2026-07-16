---
quality: null
quality: null
id: p11_out_tpl_revision_loop_policy
kind: output_template
pillar: P05
llm_function: PRODUCE
purpose: P05 output shape for revision_loop_policy artifacts
title: "Output Template: Revision Loop Policy"
version: "1.0.0"
author: n03_builder
tags: [output_template, revision_loop_policy, builder, p05, p11]
domain: "revision_loop_policy construction"
created: "2026-04-18"
updated: "2026-04-18"
tldr: "P05 output shape for revision_loop_policy artifacts"
8f: "F6_produce"
keywords: [revision_loop_policy construction, output template, revision loop policy, output_template, revision_loop_policy, builder, ### body (required sections), output shape

every, revision policy, revision loop behavior]
density_score: 0.89
related:
 - rlp_{{name}}
 - revision-loop-policy-builder
 - n00_revision_loop_policy_manifest
 - p11_ins_revision_loop_policy
 - kc_revision_loop_policy
---
## Output Shape

Every `revision_loop_policy` artifact must follow this exact structure:

### Frontmatter (required)

```yaml
---
id: rlp_{{name}}
kind: revision_loop_policy
pillar: P11
title: "Revision Policy: {{name}}"
max_iterations: {{max_iterations}}
iteration_on_quality_floor: {{quality_floor}}
priority_order: [security, quality, implementation]
escalation_target: {{escalation_target}}
escalation_message_template: "Reached {{max_iterations}} revisions without passing gates: {{failing_gates}}"
per_scenario_overrides:
 security_critical: 5
 documentation: 2
version: 1.0.0
quality: null
tags: [hermes_origin, revision, escalation, policy]
---
```

### Body (required sections)

```markdown
## Policy: {{name}}

### Revision Loop Behavior

| Parameter | Value | Notes |
|-----------|-------|-------|
| Max iterations | {{max_iterations}} | {{rationale}} |
| Quality floor | {{quality_floor}} | Trigger revision if score below this |
| Priority | security > quality > implementation | Conflict resolution order |
| Escalation | {{escalation_target}} | After max_iterations exhausted |

### Scenario Overrides

| Scenario | Max Iterations | Rationale |
|----------|---------------|-----------|
| security_critical | 5 | Extra cycles for security-sensitive artifacts |
| documentation | 2 | Docs rarely need >2 revision cycles |
| {{custom_scenario}} | {{n}} | {{rationale}} |

### Escalation Protocol

1. Evaluate all quality gates for iteration N
2. IF all gates pass OR score >= {{quality_floor}}: ACCEPT artifact, stop loop
3. IF attempt < {{max_iterations}}: increment attempt, regenerate with gate failure context
4. IF attempt == {{max_iterations}}: emit escalation message, route to {{escalation_target}}

### Boundaries

- NOT `retry_policy` (P09): retry_policy handles transient failures (network, timeout)
- NOT `quality_gate` (P11): quality_gate is a single check; this orchestrates N of them
- NOT `regression_check` (P11): regression_check diffs against a baseline
- NOT `bugloop` (P11): bugloop is code-bug auto-correction, not content quality iteration

### Usage in pipeline_template

```yaml
revision_loop:
 policy_ref: rlp_{{name}}
 max_iterations: `{{max_iterations}}`
 escalation_target: `{{escalation_target}}`
```
```

## Variable Reference

| Variable | Type | Source |
|----------|------|--------|
| `{{name}}` | string | Policy slug (e.g., `standard`, `security_critical`) |
| `{{max_iterations}}` | int | From input or scenario default |
| `{{quality_floor}}` | float | Default 8.5, override per config |
| `{{escalation_target}}` | enum | user / senior_nucleus / freeze |
| `{{rationale}}` | string | Why this iteration count for this scenario |

## Size Budget
- Target: 800-1500 bytes
- Maximum: 2048 bytes
- Density target: >= 0.85 (structured content preferred)
- Naming: `p11_rlp_{{name}}.yaml` (H02 enforces pattern match)
- Required tag: `hermes_origin` (provenance marker for OpenCode-Hermes-derived policies)
- `per_scenario_overrides` block is required; minimum keys: security_critical, documentation
- `escalation_message_template` must use both `{{max_iterations}}` and `{{failing_gates}}` tokens
- `priority_order` field is non-negotiable: always [security, quality, implementation] in that exact order
- Artifacts using `freeze` escalation must include rationale comment in the body usage block

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[rlp_{{name}}]] | downstream | 0.64 |
| [[revision-loop-policy-builder]] | downstream | 0.57 |
| [[n00_revision_loop_policy_manifest]] | downstream | 0.53 |
| [[p11_ins_revision_loop_policy]] | downstream | 0.53 |
| [[kc_revision_loop_policy]] | upstream | 0.51 |
