---
kind: tools
id: bld_tools_session_state
pillar: P04
llm_function: CALL
purpose: Tools and runtime surfaces relevant to session_state production
quality: null
title: "Tools Session State"
version: "1.0.0"
author: n03_builder
tags: [session_state, builder, examples]
tldr: "Golden and anti-examples for session state construction, demonstrating ideal structure and common pitfalls."
domain: "session state construction"
created: "2026-04-07"
updated: "2026-04-07"
8f: "F5_call"
keywords: [session state construction, tools session state, session_state, builder, examples, brain_query, validate_artifact.py, p10_memory/_schema.yaml, p10_memory/templates/tpl_session_state.md, "p10_memory/compiled/p10_ss_{session}.yaml"]
density_score: 0.90
related:
  - bld_tools_dag
  - bld_tools_signal
  - bld_tools_runtime_state
  - bld_tools_handoff
  - bld_tools_retriever_config
---

# Tools: session-state-builder
## Production Tools
| Tool | Purpose | When | Status |
|------|---------|------|--------|
| `brain_query` | Search for existing session states | Phase 1 | CONDITIONAL [MCP] |
| `validate_artifact.py` | Generic artifact validator | Phase 3 | [PLANNED] |
## Runtime Interfaces
| Interface | Path | Use |
|-----------|------|-----|
| P10 schema | `P10_memory/_schema.yaml` | naming, machine format, limits |
| Session template | `P10_memory/templates/tpl_session_state.md` | human reference |
| Compiled output | `P10_memory/compiled/p10_ss_{session}.yaml` | production target |
## Tool Permissions

| Category | Tools | Status |
|----------|-------|--------|
| ALLOWED | Read, Write, Edit, Bash, Glob, Grep | Explicitly permitted |
| DENIED | (none) | Explicitly blocked |
| EFFECTIVE | Bash, Edit, Glob, Grep, Read, Write | ALLOWED minus DENIED |

## Interim Validation
Until a generic validator exists, validate manually:
1. filename matches `p10_ss_{session}.yaml`
2. YAML parses
3. required fields present
4. status in enum
5. started_at is ISO 8601
6. payload fits `session_state`, not `runtime_state` or `learning_record`

## Metadata

```yaml
id: bld_tools_session_state
pipeline: 8F
scoring: hybrid_3_layer
```

```bash
python _tools/cex_score.py --apply bld-tools-session-state.md
```

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| bld_tools_dag | sibling | 0.49 |
| [[bld_tools_signal]] | sibling | 0.49 |
| [[bld_tools_runtime_state]] | sibling | 0.47 |
| bld_tools_handoff | sibling | 0.47 |
| [[bld_tools_retriever_config]] | sibling | 0.45 |
