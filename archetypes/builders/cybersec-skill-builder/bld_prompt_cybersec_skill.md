---
id: p03_ins_cybersec_skill_builder
kind: instruction
pillar: P03
version: 1.0.0
created: 2026-05-30
updated: 2026-05-30
author: n03_builder
title: Cybersec Skill Builder Instructions
target: cybersec-skill-builder agent
phases_count: 5
prerequisites:
  - Source baseline skill exists on disk (Apache 2.0 mukul975 or equivalent)
  - source/references/standards.md exists and lists T-codes / CVEs / controls
  - domain_subtype is one of: ai_security, cloud, dfir, appsec, netsec, identity
  - if authorized_use_only=true then capability_registry artifact already exists
  - if authorized_use_only=true then _docs/cybersec_disclaimer_canon.md exists
validation_method: checklist
domain: cybersec_skill
quality: null
tags: [instruction, cybersec_skill, anti-fabrication, source-trace, P03, distillation]
idempotent: true
atomic: false
rollback: Delete generated cybersec_skill artifact and restart from Phase 1
dependencies: [source, references/standards.md]
logging: true
tldr: "Distill 1 baseline cybersec skill into 1 cybersec_skill artifact -- preserve source: trace, map frameworks (T-codes / CVE / CSF / ATLAS), gate offensive via authorized_use_only, NEVER invent citations."
8f: "F6_produce"
keywords: [cybersec_skill builder, anti-fabrication, source frontmatter, framework mapping, capability gating, audit_log, mukul975, silent-absorb]
density_score: 0.90
llm_function: REASON
related:
  - cybersec-skill-builder
  - bld_schema_cybersec_skill
  - bld_eval_cybersec_skill
---

## Context

The cybersec-skill-builder produces `cybersec_skill` artifacts -- skills distilled from
mukul975's Apache 2.0 baseline (or equivalent) with mandatory source: trace, framework
mapping, and capability gating for offensive variants. Distillation, NOT invention.

**Input contract**:
- `{{source_path}}`: absolute or repo-relative path to baseline skill directory
- `{{skill_name}}`: kebab-case capability name from baseline (e.g. `detecting-prompt-injection`)
- `{{domain_subtype}}`: one of `ai_security`, `cloud`, `dfir`, `appsec`, `netsec`, `identity`
- `{{authorized_use_only}}`: boolean -- true = offensive / dual-use; false = pure defensive
- `{{frameworks}}`: explicit list of framework codes to cite (validated against source)
- `{{trigger_value}}`: slash command in `cysk_` namespace (e.g. `/cysk_aws_cloudtrail_baseline`)

**Output contract**: A single `cybersec_skill` Markdown file with full YAML frontmatter
(skill base + 6 cybersec fields), 8 body sections (per `bld_schema_cybersec_skill`), and
ZERO citations absent from `{source}/references/standards.md`.

**Boundaries**:
- cybersec_skill handles cybersec-domain reusable capabilities with source trace.
- Pure-prompt cybersec content with no source: belongs in `prompt_template` or `instruction`.
- Org-level safety governance (not domain skills) belongs in `safety_policy`.
- Regulatory mapping (not per-skill) belongs in `compliance_framework` or `ai_rmf_profile`.
- Live tool execution belongs in `mcp_server` or `cli_tool`, invoked BY cybersec_skill phases.

## Phases

### Phase 1 -- Discover Source
- Input: `{{source_path}}`, `{{skill_name}}`
- Action: read `{source}/{skill_name}/SKILL.md` + `{source}/references/standards.md`. Parse baseline trigger, phases, citations.
- Output: parsed baseline data + verified citation pool (all T-codes / CVEs / controls in source)

### Phase 2 -- Map Frameworks
- Input: baseline citations, `{{frameworks}}` (caller-supplied targets)
- Action: cross-reference every desired framework code against the source citation pool. DROP any code NOT in source (do NOT add aliases or "equivalent" codes).
- Output: validated `frameworks: [...]` list -- subset of source citations

### Phase 3 -- Compose Frontmatter
- Input: validated frameworks, `{{authorized_use_only}}`, baseline trigger
- Action: assemble all required frontmatter fields. Set `source: {{source_path}}/{{skill_name}}`. If `authorized_use_only=true` set `capability_registry` and `disclaimer` (else null). Set `audit_log_mandatory = authorized_use_only`.
- Output: full YAML frontmatter block

### Phase 4 -- Compose Body
- Input: parsed baseline, validated frameworks
- Action: write 8 sections per schema. Quote source citations verbatim (no paraphrase of T-codes). Add `## Source Provenance` (commit SHA + license path) and `## Framework Mapping` table. If `authorized_use_only=true` add `## Authorization Notice` linking disclaimer + capability_registry.
- Output: body Markdown (<= 5120 bytes)

### Phase 5 -- Self-Validate Anti-Fabrication
- Input: composed artifact
- Action: run H_AF1..H_AF4 grep checks from `bld_eval_cybersec_skill.md`. If any fail, REMOVE the offending citation (do NOT invent). Verify `source:` path exists on disk.
- Output: artifact passing all 4 AF gates + skill-inherited H01-H06

## Anti-Fabrication Rule (NON-NEGOTIABLE)

If the source does not contain a T-code / CVE / framework control you want to cite, **OMIT it**.
Do not invent. Do not "approximate". Do not cite "similar" codes.
A cybersec_skill that fabricates a single T-code is worse than a cybersec_skill with zero T-codes.

| Tempting action | Correct action |
|-----------------|----------------|
| "T1059 is the right ATT&CK code, I'll add it" without source check | Search source first; if absent, OMIT |
| "This control maps to PR.AC-1" by inference | Verify in `{source}/references/standards.md`; if absent, OMIT |
| "Let me write CVE-2024-12345 from memory" | grep source; if absent, OMIT (memory is unverifiable) |
| "I'll paraphrase the technique description" | Quote verbatim or omit; paraphrase breaks downstream crosswalks |

## Cross-References

- **Pillar**: P03 (Prompt -- instruction layer for distillation)
- **Kind**: `instruction`
- **Artifact ID**: `p03_ins_cybersec_skill_builder`
- **Tags**: [instruction, cybersec_skill, anti-fabrication, P03]

## Builder Integration

| Aspect | Detail |
|--------|--------|
| ISO | 3 of 12 builder ISOs |
| Loader | `cex_skill_loader.py` (cybersec_skill consumes same loader as skill) |
| Pipeline | Injected at F3 (Compose) |
| Anti-Fab Gates | Enforced in F7 GOVERN via `bld_eval_cybersec_skill.md` |

## Template Loading

```yaml
loader: cex_skill_loader.py
injection_point: F3_compose
priority: high
guards:
  - H_AF1
  - H_AF2
  - H_AF3
  - H_AF4
```

```bash
python _tools/cex_skill_loader.py --verify cybersec_skill
```

## Related Artifacts

| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[cybersec-skill-builder]] | upstream | 0.70 |
| [[bld_schema_cybersec_skill]] | upstream | 0.65 |
| [[bld_eval_cybersec_skill]] | downstream | 0.60 |
