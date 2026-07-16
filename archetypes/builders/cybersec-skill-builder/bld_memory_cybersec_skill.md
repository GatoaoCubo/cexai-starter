---
kind: memory
id: bld_memory_cybersec_skill
pillar: P09
llm_function: INJECT
purpose: Persistent learnings + context-injection pool for cybersec-skill-builder
pattern: what worked, what failed, key invariants, baseline corpus pointer
memory_scope: project
observation_types: [project, reference, feedback, source]
quality: null
title: "Memory Cybersec Skill"
version: "1.0.0"
author: n03_builder
tags: [cybersec_skill, builder, memory, mukul975, baseline-corpus, source-trace, anti-fabrication]
tldr: "Memory for cybersec-skill-builder: mukul975 baseline corpus map, 4 invariants, what-worked / what-failed from cybersec_vertical Phase 1, decision_manifest references."
domain: "cybersec_skill construction"
created: "2026-05-30"
updated: "2026-05-30"
8f: "F1_constrain"
keywords: [cybersec_skill memory, mukul975 baseline, source-trace, anti-fabrication, capability gating, decision manifest, silent-absorb, lifted learnings]
density_score: 0.90
related:
  - bld_memory_skill
  - cybersec-skill-builder
  - bld_architecture_cybersec_skill
---

# Memory: cybersec-skill-builder

## Baseline Corpus Pointer (silent-absorb)

| Source | License | Mount path | Citation pool |
|--------|---------|-----------|---------------|
| mukul975/security-skills | Apache 2.0 | `_inbox/mukul975/skills/` | `_inbox/mukul975/references/standards.md` |
| (extensible) other baselines | Apache 2.0 / MIT | operator-mounted | per-source `references/standards.md` |

The mukul975 baseline is the canonical first source per Q5 LOCKED (silent absorb, no
rename). Future baselines may be added under the same Apache 2.0 / source-trace contract.

## Decision Manifest Lock-in (cybersec_vertical Phase 1)

| Question | Lock | Builder Implication |
|----------|------|---------------------|
| Q1 | LOCKED no bundles | One artifact per skill; never compose portable packs |
| Q3 | LOCKED capability-gated offensive | `authorized_use_only=true` triggers H_CG1-H_CG4 |
| Q5 | LOCKED silent absorb requires `source:` | H_AF4 mandatory |
| Q7 | LOCKED Gating Wrath canonical | Sin lens for builder identity (N05 nucleus) |
| Q10 | LOCKED U1 manual sync | No CI hooks; manual invocation only |
| Q11 | FULL-lattice anti-fabrication | 4 HARD gates (H_AF1-H_AF4) non-negotiable |
| Q12 | DURING absorption | AF gates fire at distillation time, not post-hoc |

## Learnings (from skill-builder + ai-rmf-profile-builder + safety-policy-builder)

1. Cybersec_skill is a SUBTYPE of skill, not a replacement -- inherit all skill semantics
2. Framework crosswalk patterns are best done as TABLES (NIST AI RMF builder precedent)
3. Citation discipline cannot be enforced at scoring layer alone -- HARD gates required
4. Distillation cost is dominated by source-grep verification, not body composition
5. Mukul975 baselines use `references/standards.md` as canonical citation index -- single-file grep target
6. Apache 2.0 attribution is preserved via `source:` path + license file co-location; no inline NOTICE block

## What Worked

1. Mapping cybersec to skill (P04 parent) preserved 80%+ of inherited semantics
2. AF gates as grep operations (not LLM judgment) made enforcement deterministic
3. Capability gating via `authorized_use_only` flag avoided per-skill RBAC duplication
4. Naming `cysk_` over `cs_` (collision with config_skill / case_study) reduced lookup ambiguity
5. P03 pillar (vs P04 skill) gave N05 ownership without conflicting with N03's skill-builder

## What Failed (during F4 reasoning, recorded for future variants)

1. Initial impulse to invent a new sin lens for cybersec -- REJECTED, Q7 LOCKED Gating Wrath
2. Initial impulse to bundle related skills into a "cybersec_pack" -- REJECTED, Q1 LOCKED no bundles
3. Initial impulse to auto-distill on baseline file-system change -- REJECTED, Q10 LOCKED U1 manual
4. Initial impulse to score AF compliance at SOFT layer -- REJECTED, Q11 demands HARD gates

## Key Invariants (memory-injected at F3 for every build)

| Invariant | Enforcement Layer |
|-----------|-------------------|
| Every cited code traces to source | F7 GOVERN (H_AF1-H_AF3 grep) |
| `source:` path resolves on disk | F7 GOVERN (H_AF4 test -e) |
| Offensive skills carry full gating triple | F7 GOVERN (H_CG1-H_CG4) |
| quality is null at write time | F7 GOVERN (H04 universal) |
| Single artifact per skill | F1 CONSTRAIN |
| Manual invocation only | F1 CONSTRAIN |

## Cross-Framework Recall (when injecting at F3)

| Framework | When to inject | Use |
|-----------|---------------|-----|
| MITRE ATT&CK | Always (offensive technique mapping) | `frameworks:` enumeration |
| MITRE ATLAS | When `domain_subtype=ai_security` | AI/ML adversarial technique pool |
| NIST CSF | When defensive / audit skill | Control-id crosswalk for compliance_framework |
| NIST AI RMF | When AI system in scope | Crosswalk to existing ai_rmf_profile artifacts |
| CVE-MITRE | When skill targets specific vulnerability | Source-traceable CVE ID for finding output |

## Metadata

```yaml
id: bld_memory_cybersec_skill
pipeline: 8F + AF lattice
scoring: hybrid_3_layer
sin_lens: gating_wrath
```

## Properties

| Property | Value |
|----------|-------|
| Kind | `memory` |
| Pillar | P09 |
| Domain | cybersec_skill construction |
| Pipeline | 8F (F1-F8) |
| Scorer | cex_score.py |
| Compiler | cex_compile.py |
| Retriever | cex_retriever.py |
| Quality target | 9.0+ |
| Density target | 0.85+ |

## Related Artifacts

| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[bld_memory_skill]] | parent | 0.60 |
| [[cybersec-skill-builder]] | upstream | 0.55 |
| [[bld_architecture_cybersec_skill]] | upstream | 0.50 |
