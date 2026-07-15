---
name: taxonomy-check-before-new-kind
description: Run the 5-question composability test before introducing any new kind so the 125-kind taxonomy stays intentional and gaps are filled by composition first.
when:
  - User proposes "let us create a new kind" or similar add-a-kind intent.
  - A nucleus is about to register an entry in `.cex/kinds_meta.json` for a name that does not yet exist.
  - A spec or plan calls out a missing concept that might be covered by composing existing kinds.
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
tags: [skill, autofire, taxonomy, governance, autowire, layer6]
related:
  - composable-crew
  - p06_td_cex_artifact_type_n03
---

> **[DISTILL ANNOTATION]** This file cites tool(s) not shipped in this tenant (Central-only): cex_kind_register, cex_taxonomy_scout. Inline citations are marked `[NOT SHIPPED in this tenant -- Central-only tool]`.

# Taxonomy Check Before New Kind

## When this fires
- User asks to add a new kind (any phrasing: "create a new kind", "registrar tipo novo", "add to kinds_meta").
- A nucleus is about to write to `.cex/kinds_meta.json` with a name that has no existing entry.
- A spec proposes a concept that overlaps with an existing kind family.

## What to do
1. Run the 5-question composability test from `.claude/rules/composable-crew.md` BEFORE proposing the new kind:
   - Q1: Can this be expressed as composition of 2+ existing kinds?
   - Q2: Is this a new pillar concept or just a new naming for an existing one?
   - Q3: Does it have a unique frontmatter shape, or can existing schemas absorb it?
   - Q4: Will the boundary table (`boundary` in kinds_meta) clearly distinguish it from neighbors?
   - Q5: Is the artifact lifecycle different from existing kinds?
2. If 0-2 questions return YES, prefer composition. Document the gap in a knowledge_card and stop here.
3. If 3+ return YES, draft the kind via `python _tools/cex_taxonomy_scout.py --propose <name>` (auto-PR with confidence score).  <!-- [NOT SHIPPED in this tenant -- Central-only tool] -->
4. Validate the new entry's `boundary` field is concrete and contrasts with the closest sibling kind.
5. After approval, register via `python _tools/cex_kind_register.py --apply` and create the matching builder + KC + sub-agent + schema entries.  <!-- [NOT SHIPPED in this tenant -- Central-only tool] -->
6. Never bypass the test; an undisciplined kind taxonomy erodes the system's typed knowledge guarantees.

## Example
- User proposes a `marketing_brief` kind. Skill runs the 5Q test: Q1 YES (composable as `prompt_template` + `decision_record`), Q2 NO, Q3 NO, Q4 NO, Q5 NO. Verdict: do NOT add the kind. Skill writes a knowledge_card showing how to compose `prompt_template` + `decision_record` to satisfy the use case.

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| composable-crew | upstream | 0.90 |
| p06_td_cex_artifact_type_n03 | upstream | 0.60 |
