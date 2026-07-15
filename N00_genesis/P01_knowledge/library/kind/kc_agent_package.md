---
id: p01_kc_agent_package
kind: knowledge_card
8f: F3_inject
type: kind
pillar: P02
title: "Portable Agent ISO -- Deep Knowledge for agent_package"
version: 2.0.0
created: 2026-03-30
updated: 2026-05-28
author: n04
domain: agent_package
quality: null
tags: [agent_package, p02, BECOME, kind-kc, iso, portable]
tldr: "Build an agent once from the 12 pillars, run it anywhere -- Custom GPT, Gemini Gem, Claude Project, Railway. The ISO format packages agents the way npm/pip package code."
when_to_use: "Building, reviewing, or porting an agent_package to any LLM surface"
keywords: [iso, portable, bundle, 12-pillar-fractal, full-lean-profiles, degraded-mode]
density_score: null
related:
  - p01_kc_agent
  - agent-package-builder
  - bld_model_agent_package
  - spec_agent_bundle_export
---

# Portable Agent ISO (agent_package)

## Spec
```yaml
kind: agent_package
llm_function: BECOME
max_bytes: 4096
naming: agents/{{agent_name}}/manifest.yaml
```

## What It Is
A self-contained, LLM-agnostic bundle that makes an agent portable: build ONCE from the 12
pillars, load into ANY surface. **npm/pip/docker package code; the ISO format packages
agents.** Built two ways -- the **meta-builder** prompt or **CEX-native**
(`agent-package-builder` + `cex_compile.py`); both emit the same artifact. NOT
the `agent` spec -- this is the deployable container.

## The 12-Pillar Fractal (horizontal contract)
Mirrors CEX's architecture: read one bundle, read them all.
- **HORIZONTAL (same in every agent):** 12 pillars P01..P12 (fixed order + meaning) +
  `00_instructions.md` (+1). P07 ALWAYS quality; P09 ALWAYS config.
- **VERTICAL (per agent):** the CONTENT of each pillar. Same 1:1 ISO<->pillar law CEX uses.

| Pillar | ALWAYS contains |
|--------|-----------------|
| P01 knowledge | Domain facts, rules, taxonomies |
| P02 model | Identity: persona, role, voice, expertise |
| P03 prompt | Generation recipes / templates |
| P04 tools | Capabilities + WHEN + manual substitute |
| P05 output | Output contracts: format + example |
| P06 schema | I/O schema: inputs, validation |
| P07 evaluation | Quality gates: rubric, self-check |
| P08 architecture | Pipeline: stages, decision logic |
| P09 config | Parameters, limits, defaults |
| P10 memory | Context, handoffs, state |
| P11 feedback | Guardrails, anti-hallucination, NEVER-do |
| P12 orchestration | The executable operating loop |

`00_instructions.md` (+1): compact prompt, **<= 8000 chars**, 6-section anatomy -- Identity /
Knowledge base / Operating procedure / Tools / Unbreakable rules / Output.

## Two Profiles (one source of truth)
| Profile | Files | Platform |
|---------|-------|----------|
| FULL | 13 (00_instructions + P01..P12) | Custom GPT, Claude Project, Railway |
| LEAN | 5 (P01-P05) + lean instructions | ChatGPT Projects (free), Gemini Gem |

LEAN derives from FULL: fold P06-P12 into the 5 (limits->P05; anti-hallucination->lean
instructions, MANDATORY; input->P03). Fewer FILES, not thinner content.

## The 3 Universal Rules (NON-NEGOTIABLE)
| Rule | What | Lives in |
|------|------|----------|
| 1 Anti-hallucination | Truth = user input; never fabricate numbers/certs/prices; gap -> ask or `[FILL]`; MANDATORY closing "## Assumptions to confirm" | 00_instr, P06, P07, P11 |
| 2 Paste-intake | Never assume a URL opens (bots blocked); ask user to paste from THEIR browser | P04, P06, P11 |
| 3 Code-block output | Deliverables inside fenced blocks (one per unit); chatter outside | P05, instr |

(= runtime constitution: `ground_or_abstain` + `untrusted_input`.)

## Honest Degradation (degraded_mode)
STANDALONE: NEVER invent backend/scraper/API access it lacks. Where a function needed absent
infra: (1) declare the limit (P04/P11); (2) offer the native substitute (web browsing, code
interpreter) or a manual step. Reflect in `manifest.fidelity` + `fidelity_reason`. Live > spec.

## Cross-Platform Targets
**Custom GPT** (FULL): `cex_compile.py --target customgpt`,
pillars->Knowledge. **ChatGPT Projects** (free, LEAN): lean instructions + 5 files (cap 5).
**Gemini Gem** (LEAN): instructions->Gem (native export = gap). **Claude Project / Cursor**
(FULL): `--target claude-md` / `cursorrules`. **Railway/SaaS** (FULL): manifest+pillars as
system context + `actions/`->function-calling. Tiers: minimal 3 | standard 7 | complete
13=FULL | whitelabel 13 + `{{VAR}}` + LEAN.

## Anti-Patterns
| Anti-Pattern | Fix |
|--------------|-----|
| No "Assumptions to confirm" block | Mandatory closing block (Rule 1) |
| Bundle assumes it can fetch a URL | Paste-intake (Rule 2) |

## Quality Criteria
GREAT: 13 FULL + LEAN in sync; instructions <= 8000 chars; 3 rules; honest degradation; gate
>= 8.0. FAIL: hardcoded paths; no assumptions block; promises absent infra.

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[kc_agent]] | sibling | 0.48 |
| [[agent-package-builder]] | downstream | 0.46 |
| bld_model_agent_package | downstream | 0.42 |
| spec_agent_bundle_export | related | 0.36 |
