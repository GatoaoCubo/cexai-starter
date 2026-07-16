---
quality: null
quality: null
id: p11_collab_revision_loop_policy
kind: handoff
pillar: P12
llm_function: COLLABORATE
purpose: F8 COLLABORATE signals and handoff protocol for revision_loop_policy builder
title: "Collaboration: Revision Loop Policy Builder"
version: "1.0.0"
author: n03_builder
tags:
 - "collaboration"
 - "revision_loop_policy"
 - "builder"
 - "p12"
 - "f8"
 - "signals"
 - "handoff"
domain: "revision_loop_policy construction"
created: "2026-04-18"
updated: "2026-04-18"
tldr: "F8 COLLABORATE signals and handoff protocol for revision_loop_policy builder"
8f: "F8_collaborate"
keywords:
 - "revision_loop_policy construction"
 - "revision loop policy builder"
 - "collaboration"
 - "revision_loop_policy"
 - "builder"
 - "signals"
 - "handoff"
 - "### signal format"
 - "on build complete"
 - "signal format"
density_score: 0.87
related:
 - bld_orchestration_default
 - n00_revision_loop_policy_manifest
 - p11_collab_curation_nudge
 - kc_revision_loop_policy
 - p11_fb_revision_loop_policy
---
## F8 COLLABORATE Protocol

### On Build Complete
```bash
# 1. Compile
python _tools/cex_compile.py {artifact_path}

# 2. Index (if available)
python _tools/cex_index.py 2>/dev/null || true

# 3. Commit
git add {artifact_path} {compiled_yaml_path}
git commit -m "[N03] build: revision_loop_policy/{name} via 8F pipeline"

# 4. Signal
python -c "from _tools.signal_writer import write_signal; write_signal('n03', 'complete', {score}, mission='revision_loop_policy_build')"
```

### Signal Format
```json
{
 "nucleus": "n03",
 "status": "complete",
 "quality_score": 9.0,
 "kind": "revision_loop_policy",
 "artifact": "p11_rlp_{name}.yaml",
 "mission": "revision_loop_policy_build",
 "timestamp": "{iso8601}"
}
```

### Handoff to N07 (on escalation)
When an artifact exhausts its revision budget and escalates to `senior_nucleus`:
```markdown
## Handoff: revision_loop_policy Escalation
Artifact: {artifact_path}
Iterations exhausted: {max_iterations}
Failing gates: {failing_gates}
Recommended action: review gate failures, adjust artifact manually or lower quality floor
```

### Cross-Builder Collaboration

| Builder | When to collaborate |
|---------|-------------------|
| `quality-gate-builder` | When defining per-gate thresholds embedded in revision cycles |
| `pipeline-template-builder` | When revision_loop_policy is embedded in a pipeline stage |
| `bugloop-builder` | When code-specific correction is needed alongside content revision |

### Upstream/Downstream

| Direction | System | Signal |
|-----------|--------|--------|
| Upstream | N07 orchestrator (dispatched this build) | Write signal on complete |
| Downstream | pipeline_template that references this policy | Policy `rlp_{{name}}` available for embedding |
| Peer | quality_gate artifacts (evaluated each iteration) | Read quality_gate results at F7 |

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[bld_orchestration_default]] | related | 0.34 |
| [[n00_revision_loop_policy_manifest]] | upstream | 0.31 |
| [[p11_collab_curation_nudge]] | sibling | 0.28 |
| [[kc_revision_loop_policy]] | upstream | 0.28 |
| [[p11_fb_revision_loop_policy]] | upstream | 0.27 |
