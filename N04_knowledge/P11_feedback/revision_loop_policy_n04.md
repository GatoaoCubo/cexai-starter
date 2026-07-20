---
id: revision_loop_policy_n04
kind: revision_loop_policy
8f: F7_govern
nucleus: n04
pillar: P11
mirrors: N00_genesis/compiled/tpl_revision_loop_policy.yaml
mirror_version: 1.0.0
promoted_from: null
overrides:
 tone: archival, dense, citation-thick
 voice: third-person encyclopedic
 sin_lens: Knowledge Gluttony
 required_fields:
 - sources
 - retrieval_method
 - freshness
 quality_threshold: 9.2
 density_target: 0.92
 example_corpus: 3+ examples with source manifest
max_iterations: 3
iteration_on_quality_floor: 8.5
priority_order:
 - citation_completeness # N04 extension: no claim without source
 - factual_accuracy # N04 extension: verify against corpus before passing
 - security
 - quality
 - implementation
version: 1.0.0
quality: null
tags: [mirror, n04, knowledge, revision_loop_policy, kind_import, fact_check]
keywords: [mirror, knowledge, revision_loop_policy, kind_import, fact_check, citation_missing, corpus_conflict, security_critical, documentation, last_verified]
updated: "2026-07-20"
related:
 - p11_fb_revision_loop_policy
 - revision-loop-policy-builder
when_to_use: "Load when working on revision_loop_policy in P11. Consult for how to act on this revision_loop_policy."
slots:
  artifact: "<the artifact to revise>"
  max_retries: "<retry budget before escalation>"
---

## Override Rationale

N04's fact-check loop mirrors the N00 revision policy but raises the priority of
**citation completeness** above all else -- Knowledge Gluttony demands that every
revised claim carries a traceable source. Factual accuracy is verified against the
active knowledge corpus before the iteration is counted.

## Revision Policy (N04 flavor)

| Parameter | Value | N04 Notes |
|-----------|-------|-----------|
| Quality floor | 8.5 | Trigger revision if score below |
| Priority 1 | citation_completeness | No fact without source -- N04 canonical |
| Priority 2 | factual_accuracy | Cross-check against corpus before accepting |
| Priority 3 | security | Inherited from N00 |
| Priority 4 | quality | Density >= 0.92 required |
| Priority 5 | implementation | Structural completeness |
| Escalation | user | After max_iterations exhausted without convergence |

## Scenario Overrides

| Scenario | Max Iterations | Rationale |
|----------|---------------|-----------|
| `citation_missing` | 4 | Extra cycle to locate source before accepting claim |
| `corpus_conflict` | 5 | Two sources disagree -- extra rounds for reconciliation |
| `security_critical` | 5 | Inherited from N00 |
| `documentation` | 2 | Quick documentation tasks need less cycling |

## Iteration Gate Checklist

Before counting an iteration as passing, N04 verifies:

1. **Source count**: >= 3 sources cited in body
2. **Freshness**: each source has a `last_verified` date <= 90 days old
3. **Retrieval method**: explicit (`dense | sparse | hybrid | graph`)
4. **Factual consistency**: no contradiction between cited sources
5. **Density**: body density_score >= 0.92

If any gate fails, the iteration is rejected and the loop retries.

## Links

- N00 archetype (builder ISOs): [[revision-loop-policy-builder]]
- N00 KC: [[kc_revision_loop_policy]]


### How to use

```text
You are the consuming agent that acts on this revision_loop_policy under F7 GOVERN.
- Resolve the open slots (artifact, max_retries) from the caller request.
- Honor every constraint and field contract declared above.
- Emit the result in the shape this revision_loop_policy defines; never improvise the schema.
```

### Procedure

```text
1. Load this artifact and read its contract under F7 GOVERN.
2. Bind artifact and max_retries from the incoming request.
3. Validate the inputs against the constraints declared above.
4. Execute the revision_loop_policy behavior; resolve each open slot at act-time.
5. Verify the output shape, then signal completion to the orchestrator.
```

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[p11_fb_revision_loop_policy]] | related | 0.24 |
| [[revision-loop-policy-builder]] | related | 0.24 |
