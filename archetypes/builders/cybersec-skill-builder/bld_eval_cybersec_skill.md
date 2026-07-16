---
kind: quality_gate
id: p11_qg_cybersec_skill
pillar: P11
llm_function: GOVERN
purpose: Quality gates for cybersec_skill -- inherits skill gates and ADDS 4 anti-fabrication HARD gates
pattern: "few-shot learning -- LLM reads these before producing; F7 GOVERN executes them"
quality: null
title: 'Gate: Cybersec Skill'
version: 1.0.0
author: n03_builder
tags: [eval, P11, quality_gate, cybersec_skill, anti-fabrication, source-trace]
tldr: "Cybersec_skill gates: 6 universal H01-H06 + 6 skill SOFT scoring + 4 anti-fabrication HARD gates (T-code / CVE / control / source provenance)."
domain: cybersec_skill
created: '2026-05-30'
updated: '2026-05-30'
last_reviewed: '2026-05-30'
8f: "F7_govern"
keywords: [cybersec_skill, quality gates, anti-fabrication, T-code, CVE, framework controls, source provenance, capability gating, audit_log]
density_score: 0.88
related:
  - bld_schema_cybersec_skill
  - bld_feedback_cybersec_skill
---

## Quality Gate

## Definition
A cybersec_skill is a `skill` extended with mandatory source: trace, framework mapping, and capability gating. Passes when ALL skill universal gates pass AND ALL 4 anti-fabrication gates pass AND (if `authorized_use_only=true`) capability_registry + disclaimer + audit_log linkage are present.

## HARD Gates (universal, inherited from skill)

Failure on any HARD gate = immediate REJECT regardless of score.

| ID  | Check | Rationale |
|-----|-------|-----------|
| H01 | Frontmatter parses as valid YAML | Unparseable file cannot be indexed |
| H02 | `id` matches directory namespace + filename stem | Routing failures |
| H03 | `kind` is exactly `cybersec_skill` | Loader silently misroutes wrong literal |
| H04 | `quality` field is `null` | Quality is assigned by this gate, not author |
| H05 | All required frontmatter fields present (per `bld_schema_cybersec_skill.md`) | Incomplete frontmatter breaks consumers |
| H06 | Body <= 5120 bytes | Per `max_bytes` constraint |

## HARD Gates (cybersec-specific, ADDED)

These 4 gates are non-negotiable. They enforce Q5 (silent absorb requires source:) + Q11 (FULL-lattice anti-fabrication risk surface) from the cybersec_vertical decision manifest.

| ID    | Check | Rationale | Failure Mode |
|-------|-------|-----------|--------------|
| H_AF1 | Every `T<digits>(.<digits>)?` token in body MUST appear verbatim in `{source}/references/standards.md` | T-codes are MITRE ATT&CK technique IDs; fabricating them is technically false and undermines trust | REJECT + log cited token + missing-from-source |
| H_AF2 | Every `CVE-\d{4}-\d+` token in body MUST appear verbatim in `{source}/references/standards.md` | CVE IDs reference specific CVE-MITRE records; fabrication is verifiable and damaging | REJECT + log cited CVE + missing-from-source |
| H_AF3 | Every framework control id (e.g. `PR.AC-1`, `AML.T0051`, `ID.AM-3`) in body MUST appear verbatim in `{source}/references/standards.md` | Cross-framework crosswalks must trace to canonical text; invented control IDs poison downstream compliance maps | REJECT + log cited control + missing-from-source |
| H_AF4 | `source:` frontmatter path MUST exist on disk at build time | Provenance is the entire integrity premise of the silent-absorb model (Q5); a broken path is a broken license trace | REJECT + log path + "source not found" |

## HARD Gates (capability-gated, conditional)

Fire only when `authorized_use_only: true`:

| ID    | Check | Rationale |
|-------|-------|-----------|
| H_CG1 | `capability_registry` field MUST be non-null and reference an existing `capability_registry` artifact | Q3 capability gating contract; offensive use requires registered principal |
| H_CG2 | `disclaimer` field MUST point to an existing file (default `_docs/cybersec_disclaimer_canon.md`) | Legal canon must accompany every offensive distribution |
| H_CG3 | `audit_log_mandatory` MUST be `true` when `authorized_use_only=true` | Offensive without audit = unaccountable; non-negotiable |
| H_CG4 | Body MUST contain `## Authorization Notice` section linking to disclaimer + capability_registry | Visible warning to consumers; not buried in frontmatter |

## SOFT Scoring (cybersec-extended)

Dimensions weighted; total normalized weight = 100%.

| # | Dimension | Weight | 1 (Poor) | 5 (Good) | 10 (Excellent) |
|---|-----------|--------|----------|----------|----------------|
| 1 | Source provenance density (commit SHA + license path + attribution line) | 1.0 | Source path only | Path + license | Path + license + commit SHA + attribution paragraph |
| 2 | Framework mapping completeness (every relevant T-code/CSF/ATLAS cited) | 1.0 | None cited | Domain-primary framework only | All three (ATT&CK + CSF + ATLAS if applicable) cross-walked |
| 3 | Anti-fabrication discipline (zero invented codes / clear OMIT-not-invent statements) | 1.5 | Suspicious citations | Clean but unverified | All citations source-grep-able; explicit OMIT comments where truncated |
| 4 | Trigger specificity (cybersec namespace, not generic) | 1.0 | Generic "scan" | Domain-scoped | Specific tool + target + mode (e.g. `/cysk_aws_cloudtrail_baseline --read-only`) |
| 5 | Phases with cybersec-relevant I/O (artifact, target, evidence, finding) | 1.0 | Untyped | Partial typing | Every phase typed with finding / evidence / target boundary |
| 6 | Authorization notice clarity (if applicable) | 0.5 | Missing or buried | Present | Top of body + linked disclaimer + capability_registry |

Density target: >= 0.85 (same as skill).
Final score target: >= 9.0 (CEX floor).

## Anti-Fabrication Self-Check (author must run before commit)

```bash
# H_AF1: T-codes
grep -oE 'T[0-9]+(\.[0-9]+)?' p03_cysk_<name>.md | sort -u > /tmp/cited_tcodes.txt
grep -F -f /tmp/cited_tcodes.txt <source>/references/standards.md || echo "H_AF1 FAIL: missing T-codes"

# H_AF2: CVEs
grep -oE 'CVE-[0-9]{4}-[0-9]+' p03_cysk_<name>.md | sort -u > /tmp/cited_cves.txt
grep -F -f /tmp/cited_cves.txt <source>/references/standards.md || echo "H_AF2 FAIL: missing CVEs"

# H_AF3: framework control ids
grep -oE '[A-Z]{2}\.[A-Z][A-Z]?-?[0-9]+|AML\.T[0-9]+' p03_cysk_<name>.md | sort -u > /tmp/cited_controls.txt
grep -F -f /tmp/cited_controls.txt <source>/references/standards.md || echo "H_AF3 FAIL: missing controls"

# H_AF4: source path exists
test -e <source> || echo "H_AF4 FAIL: source path missing"
```

## Correction Protocol (when AF gate fails)

| Step | Action |
|------|--------|
| 1 | Identify the missing token in the AF gate output |
| 2 | OPEN the source `references/standards.md`. Search for the token. |
| 3 | If found: copy the verbatim line into the artifact (do not paraphrase). |
| 4 | If absent: REMOVE the citation from the artifact. Do not invent or guess. |
| 5 | Re-run F7 GOVERN. Max 2 retries before escalating to N07. |

## Related Artifacts

| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[bld_schema_cybersec_skill]] | upstream | 0.80 |
| [[bld_feedback_cybersec_skill]] | downstream | 0.60 |
