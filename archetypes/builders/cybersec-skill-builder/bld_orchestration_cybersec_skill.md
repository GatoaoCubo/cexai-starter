---
kind: collaboration
id: bld_collaboration_cybersec_skill
pillar: P12
llm_function: COLLABORATE
purpose: How cybersec-skill-builder works in crews with other builders + commit pattern
pattern: each builder must know its ROLE in a team, what it RECEIVES and PRODUCES, and how it signals
quality: null
title: "Collaboration Cybersec Skill"
version: "1.0.0"
author: n03_builder
tags: [cybersec_skill, builder, collaboration, P12, F8, commit-pattern, dogfood-loop]
tldr: "Cybersec-skill-builder collaboration: receives baseline + frameworks list; produces 1 cybersec_skill; commit pattern `[N05] cybersec/<domain>/<skill>: distill 1 source -> N derived (F7c PASS)`; dogfood loop with N05 capability_registry-builder + N04 audit_log-builder."
domain: "cybersec_skill construction"
created: "2026-05-30"
updated: "2026-05-30"
8f: "F8_collaborate"
keywords: [cybersec_skill collaboration, dogfood loop, commit pattern, capability_registry handoff, audit_log handoff, F7c PASS, mukul975 distillation crew]
density_score: 0.90
related:
  - cybersec-skill-builder
  - bld_architecture_cybersec_skill
  - bld_memory_cybersec_skill
---

# Collaboration: cybersec-skill-builder

## My Role in Crews

I am a SPECIALIST. I answer ONE question: "what cybersec capability does this baseline encode, with which framework codes, under which authorization?"

I do not write generic skills (delegate to `skill-builder`). I do not author `safety_policy` (delegate to `safety-policy-builder`). I do not define `compliance_framework` mappings (delegate to `compliance-framework-builder`). I do not implement live offensive tools (delegate to `mcp-server-builder` + `sandbox-spec-builder`).

I produce cybersec_skill artifacts so downstream builders can integrate them into agents (P02), workflows (P12), and capability registries (P11).

## Crew Compositions

### Crew: "Defensive Cybersec Skill End-to-End"

```
1. knowledge-card-builder     -> "domain KC for cybersec capability"
2. cybersec-skill-builder     -> "cybersec_skill (distilled from baseline)"
3. instruction-builder         -> "execution steps for skill usage"
4. agent-builder               -> "agent that uses this skill"
```

Output: 1 cybersec_skill ready for N05 dispatch.

### Crew: "Offensive Cybersec Skill (capability-gated)"

```
1. capability_registry-builder -> "register the offensive capability principal"
2. cybersec-skill-builder      -> "cybersec_skill with authorized_use_only=true"
3. audit-log-builder            -> "audit_log spec for per-invocation event"
4. guardrail-builder            -> "boundary constraint for cross-skill misuse"
```

Output: 1 cybersec_skill + 1 capability_registry + 1 audit_log + 1 guardrail.

### Crew: "Cybersec Vertical Phase 1 (all-3-domain parallel)"

```
Parallel cell A (ai_security):  cybersec-skill-builder x N (per mukul975 ai_security skill)
Parallel cell B (cloud):        cybersec-skill-builder x N (per mukul975 cloud skill)
Parallel cell C (dfir):         cybersec-skill-builder x N (per mukul975 dfir skill)
Consolidate (N07):              dispatch.sh stop -> doctor -> commit
```

Output: N x 3 cybersec_skill artifacts (one per absorbed baseline).

## What I Receive

- Source path to baseline skill directory (Apache 2.0)
- `references/standards.md` for citation pool
- `domain_subtype` choice + `authorized_use_only` decision (from caller)
- `frameworks:` target list (validated against citation pool)
- If offensive: `capability_registry` skill_id + `disclaimer` path

## What I Produce

- 1 cybersec_skill artifact (frontmatter + 8 body sections)
- F7c-passing AF self-check evidence (logged in commit message)
- Optionally: a handoff payload to capability_registry-builder for offensive variants

## Commit Pattern (per cybersec_vertical Phase 1)

```
[N05] cybersec/<domain>/<skill>: distill 1 source -> N derived (F7c PASS)
```

Examples:
- `[N05] cybersec/ai_security/detecting_prompt_injection: distill 1 source -> 1 derived (F7c PASS)`
- `[N05] cybersec/cloud/aws_cloudtrail_baseline: distill 1 source -> 1 derived (F7c PASS)`
- `[N05] cybersec/dfir/windows_shellbag_analysis: distill 1 source -> 1 derived (F7c PASS)`

`F7c PASS` = consensus across the 4 AF gates + scoring rubric (>= 9.0). If F7c fails, the
commit is `(F7c FAIL: AF_gate=<id> reason=<missing_code>)` and the cell escalates to N07
for guidance per the Correction Protocol in `bld_feedback_cybersec_skill.md`.

## Signal Protocol

```python
from _tools.signal_writer import write_signal
write_signal(
    nucleus='n05',
    status='complete',
    score=9.0,
    payload={
        'kind': 'cybersec_skill',
        'skill_id': 'p03_cysk_<name>',
        'source': '<path>',
        'af_gates_passed': 4,
        'cg_gates_applicable': 0,
        'authorized_use_only': False
    }
)
```

## Dogfood Loop (Q12 DURING absorption)

The cybersec_vertical Phase 1 mandates the dogfood-first model: every absorbed baseline
becomes a cybersec_skill that the N05 cybersec-skill-builder ITSELF can later distill from
again on re-absorption (e.g. mukul975 baseline updates). The loop:

1. Absorb v1 baseline -> produce v1 cybersec_skill (commit)
2. Mukul975 updates baseline -> re-run cybersec-skill-builder with same skill_id
3. Diff v2 vs v1 -- AF gates verify new citations also trace to updated source
4. Bump `version:` field; preserve `created:` date; update `updated:`
5. Commit pattern: `[N05] cybersec/<domain>/<skill>: refresh v1->v2 (F7c PASS)`

This is manual per Q10 LOCKED -- no CI auto-trigger on baseline changes.

## Pipeline Integration

1. Created via 8F pipeline (F1-F8) + AF lattice (4 anti-fabrication gates)
2. Scored by cex_score across structural + rubric + semantic layers
3. Compiled by cex_compile for structural validation
4. Retrieved by cex_retriever for context injection in future cybersec_skill builds
5. Evolved by cex_evolve when quality regresses below 9.0
6. Re-absorbed manually when upstream baseline updates (dogfood loop)

## Properties

| Property | Value |
|----------|-------|
| Kind | `collaboration` |
| Pillar | P12 |
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
| [[cybersec-skill-builder]] | upstream | 0.68 |
| [[bld_architecture_cybersec_skill]] | upstream | 0.55 |
| [[bld_memory_cybersec_skill]] | upstream | 0.52 |
