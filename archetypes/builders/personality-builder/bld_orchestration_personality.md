---
kind: collaboration_config
id: bld_collaboration_personality
pillar: P12
llm_function: COLLABORATE
purpose: F8 collaboration protocol for personality-builder -- save, compile, signal
quality: null
title: "Collaboration: personality-builder"
version: "1.0.0"
author: n03_builder
tags:
  - "personality"
  - "builder"
  - "collaboration"
  - "P12"
  - "hermes_origin"
  - "F8"
tldr: "F8 protocol: save to P02, compile .md->.yaml, run doctor, commit, signal n03 complete."
domain: "persona construction"
created: "2026-04-18"
updated: "2026-04-18"
8f: "F8_collaborate"
keywords:
  - "persona construction"
  - "save to p"
  - "run doctor"
  - "signal n"
  - "personality"
  - "builder"
  - "collaboration"
  - "hermes_origin"
  - "## save location"
  - "## compile"
density_score: 0.87
related:
  - bld_architecture_personality
  - bld_memory_personality
  - bld_tools_personality
  - kc_personality
---
# Collaboration: personality-builder

## F8 COLLABORATE Checklist

```
[ ] 1. Save artifact to correct pillar directory
[ ] 2. Run cex_compile.py on saved file
[ ] 3. Run cex_doctor.py (quick health check)
[ ] 4. git add + git commit with standard message
[ ] 5. Signal complete via signal_writer
```

## Save Location
```
Archetype:  N00_genesis/P02_model/p02_per_{{name}}.md
Nucleus:    N0X_*/P02_model/p02_per_{{name}}.md
Compiled:   same dir / compiled/p02_per_{{name}}.yaml
```

## Compile
```bash
python _tools/cex_compile.py N00_genesis/P02_model/p02_per_{{name}}.md
# OR for all:
python _tools/cex_compile.py --all
```

## Commit Message Format
```
[N03] personality: add per_{{name}} ({{register}}/{{verbosity}}/{{humor}}, {{value_count}} values)
```

## Signal
```python
from _tools.signal_writer import write_signal
write_signal('n03', 'complete', 9.0, mission='personality_built', kind='personality', name='{{name}}')
```

## Cross-Nucleus Handoff

| Consumer | How they use personality |
|----------|------------------------|
| N03 (builder) | Produces personality artifacts via this builder |
| Any agent (N01-N07) | Reads p02_per_{{name}}.md from P02 at runtime via /personality command |
| N07 (orchestrator) | Dispatches personality build tasks to N03 |
| user_model (N04) | May store preferred_personality in user_model.preferences collection |

## A2A Signal Schema
```json
{
  "nucleus": "n03",
  "status": "complete",
  "score": 9.0,
  "mission": "personality_built",
  "kind": "personality",
  "artifact_id": "per_{{name}}",
  "path": "N00_genesis/P02_model/p02_per_{{name}}.md"
}
```

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[bld_architecture_personality]] | upstream | 0.44 |
| [[bld_memory_personality]] | upstream | 0.41 |
| [[bld_tools_personality]] | upstream | 0.39 |
| [[kc_personality]] | upstream | 0.31 |
| n00_personality_manifest | upstream | 0.31 |
