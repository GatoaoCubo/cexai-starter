---
quality: null
quality: null
kind: tools
id: bld_tools_prospective_memory
pillar: P04
llm_function: CALL
purpose: Tools for prospective_memory production
title: "Tools Prospective Memory"
version: "1.0.0"
author: n03_builder
tags: [prospective_memory, builder, tools]
tldr: "Tools for prospective_memory production."
domain: "prospective memory construction"
created: "2026-04-17"
updated: "2026-04-17"
8f: "F5_call"
keywords: [tools for prospective_memory production, prospective memory construction, tools prospective memory, prospective_memory, builder, tools, ^p10_pm_, production tools, execution mechanisms reference, claude code]
density_score: 0.90
related:
  - bld_tools_episodic_memory
  - bld_tools_default
  - bld_tools_data_contract
  - bld_tools_pipeline_template
  - bld_tools_cli_tool
---
# Tools: prospective-memory-builder

## Production Tools
| Tool | Purpose | When | Status |
|------|---------|------|--------|
| cex_retriever.py | Find similar prospective_memory artifacts | Phase 1 | AVAILABLE |
| cex_score.py | Score artifact | Phase 3 | AVAILABLE |
| cex_compile.py | Compile to yaml | Phase 3 | AVAILABLE |

## Execution Mechanisms Reference
| Mechanism | CEX Tool | Notes |
|-----------|---------|-------|
| schedule_signal | ScheduleWakeup (Claude Code) | Native Claude Code scheduling |
| polling | cex_signal_watch.py | Polling loop for condition triggers |
| wake_notification | boot/cex.ps1 | Session-start check of pending reminders |

## Tool Permissions
| Category | Tools | Status |
|----------|-------|--------|
| ALLOWED | Read, Write, Edit, Bash, Glob, Grep | Permitted |
| EFFECTIVE | Bash, Edit, Glob, Grep, Read, Write | |

## Validation
id `^p10_pm_`, owner non-empty, reminders >= 1, trigger_type per reminder, action_payload non-vague, execution_mechanism declared, quality null, body <= 2048 bytes.

## Tool Integration Checklist

- Verify tool name follows snake_case convention
- Validate input/output schema matches interface contract
- Cross-reference with capability_registry for discoverability
- Test tool invocation in sandbox before production use

## Invocation Pattern

```yaml
# Tool invocation contract
name: tool_name
input_schema: validated
output_schema: validated
error_handling: defined
timeout: configured
```

```bash
python _tools/cex_compile.py {FILE}
python _tools/cex_doctor.py --scope {BUILDER}
```

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[bld_tools_episodic_memory]] | sibling | 0.50 |
| [[bld_tools_default]] | related | 0.37 |
| [[bld_tools_data_contract]] | downstream | 0.36 |
| [[bld_tools_pipeline_template]] | sibling | 0.35 |
| [[bld_tools_cli_tool]] | sibling | 0.34 |
