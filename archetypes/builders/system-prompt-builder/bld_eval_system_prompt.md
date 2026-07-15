---
kind: quality_gate
id: p11_qg_system_prompt
pillar: P03
llm_function: GOVERN
purpose: Golden and anti-examples of system_prompt artifacts
pattern: "few-shot learning \u2014 LLM reads these before producing"
quality: null
title: 'Gate: System Prompt'
version: 1.0.0
author: builder
tags:
- eval
- P03
- quality_gate
- examples
tldr: Validates LLM identity and persona prompts for specificity, safety constraints,
  and behavioral clarity.
domain: system_prompt
created: '2026-03-27'
updated: '2026-03-27'
8f: "F7_govern"
keywords: [system prompt, safety constraints, system_prompt, persona, tone]
density_score: 0.85
related:
  - system-prompt-builder
  - bld_collaboration_system_prompt
  - bld_memory_system_prompt
  - action-prompt-builder
  - bld_knowledge_card_system_prompt
---
## Quality Gate

## Definition
A system prompt establishes the identity, rules, and behavioral boundaries of a language model for a specific domain or role. It is not a task instruction and not a template with placeholders. This gate ensures every system prompt is specific, safe, self-contained, and clearly separated from prompt templates and action prompts.
## HARD Gates
Failure on any HARD gate causes immediate REJECT. No score is computed.
| ID  | Check | Rule |
|-----|-------|------|
| H01 | Frontmatter parses | YAML frontmatter is valid and complete with no syntax errors |
| H02 | ID matches namespace | `id` matches pattern `^p03_sp_[a-z][a-z0-9_]+$` |
| H03 | ID equals filename | `id` slug matches the parent directory or filename stem |
| H04 | Kind matches literal | `kind` is exactly `system_prompt` |
| H05 | Quality is null | `quality` field is `null` (not yet scored) |
| H06 | Required fields present | `domain`, `persona`, `tone`, `knowledge_boundary` all defined and non-empty |
## SOFT Scoring
Score each dimension 0 or 10. Multiply by weight. Divide total by sum of weights, scale to 0-10.
| Dimension | Weight | Pass Condition |
|-----------|--------|----------------|
| Density >= 0.80 | 1.0 | Prompt is tight; no filler prose or redundant restatements |
| Persona is domain-specific | 1.0 | Identity describes a concrete role, not a generic "helpful assistant" |
| Rules have justification | 0.5 | Each ALWAYS/NEVER rule states why it exists |
| Knowledge boundary defined | 1.0 | `knowledge_boundary` field specifies what the model knows and does not know |
| Tone calibrated for domain | 0.5 | Tone matches the domain audience (technical, conversational, formal, etc.) |
| Tags include system-prompt | 0.5 | `tags` list contains `"system-prompt"` |
Sum of weights: 9.0. `soft_score = sum(weight * gate_score) / 9.0 * 10`
## Actions
| Score | Action |
|-------|--------|
| >= 9.5 | GOLDEN — archive to pool as reference system prompt |
| >= 8.0 | PUBLISH — safe to attach to production model configurations |
| >= 7.0 | REVIEW — usable but persona or constraints need sharpening |
| < 7.0 | REJECT — do not deploy; identity or safety gaps present |
## Bypass
| Field | Value |
|-------|-------|
| condition | Rapid prototyping in an isolated sandbox where the model has no external access |
| approver | Domain owner who defined the persona requirements |
| audit_log | Entry required in `.claude/bypasses/system_prompt_{date}.md` with sandbox proof |
| expiry | 7 days; prompt must reach PUBLISH score before moving out of sandbox |
H01 (frontmatter parses) and H05 (quality is null) cannot be bypassed under any condition.

## Examples

# Examples: system-prompt-builder
## Golden Example
INPUT: "Create system prompt for the knowledge-card-builder agent"
OUTPUT:
```yaml
id: p03_sp_knowledge_card_builder
kind: system_prompt
pillar: P03
version: "1.0.0"
created: "2026-03-26"
updated: "2026-03-26"
author: "builder"
title: "Knowledge Card Builder System Prompt"
```
## Identity
You are knowledge-card-builder, a CEX archetype specialist.
You know EVERYTHING about knowledge distillation: atomic facts, density scoring,
bullet compression, source attribution, and the boundary between knowledge_cards (P01),
context_docs (P01), and glossary_entries (P01).
You produce knowledge_card artifacts with dense bullets and verified sources, no filler.
## Rules
1. ALWAYS read SCHEMA.md first; it is the source of truth
2. NEVER self-assign quality score (quality: null always)
3. ALWAYS write bullets <= 80 chars with concrete data
4. NEVER include internal paths (records/, .claude/, /home/)
5. ALWAYS achieve density_score >= 0.80 (no filler phrases)
6. ALWAYS include >= 4 body sections with >= 3 lines each
7. NEVER produce context_doc or glossary_entry — redirect to correct builder
8. ALWAYS verify sources exist before citing
## Output Format
- Format: YAML frontmatter + markdown body
- Sections: TL;DR, Conceitos, Regras de Ouro, Comparativo, Flow, References
- Constraints: body 200-5120 bytes, bullets max 80 chars
## Constraints
Knowledge boundary: CEX knowledge system, distillation patterns, P01 schema. Does NOT know agent routing, deployment infra, or marketing copy.
I do NOT: route tasks, deploy agents, generate marketing content.
If asked outside my boundary, I say so and suggest the correct builder.
WHY THIS IS GOLDEN:
- quality: null (H05 pass)
- id matches p03_sp_ pattern (H02 pass)
- kind: system_prompt (H04 pass)
- 19 required fields present (H06 pass)
## Anti-Example
INPUT: "Create system prompt for a helper agent"
BAD OUTPUT:
```yaml
id: helper_prompt
kind: prompt
pillar: prompt
title: Helper
target_agent: helper
quality: 8.5
rules_count: 2
tone: friendly
tags: [helper]
tldr: "This is a system prompt for a helpful assistant that helps users with various tasks and provides assistance."
```
You are a helpful assistant. You help users with tasks. Be nice and provide good answers.

### S_RELATED
-0.3 if `related:` < 3 or body lacks Related Artifacts

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[system-prompt-builder]] | related | 0.47 |
| [[bld_orchestration_system_prompt]] | related | 0.37 |
| [[bld_memory_system_prompt]] | downstream | 0.34 |
| [[action-prompt-builder]] | related | 0.34 |
| [[bld_knowledge_system_prompt]] | related | 0.33 |
