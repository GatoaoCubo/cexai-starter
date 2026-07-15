---
kind: collaboration
id: bld_collaboration_context_file
pillar: P03
llm_function: COLLABORATE
purpose: How context-file-builder works in crews with other builders
pattern: each builder must know its ROLE in a team, what it RECEIVES and PRODUCES
quality: null
title: "Collaboration: context-file-builder"
version: "1.0.0"
author: n03_builder
tags: [context_file, builder, collaboration, hermes_origin]
tldr: "Collaboration protocol for context-file-builder: crew roles, handoff protocol, upstream/downstream builders."
domain: "workspace instruction auto-injection"
created: "2026-04-18"
updated: "2026-04-18"
8f: "F3_inject"
keywords: [workspace instruction auto-injection, collaboration protocol for context-file-builder, crew roles, handoff protocol, downstream builders, context_file, builder, collaboration, hermes_origin, "### crew: nucleus setup"]
density_score: 0.90
related:
 - bld_collaboration_system_prompt
 - context-file-builder
 - n00_context_file_manifest
 - kc_context_file
 - bld_collaboration_agent
---
# Collaboration: context-file-builder

## My Role in Crews
I am a SCOPE INSTRUCTION SPECIALIST. I answer ONE question: "what standing behavioral rules
apply to this scope and how should they auto-inject?"
I define scope taxonomy, injection strategy, inheritance chains, and instruction body.
I do NOT write agent identity (system_prompt), domain facts (knowledge_card), parameterized
templates (prompt_template), or task-scoped recipes (instruction kind).

## Crew Compositions

### Crew: "Workspace Bootstrap"
```
 1. knowledge-card-builder -> "provides domain KC to establish facts for the workspace"
 2. context-file-builder -> "builds standing workspace instructions (CLAUDE.md pattern)"
 3. system-prompt-builder -> "defines agent identity that uses the context_file"
```

### Crew: "Nucleus Setup"
```
 1. system-prompt-builder -> "defines nucleus identity (BECOME layer)"
 2. context-file-builder -> "adds nucleus-scoped standing rules (INJECT layer)"
 3. agent-builder -> "assembles full agent definition referencing both"
```

### Crew: "kind assimilation Wave"
```
 1. context-file-builder -> "workspace/nucleus context for assimilated kinds"
 2. messaging-gateway-builder -> "multi-platform transport stub"
 3. personality-builder -> "SOUL.md hot-swap persona overlay"
```

## Handoff Protocol

### I Receive
- seeds: target scope name, scope_type (workspace/nucleus/session/global), applies_to_nuclei
- optional: existing context_files in inheritance chain, priority number, byte budget
- optional: list of behavioral rules derived from domain conventions

### I Produce
- `context_file` artifact (YAML frontmatter 13 fields + instruction-only body sections)
- committed to: `N0X_{domain}/P03_prompt/ctx_{scope}.md` or project root
- compilation: `python _tools/cex_compile.py {path}`

### I Signal
- signal: complete (with quality score from bld_quality_gate_context_file.md)
- if quality < 8.0: signal retry with specific gate failures

## Builders I Depend On
| Builder | Why |
|---------|-----|
| knowledge-card-builder | Domain KCs inform which facts to exclude from context_file body (facts go in KC, not here) |
| system-prompt-builder | Agent identity defines the context in which context_file rules apply |

## Builders That Depend On Me
| Builder | Why |
|---------|-----|
| agent-builder | Agent definitions reference which context_files to load at which injection_points |
| system-prompt-builder | System prompts may reference workspace context_file for project conventions |
| workflow-builder | Workflow definitions benefit from workspace/nucleus context_files for standing rules |
| agents-md-builder | AGENTS.md is a multi-agent coordination context_file variant |

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[bld_orchestration_system_prompt]] | sibling | 0.41 |
| [[context-file-builder]] | related | 0.41 |
| n00_context_file_manifest | related | 0.37 |
| [[kc_context_file]] | upstream | 0.37 |
| [[bld_orchestration_agent]] | sibling | 0.35 |
