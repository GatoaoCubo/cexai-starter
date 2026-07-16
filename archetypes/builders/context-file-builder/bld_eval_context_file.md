---
kind: quality_gate
id: p11_qg_context_file
pillar: P03
llm_function: GOVERN
purpose: Golden and anti-examples of context_file artifacts
pattern: few-shot learning -- LLM reads these before producing
quality: null
title: 'Gate: context_file'
version: 1.0.0
author: n03_builder
tags:
- eval
- P03
- quality_gate
- examples
tldr: Validates context_file artifacts for correct scope, injection_point, instruction-only
  body, and inheritance chain integrity.
domain: context_file
created: '2026-04-18'
updated: '2026-04-18'
8f: "F7_govern"
keywords:
  - "^ctx_[a-z][a-z0-9_]+$"
  - "context_file"
  - "quality"
  - "scope"
  - "workspace"
  - "quality gate"
  - "gates failure"
density_score: 0.92
related:
  - context-file-builder
  - kc_context_file
  - ctx_{{scope}}
  - bld_memory_context_file
---
## Quality Gate

## Definition
A context_file is a static, project-scoped instruction file auto-injected into agent context.
It must carry behavioral rules (not facts, not template vars, not procedural recipes) and
be correctly scoped with a valid injection strategy. This gate ensures scope taxonomy
correctness, body instruction purity, byte budget compliance, and inheritance chain validity.

## HARD Gates
Failure on any HARD gate causes immediate REJECT. No score is computed.

| ID | Check | Rule |
|----|-------|------|
| H01 | Frontmatter parses | YAML frontmatter is valid with no syntax errors |
| H02 | id regex match | `id` matches `^ctx_[a-z][a-z0-9_]+$` |
| H03 | id equals filename stem | `id` slug matches the filename stem |
| H04 | kind literal | `kind` is exactly `context_file` |
| H05 | quality is null | `quality` field is `null` (never self-scored) |
| H06 | scope valid | `scope` is one of: `workspace`, `nucleus`, `session`, `global` |

## SOFT Scoring
Score each dimension 0 or 10. Multiply by weight. Scale to 0-10.

| Dimension | Weight | Pass Condition |
|-----------|--------|----------------|
| Byte budget respected | 1.0 | body_bytes <= max_bytes |
| No template vars in body | 1.0 | Body contains no `{{var}}` placeholders |
| No facts in body | 1.0 | Body contains behavioral rules only (no "X is defined as...", no citations) |
| inheritance_chain valid | 0.5 | All parent IDs in chain reference existing context_files |
| hermes_origin tag present | 0.5 | `tags` list contains `hermes_origin` |
| scope name in tags | 0.5 | `tags` list contains the scope value |

Sum of weights: 9.0. `soft_score = sum(weight * gate_score) / 9.0 * 10`

## Actions
| Score | Action |
|-------|--------|
| >= 9.5 | GOLDEN -- archive to reference context_file pool as reference |
| >= 8.0 | PUBLISH -- safe to activate for scope injection |
| >= 7.0 | REVIEW -- usable but scope or body needs clarification |
| < 7.0 | REJECT -- do not activate; injection will produce unreliable results |

## Bypass
| Field | Value |
|-------|-------|
| condition | Temporary session_scope file created during rapid prototyping (scope: session, expires on close) |
| approver | Nucleus owner for that session |
| audit_log | Entry in `.cex/runtime/decisions/` with session ID and bypass justification |
| expiry | Session close; no durable bypass allowed |

H01 (frontmatter parses) and H05 (quality is null) cannot be bypassed under any condition.

## Examples

# Examples: context-file-builder

## Golden Example 1 -- Workspace Scope (CLAUDE.md equivalent)
INPUT: "Create workspace context file for the CEX engineering repo"
OUTPUT:
```yaml
id: ctx_cex_workspace
kind: context_file
pillar: P03
title: "CEX Engineering Workspace Context"
scope: workspace
injection_point: session_start
inheritance_chain: []
max_bytes: 8192
```
## Build Rules
1. ALWAYS follow the 8F pipeline (F1-F8) for every artifact produced
2. NEVER commit without compiling (`python _tools/cex_compile.py {path}`) and signaling
3. ALWAYS set `quality: null` -- never self-score
4. NEVER use non-ASCII characters in .py or .ps1 files
5. ALWAYS save artifacts to the correct pillar directory before compiling

## Commit Rules
1. ALWAYS prefix commit messages with `[N0X] ` where X is the nucleus ID
2. NEVER amend published commits -- create a new commit instead
3. ALWAYS run `python _tools/cex_doctor.py` after wave completion

WHY THIS IS GOLDEN:
- scope: workspace + inheritance_chain: [] (root, correct for CLAUDE.md equivalent)
- injection_point: session_start (cheapest; rules are stable)
- body: instructions only -- no facts, no template vars, no procedural recipes
- quality: null (H05 pass)

---

## Golden Example 2 -- Nucleus Scope (per-builder conventions)
INPUT: "Create nucleus context file for N03 builder nucleus"
OUTPUT:
```yaml
id: ctx_n03_nucleus
kind: context_file
pillar: P03
title: "N03 Engineering Nucleus Build Conventions"
scope: nucleus
injection_point: session_start
inheritance_chain: [ctx_cex_workspace]
max_bytes: 4096
```
## ISO Structure Rules
1. ALWAYS produce all 12 ISOs for any new builder kind
2. ALWAYS name ISOs `bld_{iso_type}_{kind}.md` in kebab-case builder directory
3. NEVER skip bld_schema, bld_instruction, or bld_manifest ISOs -- they are mandatory

## Kind Registry Rules
1. ALWAYS update `_schema.yaml`, `kind_index.md`, `.cex/kinds_meta.json`, and p03_pc_cex_universal.md for any new kind
2. ALWAYS update sub-agent definition in `.claude/agents/{kind}-builder.md`

WHY THIS IS GOLDEN:
- scope: nucleus + applies_to_nuclei: [n03] (correctly scoped)
- inheritance_chain: [ctx_cex_workspace] (correctly inherits from broader scope)
- priority: 2 (correctly higher number than workspace priority: 1)
- body: new rules only; does NOT duplicate workspace rules (child extends parent)

---

### S_RELATED: Cross-Reference Check (SOFT)
- [ ] `related:` frontmatter field populated (3-15 entries)
- [ ] `## Related Artifacts` section present in artifact body
- [ ] At least 1 upstream and 1 downstream reference
- Penalty: -0.3 if empty (does not block, encourages wiring)
