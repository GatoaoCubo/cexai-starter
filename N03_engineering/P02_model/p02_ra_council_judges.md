---
id: p02_ra_council_judges
kind: role_assignment
pillar: P02
title: "Council Judge Role Assignments"
version: 1.1.0
created: 2026-04-27
quality: null
density_score: 0.90
tags: [role_assignment, council, judges, multi_provider, become]
tldr: "Binds 4 judge roles (Claude/Gemini/GPT/Ollama) to provider-overridden judge_config instances -- so the cross-provider council scores one artifact 4 ways under the same rubric to surface divergence."
when_to_use: "Load (F2 BECOME) when instantiating the cross-provider council. Consult for 'which judge roles exist, what provider each uses, and why each is in the panel?'"
primary_8f: BECOME
related:
  - p12_ct_cross_provider_council
  - judge-config-builder
  - scoring-rubric-builder
---

## Overview

Binds 4 judge roles to specific provider-overridden `judge_config` instances
for use by the [[p12_ct_cross_provider_council]] crew_template.
Each role evaluates the same artifact independently using the same
`scoring_rubric`, differing only in the LLM provider.

### How to use

```text
8F verb: BECOME (F2). The crew planner reads these bindings to spawn one judge per
provider. Each judge adopts its role_name + provider_override, reads the shared
scoring_rubric + artifact, and scores in isolation (no role sees another's output).
To add a provider, copy a Role Binding and fill the slots below.
```

```yaml
role_name: {{role_name}}                  # e.g. judge_gemini
agent_id: {{agent_id}}                    # the generic llm_judge agent
provider_override: {{provider_override}}  # claude | gemini | gpt | ollama
goal: {{goal}}                            # score artifact against the rubric
delegation: {{delegation}}                # false -- judges never delegate
```

## Role Bindings

### judge_claude

| Field | Value |
|-------|-------|
| role_name | judge_claude |
| agent_id | llm_judge (generic) |
| provider_override | claude |
| goal | Score artifact against rubric using Claude reasoning |
| backstory | Primary cloud model. High reasoning capability. Potential self-bias on Claude-generated artifacts -- council mitigates this. |
| tools | scoring_rubric (read), artifact (read), judge_config (read) |
| delegation | false |

### judge_gemini

| Field | Value |
|-------|-------|
| role_name | judge_gemini |
| agent_id | llm_judge (generic) |
| provider_override | gemini |
| goal | Score artifact against rubric using Gemini reasoning |
| backstory | Cross-family diversity. Different training corpus and alignment approach. Detects patterns Claude may normalize. |
| tools | scoring_rubric (read), artifact (read), judge_config (read) |
| delegation | false |

### judge_gpt

| Field | Value |
|-------|-------|
| role_name | judge_gpt |
| agent_id | llm_judge (generic) |
| provider_override | gpt |
| goal | Score artifact against rubric using GPT reasoning |
| backstory | Independent alignment family. Strongest on factual verification and citation checking. |
| tools | scoring_rubric (read), artifact (read), judge_config (read) |
| delegation | false |

### judge_ollama

| Field | Value |
|-------|-------|
| role_name | judge_ollama |
| agent_id | llm_judge (generic) |
| provider_override | ollama |
| goal | Score artifact against rubric using local model reasoning |
| backstory | Local execution. No API dependency. Different model scale provides calibration anchor -- if a small model also scores high, the artifact is likely strong. |
| tools | scoring_rubric (read), artifact (read), judge_config (read) |
| delegation | false |

## Shared Configuration

All 4 roles share:
- **scoring_rubric**: passed via crew charter at instantiation
- **scoring_scale**: inherited from rubric (typically 1-10)
- **judge_type**: `rubric` (direct scoring against anchored descriptors)
- **isolation**: mandatory -- no role sees another role's output

## Related Artifacts

| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[p12_ct_cross_provider_council]] | parent | 0.90 |
| [[judge-config-builder]] | upstream | 0.60 |
| [[scoring-rubric-builder]] | upstream | 0.55 |
| [[p12_ct_product_launch]] | sibling_pattern | 0.40 |
