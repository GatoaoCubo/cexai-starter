---
quality: null
id: p11_fb_cybersec_skill
kind: builder_default
pillar: P11
title: "Feedback: Cybersec Skill"
domain: cybersec_skill
version: 1.0.0
tags: [feedback, anti-patterns, P11, cybersec_skill, anti-fabrication, capability-gating]
8f: "F7_govern"
keywords: [cybersec_skill anti-patterns, anti-fabrication failures, capability gating violations, source-trace failures, correction protocol, worked examples, mukul975]
tldr: "Anti-patterns and worked examples for cybersec_skill: 8 NEVER rules + 5 failure modes + 4-step correction + 3 mukul975 worked examples (detecting-prompt-injection, aws-cloudtrail-baseline, windows-shellbag-analysis)."
author: n03_builder
llm_function: GOVERN
density_score: 0.88
created: "2026-05-30"
updated: "2026-05-30"
related:
  - bld_eval_cybersec_skill
  - cybersec-skill-builder
---

# Feedback: Cybersec Skill

## Anti-Patterns (NEVER do)

| Rule | Violation | Gate |
|------|-----------|------|
| No self-score | Never assign quality score to own output | H04 |
| No fabricated T-code | Never cite ATT&CK techniques absent from `{source}/references/standards.md` | H_AF1 |
| No fabricated CVE | Never cite CVE IDs absent from source | H_AF2 |
| No fabricated control | Never cite framework control IDs absent from source | H_AF3 |
| No missing source: | source: frontmatter field MUST be a real on-disk path | H_AF4 |
| No offensive without gating | `authorized_use_only=true` requires capability_registry + disclaimer + audit_log | H_CG1-H_CG3 |
| ASCII-only code blocks | No emoji, no accented chars in code fences | sanitize |
| No partial output | Complete artifact; no truncation, no "..." | H06 |

## Common Failure Modes

| Failure Mode | Signal | Fix |
|-------------|--------|-----|
| Memory-cited T-code | LLM "knows" T1059 maps; H_AF1 grep fails | OMIT or verify via Read on source |
| Paraphrased technique description | Source-grep finds the code but not the verbatim phrase | Quote verbatim from source |
| Offensive variant without capability_registry | H_CG1 fail at F7 | Build capability_registry first; reference its skill_id |
| `audit_log_mandatory=false` with `authorized_use_only=true` | H_CG3 fail | Set both to true; offensive WITHOUT audit is unaccountable |
| Body prose only | density < 0.85, no Framework Mapping table | Convert citations to table with source-line column |

## Correction Protocol

| Step | Action | Gate |
|------|--------|------|
| 1 | Run AF grep block from `bld_eval_cybersec_skill.md` | F7 |
| 2 | For each failing citation: open source `references/standards.md`, search verbatim | F7 |
| 3 | If found: copy verbatim into body. If absent: REMOVE the citation entirely | F6 |
| 4 | Re-run F7 GOVERN. Max 2 retries before escalating to N07 | F8 |

## Worked Examples (from mukul975 baseline -- silent-absorb)

These 3 examples are the canonical reference set per the cybersec_vertical Phase 1 manifest.
They illustrate the 3 typical shapes a cybersec_skill takes.

### Example 1: detecting-prompt-injection (ai_security / defensive)

| Attribute | Value |
|-----------|-------|
| source | `_inbox/mukul975/skills/detecting-prompt-injection/` |
| domain_subtype | ai_security |
| authorized_use_only | false |
| frameworks | [AML.T0051, AML.T0054] (ATLAS adversarial-ML techniques) |
| trigger | `/cysk_detecting_prompt_injection` |
| phases | [scan_inputs, classify_injection, emit_finding] |
| Why golden | Defensive (no capability gate needed); ATLAS-mapped (AI-specific); detection-oriented (finding output); source-grep clean |

### Example 2: aws-cloudtrail-baseline (cloud / defensive)

| Attribute | Value |
|-----------|-------|
| source | `_inbox/mukul975/skills/aws-cloudtrail-baseline/` |
| domain_subtype | cloud |
| authorized_use_only | false |
| frameworks | [PR.DS-1, PR.PT-1, DE.AE-3] (NIST CSF controls) |
| trigger | `/cysk_aws_cloudtrail_baseline` |
| phases | [enumerate_trails, validate_config, emit_audit_report] |
| Why golden | CSF-mapped (compliance-aligned); read-only cloud op (no offensive risk); audit-output (typed finding); clean crosswalk |

### Example 3: windows-shellbag-analysis (dfir / defensive)

| Attribute | Value |
|-----------|-------|
| source | `_inbox/mukul975/skills/windows-shellbag-analysis/` |
| domain_subtype | dfir |
| authorized_use_only | false |
| frameworks | [T1083, T1564] (ATT&CK enterprise techniques -- file discovery / hide artifacts) |
| trigger | `/cysk_windows_shellbag_analysis` |
| phases | [load_artifact, parse_shellbags, correlate_timeline, emit_findings] |
| Why golden | Forensic (post-incident, not live exploit); ATT&CK-mapped (defensive technique-perspective); evidence-typed I/O; 4-phase canonical structure |

## Key Behaviors

- Builder MUST load all 12 ISOs (1:1 with pillars) before producing any artifact
- Builder MUST run AF grep block before F7 GOVERN signoff
- Builder MUST compile output via cex_compile.py after saving
- Builder MUST signal completion with quality score to N07
- Builder MUST NOT self-score (quality field always null)
- Builder MUST NOT add CI / automation hooks (Q10 LOCKED)
- Builder MUST NOT bundle related cybersec_skills into a portable pack (Q1 LOCKED)

## Quality Thresholds

| Dimension | Weight | Target | Gate |
|-----------|--------|--------|------|
| Structural completeness | 25% | >= 8.0 | L1 |
| Rubric compliance (incl. AF gates) | 35% | >= 8.5 | L2 (HARD-gated) |
| Semantic coherence | 30% | >= 8.5 | L3 |
| Anti-fabrication compliance | 10% | 4/4 gates pass | HARD-only |
| Density score | -- | >= 0.85 | S09 |
| Tables present | -- | >= 1 | S05 |

## Gate Check

```bash
python _tools/cex_score.py {FILE} --layer structural
python _tools/cex_score.py {FILE} --layer rubric
bash <(grep -E '^# H_AF' archetypes/builders/cybersec-skill-builder/bld_eval_cybersec_skill.md)
```

```yaml
# Expected output structure
structural: 8.5+
rubric: 8.0+
average: 9.0+
af_gates_passed: 4/4
cg_gates_applicable: 0 or 4
density: 0.85+
```

## Related Artifacts

| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[bld_eval_cybersec_skill]] | upstream | 0.75 |
| [[cybersec-skill-builder]] | upstream | 0.55 |
