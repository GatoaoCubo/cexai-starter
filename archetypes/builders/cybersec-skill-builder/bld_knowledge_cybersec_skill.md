---
kind: knowledge_card
id: bld_knowledge_card_cybersec_skill
pillar: P04
llm_function: INJECT
purpose: Domain knowledge for cybersec_skill production -- atomic searchable facts
sources: cybersec-skill-builder schema + mukul975 baseline + cybersec_vertical decision_manifest
quality: null
title: "Knowledge Card Cybersec Skill"
version: "1.0.0"
author: n03_builder
tags: [cybersec_skill, builder, knowledge, source-trace, anti-fabrication, mukul975, ATT&CK, CSF, ATLAS, CVE]
tldr: "Atomic facts for cybersec_skill construction: 6 cybersec frontmatter fields, 4 anti-fabrication HARD gates, 4 framework crosswalk targets, 6 domain subtypes, capability-gating contract."
domain: "cybersec_skill construction"
created: "2026-05-30"
updated: "2026-05-30"
8f: "F3_inject"
keywords: [cybersec_skill, source frontmatter, anti-fabrication, ATT&CK T-code, CSF control, ATLAS technique, CVE, capability_registry, disclaimer, audit_log, mukul975, silent-absorb]
density_score: 0.90
related:
  - cybersec-skill-builder
  - bld_schema_cybersec_skill
  - bld_eval_cybersec_skill
  - p01_kc_cybersec_skill
  - bld_knowledge_card_skill
---

# Domain Knowledge: cybersec_skill

## Executive Summary

A cybersec_skill is a `skill` (P04 reusable capability) extended with mandatory source: trace (Apache 2.0 attribution to mukul975 or equivalent baseline), framework mapping (MITRE ATT&CK T-codes / NIST CSF controls / MITRE ATLAS techniques / CVE IDs), capability gating (`authorized_use_only` + `capability_registry` + `disclaimer` for offensive variants), and 4 anti-fabrication HARD gates. The kind exists to enable silent-absorb of external cybersec corpora WITHOUT the integrity rot that comes from re-typed citations.

## Spec Table

| Property | Value |
|----------|-------|
| Pillar | P03 |
| Nucleus owner | N05 (Gating Wrath) |
| Format | YAML (frontmatter) + Markdown (body) |
| Naming | `p03_cysk_{name}.md` + `.yaml` |
| ID regex | `^p03_cysk_[a-z][a-z0-9_]+$` |
| Max body bytes | 5120 |
| Required frontmatter (skill base) | 19 |
| Required frontmatter (cybersec-add) | 6 |
| Optional cybersec frontmatter | 5 |
| HARD gates (universal) | 6 (H01-H06) |
| HARD gates (cybersec) | 4 (H_AF1-H_AF4) |
| HARD gates (capability-conditional) | 4 (H_CG1-H_CG4) |
| Quality field | null always -- invariant |

## Six Cybersec Frontmatter Fields

| Field | When required | Purpose |
|-------|--------------|---------|
| `source` | always | Path to baseline skill directory -- existence enforced at build (H_AF4) |
| `frameworks` | when citing T/CSF/ATLAS/CVE | List of codes -- each must appear in source (H_AF1-H_AF3) |
| `authorized_use_only` | always | bool; gates downstream tools and audit requirements |
| `audit_log_mandatory` | always | bool; must be true when authorized_use_only=true (H_CG3) |
| `capability_registry` | when authorized_use_only=true | skill_id of registered principal granting offensive use |
| `disclaimer` | when authorized_use_only=true | path to _docs/cybersec_disclaimer_canon.md or equivalent |

## Four Framework Crosswalk Targets

| Framework | Code Pattern | Source | Role |
|-----------|-------------|--------|------|
| MITRE ATT&CK | `T<digits>(.<digits>)?` | attack.mitre.org | Adversary techniques (enterprise / mobile / ICS) |
| NIST CSF | `<ID>.<XX>-<digits>` (e.g. PR.AC-1) | csrc.nist.gov | Cybersecurity Framework controls |
| MITRE ATLAS | `AML.T<digits>` | atlas.mitre.org | AI/ML-adversarial techniques |
| CVE-MITRE | `CVE-<year>-<id>` | cve.mitre.org | Vulnerability identifiers |

## Six Domain Subtypes

| Subtype | Scope | Typical authorized_use_only |
|---------|-------|----------------------------|
| ai_security | LLM / agent security (prompt injection, jailbreak, model theft) | false (defensive) / true (red-team variants) |
| cloud | AWS / GCP / Azure baselines + misconfig detection | false (audit) / true (lateral movement variants) |
| dfir | Digital forensics + incident response | false (analysis) |
| appsec | Application security (SAST / DAST / SCA findings triage) | false (audit) / true (exploitation variants) |
| netsec | Network security (Sigma rules, packet analysis) | false (detection) |
| identity | IAM, SSO, credential hygiene | false (audit) / true (privilege escalation variants) |

## Anti-Fabrication Discipline (Q11 LOCKED FULL-lattice)

The single most important domain rule: **never invent a citation**. If a T-code / CVE /
framework control is desired but absent from `{source}/references/standards.md`, OMIT it.

| Behavior | Status |
|----------|--------|
| Cite verbatim from source | REQUIRED |
| Paraphrase technique description | REJECT (verbatim or omit) |
| Add "equivalent" code by inference | REJECT |
| Cite from memory without source check | REJECT (memory is unverifiable) |
| OMIT a citation that has no source match | REQUIRED |

This is enforced by the 4 grep-based HARD gates in `bld_eval_cybersec_skill.md`.

## Capability Gating Contract (Q3)

When `authorized_use_only=true`:
1. The skill MUST reference a `capability_registry` artifact granting the principal
2. The skill MUST link `_docs/cybersec_disclaimer_canon.md` (or org-equivalent)
3. The skill MUST set `audit_log_mandatory=true`
4. The skill body MUST contain a `## Authorization Notice` section (not just frontmatter)

This is enforced by H_CG1-H_CG4 in `bld_eval_cybersec_skill.md`.

## Distinction Table

| cybersec_skill IS | cybersec_skill IS NOT |
|-------------------|-----------------------|
| Distilled from a baseline with attribution preserved | Original cybersec authorship (uses `skill` + KCs instead) |
| Framework-mapped (every code source-traceable) | Free-form cybersec prose |
| Capability-gated for offensive use | Unfettered offensive tooling (use `mcp_server` + RBAC) |
| Phased reusable capability (inherits skill semantics) | Single-shot exploit script (use `cli_tool` + sandbox_spec) |
| ASCII-friendly (body may use UTF-8; code blocks ASCII) | Bundle-packaged for portable distribution (Q1 LOCKED no bundles) |

## Application

1. Identify baseline path (e.g. `_inbox/mukul975/skills/aws-cloudtrail-baseline/`)
2. Read `SKILL.md` + `references/standards.md`. Catalog citation pool.
3. Choose `domain_subtype` + decide `authorized_use_only`.
4. If offensive: ensure `capability_registry` artifact exists; ensure disclaimer path resolves.
5. Compose frontmatter (skill base + 6 cybersec fields).
6. Compose body (8 sections per schema). Quote citations verbatim.
7. Run AF self-check grep block. Remove any citation absent from source.
8. F7 GOVERN (cex_doctor + scoring rubric + AF gates). Target >= 9.0.

## References

- Schema: `bld_schema_cybersec_skill.md` (P06)
- Eval: `bld_eval_cybersec_skill.md` (P11) -- 14 gates total
- Baseline source: mukul975/security-skills (Apache 2.0) -- silent-absorb model
- Boundary: skill (P04 generic), safety_policy (P11 org-level), ai_rmf_profile (P11 NIST mapping)

## Related Artifacts

| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[cybersec-skill-builder]] | upstream | 0.65 |
| [[bld_schema_cybersec_skill]] | downstream | 0.62 |
| [[bld_eval_cybersec_skill]] | downstream | 0.60 |
| [[p01_kc_cybersec_skill]] | sibling | 0.70 |
| [[bld_knowledge_card_skill]] | parent | 0.55 |
