---
name: crew-on-multi-role
description: Route work to a composable crew when the user mentions team or crew or multiple agents instead of building a single artifact solo.
when:
  - User input contains words like team, crew, multiple agents, squad, or sequential roles.
  - The deliverable requires N specialists with handoffs (research then copy then design then QA).
  - A single builder cannot cover the deliverable but the work is one coherent package.
kind: skill
pillar: P04
nucleus: all
quality: null
version: 1.0.0
created: 2026-04-27
updated: 2026-04-27
multi_runtime: true
runtimes: [claude, codex, gemini, ollama]
density_score: 0.85
tags: [skill, autofire, crew, multi-role, composable, autowire, layer6]
related:
  - composable-crew
  - crew_template
---

# Crew on Multi Role

## When this fires
- User input contains team, crew, multiple agents, squad, or sequential roles.
- The deliverable is one coherent package (launch kit, RFP response, postmortem, course).
- Multiple specialties are needed AND they must hand off artifacts to each other.

## What to do
1. Run `python _tools/cex_crew.py list` to discover existing crew_template artifacts.
2. If a matching crew exists, run `python _tools/cex_crew.py show <name>` to inspect roles, process topology, and required charter fields.
3. Author or reuse a `team_charter` artifact with mission, budget, deadline, and quality gate.
4. Execute via `python _tools/cex_crew.py run <name> --charter <charter_path> --execute`.
5. Pick topology by load: sequential (each role waits for prior artifact), hierarchical (manager + workers, 5+ roles), consensus (parallel + vote).
6. Use crew when roles need handoffs. Use grid when N independent artifacts of different kinds. Use swarm when N parallel builders of the same kind. Never crowbar a crew where a solo build suffices.

## Example
- User asks for a complete product launch package. Skill discovers `product_launch` crew (4 roles, sequential). N07 writes a charter (mission: launch X, deadline 2026-05-15, budget 30K tokens) and runs the crew; research -> copy -> design -> QA produces the package.

## Related Artifacts
| Artifact | Relationship | Score |
|----------|-------------|-------|
| composable-crew | upstream | 0.85 |
| crew_template | sibling | 0.75 |
