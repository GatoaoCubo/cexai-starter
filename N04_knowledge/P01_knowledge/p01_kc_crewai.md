---
quality: null
id: p01_kc_crewai
kind: knowledge_card
8f: F3_inject
kc_type: industry_reference
pillar: P01
nucleus: n04
version: 1.0.0
created: "2026-05-05"
updated: "2026-05-05"
author: n04_knowledge
title: "CrewAI -- Role-Based Multi-Agent Orchestration"
domain: ai_agent_systems
subdomain: industry_reference
tags: [crewai, multi_agent, role_based, sequential, hierarchical, consensus, industry_reference, comparison]
tldr: "CrewAI is the most adopted role-based multi-agent framework. Defines crews as a topology of Agents with roles + goals + backstories, executing tasks in sequential, hierarchical, or consensus process. CEXAI adopts the role/crew/process vocabulary verbatim (it became the WAVE8 primitives) but elevates it from runtime objects to typed artifacts in P02/P12."
keywords: [crewai, crew, agent, role, goal, backstory, task, process, sequential, hierarchical, consensus, delegation, manager agent, planning, memory, kickoff]
density_score: 0.89
related:
  - p01_kc_langchain
  - p01_kc_dspy
  - kc_crew_template
---

# CrewAI — Role-Based Multi-Agent Orchestration

## Definition

CrewAI is an open-source Python framework (released October 2023 by Joao Moura) for orchestrating teams of LLM agents. Where LangChain treats an agent as a single executor with tools, CrewAI treats agent *teams* as the primitive: a `Crew` is a topology of `Agent`s, each with a role, goal, and backstory, executing `Task`s in a defined `Process`. It became the canonical reference for "multi-agent" patterns and its vocabulary now appears in nearly every framework that ships role-based agents (LangGraph supervisors, AutoGen group chat, OpenAI Swarm).

## Key Concepts

| Primitive | Meaning | CEXAI analogue |
|-----------|---------|----------------|
| `Agent` | LLM with role + goal + backstory + allowed tools + delegation flag | `agent` kind (P02) |
| `Role` | Job title (e.g. "Senior Researcher") that frames the agent's identity | embedded in `role_assignment` kind (P02) |
| `Goal` | Single-sentence objective the agent optimizes for | `role_assignment.goal` field |
| `Backstory` | Persona narrative that conditions style and judgement | `role_assignment.backstory` field |
| `Task` | Unit of work: description + expected_output + agent + tools | `workflow_node` kind (P12) |
| `Crew` | Container of agents + tasks + process + memory | `crew_template` kind (P12) |
| `Process.sequential` | Tasks run in declared order; output of N feeds task N+1 | `crew_template.process: sequential` |
| `Process.hierarchical` | Manager agent coordinates workers; may delegate | `crew_template.process: hierarchical` |
| `Process.consensus` | All agents vote / aggregate (recently added) | `crew_template.process: consensus` |
| `Manager LLM` | Dedicated model for the manager agent in hierarchical mode | `nucleus_def` (N07-style) |
| `Memory` | Short-term + long-term + entity + contextual stores | `memory_architecture` (P10) |
| `Planning` | Pre-execution plan generation step | F4 REASON (8F) |
| `Kickoff` | Method that runs the crew end-to-end | `cex_crew.py run` |

## What CEXAI Adopts

1. **The role/crew/process trinity is canonical.** CEXAI's WAVE8 primitives (`crew_template`, `role_assignment`, `team_charter`, `nucleus_def`, `capability_registry`) are direct descendants of CrewAI vocabulary. We use the same words because CrewAI established the contract.
2. **Three process topologies.** Sequential, hierarchical, consensus map 1:1. CEXAI's `cex_crew.py` accepts the same enum.
3. **Goal + backstory as identity scaffolding.** Empirically these short narrative fields measurably improve LLM consistency; CEXAI keeps them in `role_assignment`.
4. **Manager-coordinator pattern.** N07 Orchestrator is essentially a manager agent at the *system* level. The same hierarchical pattern recurses inside crews when `process: hierarchical` is set.
5. **Pre-execution planning step.** CrewAI's `planning=True` produces a plan before execution; CEXAI's F4 REASON does the same and is mandatory.
6. **Memory as a first-class feature of the crew.** CEXAI's P10 pillar (memory_architecture, entity_memory, episodic_memory, working_memory, prospective_memory) is a denser version of CrewAI's memory module.

## What CEXAI Differs

1. **Crews are artifacts, not Python objects.** A CrewAI `Crew` lives in code: `Crew(agents=[...], tasks=[...])`. A CEXAI crew_template is a `.md` file with frontmatter, version-controlled, peer-scored, runtime-portable. You can ship a crew without shipping Python.
2. **Roles bind to nuclei, not free-form personas.** CrewAI lets you write any role string. CEXAI roles are typically bound to one of the 7 nuclei (N01..N07) with their fixed sin lens — Analytical Envy for research, Knowledge Gluttony for indexing, etc. This forces architectural consistency across crews.
3. **8F pipeline runs *inside* every role.** CrewAI's task execution is a single LLM call with optional tools. In CEXAI each role runs a full F1-F8 pipeline internally — F3 INJECT, F7 GOVERN, F8 COLLABORATE all happen per-role.
4. **Charter as a quality contract.** CEXAI separates `crew_template` (the recipe) from `team_charter` (the per-instance contract: budget, deadline, quality gate). CrewAI conflates them. The split lets one template serve many missions.
5. **Grid-of-crews as a first-class composition.** CEXAI explicitly supports running N crew instances in parallel via `Task tool: dispatch grid` — N parallel packages, each with its own charter. CrewAI does not have a native grid concept; you write Python loops.
6. **Multi-runtime, not Python-only.** A CEXAI crew_template can dispatch roles to Claude, Codex, Gemini, or Ollama — chosen per role via `nucleus_models.yaml`. CrewAI is Python + LangChain integrations.
7. **No agent self-delegation by default.** CrewAI's `allow_delegation=True` lets an agent ask another agent. CEXAI requires delegation through N07 (the orchestrator) to keep the audit trail intact.

## When to Reach for CrewAI Directly

Use CrewAI when prototyping a 3-5 role flow that fits inside a single Python script and doesn't need: typed persistence, multi-runtime portability, or compliance-grade quality gates. For anything that will be re-run, audited, or migrated across providers, write a CEXAI `crew_template` instead — same vocabulary, durable substrate.

## Related Artifacts

| Artifact | Relationship |
|----------|-------------|
| [[p01_kc_langchain]] | sibling industry reference |
| [[p01_kc_dspy]] | sibling industry reference |
| [[kc_crew_template]] | direct CEXAI implementation |
| p12_ct_product_launch | example crew built on this model |
