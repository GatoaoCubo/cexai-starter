---
name: gdp-on-subjective
description: Invoke the /guide skill whenever a decision involves tone, audience, style, or other subjective dimensions instead of guessing for the user.
when:
  - A pending decision involves tone, audience, voice, brand style, color palette, or copywriting choices.
  - F4 REASON identifies a subjective fork the decision_manifest does not cover.
  - The user said /guide or used phrases like "ask me first" or "walk me through".
kind: skill
pillar: P04
nucleus: all
quality: null
version: 1.0.0
created: 2026-04-27
updated: 2026-04-27
multi_runtime: true
runtimes: [claude, codex, gemini, ollama]
density_score: 0.86
tags: [skill, autofire, gdp, decisions, autowire, layer6]
related:
  - guided-decisions
  - skill_guided_decisions
  - n07-orchestrator
  - 8f-reasoning
---

# GDP on Subjective

## When this fires
- F4 REASON or F1 CONSTRAIN reaches a subjective decision point (tone, audience, palette, voice, message hierarchy).
- The active decision_manifest does NOT cover the fork.
- The user explicitly invoked /guide or asked CEX to "ask before deciding".

## What to do
1. Stop autonomous execution at the fork. Do NOT pick a direction silently.
2. Invoke /guide with the specific subjective question; present 2-4 viable options with one tagged `* Recommended` based on brand_config + prior decisions.
3. Wait for the user's choice. Record it in `.cex/runtime/decisions/decision_manifest.yaml` so future nuclei do not re-ask.
4. If the user enabled auto_accept on the handoff, apply the recommended default and log it to `.cex/runtime/decisions/autofilled/<ts>_<nucleus>.yaml` instead of blocking.
5. Never make the user re-answer a question already in the manifest -- read first, ask only on gaps.
6. Resume the 8F pipeline at F1 with the locked decision treated as a hard constraint.

## Example
- N02 builds ad copy. F4 needs a tone (formal | playful | urgent). Manifest is silent. Skill invokes /guide; user picks `playful`. Decision is written to manifest. F4 proceeds with playful as a hard constraint; subsequent waves never re-ask.

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| guided-decisions | upstream | 0.90 |
| [[skill_guided_decisions]] | sibling | 0.85 |
| n07-orchestrator | upstream | 0.60 |
| 8f-reasoning | upstream | 0.50 |
