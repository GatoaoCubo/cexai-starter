---
id: kc_orchestration_vocabulary
kind: knowledge_card
8f: F3_inject
pillar: P01
nucleus: n07
title: "N07 Orchestration Domain Controlled Vocabulary"
version: "1.0.0"
created: "2026-04-26"
author: n04_knowledge
domain: orchestration
type: controlled_vocabulary
quality: null
tags: [controlled_vocabulary, ubiquitous_language, n07, orchestration_terms, orchestrating_sloth, canonical]
tldr: "Canonical vocabulary for N07 Orchestration domain: 20 terms mapped to industry definitions, N07 application, and anti-patterns. This KC makes N07 think in correct orchestration terminology automatically."
keywords: [multi-agent orchestration, dispatch, grid, wave, crew, consolidation, GDP, handoff, session management, intent resolution]
density_score: 0.90
updated: "2026-04-26"
related:
  - kc_admin_vocabulary
---

<!-- 8F: F1 constrain=P01/knowledge_card F2 become=knowledge-card-builder F3 inject=ubiquitous-language-rule+spec_metaphor_dictionary+n07-orchestrator-rules+composable-crew F4 reason=vocabulary KC captures all N07 orchestration terms mapped to industry standards F5 call=cex_compile F6 produce=kc_orchestration_vocabulary.md F7 govern=frontmatter+ascii+tables F8 collaborate=N07_admin/P01_knowledge/ -->

## Purpose

This KC implements the Ubiquitous Language Protocol (`.claude/rules/ubiquitous-language.md`)
for the N07 Orchestration domain.

Loading this KC at F2b SPEAK ensures that:
- All N07 outputs use canonical orchestration and distributed systems terms
- CEX metaphors are transmuted to industry terms automatically
- Cross-nucleus communication is unambiguous (LLM-to-LLM interoperability)
- Vocabulary drift is prevented over time

## Canonical Vocabulary (20 Terms)

| Term | Industry Definition | N07 Domain Application | Anti-Pattern (Never Use) |
|------|-------------------|----------------------|--------------------------|
| dispatch | sending a task to a worker agent via structured specification | N07's primary action: write handoff to .cex/runtime/handoffs/, call monitor | "send", "assign", "give task to" |
| handoff | structured task document specifying inputs, context, and expected outputs for an agent | N07 writes handoffs; nuclei read them on boot at .cex/runtime/handoffs/n0X_task.md | "task file", "instructions", "brief" |
| grid | parallel dispatch topology where multiple agents execute concurrently | N07 dispatches grids for multi-nucleus missions via the Task tool grid | "parallel run", "multi-agent batch" |
| wave | sequential execution phase grouping parallel dispatches with a gate between phases | N07 organizes mission execution into waves; gate must pass before next wave | "phase", "stage", "round" |
| crew | multi-role agent team with inter-role handoffs producing one coherent deliverable | N07 assembles crews from capability_registry; 3 topologies: sequential, hierarchical, consensus | "team", "group", "squad" |
| solo | single-agent dispatch for focused single-builder tasks | N07 uses solo when exactly one nucleus is needed: the Task tool solo n03 "task" | "single run", "one agent" |
| signal | JSON completion event written by agent after task execution (event-driven architecture) | N07 monitors .cex/runtime/signals/ to detect wave completion and trigger consolidation | "status", "done message", "notification" |
| consolidate | post-execution verification: validate deliverables, terminate processes, run diagnostics, commit | N07's mandatory step after every wave: doctor check, process cleanup, git commit, archive | "wrap up", "finalize", "clean up" |
| mission | end-to-end goal decomposed into waves, dispatches, quality gates, and consolidation cycles | N07's highest-level orchestration unit; spans plan -> guide -> spec -> grid -> consolidate | "project", "big task", "initiative" |
| schedule | time-based trigger for recurring or deferred task execution (kind: schedule, P12) | N07 manages cron schedules for overnight evolve, periodic audits, and deferred dispatch | "timer", "recurring task" |
| workflow | directed acyclic graph of steps with conditions, branching, and error handling (kind: workflow) | N07 designs workflows for complex multi-step orchestration processes | "process", "flow" (never "pipeline" -- that means 8F) |
| GDP | Guided Decision Protocol: framework for separating subjective (user) from objective (LLM) decisions | N07 activates GDP before any mission with tone, audience, style, or brand decisions | "asking the user", "getting input" |
| decision_manifest | serialized record of all GDP decisions for a mission, consumed by autonomous nuclei | N07 writes to .cex/runtime/decisions/decision_manifest.yaml; nuclei read, never re-ask | "decision file", "user choices" |
| PID_tracking | process lifecycle monitoring for spawned agent processes with session isolation | N07 tracks in .cex/runtime/pids/spawn_pids.txt: {pid} {nucleus} {cli} {session_id} {timestamp} | "process monitoring" |
| session_id | unique orchestrator instance identifier enabling safe multi-N07 concurrent operation | N07 tags spawned processes; stop kills only same-session PIDs by default | "run ID", "instance ID" |
| intent_resolution | mapping user natural language to structured action tuple {kind, pillar, nucleus, verb} | N07's F1 CONSTRAIN step via prompt_compiler + cex_intent_resolver.py | "understanding what the user wants" |
| swarm | parallel dispatch of N builders of the same kind for breadth/variant generation | N07 uses swarm when goal is coverage, not integration: the Task tool swarm agent 5 "task" | "mass dispatch", "bulk build" |
| depth_amplifier | task enrichment technique that increases handoff complexity (multi-artifact, cross-ref, research) | N07 requires 3+ depth amplifiers per handoff to maximize nucleus context utilization | "making it harder", "extra work" |
| tree_kill | cascading process termination that kills parent and all descendants | N07 uses taskkill /F /PID /T; never Stop-Process (orphans workers) | "kill process", "stop it" |
| preflight | multi-phase context preparation before dispatch: MCP gather, TF-IDF retrieval, Haiku reranking | N07 runs cex_preflight.py for external context injection into handoffs | "preparation", "setup phase" |

## Cross-Nucleus Shared Terms (DO NOT REDEFINE HERE)

These terms are defined in N00_genesis and are imported, not redefined:

| Term | Definition Source | N07 Application |
|------|-----------------|----------------|
| 8F pipeline | `.claude/rules/8f-reasoning.md` | N07 follows F1-F8 for orchestration reasoning |
| kind | `.cex/kinds_meta.json` | N07 resolves user intent to kinds via prompt_compiler |
| pillar | N00_genesis P01-P12 | N07 routes to nuclei based on pillar ownership |
| quality_gate | P07 definition | N07 enforces wave_gate between dispatch phases |
| signal | F8 COLLABORATE convention | N07 reads signals: .cex/runtime/signals/signal_n0X_*.json |
| density_score | N00_genesis schema | N07 validates density >= 0.85 in consolidated artifacts |

## Trigger Phrases -> Dispatch Activation

| User Phrase | Activates Mode | Action |
|-------------|---------------|--------|
| "build", "create", "scaffold", "make me" | SOLO dispatch | intent_resolution -> kind -> nucleus -> solo dispatch |
| "mission", "launch all", "full pipeline" | GRID dispatch | GDP -> decision_manifest -> wave plan -> grid dispatch |
| "research", "analyze", "investigate" | N01 route | dispatch to N01 with research handoff |
| "write copy", "marketing", "campaign", "landing page" | N02 route | dispatch to N02 with marketing handoff |
| "deploy", "test", "fix", "CI", "MCP" | N05 route | dispatch to N05 with operations handoff |
| "price", "monetize", "course", "funnel" | N06 route | dispatch to N06 with commercial handoff |
| "guide me", "ask me first", "let's decide" | GDP mode | activate Guided Decision Protocol, present decision points |
| "status", "what's running", "check progress" | Monitor mode | the Task tool status + git log + signal scan |
| "stop", "kill", "clean up" | Consolidate mode | tree_kill processes + doctor check + archive signals |
| "overnight", "evolve", "improve all" | Batch mode | overnight.ps1 or cex_evolve.py sweep |

## Vocabulary Load Protocol

At F2b SPEAK:
```
load: N07_admin/P01_knowledge/kc_orchestration_vocabulary.md
load: _docs/specs/spec_metaphor_dictionary.md (Industry term column)
load: N00_genesis/P03_prompt/layers/p03_pc_cex_universal.md (prompt_compiler)
activate: drift_prevention = True
```

All subsequent F3-F8 output must use terms from this KC.
Violation detection: F7 GOVERN checks for vocabulary compliance in handoffs.

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| [[kc_admin_vocabulary]] | sibling | 0.51 |
| n00_p12_kind_index | sibling | 0.43 |
| skill_catalog_cex | sibling | 0.42 |
| p01_kc_orchestration_best_practices | sibling | 0.41 |
| p12_wf_orchestration_pipeline | downstream | 0.40 |
