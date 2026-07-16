---
kind: config
id: bld_config_cybersec_skill
pillar: P09
llm_function: CONSTRAIN
purpose: Naming conventions, file paths, size limits, operational constraints
pattern: CONFIG restricts SCHEMA, never contradicts it
effort: medium
max_turns: 25
disallowed_tools: [network_egress, live_exploit_execution]
permission_scope: pillar
quality: null
title: "Config Cybersec Skill"
version: "1.0.0"
author: n03_builder
tags: [cybersec_skill, builder, config, naming, size-limits, capability-gating]
tldr: "Operational config for cybersec_skill: naming (p03_cysk_{name}), file paths (N05 ownership), size limits (5120B body), framework code regex patterns, capability-gating rules."
domain: "cybersec_skill construction"
created: "2026-05-30"
updated: "2026-05-30"
8f: "F1_constrain"
keywords: [cybersec_skill config, naming convention, file paths, size limits, framework regex, capability gating, authorized_use_only rules]
density_score: 0.90
related:
  - bld_config_skill
  - bld_schema_cybersec_skill
  - cybersec-skill-builder
  - bld_architecture_cybersec_skill
  - p11_qg_cybersec_skill
---

# Config: cybersec_skill Production Rules

## Naming Convention

| Scope | Convention | Example |
|-------|-----------|---------|
| Artifact files | `p03_cysk_{name}.md` | `p03_cysk_detecting_prompt_injection.md` |
| Compiled YAML | `p03_cysk_{name}.yaml` | `p03_cysk_detecting_prompt_injection.yaml` |
| Builder directory | kebab-case | `cybersec-skill-builder/` |
| Frontmatter fields | snake_case | `authorized_use_only`, `audit_log_mandatory` |
| Skill name slug | snake_case, lowercase, kebab-equivalent of baseline | `detecting_prompt_injection` (from `detecting-prompt-injection`) |
| Trigger | `/cysk_<name>` slash command | `/cysk_aws_cloudtrail_baseline` |

Rule: id MUST equal filename stem.
Rule: trigger slug matches filename slug (`p03_cysk_X.md` -> `/cysk_X`).

## File Paths

- Source (read-only): `_inbox/mukul975/skills/{baseline_name}/` (or operator-defined baseline mount)
- Output: `N05_operations/P03_prompt/cybersec_skills/p03_cysk_{name}.md`
- Compiled: `N05_operations/P03_prompt/compiled/p03_cysk_{name}.yaml`
- Capability registry (if offensive): `N05_operations/P11_feedback/capability_registry/p11_cr_{name}.md`
- Disclaimer canon: `_docs/cybersec_disclaimer_canon.md`
- Audit log emission: `_runtime/audit/cysk_{name}_<ISO_timestamp>.jsonl`

## Size Limits (aligned with SCHEMA)

- Body: max 5120 bytes
- Total (frontmatter + body): ~7000 bytes (cybersec frontmatter adds ~800B)
- Density: >= 0.85

## Phase Count

| Count | Status | Notes |
|-------|--------|-------|
| 1 | INVALID | Single-phase is an action_prompt, not a cybersec_skill |
| 2 | MINIMAL | Acceptable for terse detection skills |
| 3-4 | CANONICAL | discover + map + execute + audit |
| 5-6 | EXTENDED | Valid for multi-stage forensic / response workflows |
| 7+ | REJECT | Split into sub_skills |

## Framework Code Regex (used by AF gates)

| Framework | Regex | Match Example |
|-----------|-------|---------------|
| MITRE ATT&CK | `T[0-9]+(\.[0-9]+)?` | T1059, T1059.001 |
| MITRE ATLAS | `AML\.T[0-9]+` | AML.T0051 |
| NIST CSF | `[A-Z]{2}\.[A-Z][A-Z]?-?[0-9]+` | PR.AC-1, ID.AM-3 |
| CVE-MITRE | `CVE-[0-9]{4}-[0-9]+` | CVE-2024-12345 |

The 4 regexes are the canonical extraction patterns used by `bld_eval_cybersec_skill.md`
H_AF1-H_AF3 grep blocks. Do not edit these without updating the eval ISO.

## Capability Gating Rules

| Situation | Required Fields | Required Body |
|-----------|----------------|----------------|
| `authorized_use_only=false` (defensive) | none extra | optional `## Authorization Notice` |
| `authorized_use_only=true` (offensive / dual-use) | `capability_registry` + `disclaimer` + `audit_log_mandatory=true` | mandatory `## Authorization Notice` |
| Severity = critical AND defensive | `severity: critical` | recommend `detection_signatures` list |
| Severity = critical AND offensive | All above + `safe_mode_default: true` | mandatory `## Authorization Notice` + invocation-time confirmation |

## Boolean Field Rules

- `user_invocable: true` ONLY when trigger starts with `/cysk_`
- `authorized_use_only=true` REQUIRES `audit_log_mandatory=true`
- `audit_log_mandatory=true` may be standalone (defensive skills may opt in)
- `safe_mode_default: true` REQUIRED when `authorized_use_only=true` AND `severity=critical`

## Body Section Requirements

- `## Purpose`: 2-4 sentences, must state distillation rationale vs. raw baseline
- `## Source Provenance`: 4 facts (path / license / commit SHA / attribution)
- `## Framework Mapping`: every `frameworks:` entry rows here
- `## Workflow Phases`: one `###` per phase with typed Input / Action / Output
- `## Anti-Fabrication Checklist`: author checks all 4 boxes pre-commit
- `## Authorization Notice`: only if `authorized_use_only=true`
- `## Anti-Patterns`: >= 3 named failures with avoidance
- `## Metrics`: >= 2 measurable success criteria

## Operational Constraints

- Manual invocation only (Q10 LOCKED U1 manual sync; no CI hooks)
- Single artifact per skill (Q1 LOCKED no bundles)
- Silent-absorb attribution preserved (Q5 LOCKED `source:` mandatory)
- No automated promotion to public registry without N07 approval
- Capability gating enforced before downstream consumption (Q3 LOCKED)

## Related Artifacts

| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[bld_config_skill]] | parent | 0.65 |
| [[bld_schema_cybersec_skill]] | upstream | 0.62 |
| [[cybersec-skill-builder]] | upstream | 0.58 |
| [[bld_architecture_cybersec_skill]] | upstream | 0.55 |
| [[p11_qg_cybersec_skill]] | downstream | 0.55 |
