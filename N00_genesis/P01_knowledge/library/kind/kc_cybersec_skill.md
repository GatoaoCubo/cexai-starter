---
id: p01_kc_cybersec_skill
kind: knowledge_card
8f: F3_inject
type: kind
pillar: P03
title: "Cybersec Skill -- Deep Knowledge for cybersec_skill"
version: 1.0.0
created: 2026-05-30
updated: 2026-05-30
author: n03_builder
domain: cybersec_skill
quality: null
tags: [cybersec_skill, p03, n05, mukul975, source-trace, anti-fabrication, gating-wrath, kind-kc]
tldr: "Cybersec-domain reusable capability distilled from external baselines (mukul975 Apache 2.0 lead) with mandatory source: trace, framework mapping (ATT&CK / ATLAS / CSF / CVE), and capability gating for offensive variants."
when_to_use: "Building, reviewing, or reasoning about cybersec_skill artifacts -- defensive detection skills, capability-gated offensive skills, or framework-mapped audit skills"
keywords: [cybersec_skill, ATT&CK, ATLAS, CSF, CVE, mukul975, silent-absorb, anti-fabrication, capability gating, audit_log, distillation]
feeds_kinds: [cybersec_skill]
density_score: null
related:
  - p01_kc_skill
  - kc_safety_policy
  - kc_ai_rmf_profile
  - kc_guardrail
  - cybersec-skill-builder
---

# Cybersec Skill

## Spec

```yaml
kind: cybersec_skill
pillar: P03
nucleus_owner: n05
llm_function: BECOME
max_bytes: 5120
naming: p03_cysk_{{name}}.md + .yaml
core: false
depends_on: [skill, safety_policy, guardrail, compliance_framework]
requires_external_context: true
requires_live_tools: false
primary_8f: F2_become
parent: skill (P04)
```

## What It Is

A cybersec_skill is a reusable cybersec capability distilled from an external Apache 2.0
baseline (canonically mukul975/security-skills) with: (1) mandatory `source:` frontmatter
trace, (2) framework mapping table (MITRE ATT&CK T-codes / NIST CSF controls / MITRE ATLAS
techniques / CVE-MITRE IDs), and (3) capability gating (`authorized_use_only` +
`capability_registry` + `disclaimer` + `audit_log_mandatory`) for offensive variants.

It inherits ALL `skill` semantics (trigger, phases, typed I/O, when_to_use / when_not_to_use)
and ADDS the cybersec-integrity contract enforced via 4 anti-fabrication HARD gates
(H_AF1-H_AF4) at F7 GOVERN.

Cybersec_skill exists to enable the silent-absorb model: lift external cybersec corpora
WITHOUT the integrity rot that comes from re-typed citations. Every cited code traces to
source via grep, or it is OMITTED.

## Cross-Framework Map

| Framework/Provider | Class/Concept | Notes |
|-------------------|---------------|-------|
| Claude Code | bundled skill (markdown + frontmatter) | mukul975 baseline shape; 1:1 lift |
| MITRE ATT&CK | Technique IDs (T<digits>) | Adversary technique enumeration |
| MITRE ATLAS | Technique IDs (AML.T<digits>) | AI/ML-adversarial techniques |
| NIST CSF | Control IDs (ID.AM-1, PR.AC-1, etc.) | Cybersecurity Framework controls |
| CVE-MITRE | CVE-<year>-<id> | Vulnerability identifiers |
| Sigma | Sigma rule files (optional pointer) | Detection signature crosswalk |
| OpenC2 | Action / target / actuator | Future crosswalk target |

## Key Parameters

| Parameter | Type | Default | Tradeoff |
|-----------|------|---------|----------|
| source | string (path) | required | Apache 2.0 trace; no source = no skill |
| frameworks | list[string] | [] | More codes = more crosswalk, more AF gate surface |
| authorized_use_only | bool | false | true = offensive; gates downstream tools + audit |
| audit_log_mandatory | bool | false | true paired with authorized_use_only (forced) |
| capability_registry | skill_id | null | required if authorized_use_only=true |
| disclaimer | path | null | required if authorized_use_only=true |
| domain_subtype | enum | required | One of: ai_security, cloud, dfir, appsec, netsec, identity |
| severity | enum | optional | low / medium / high / critical |
| safe_mode_default | bool | true (for offensive) | Dry-run by default reduces accidental harm |

## Domain Subtypes

| Subtype | Scope | Typical authorized_use_only |
|---------|-------|----------------------------|
| ai_security | LLM / agent security | false (defensive) / true (red-team) |
| cloud | AWS / GCP / Azure baselines | false (audit) / true (lateral move) |
| dfir | Forensics + incident response | false (analysis) |
| appsec | Application security | false (audit) / true (exploit) |
| netsec | Network security | false (detection) |
| identity | IAM, SSO, credentials | false (audit) / true (priv-esc) |

## Anti-Fabrication Lattice (4 HARD gates)

| Gate | Check | Failure |
|------|-------|---------|
| H_AF1 | T-codes in body grep-verifiable in `{source}/references/standards.md` | REJECT |
| H_AF2 | CVE IDs in body grep-verifiable in source | REJECT |
| H_AF3 | Framework control IDs (CSF, ATLAS) in body grep-verifiable in source | REJECT |
| H_AF4 | `source:` path exists on disk at F8 | REJECT |

These are NOT scored at SOFT layer -- single failure = artifact REJECT. The lattice IS the
integrity contract; without it the distillation is unfalsifiable claim-laundering.

## Capability Gating Contract

| When | Required |
|------|---------|
| authorized_use_only=true | capability_registry skill_id (H_CG1) |
| authorized_use_only=true | disclaimer path (H_CG2) |
| authorized_use_only=true | audit_log_mandatory=true (H_CG3) |
| authorized_use_only=true | `## Authorization Notice` body section (H_CG4) |

## Quality Gates Summary

| Gate Layer | Count | Type |
|-----------|-------|------|
| H01-H06 | 6 | Universal CEX hard gates |
| H_AF1-H_AF4 | 4 | Cybersec anti-fabrication hard gates |
| H_CG1-H_CG4 | 4 | Capability-gating hard gates (conditional) |
| SOFT rubric | 6 dimensions | Weighted scoring |
| Density | 1 | >= 0.85 target |

## Usage Examples

```yaml
# Defensive ai_security skill (no capability gate)
id: p03_cysk_detecting_prompt_injection
kind: cybersec_skill
source: "_inbox/mukul975/skills/detecting-prompt-injection/"
frameworks: [AML.T0051, AML.T0054]
authorized_use_only: false
audit_log_mandatory: false
domain_subtype: ai_security
trigger: /cysk_detecting_prompt_injection

# Offensive cybersec skill (full capability gate)
id: p03_cysk_aws_priv_escalation_chain
kind: cybersec_skill
source: "_inbox/redteam/skills/aws-priv-esc-chain/"
frameworks: [T1078.004, T1098]
authorized_use_only: true
audit_log_mandatory: true
capability_registry: "p11_cr_aws_offensive_principal"
disclaimer: "_docs/cybersec_disclaimer_canon.md"
safe_mode_default: true
domain_subtype: cloud
severity: high
```

## Anti-Patterns

| Anti-Pattern | Why Wrong | Correct Approach |
|--------------|-----------|------------------|
| Cite T-code from memory | Unverifiable, fabrication | grep source first; OMIT if absent |
| Drop source: "because obvious" | Breaks H_AF4 + license trace | Always keep source: |
| Offensive without capability_registry | Q3 LOCKED gate violated | Build capability_registry first |
| Paraphrase framework description | Breaks downstream crosswalks | Verbatim or omit |
| Bundle related cybersec skills | Q1 LOCKED no bundles | One artifact per skill |
| Add CI auto-distill hook | Q10 LOCKED U1 manual | Manual invocation only |

## Distinction Table

| cybersec_skill IS | cybersec_skill IS NOT |
|-------------------|-----------------------|
| Distilled from baseline with attribution | Original authorship (use `skill`) |
| Framework-mapped (source-traced) | Free-form prose |
| Capability-gated when offensive | Unfettered offensive tooling (use mcp_server + RBAC) |
| Phased reusable capability | One-shot exploit (use cli_tool + sandbox_spec) |
| Source-trace verified | Memory-cited |
| Single-file artifact | Bundled (Q1 LOCKED) |
| Manually invoked | CI-automated (Q10 LOCKED) |

## Integration Points

- **F1 CONSTRAIN**: schema enforces source: + frameworks + capability_registry rules
- **F2 BECOME**: cybersec-skill-builder identity (Gating Wrath sin lens, N05 owner)
- **F3 INJECT**: load baseline corpus pointer + decision_manifest locks
- **F5 CALL**: grep tools for AF verification
- **F6 PRODUCE**: 8 body sections per output template
- **F7 GOVERN**: 4 AF gates + 4 CG gates (conditional) + 6 universal gates
- **F8 COLLABORATE**: per-skill commit pattern + signal to N05 capability_registry-builder

## Production Reference (mukul975 baseline)

| Skill | Domain | authorized_use_only | Frameworks |
|-------|--------|---------------------|------------|
| detecting-prompt-injection | ai_security | false | AML.T0051, AML.T0054 |
| aws-cloudtrail-baseline | cloud | false | PR.DS-1, PR.PT-1, DE.AE-3 |
| windows-shellbag-analysis | dfir | false | T1083, T1564 |

These are the canonical Phase 1 reference shapes (per cybersec_vertical decision_manifest).

## Related Artifacts

| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[p01_kc_skill]] | parent | 0.70 |
| [[kc_safety_policy]] | sibling | 0.55 |
| [[kc_ai_rmf_profile]] | sibling | 0.55 |
| [[kc_guardrail]] | sibling | 0.50 |
| [[cybersec-skill-builder]] | downstream | 0.65 |
