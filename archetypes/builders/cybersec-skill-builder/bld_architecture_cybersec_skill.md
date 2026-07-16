---
kind: architecture
id: bld_architecture_cybersec_skill
pillar: P08
llm_function: CONSTRAIN
purpose: Component map of cybersec_skill -- inventory, dependencies, architectural position
quality: null
title: "Architecture Cybersec Skill"
version: "1.0.0"
author: n03_builder
tags: [cybersec_skill, builder, architecture, source-trace, capability-gating, framework-mapping]
tldr: "Component map: source baseline + frontmatter (skill + 6 cybersec) + phase list + framework mapping + (conditional) authorization notice + audit log linkage. Dependencies: skill (P04 parent), capability_registry (when offensive), disclaimer canon."
domain: "cybersec_skill construction"
created: "2026-05-30"
updated: "2026-05-30"
8f: "F1_constrain"
keywords: [cybersec_skill architecture, component map, capability gating, source provenance, framework mapping, authorization notice, audit_log linkage]
density_score: 0.90
related:
  - cybersec-skill-builder
---

# Architecture: cybersec_skill in the CEX

## Component Inventory

| Name | Role | Owner | Status |
|------|------|-------|--------|
| frontmatter block | Metadata header (skill base + 6 cybersec fields) | cybersec-skill-builder | active |
| source_path | Apache 2.0 baseline directory pointer (mukul975 lead) | author | active |
| trigger_definition | Slash command in `/cysk_` namespace or agent-invoked | author | active |
| phase_list | Ordered execution phases with cybersec-typed I/O | author | active |
| input_contract | Typed (target / artifact / evidence / finding) | author | active |
| output_contract | Typed (finding / IOC / remediation / audit_event) | author | active |
| framework_mapping_table | Crosswalk of cited codes to source lines | author | active |
| authorization_notice | Capability gate + disclaimer (offensive only) | author | conditional |
| audit_log_linkage | Per-invocation event emission spec | author | conditional |
| anti_fabrication_checklist | Author self-attestation block | author | active |

## Dependency Graph

```
baseline_skill   --absorbed-->   cybersec_skill  --produces-->     finding/IOC
trigger_event    --activates-->  cybersec_skill  --signals-->      completion + audit_event
cybersec_skill   --requires-->   skill (P04 parent semantics)
cybersec_skill   --requires-->   source baseline on disk (H_AF4)
cybersec_skill   --requires_when_offensive--> capability_registry (H_CG1)
cybersec_skill   --requires_when_offensive--> disclaimer canon (H_CG2)
cybersec_skill   --emits_when_offensive-->    audit_log (H_CG3)
```

| From | To | Type | Data |
|------|----|------|------|
| baseline_skill (external) | cybersec_skill | absorbs | Apache 2.0 silent-absorb with attribution |
| skill (P04) | cybersec_skill | parent | inherits all skill semantics (trigger / phases / I/O) |
| references/standards.md | cybersec_skill | citation_source | every cited code must trace here |
| capability_registry (P11) | cybersec_skill | gates | offensive variants only |
| disclaimer canon (_docs) | cybersec_skill | gates | offensive variants only |
| cybersec_skill | audit_log (P11) | emits | when audit_log_mandatory=true |
| cybersec_skill | finding (P05 output) | produces | structured detection / IOC / remediation |
| ai_rmf_profile (P11) | cybersec_skill | crosswalks | shared framework codes |

## Boundary Table

| cybersec_skill IS | cybersec_skill IS NOT |
|-------------------|-----------------------|
| Distillation of external baseline with attribution | Original cybersec authorship (use `skill` + KCs) |
| Framework-mapped (ATT&CK + ATLAS + CSF + CVE) | Free-form prose with handwaved citations |
| Capability-gated when offensive (`authorized_use_only=true`) | Unfettered offensive tooling (use `mcp_server` + RBAC) |
| Phased reusable capability (inherits skill semantics) | One-shot exploit (use `cli_tool` + `sandbox_spec`) |
| Source-traced (every code grep-verifiable) | Memory-cited (Q11 LOCKED FULL-lattice anti-fabrication) |
| ASCII-friendly in code blocks | Bundle-packaged (Q1 LOCKED no portable bundles) |
| Manually invoked (Q10 LOCKED U1 manual) | CI-automated distillation |

## Layer Map

| Layer | Components | Purpose |
|-------|------------|---------|
| Provenance | source_path, license_ref, attribution | Preserve Apache 2.0 trace (Q5 silent-absorb) |
| Trigger | trigger_definition, user_invocable_flag | `/cysk_` namespace activation |
| Contract | frontmatter (skill+cybersec), input_contract, output_contract | Typed I/O across phases |
| Framework | framework_mapping_table, frameworks frontmatter | Crosswalk to source codes |
| Execution | phase_list, action_prompts | Ordered phases with typed I/O |
| Authorization | authorization_notice, capability_registry_ref, disclaimer_ref | Conditional gating (offensive) |
| Audit | audit_log_linkage, audit_log_mandatory flag | Per-invocation accountability |
| Output | finding, audit_event, completion_signal | Deliver result + accountability |
| Governance | anti_fabrication_checklist, AF grep block | Pre-commit self-attestation |

## Architectural Invariants

1. `source:` path MUST exist on disk at every F8 COLLABORATE moment (H_AF4)
2. Every cited code in body MUST appear in `{source}/references/standards.md` (H_AF1-H_AF3)
3. `authorized_use_only=true` IMPLIES `capability_registry` + `disclaimer` + `audit_log_mandatory=true` (H_CG1-H_CG3)
4. `## Authorization Notice` section is present iff `authorized_use_only=true` (H_CG4)
5. The artifact is a single file per skill -- no bundles (Q1 LOCKED)
6. Distillation is manual -- no CI hook triggers cybersec_skill creation (Q10 LOCKED)

## Position in Vertical Stack

```
N05 Operations (Gating Wrath)
  P03 Prompt
    cybersec_skill  <-- this kind
      uses: skill (P04, parent semantics)
      requires (offensive): capability_registry (P11)
      crosswalks: ai_rmf_profile (P11), safety_policy (P11)
      emits: audit_log (P11)
      consumed_by: workflow (P12), agent (P02)
```

## Execution Instructions

1. You are executing builder `cybersec-skill-builder` for pipeline function `CONSTRAIN`.
2. Follow the builder's ISO instructions precisely.
3. Generate the complete output artifact.
4. Quality target: >= 9.0 (no filler; AF gates non-negotiable).
5. quality field is null -- never self-score.

## Related Artifacts

| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[cybersec-skill-builder]] | upstream | 0.68 |
