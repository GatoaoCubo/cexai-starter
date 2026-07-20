---
id: p01_kc_skill
kind: knowledge_card
8f: F3_inject
type: kind
pillar: P04
title: "Skill — Deep Knowledge for skill"
version: 1.1.0
created: 2026-04-02
updated: 2026-07-17
author: n04_knowledge
domain: skill
quality: null
tags: [skill, P04, BECOME, kind-kc]
tldr: "Reusable, phase-structured capability with an explicit trigger (AgentSkills.io / Semantic Kernel pattern), invoked by name, no identity"
when_to_use: "Building, reviewing, or reasoning about skill artifacts"
keywords: [skill, phases, trigger, user_invocable, AgentSkills, Semantic Kernel, progressive disclosure]
feeds_kinds: [skill]
density_score: null
related:
  - p01_kc_hook
  - p01_kc_agent
  - p01_kc_action_prompt
  - p01_kc_workflow
  - p01_kc_function_def
---

# Skill

## Spec
```yaml
kind: skill
pillar: P04
llm_function: BECOME
max_bytes: 5120
naming: p04_skill_{{name}}.md
```
Source: kinds_meta.json (the `.cex/` kind registry, skill entry) -- corrects a prior drift where
this card claimed `llm_function: TOOL` (not one of the 8 canonical
llm_function verbs). `max_bytes` is not set in kinds_meta.json for this kind;
5120 (body only) comes from schema_ref
`archetypes/builders/skill-builder/bld_schema_skill.md`, which also records a
`+ .yaml` naming suffix kinds_meta's bare `p04_skill_{{name}}.md` does not
carry -- noted, not silently merged.

## What It Is
A skill is a reusable, phase-structured capability with an explicit trigger
-- "Reusable capability with trigger + phases (AgentSkills.io / Semantic
Kernel pattern)" per kinds_meta.json (the `.cex/` registry, skill.description). It answers
"what capability, invoked how, in what phases?" -- never "who am I?" (`agent`,
P02, identity/persona) nor "what are the cross-role steps?" (`workflow`, P12)
nor "do this one thing now" (`action_prompt`, P03, single-turn, no phases).
CEX mirrors the open Agent Skills format: minimal frontmatter (name +
description at minimum), read in full only when its trigger matches --
"progressive disclosure" in three stages: Discovery, Activation, Execution.
Originated by Anthropic, released as an open standard, now adopted by 26+
agent platforms including Claude Code (source: agentskills.io/home).

## Cross-Framework Map
| Framework | Concept | Notes |
|---|---|---|
| AgentSkills.io (open standard) | SKILL.md: name+description (min), scripts/, references/, assets/ | Discovery -> Activation -> Execution (source: agentskills.io/home) |
| Claude Code (Anthropic) | `.claude/skills/{name}/SKILL.md`, Skill tool | Format originated here pre-standard |
| Microsoft Semantic Kernel | `KernelPlugin` / `KernelFunction` | Named function grouped into a plugin |
| LangChain | `@tool`-decorated function / `StructuredTool` | Callable capability, no persona |

## Key Parameters
| Parameter | Type | Default | Tradeoff |
|---|---|---|---|
| user_invocable | bool | false | true requires a slash `trigger`; false = agent/event-invoked |
| trigger | string | required | Exact invocation pattern (slash, keyword, or event) |
| phases | list[string], 2-6 | required | Must match body `###` subsections 1:1 |
| when_to_use / when_not_to_use | list[string], parallel | required | Precise routing vs. over-specification |
| sub_skills | list[string] | none | Delegation keeps a skill focused; avoids a "god skill" |

Source: `archetypes/builders/skill-builder/bld_schema_skill.md`.

## Patterns
| Pattern | Rule | Example |
|---|---|---|
| Phase alignment | frontmatter `phases` matches body `###` subsections 1:1 | one `phases` list, four matching headings below it |
| Canonical 4-phase shape | discover->configure->execute->validate: gather context, set params, run it, check quality | a commit skill: discover changes, configure message, execute commit, validate push |
| Slash-command trigger | `user_invocable: true` requires `/`-prefixed trigger | `/code-review` |
| Agent-invoked trigger | `user_invocable: false` + keyword/event, no slash | fires when a subagent's task matches the description |
| Sub-skill delegation | Delegate via `sub_skills`; never re-implement inline | a deploy skill delegates to a run-tests skill |

## Anti-Patterns
| Anti-Pattern | Why It Fails |
|---|---|
| Persona language ("You are...") in the body | Skills carry no identity; belongs in `agent` / `system_prompt` |
| `phases` mismatched to body subsections | Hard gate failure -- names must be 1:1 |
| `user_invocable: true` with non-slash trigger | Schema violation |
| Single monolithic phase | Loses the phase contract; minimum 2 |

## Integration Graph
```
[trigger: slash|keyword|event] --> [skill] --> [phase_1 -> phase_2 -> ... -> phase_N]
                                        |
                          [sub_skills delegation, allowed tools]
```

## Decision Tree
- IF the artifact needs identity/persona THEN `agent` (P02), not skill
- IF one single-turn instruction with no phases THEN `action_prompt` (P03)
- IF it orchestrates multiple roles/nuclei across steps THEN `workflow` (P12)
- IF it reacts to a system EVENT rather than being invoked THEN `hook` (P04)
- DEFAULT: `skill` for any reusable, phase-structured, triggered capability

## Quality Criteria
- GOOD: all required fields present; `phases` matches subsections 1:1; description <=120 chars
- GREAT: 2+ concrete examples; `when_not_to_use` as precise as `when_to_use`; `sub_skills` over a monolith
- FAIL: persona language in body; phases/subsections mismatched; invocable without slash trigger

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[p01_kc_hook]] | sibling P04 capability kind | 0.35 |
| [[p01_kc_agent]] | boundary (NOT -- carries identity) | 0.42 |
| [[p01_kc_action_prompt]] | boundary (NOT -- single-turn) | 0.40 |
| [[p01_kc_workflow]] | boundary (NOT -- cross-role orchestration) | 0.38 |
| [[p01_kc_function_def]] | dependency (depends_on) | 0.36 |
