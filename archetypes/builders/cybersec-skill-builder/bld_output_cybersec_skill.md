---
kind: output_template
id: bld_output_template_cybersec_skill
pillar: P05
llm_function: PRODUCE
purpose: Template with {{vars}} that the LLM fills to produce a cybersec_skill
pattern: every field here exists in SCHEMA -- template derives, never invents
quality: null
title: "Output Template Cybersec Skill"
version: "1.0.0"
author: n03_builder
tags: [cybersec_skill, builder, output_template, source-trace, anti-fabrication]
tldr: "Output template for cybersec_skill: skill frontmatter + 6 cybersec fields + 8 body sections (Purpose / Source Provenance / Framework Mapping / Workflow Phases / Anti-Fabrication Checklist / Authorization Notice / Anti-Patterns / Metrics)."
domain: "cybersec_skill construction"
created: "2026-05-30"
updated: "2026-05-30"
8f: "F6_produce"
keywords: [cybersec_skill, output template, frontmatter, source provenance, framework mapping, authorization notice, anti-fabrication checklist]
density_score: 0.90
related:
  - bld_schema_cybersec_skill
  - bld_eval_cybersec_skill
  - cybersec-skill-builder
---

# Output Template: cybersec_skill

## Frontmatter Template

```yaml
id: p03_cysk_{{name}}
kind: cybersec_skill
pillar: P03
version: "1.0.0"
created: "{{YYYY-MM-DD}}"
updated: "{{YYYY-MM-DD}}"
author: "{{who_produced}}"
name: "{{human_readable_capability_name}}"
description: "{{one_line_capability_max_120ch}}"
user_invocable: {{true|false}}
trigger: "/cysk_{{name}}"
phases:
  - "{{phase_1_name}}"
  - "{{phase_2_name}}"
  - "{{phase_3_name}}"
when_to_use:
  - "{{condition_1}}"
  - "{{condition_2}}"
when_not_to_use:
  - "{{exclusion_1}}"
  - "{{exclusion_2}}"
examples:
  - "{{invocation_example_1}}"
  - "{{invocation_example_2}}"
quality: null
tags: [cybersec_skill, {{domain_subtype}}, {{frameworks[0]}}, P03]
tldr: "{{one_line_summary}}"
domain: cybersec_skill

# Cybersec-mandatory
source: "{{path_to_baseline_skill_directory}}"
frameworks: ["{{T_code_1}}", "{{CSF_control_1}}", "{{ATLAS_technique_1}}"]
authorized_use_only: {{true|false}}
audit_log_mandatory: {{same_as_authorized_use_only}}
capability_registry: "{{capability_registry_skill_id_or_null}}"
disclaimer: "{{path_to_disclaimer_or_null}}"

# Cybersec-optional
domain_subtype: "{{ai_security|cloud|dfir|appsec|netsec|identity}}"
severity: "{{low|medium|high|critical}}"
privilege_required: "{{none|user|admin|root}}"
detection_signatures: ["{{sigma_path_or_omit}}"]
safe_mode_default: {{true|false}}
```

## Body Template (8 sections)

```markdown
# {{human_readable_capability_name}}

## Purpose
{{what_capability_this_provides_to_security_practitioner}}
{{why_distilled_from_source_vs_original_authorship}}

## Source Provenance
- Baseline: `{{source}}`
- License: `{{source}}/LICENSE` (Apache 2.0)
- Commit SHA: `{{baseline_commit_sha}}`
- Attribution: `{{baseline_attribution_line}}`
- Silent-absorb rationale: {{2-sentence_why}}

## Framework Mapping

| Cited code | Framework | Source line | Notes |
|------------|-----------|-------------|-------|
| {{T_code_1}} | MITRE ATT&CK | `references/standards.md:{{line}}` | {{technique_short_name}} |
| {{CSF_control_1}} | NIST CSF | `references/standards.md:{{line}}` | {{control_short_name}} |
| {{ATLAS_technique_1}} | MITRE ATLAS | `references/standards.md:{{line}}` | {{ml_specific}} |
| {{CVE_1}} | CVE-MITRE | `references/standards.md:{{line}}` | {{cvss_score}} |

## Workflow Phases

### {{phase_1_name}}
- **Input**: {{typed_input_fields}}
- **Action**: {{what_phase_does}}
- **Output**: {{typed_output_fields}}

### {{phase_2_name}}
- **Input**: {{typed_input_fields}}
- **Action**: {{what_phase_does}}
- **Output**: {{typed_output_fields}}

### {{phase_3_name}}
- **Input**: {{typed_input_fields}}
- **Action**: {{what_phase_does}}
- **Output**: {{typed_output_fields}}

## Anti-Fabrication Checklist (author self-attests)

- [ ] H_AF1: every T-code in body grep-verified in `{{source}}/references/standards.md`
- [ ] H_AF2: every CVE in body grep-verified in `{{source}}/references/standards.md`
- [ ] H_AF3: every framework control in body grep-verified in `{{source}}/references/standards.md`
- [ ] H_AF4: `source:` path exists on disk at build time
- [ ] No paraphrase: technique descriptions are quoted verbatim or OMITTED
- [ ] No memory citation: nothing cited that wasn't grep-verified

## Authorization Notice
{{INCLUDE_ONLY_IF_authorized_use_only_IS_TRUE}}

This capability is `authorized_use_only`. Invocation requires:
- Active `capability_registry` artifact: `{{capability_registry}}`
- Acceptance of disclaimer: `{{disclaimer}}`
- Audit log emission per invocation: `audit_log_mandatory=true`

Operating principal MUST hold the registered capability before execution. Audit log
events emitted to: `_runtime/audit/cysk_{{name}}_<timestamp>.jsonl`.

## Anti-Patterns

| Anti-pattern | Why wrong | Correct approach |
|--------------|-----------|------------------|
| Cite T-code from memory | Unverifiable, fabrication risk | grep source first; OMIT if absent |
| Paraphrase framework description | Breaks downstream crosswalks | Verbatim quote or omit |
| Drop source: "because obvious" | Breaks H_AF4; license trace lost | Keep source: always |
| Offensive without capability_registry | Q3 LOCKED gate violated | Build capability_registry first |
| Add CI hook for auto-distill | Q10 LOCKED U1 manual | Manual invocation only |
| Bundle multiple skills into portable pack | Q1 LOCKED no bundles | One skill per artifact |

## Metrics

| Metric | Target | Source |
|--------|--------|--------|
| AF gates passed | 4/4 | bld_eval_cybersec_skill.md grep block |
| Framework crosswalk completeness | >= 80% of source-cited codes preserved | manual review |
| Density score | >= 0.85 | cex_score.py --layer semantic |
| Quality score | >= 9.0 | cex_score.py aggregate |
```

## Template Standards

1. Every `{{var}}` corresponds to a frontmatter or body field in `bld_schema_cybersec_skill.md`
2. The 8 body sections are ORDERED -- do not reorder
3. `## Authorization Notice` is conditional (only when `authorized_use_only=true`)
4. `## Framework Mapping` table MUST include every code from `frameworks:` frontmatter list
5. Citations in body MUST appear in `{{source}}/references/standards.md`

## Properties

| Property | Value |
|----------|-------|
| Kind | `output_template` |
| Pillar | P05 |
| Domain | cybersec_skill construction |
| Pipeline | 8F (F1-F8) + AF lattice |
| Scorer | cex_score.py |
| Compiler | cex_compile.py |
| Retriever | cex_retriever.py |
| Quality target | 9.0+ |
| Density target | 0.85+ |

## Related Artifacts

| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[bld_schema_cybersec_skill]] | upstream | 0.70 |
| [[bld_eval_cybersec_skill]] | downstream | 0.55 |
| [[cybersec-skill-builder]] | upstream | 0.60 |
