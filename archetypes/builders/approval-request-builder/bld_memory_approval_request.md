---
id: p10_lr_approval_request_builder
kind: learning_record
pillar: P10
version: 1.0.0
created: 2026-07-03
updated: 2026-07-03
author: builder_agent
observation: "This kind carries a documented PRIOR decision AGAINST scaffolding a builder: cexai/docs/adr_v03_governance_taxonomy.md (Accepted, N07, 2026-05-26) explicitly ships a LEAN registration (kinds_meta + KC + manifest only) and states verbatim: 'Deliberately OMITTED (documented here so a future wave does not fix a phantom gap): archetypes/builders/approval-request-builder/, .claude/agents/approval-request-builder.md, and a builder-authored schema.' Its own re-evaluation trigger: 'add a builder ONLY if an authoring flow (intent -> request) ever appears; today it is runtime-emitted.' The 2026-07-03 evidence-based triage (docs/DECISION_BUILDERLESS_KINDS_2026_07_03.md) reached verdict SCAFFOLD for this kind without citing or explicitly overriding that ADR section -- its own evidence trail (Sec 2.1 item 3) references the governance module's registration comment but not the ADR's builder-scope section specifically."
pattern: "Before scaffolding ANY builder-less kind, search for an existing decision_record/ADR that already evaluated builder-vs-lean-registration for that SPECIFIC kind (not just general kind-realness evidence). A kind being REAL (producer/consumer exists) does not automatically mean a builder is warranted -- runtime-emitted instance kinds (this one) can be simultaneously real AND deliberately builder-less by design. When such a prior ADR is found and a newer directive still requests scaffolding, PROCEED (the newer directive is presumably informed by a human/orchestrator decision at a level this builder cannot see) but (1) prominently cite the conflict for keystone/founder review, (2) design the new builder to be honest about the SECONDARY nature of its authoring flow rather than silently supplanting the ADR's stated primary-path facts, and (3) patch only the specific stale claims in kind-adjacent docs that the new builder's existence falsifies (never silently leave a proven-false statement standing)."
evidence: "cexai/cexai/governance/hitl/file_gate.py + cexai/cexai/governance/_shared/types.py confirm the runtime emission path is real, tested (31/31 passed, cexai/tests/governance/hitl/test_file_approval_gate.py, re-run 2026-07-03), and complete on its own -- no gap existed that required a builder to fill. The scaffold in this wave is additive (new directory, new files) and reversible (the ADR itself pre-registered: 'if the founder prefers to keep the registry at 301 and model approval requests as hitl_config instances, revert is trivial'), which is why proceeding-with-flagging was chosen over blocking outright."
confidence: 0.75
outcome: SUCCESS
domain: approval_request
tags:
  - approval-request
  - hitl
  - governance
  - adr-conflict
  - scaffold-vs-lean
  - runtime-emitted
quality: null
title: "Memory Approval Request"
tldr: "A prior ADR (2026-05-26) explicitly said do NOT scaffold this builder; the 2026-07-03 triage said SCAFFOLD anyway without citing that section. Proceeded + flagged for founder review; never silently overwrite a settled architectural decision."
impact_score: 8.6
decay_rate: 0.03
agent_group: builder
memory_scope: project
observation_types: [feedback, project, reference]
8f: "F7_govern"
keywords: [memory approval request, adr conflict, scaffold vs lean registration, runtime-emitted, prior decision record, approval-request-builder, cex_skill_loader.py, cex_memory_select.py, builder context this, pipeline blocks]
density_score: 0.88
llm_function: INJECT
related:
  - bld_knowledge_card_approval_request
  - p01_kc_approval_request
  - adr_v03_governance_taxonomy
  - p11_qg_approval_request
  - bld_config_approval_request
---
## Summary
`approval_request` is the first kind in this codebase's history where a scaffold wave collided
with an EXPLICIT, ACCEPTED, prior decision against scaffolding. The lesson is procedural, not just
domain-specific: kind-realness evidence and builder-scope decisions are TWO SEPARATE QUESTIONS, and
a triage that only checks the former can silently override the latter.

## Pattern
**Two separate questions**: (1) "is this kind real / does it have a genuine producer-consumer?" and
(2) "should authoring of this kind go through a 12-ISO builder pipeline, or is a LEAN registration
(kinds_meta + KC + manifest, no builder) the correct, deliberate shape?" A kind can pass (1) with
overwhelming evidence (this kind: a frozen dataclass, a concrete gate implementation, 31/31 passing
tests) while a prior, reasoned ADR already answered (2) in the negative, FOR EXACTLY THIS KIND,
because instances are emitted by running code, not authored from intent.

**Detecting the conflict**: `Glob`/`Grep` for `decision_record`/ADR files mentioning the kind name
BEFORE writing a single builder file -- not just the KC and kinds_meta entry. This session found
`cexai/docs/adr_v03_governance_taxonomy.md` only because Sec 2.1's own evidence trail (in the newer
triage doc) pointed at `cexai/cexai/governance/__init__.py:22-25`'s comment about "a dedicated W3b
ADR cell," which led one hop further to the ADR itself.

**Resolving the conflict without unilaterally overruling an upstream decision**: when the CURRENT
directive is explicit, recent, framed as already-GDP-closed, and the requested change is additive
+ reversible, proceed -- but make the tension impossible to miss: cite the ADR verbatim in the
builder's own Identity/Boundary sections (not just in a private note), patch the specific stale
claims the new builder falsifies (surgical edits only, never a rewrite), and flag the conflict at
the top of the completion report for founder/keystone review.

## Anti-Pattern
1. Scaffolding a builder for a runtime-emitted kind without checking for a prior ADR that already
   decided against it -- risks contradicting a founder-reviewed decision silently.
2. Treating "the kind is real" as sufficient justification for "the kind needs a builder" -- these
   are independent questions; this kind proves a kind can be maximally real and deliberately
   builder-less at the same time.
3. Leaving a stale "there is no 12-ISO builder for this kind" claim standing in the KC/manifest
   after scaffolding one -- an unpatched contradiction is a self-inflicted credibility gap.
4. Silently blocking on a conflict without executing an additive, reversible, explicitly-directed
   task -- under-delivers relative to the mandate when the blast radius does not justify a halt.
5. Presenting a synthetic scaffold as if it now IS the live runtime path -- the builder must state,
   every time, that runtime emission via `ApprovalGate.request()` remains canonical.

## Builder Context
This ISO operates within the `approval-request-builder` stack, one of 300+
specialized builders in the CEX architecture. Loads via `cex_skill_loader.py`
at pipeline stage F3, merged with relevant memory from `cex_memory_select.py`,
producing artifacts that pass the quality gate at F7.

| Component | Purpose |
|-----------|---------|
| System prompt | Identity and behavioral rules |
| Instruction | Step-by-step procedure |
| Output template | Structural scaffold |
| Quality gate | Scoring rubric |
| Examples | Few-shot references |

## Reference

```yaml
id: p10_lr_approval_request_builder
pipeline: 8F
scoring: hybrid_3_layer
target: 9.0
```

```bash
python _tools/cex_score.py --apply --verbose p10_lr_approval_request_builder.md
```

## Properties

| Property | Value |
|----------|-------|
| Kind | `learning_record` |
| Pillar | P10 |
| Domain | approval_request |
| Pipeline | 8F |
| Scorer | cex_score.py |
| Compiler | cex_compile.py |
| Retriever | cex_retriever.py |
| Target | 9.0+ |
| Density | 0.85+ |

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[bld_knowledge_card_approval_request]] | upstream | 0.45 |
| [[p01_kc_approval_request]] | downstream | 0.40 |
| [[adr_v03_governance_taxonomy]] | upstream (the conflicting prior decision) | 0.50 |
| [[p11_qg_approval_request]] | downstream | 0.32 |
| [[bld_config_approval_request]] | upstream | 0.30 |
