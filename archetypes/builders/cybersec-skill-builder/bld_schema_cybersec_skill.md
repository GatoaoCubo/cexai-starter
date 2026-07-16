---
kind: schema
id: bld_schema_cybersec_skill
pillar: P06
llm_function: CONSTRAIN
purpose: Formal schema -- SINGLE SOURCE OF TRUTH for cybersec_skill (source-traced, framework-mapped, anti-fabrication-gated)
pattern: TEMPLATE derives from this. CONFIG restricts this. EVAL enforces this.
quality: null
title: "Schema Cybersec Skill"
version: "1.0.0"
author: n03_builder
tags: [cybersec_skill, builder, schema, source-trace, anti-fabrication, P06, mukul975]
tldr: "Schema for cybersec_skill: skill kind extended with mandatory source: trace, framework mapping (T-codes/CSF/ATLAS), authorized_use_only gating, and 4 anti-fabrication HARD gates."
domain: "cybersec_skill construction"
created: "2026-05-30"
updated: "2026-05-30"
8f: "F1_constrain"
keywords: [cybersec_skill, schema, source frontmatter, frameworks, authorized_use_only, audit_log_mandatory, capability_registry, disclaimer, anti-fabrication]
density_score: 0.90
related:
  - bld_schema_skill
  - bld_schema_safety_policy
  - bld_schema_ai_rmf_profile
  - bld_schema_guardrail
---

# Schema: cybersec_skill

## Inheritance

Inherits 100% of `skill` schema (see `bld_schema_skill.md`) and ADDS 6 cybersec-mandatory frontmatter fields + 4 anti-fabrication HARD gates. Conflicting fields take cybersec-schema precedence.

## Frontmatter Fields

### Inherited from skill (all required unchanged)

`id`, `kind`, `pillar`, `version`, `created`, `updated`, `author`, `name`,
`description`, `user_invocable`, `trigger`, `phases`, `when_to_use`,
`when_not_to_use`, `examples`, `quality`, `tags`, `tldr`, `domain`.

### Cybersec-specific (MANDATORY)

| Field | Type | Required | Default | Notes |
|-------|------|----------|---------|-------|
| source | string (path) | YES | -- | Apache 2.0 trace to baseline skill (mukul975 or other) -- path MUST exist on disk |
| frameworks | list[string] | YES if applicable | [] | Framework codes: MITRE ATT&CK T-codes, NIST CSF controls, MITRE ATLAS techniques, CVE IDs |
| authorized_use_only | boolean | YES | false | true = offensive / dual-use; gates downstream tools via capability_registry |
| audit_log_mandatory | boolean | YES | false | true = every invocation must emit audit_log entry (paired with authorized_use_only) |
| capability_registry | string (skill_id) | YES if authorized_use_only=true | null | Reference to `capability_registry` artifact granting this skill's principal |
| disclaimer | string (path) | YES if authorized_use_only=true | null | Reference to `_docs/cybersec_disclaimer_canon.md` or equivalent legal canon |

### Cybersec-specific (OPTIONAL)

| Field | Type | Notes |
|-------|------|-------|
| domain_subtype | string | One of: ai_security, cloud, dfir, appsec, netsec, identity |
| severity | string | low / medium / high / critical (per CVSS or domain convention) |
| privilege_required | string | none / user / admin / root (for offensive only) |
| detection_signatures | list[string] | Pointers to Sigma/Yara/Snort rule files if defensive |
| safe_mode_default | boolean | true = dry-run by default (offensive only) |

## ID Pattern

Regex: `^p03_cysk_[a-z][a-z0-9_]+$`

Rule: id MUST equal filename stem. `cysk` = cybersec_skill (4-char abbrev consistent with `sp` / `rmf` / `cfw` pillar-P11 codes).

## Body Structure (required sections, inherited + extended)

1. `## Purpose` (from skill) -- WHY this cybersec capability exists vs. raw mukul975 source
2. `## Source Provenance` (NEW) -- Apache 2.0 attribution + commit SHA of source + license file path
3. `## Framework Mapping` (NEW) -- table mapping every cited T-code / CVE / CSF control to source `references/standards.md` line
4. `## Workflow Phases` (from skill) -- one `###` per phase with Input / Action / Output
5. `## Anti-Fabrication Checklist` (NEW) -- author self-attests H_AF1..H_AF4 before commit
6. `## Authorization Notice` (NEW, only if `authorized_use_only=true`) -- explicit capability boundary + disclaimer pointer
7. `## Anti-Patterns` (from skill) -- includes cybersec-specific: "do not cite T-codes absent from source"
8. `## Metrics` (from skill)

## Constraints

- max_bytes: 5120 (body only)
- naming: `p03_cysk_{name}.md` + `.yaml`
- machine_format: yaml (frontmatter) + markdown (body)
- id == filename stem
- `source:` path MUST exist on disk (H_AF4)
- every T-code / CVE / framework control cited in body MUST appear in `{source}/references/standards.md` (H_AF1, H_AF2, H_AF3)
- if `authorized_use_only=true` then both `capability_registry` and `disclaimer` MUST be non-null
- if `audit_log_mandatory=true` then the skill body MUST reference an `audit_log` kind artifact in `## Authorization Notice`
- `quality: null` always (per CEX universal H05)
- ASCII-only in code blocks (body prose may use UTF-8 per CEX convention)

## Anti-Fabrication HARD Gates (enforced by bld_eval)

| Gate | Check | Source |
|------|-------|--------|
| H_AF1 | every `T<digits>(.<digits>)?` cited in body appears verbatim in `{source}/references/standards.md` | MITRE ATT&CK |
| H_AF2 | every `CVE-\d{4}-\d+` cited in body appears verbatim in `{source}/references/standards.md` | NVD / MITRE |
| H_AF3 | every framework control id (e.g. `PR.AC-1`, `AML.T0051`) cited in body appears verbatim in `{source}/references/standards.md` | NIST CSF / ATLAS |
| H_AF4 | `source:` frontmatter path MUST exist on disk (filesystem check) | provenance |

A single AF gate failure = REJECT regardless of structural score. This is the core integrity contract; without it the distillation is unfalsifiable claim-laundering.

## Related Artifacts

| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[bld_schema_skill]] | parent | 0.90 |
| [[bld_schema_safety_policy]] | sibling | 0.62 |
| [[bld_schema_ai_rmf_profile]] | sibling | 0.58 |
| [[bld_schema_guardrail]] | sibling | 0.55 |
