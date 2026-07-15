---
name: dispatch-before-build
description: STOP before any Write/Edit on artifact territory paths from N07. Force dispatch routing to the correct nucleus via cex_capability_index + cex_intent_resolver. Block authorial creation of typed artifacts from the orchestrator session — only N03/N02/N04 etc. own those paths. Bypasses allowed for N07 SAFE paths (handoffs, decisions, runtime state, dashboard, skills, specs) and explicit surgical edits.
when:
  - User input matches authorial intent keywords (criar/escrever/produzir/build/write/refine/refactor/redo) combined with artifact nouns (module/aula/copy/script/roteiro/conteudo/artifact/módulo/lesson/kind).
  - Claude (N07) is about to call Write/Edit on a path inside artifact territory (_courses/video_series/cexai_modules/, N0*/P*/, archetypes/builders/, N00_genesis/P*/).
  - A planned tool call would author NEW typed-kind content (course_module, knowledge_card, prompt_template, agent, etc.) from an N07 session.
kind: skill
pillar: P12
nucleus: n07
quality: null
version: 1.0.0
created: "2026-05-21"
updated: "2026-05-21"
multi_runtime: true
runtimes: [claude, codex, gemini, ollama]
density_score: 0.90
tags: [skill, autofire, governance, dispatch, layer6, n07_enforcement, anti_violation]
related:
  - intent_resolution
  - gdp_on_subjective
  - n07-orchestrator
---

> **[DISTILL ANNOTATION]** This file cites tool(s) not shipped in this tenant (Central-only): cex_capability_index. Inline citations are marked `[NOT SHIPPED in this tenant -- Central-only tool]`.

# Dispatch Before Build

> **The core rule this enforces**: per `CLAUDE.md`, *N07 NEVER builds artifacts*.
> Documentation alone has failed (proven by repeat violations). This skill is the
> active guardrail: it intercepts authorial intent and forces routing decision
> BEFORE any tool call hits the filesystem.

## When this fires

Trigger A — **lexical match in user input**:
- Authorial verbs: `criar`, `crie`, `cria`, `escrever`, `escreva`, `produzir`, `produz`, `build`, `write`, `author`, `refine`, `refactor`, `redo`, `rework`, `reescrever`
- Combined with artifact nouns: `module`, `módulo`, `aula`, `lesson`, `copy`, `script`, `roteiro`, `conteúdo`, `artifact`, `kind`, `card`, `agent`, `prompt`, `workflow`, `schema`

Trigger B — **path match before tool call**:
The skill MUST intercept when a planned `Write` or `Edit` would land in one of these paths:
- `_courses/video_series/cexai_modules/*`
- `_courses/video_series/<internal-era-brand>_modules/*` (legacy)
- `N0*_*/P*/*.md` (any nucleus artifact)
- `N0*_*/P*/compiled/*.yaml`
- `archetypes/builders/*/bld_*.md`
- `N00_genesis/P*/*.md`
- `_docs/products/*.md`

Trigger C — **the planned content matches a typed kind**:
Even if the path looks innocent, if the body would author one of the 125 kinds in
`.cex/kinds_meta.json` (course_module, knowledge_card, prompt_template, agent,
workflow, retriever, etc.), the work belongs to the kind's owning nucleus, not N07.

## What to do (decision tree)

```
[planned Write/Edit on path P]
         │
         ▼
┌─────────────────────────┐
│ Is P in N07 SAFE list?  │
│ (handoffs/decisions/    │
│  signals/dashboard/     │
│  skills/specs/runtime)  │
└──────────┬──────────────┘
           │
   ┌───────┴───────┐
  YES             NO
   │               │
   ▼               ▼
 PROCEED      ┌─────────────────────────────┐
              │ Did user ask for SURGICAL   │
              │ edit (fix typo / rename /   │
              │ adjust line X)?             │
              └────────────┬────────────────┘
                           │
                  ┌────────┴────────┐
                 YES               NO
                  │                 │
                  ▼                 ▼
              PROCEED         ┌───────────────────────┐
              (narrow scope)  │ DISPATCH PROTOCOL     │
                              │ 1. Run                │
                              │ cex_intent_resolver.py│
                              │ 2. Get tuple          │
                              │ {kind, pillar,        │
                              │  nucleus, verb}       │
                              │ 3. If conf >= 0.6 →   │
                              │ the Task tool solo nXX  │
                              │ 4. If conf < 0.6 →    │
                              │ fire gdp-on-subjective│
                              └───────────────────────┘
```

## N07 SAFE paths (direct Write/Edit allowed)

These paths represent orchestration state, not authored content:

- `.cex/runtime/handoffs/*` — mission handoffs N07 writes for nuclei
- `.cex/runtime/decisions/*` — GDP decision manifests
- `.cex/runtime/signals/*` — completion signals
- `.cex/runtime/archive/*` — archived state
- `_courses/video_series/_dashboard.html` — orchestration dashboard
- `_courses/video_series/_*.yaml` — orchestration config (visual_manifest, brand_config)
- `.claude/skills/*.md` — skill catalog (N07 maintains this)
- `_docs/specs/*.md` — system architecture specs
- `CLAUDE.md` + `.claude/rules/*.md` — governance docs
- `MEMORY.md` + `memory/*.md` — auto-memory store

## Surgical-edit bypass

If user input explicitly scopes the change to one of these forms, N07 may edit directly:
- "Fix typo in line N of file X"
- "Rename variable Y to Z in file X"
- "Update timestamp in line N"
- "Change color #FF1493 to #D85A88 wherever it appears" (mechanical find-replace)
- "Remove the deprecated section about Y"

These are mechanical, not authorial. They don't require nucleus context.

## Authorial work — MUST dispatch

These are authorial and MUST dispatch:
- "Write the script for M00.2"
- "Produz o roteiro do módulo X"
- "Refactor M00.1 with new direction"  ← yes, even refactor is authorial if it changes content/voice
- "Create a knowledge card about Y"
- "Refine the M00.1 copy with deeper CEXAI vocabulary"
- "Add 3 new sections to the M01 spec"

## How to dispatch (concrete commands)

```bash
# Solo dispatch (1 nucleus, 1 task)
# in-session dispatch (Task tool): solo n02 "execute MODULE_0_LEARNING_TRAIL_COPY mission"

# Read decision manifest first
cat .cex/runtime/decisions/decision_manifest.yaml

# Write handoff to .cex/runtime/handoffs/{MISSION}_{nucleus}.md
# AND copy to .cex/runtime/handoffs/{nucleus}_task.md (boot reads this)

# After dispatch, monitor:
# in-session dispatch (Task tool): status
git log --oneline --since="3 minutes ago"
```

## Anti-patterns (BLOCKED)

| Pattern | Why blocked | Correct path |
|---------|-------------|--------------|
| "Vou escrever rapidinho o M00.2" | Cumulative N07 building violation | Dispatch to N02 |
| "É só uma alteração pequena no script" if alteração = mudar voz/conteúdo | Authorial under scope-creep camouflage | Dispatch to N02 |
| "Deixa que eu faço o roteiro agora" | Explicit role violation | Dispatch to N02 |
| Skipping `cex_capability_index.py` check | No catalog reference = blind routing | Always check catalog first |
| Editing `cexai_modules/*.md` from N07 session | Authorial path | Dispatch to N02 |

## Cross-references at runtime

- Catalog of nuclei + builders: `.cex/P09_config/dispatch_catalog.md`
- Live intent resolver: `python _tools/cex_intent_resolver.py --input "<phrase>" --json`
- Capability index query: `python _tools/cex_capability_index.py --query "<keyword>"`  <!-- [NOT SHIPPED in this tenant -- Central-only tool] -->
- Dispatch CLI: `Task tool: dispatch solo|grid <nucleus> "<task>"`
- GDP for subjective decisions: gdp_on_subjective
- Intent transmutation: intent_resolution

## Related Artifacts

| Artifact | Relationship | Score |
|----------|-------------|-------|
| intent_resolution | sibling skill (resolves the tuple this skill routes on) | 0.85 |
| gdp_on_subjective | downstream (called when intent confidence low) | 0.80 |
| n07-orchestrator | upstream rule (the rule this enforces) | 0.90 |
