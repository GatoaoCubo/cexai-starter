---
id: p11_fb_approval_request
kind: builder_default
pillar: P11
title: "Feedback: Approval Request"
domain: approval_request
quality: null
tags: [feedback, anti-patterns, P11, approval_request]
tldr: "Approval Request feedback: anti-patterns, regression signals, and quality improvement triggers"
8f: "F7_govern"
keywords: [approval request, approval request feedback, regression signals, quality improvement triggers, feedback, anti-patterns, approval_request, common failure modes, correction protocol, key behaviors]
density_score: 1.0
updated: "2026-07-03"
related:
  - p11_fb_hitl_config
  - p11_fb_permission
  - p11_fb_incident_report
  - p10_lr_approval_request_builder
  - adr_v03_governance_taxonomy
---
# Feedback: Approval Request

## Anti-Patterns (NEVER do)

- **No self-score**: never assign quality score to your own output
- **No hallucination**: cite sources; do not invent facts, metrics, or references
- **No live-file impersonation**: never claim this artifact IS, or write to, the live runtime
  watch file at `.cexai/approvals/{request_id}.json`
- **No missing scope disclaimer**: every instance MUST declare `scope: fixture` or
  `scope: audit_transcription` -- an undisclosed instance risks being read as a real pending gate
- **No mutated terminal state**: `approved`/`denied`/`timeout` are final in the real mechanism;
  never hand-edit a terminal instance's status in place -- author a new instance instead
- **ASCII-only code**: no emoji, no accented chars in .py/.ps1/.sh output
- **No partial output**: produce complete artifact; no truncation, no "..." placeholders
- **No frontmatter omission**: every artifact must start with valid YAML frontmatter
- **No quality below 8.0**: re-draft before publishing if self-assessment < 8.0

## Common Failure Modes for Approval Request

- Conflating this kind with `hitl_config` (the durable policy) -- describing WHAT gets gated in
  general, rather than ONE specific gated event
- Vague or missing `operation` string that cannot be traced to an emitting `hitl_config`'s
  `review_trigger`
- Missing required frontmatter fields (id, kind, pillar, request_id, operation, requester,
  expires_at, status, scope)
- Body prose only -- no tables, no structured data (density < 0.85), especially costly here given
  the tight 2048-byte body budget
- Output not matching the output template schema
- Treating M-of-N fields as always-required (they are optional; omit for the 1-of-1 default)

## Correction Protocol

1. Identify which H01-H07 gate failed
2. Return to F6 PRODUCE with explicit fix instruction
3. Re-run F7 GOVERN
4. Maximum 2 retries before escalating to N07

## Key Behaviors

- Builder MUST load all 12 ISOs (1:1 with pillars) before producing any artifact
- Builder MUST run F7 GOVERN quality gate before saving output
- Builder MUST compile output via cex_compile.py after saving (F8 COLLABORATE)
- Builder MUST signal completion with quality score to N07 orchestrator
- Builder MUST NOT self-score: quality field is always null in own output
- Builder MUST NOT write to `.cexai/approvals/**` under any circumstance

## Quality Thresholds

| Dimension | Weight | Target | Gate |
|-----------|--------|--------|------|
| Structural completeness | 30% | >= 8.0 | L1 |
| Rubric compliance | 30% | >= 8.0 | L2 |
| Semantic coherence | 40% | >= 8.5 | L3 |
| Density score | -- | >= 0.85 | S09 |
| Tables present | -- | >= 1 | S05 |

## Gate Check

```bash
python _tools/cex_score.py {FILE} --layer structural
python _tools/cex_score.py {FILE} --layer rubric
```

```yaml
# Expected output structure
structural: 8.5+
rubric: 7.5+
average: 8.0+
gates_passed: 7/7
density: 0.85+
```

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[p11_fb_hitl_config]] | sibling (emitting-policy builder's feedback) | 0.78 |
| [[p11_fb_permission]] | sibling (contrast: standing grant) | 0.74 |
| [[p11_fb_incident_report]] | sibling (contrast: post-mortem) | 0.72 |
| [[p10_lr_approval_request_builder]] | sibling | 0.68 |
| [[adr_v03_governance_taxonomy]] | related (scope-defining ADR) | 0.40 |
